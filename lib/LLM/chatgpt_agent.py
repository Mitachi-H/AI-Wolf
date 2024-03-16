from lib.LLM.openai_client import OpenAIClient
from typing import List
import os, json, re

class ChatGPTAgent(OpenAIClient):
    def __init__(self) -> None:
        super().__init__()
        self.agent_idx = None
        self.role = None
        self.prompts_loaded = False
    
    def set_agent_idx(self, agent_idx: int) -> None:
        self.agent_idx = agent_idx

    def set_role(self, role: str) -> None:
        self.role = role

    def load_prompts(self) -> None:
        files = [f for f in os.listdir('lib/LLM/prompts') if f.endswith('.txt')]
        for file in files:
            with open(f'lib/LLM/prompts/{file}', 'r') as f:
                var_name = os.path.splitext(file)[0]
                setattr(self, var_name, f.read())
        
        files = [f for f in os.listdir(f'lib/LLM/prompts/{self.role}') if f.endswith('.txt')]
        for file in files:
            with open(f'lib/LLM/prompts/{self.role}/{file}', 'r') as f:
                var_name = os.path.splitext(file)[0]
                setattr(self, var_name, f.read())

        self.prompts_loaded = True
    
    def talk(self, gameTextRecords: List[str]) -> str:
        # print("gameTextRecords")
        # print(gameTextRecords)
        if not self.prompts_loaded:
            self.load_prompts()

        system = f"""
あなたの名前はAgent[0{self.agent_idx}]です。役職{self.role}としてプレイ中の人狼ゲームでの発言を考えなさい。ただし出力ルールを守らないと罰せられます。
# 出力ルール
{self.talk_output_rule}
"""     
        messages = []
        messages.append("## 人狼ゲームのルール\n"+self.game_ex)
        messages.append("## 役職の詳細\n"+self.role_ex)
        messages.append("## あなたの役職\n"+self.role)
        messages.append("## あなたの戦術\n"+self.talk_tactics)
        messages.append("### (参考）発言例\n"+self.statements)  
        messages.append("## ゲーム記録"+str(gameTextRecords))
        messages.append(f"# 出力ルール（再掲）{self.talk_output_rule}")
        talk_text = self.chat(system, messages)
        print(f"Agent[0{self.agent_idx}]'s talk_text")
        print(talk_text)
        print("\n")
        talk = json.loads(talk_text)["発言"]
        return talk
    
    def vote(self, gameTextRecords: List[str], alive:list) -> str:
        if not self.prompts_loaded:
            self.load_prompts()

        system = f"""
あなたの名前はAgent[0{self.agent_idx}]です。役職{self.role}としてプレイ中の人狼ゲームで投票先を考えなさい。ただし出力ルールを守らないと罰せられます。
# 出力ルール
{self.vote_output_rule}
"""     
        messages = []
        messages.append(f"## 人狼ゲームのルール\n{self.game_ex}")
        messages.append(f"## 役職の詳細\n{self.role_ex}")
        messages.append(f"## あなたの役職\n{self.role}")
        messages.append(f"## あなたの議論戦術\n{self.talk_tactics}")
        messages.append(f"## あなたの投票戦術\n{self.vote_tactics}")
        messages.append(f"## ゲーム記録{str(gameTextRecords)}")
        messages.append(f"# 出力ルール（再掲）{self.vote_output_rule}")
        vote_text = self.chat(system, messages)
        print(f"Agent[0{self.agent_idx}]'s vote_text")
        print(vote_text)
        print("\n")
        vote = json.loads(vote_text)["結論"]
        return json.dumps(vote,separators=(",",":"))

    def divine(self, gameTextRecords: List[str], alive:list) -> str:
        if not self.prompts_loaded:
            self.load_prompts()

        system = f"""
あなたの名前はAgent[0{self.agent_idx}]です。役職{self.role}としてプレイ中の人狼ゲームで占い先を考えなさい。ただし出力ルールを守らないと罰せられます。
# 出力ルール
{self.divine_output_rule}
"""     
        messages = []
        messages.append(f"## 人狼ゲームのルール\n{self.game_ex}")
        messages.append(f"## 役職の詳細\n{self.role_ex}")
        messages.append(f"## あなたの役職\n{self.role}")
        messages.append(f"## あなたの議論戦術\n{self.talk_tactics}")
        messages.append(f"## あなたの占い戦術\n{self.divine_tactics}")
        messages.append(f"## ゲーム記録{str(gameTextRecords)}")
        messages.append(f"# 出力ルール（再掲）{self.divine_output_rule}")
        divine_text = self.chat(system, messages)
        print(f"Agent[0{self.agent_idx}]'s divine_text")
        print(divine_text)
        print("\n")
        divine = json.loads(divine_text)["結論"]
        return json.dumps(divine,separators=(",",":"))

    def attack(self, gameTextRecords: List[str], alive:list) -> str:
        if not self.prompts_loaded:
            self.load_prompts()

        system = f"""
あなたの名前はAgent[0{self.agent_idx}]です。役職{self.role}としてプレイ中の人狼ゲームで襲撃先を考えなさい。ただし出力ルールを守らないと罰せられます。
# 出力ルール
{self.attack_output_rule}
"""     
        messages = []
        messages.append(f"## 人狼ゲームのルール\n{self.game_ex}")
        messages.append(f"## 役職の詳細\n{self.role_ex}")
        messages.append(f"## あなたの役職\n{self.role}")
        messages.append(f"## あなたの議論戦術\n{self.talk_tactics}")
        messages.append(f"## あなたの襲撃戦術\n{self.attack_tactics}")
        messages.append(f"## ゲーム記録{str(gameTextRecords)}")
        messages.append(f"# 出力ルール（再掲）{self.attack_output_rule}")
        attack_text = self.chat(system, messages)
        print(f"Agent[0{self.agent_idx}]'s attack_text")
        print(attack_text)
        print("\n")
        attack = json.loads(attack_text)["結論"]
        return json.dumps(attack,separators=(",",":"))