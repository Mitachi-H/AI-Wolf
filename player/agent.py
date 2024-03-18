import configparser
import json
from lib import util
from lib.LLM.chatgpt_agent import ChatGPTAgent as ChatGPTAgent_class
from lib.AIWolf.commands import AIWolfCommand
from typing import List

class Agent:
    def __init__(self, inifile:configparser.ConfigParser, name:str) -> None:
       self.name = name
       self.role = None
       self.received = []
       self.gameContinue = True

       self.gameInfo = None
       self.gameTextRecords = []
       self.alive = []
       self.talkHistory = []

       randomTalk = inifile.get("randomTalk","path")
       _ = util.check_config(randomTalk)

       self.ChatGPTAgent = ChatGPTAgent_class()
       self.ChatGPTAgent_initialized = False

       self.comments = util.read_text(randomTalk)
    
    def set_received(self, received:list) -> None:
        self.received = received

    def parse_info(self, receive: str) -> None:

        received_list = receive.split("}\n{")

        for index in range(len(received_list)):
            received_list[index] = received_list[index].rstrip()

            if received_list[index][0] != "{":
                received_list[index] = "{" + received_list[index]

            if received_list[index][-1] != "}":
                received_list[index] += "}"

            self.received.append(received_list[index])
    
    def get_info(self):
        data = json.loads(self.received.pop(0))

        if data["gameInfo"]:
            self.old_gameInfo = self.gameInfo
            self.gameInfo = data["gameInfo"]
            self.find_gameInfo_difference()

        self.gameSetting = data["gameSetting"]
        self.request = data["request"]

        if data["talkHistory"]:
            self.add_talk_to_gameTextRecords(data["talkHistory"])

        self.whisperHistory = data["whisperHistory"]
   
    def add_talk_to_gameTextRecords(self, talkHistory: List[dict]) -> None:
        for talk in talkHistory:
            if talk["day"] == self.gameInfo["day"]:
                self.update_gameTextRecords(f"Day[{talk['day']}] idx[{talk['idx']}] Agent[0{talk['agent']}] said: {talk['text']}")

    def find_gameInfo_difference(self) -> None:
        # print("find_gameInfo_difference")
        def vote_text_list(voteList) -> List[str]:
            vote_text_list = []
            for vote in voteList:
                vote_text_list.append(f"Vote:Agent[0{vote['agent']}] -> Agent[0{vote['target']}]")
            return vote_text_list
        def divine_result_in_text(divine_result) -> str:
            if divine_result is None:
                return "占い結果なし"
            return f"Agent[0{divine_result['target']}]を占い、結果は{divine_result['result']}でした"
        def attackVoteList_in_text(attackVoteList) -> str:
            if len(attackVoteList) == 0:
                return "No attack vote"
            return f"AttackVote: Agent[0{attackVoteList[0]['agent']}] -> Agent[0{attackVoteList[0]['target']}]"

        if self.old_gameInfo is None or self.gameInfo is None:
            return
        
        # ignore_key_list = ["remain_talk_map", "remain_whisper_map", "latest_executedAgent", "latest_voteList", "status_map", "day", "talk_list", "latest_voteList", "role_map"]
        vote_key_list = ["voteList", "executedAgent"]
        action_key_list = ["divineResult", "attackVoteList", "attackedAgent"]
        for key in vote_key_list+action_key_list:
            if self.old_gameInfo[key] != self.gameInfo[key]:
                if key == "voteList":
                        self.update_gameTextRecords("=====Vote=====")
                elif key == "divineResult" or key == "attackVoteList":
                        self.update_gameTextRecords("=====Actions=====")
                game_text_record = f"{key}: {self.gameInfo[key]}"
                if key == "voteList":
                        newline = "\n"
                        game_text_record = f"{ newline.join(vote_text_list(self.gameInfo['voteList'])) }"
                elif key == "executedAgent":
                        
                        game_text_record = f"Agent[0{self.gameInfo['executedAgent']}] が処刑された"
                elif key == "divineResult":
                        game_text_record = divine_result_in_text(self.gameInfo["divineResult"])
                elif key == "attackVoteList":
                        game_text_record = attackVoteList_in_text(self.gameInfo["attackVoteList"])
                self.update_gameTextRecords(game_text_record)

    def update_gameTextRecords(self, game_text_record: str) -> None:
        # print(game_text_record)
        self.gameTextRecords.append(game_text_record)

    def initialize(self) -> None:
        self.index = self.gameInfo["agent"]
        self.role = self.gameInfo["roleMap"][str(self.index)]

        self.update_gameTextRecords("====================Game Start====================")
        self.update_gameTextRecords(f"me: Agent[0{self.index}]")
        self.update_gameTextRecords(f"my_role: {self.role}")
        if self.ChatGPTAgent_initialized == False:
            self.initialize_ChatGPTAgent()
    
    def initialize_ChatGPTAgent(self) -> None:
        self.ChatGPTAgent.initialize_openai_client()
        self.ChatGPTAgent.set_agent_idx(self.index)
        self.ChatGPTAgent.set_role(self.role)
        self.ChatGPTAgent_initialized = True

    def daily_initialize(self) -> None:
        # print("daily_initialize")
        game_text_record = f"==========Day {self.gameInfo['day']}=========="
        self.update_gameTextRecords(game_text_record)
        self.record_latest_killed()
        self.get_alive_agent_in_text()
        self.update_gameTextRecords("=====Talk=====")

    def record_latest_killed(self) -> None:
        if len(self.gameInfo['lastDeadAgentList']) == 0:
            return
        game_text_recod = [ f"Agent[0{agent}]" for agent in self.gameInfo['lastDeadAgentList']]
        self.update_gameTextRecords(f"昨晩の犠牲者: {game_text_recod}")
    
    def get_alive_agent_in_text(self) -> None:
        self.alive = []
        for agent_num in self.gameInfo["statusMap"]:
            if self.gameInfo["statusMap"][agent_num] == "ALIVE":
                self.alive.append(int(agent_num))

        alive_agent_in_text = [f"Agent[0{agent}]" for agent in self.alive]
        game_text_record = f"生存者: {alive_agent_in_text}"
        self.update_gameTextRecords(game_text_record)

    def daily_finish(self) -> None:
        pass
    
    def get_name(self) -> str:
        return self.name
    
    def get_role(self) -> str:
        return self.role
    
    def talk(self) -> str:
        if self.gameInfo["day"] in [0]:
            return "Over"
        # print(f"{self.name} talking")
        talk = self.ChatGPTAgent.talk(self.gameTextRecords)
        return talk

    def vote(self) -> str:
        vote = self.ChatGPTAgent.vote(self.gameTextRecords, self.alive)
        return vote

    def whisper(self) -> None:
        pass

    def finish(self) -> str:
        self.gameContinue = False

    def action(self) -> str:
        if AIWolfCommand.is_initialize(request=self.request):
            self.initialize()
        elif AIWolfCommand.is_name(request=self.request):
            return self.get_name()
        elif AIWolfCommand.is_role(request=self.request):
            return self.get_role()
        elif AIWolfCommand.is_daily_initialize(request=self.request):
            self.daily_initialize()
        elif AIWolfCommand.is_daily_finish(request=self.request):
            self.daily_finish()
        elif AIWolfCommand.is_talk(request=self.request):
            return self.talk()
        elif AIWolfCommand.is_vote(request=self.request):
            return self.vote()
        elif AIWolfCommand.is_whisper(request=self.request):
            self.whisper()
        elif AIWolfCommand.is_finish(request=self.request):
            self.finish()
        
        return ""
    
    def hand_over(self, new_agent) -> None:
        # __init__
        new_agent.name = self.name
        new_agent.received = self.received
        new_agent.gameContinue = self.gameContinue
        new_agent.comments = self.comments
        new_agent.received = self.received

        # get_info
        new_agent.gameInfo = self.gameInfo
        new_agent.gameSetting = self.gameSetting
        new_agent.request = self.request
        new_agent.talkHistory = self.talkHistory
        new_agent.whisperHistory = self.whisperHistory

        # initialize
        new_agent.index = self.index
        new_agent.role = self.role

        new_agent.role = self.role
        new_agent.gameTextRecords = self.gameTextRecords
        new_agent.alive = self.alive
        new_agent.talkHistory = self.talkHistory

        new_agent.ChatGPTAgent = self.ChatGPTAgent
        new_agent.ChatGPTAgent_initialized = self.ChatGPTAgent_initialized
