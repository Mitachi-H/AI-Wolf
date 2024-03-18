from lib.LLM.openai_client import OpenAIClient
from typing import List
import os, json, re

class ChatGPTAgent(OpenAIClient):
    def __init__(self) -> None:
        super().__init__()
        self.agent_idx = None
        self.role = None
        self.prompts_loaded = False

        self.discussionHistory = {"talk": [""], "vote": [""], "divine": [""], "attack": [""]}
    
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
        if not self.prompts_loaded:
            self.load_prompts()

        system = f"""
あなたの名前はAgent[0{self.agent_idx}]です。
{self.talk_output_rule}
"""     
        messages = []
        messages.append("## 役職の詳細\n"+self.role_ex)
        messages.append("## あなたの役職\n"+self.role)
        messages.append("## ゲーム記録"+"\n".join(gameTextRecords))
        messages.append("## 最後の自分の発言の前に考えたこと"+"\n".join(self.discussionHistory["talk"][-1]))
        messages.append(f"# システム文（再掲） {system}")

        talk_text = self.chat(system, messages)
        print(f"Agent[0{self.agent_idx}]({self.role})'s talk_text")
        print(talk_text)
        print("\n")
        talk = json.loads(talk_text)["発言"]
        self.discussionHistory["talk"].append(talk_text["議論"])
        return talk


    def vote(self, gameTextRecords: List[str], alive:list) -> str:
        if not self.prompts_loaded:
            self.load_prompts()

        system = f"""
あなたの名前はAgent[0{self.agent_idx}]です。
{self.vote_output_rule}
"""     
        messages = []
        messages.append(f"## 役職の詳細\n{self.role_ex}")
        messages.append(f"## あなたの役職\n{self.role}")
        messages.append("## ゲーム記録"+"\n".join(gameTextRecords))
        messages.append("## 最後の自分の発言の前に考えたこと"+"\n".join(self.discussionHistory["talk"][-1]))
        messages.append(f"# システム文（再掲） {system}")

        vote_text = self.chat(system, messages)
        print(f"Agent[0{self.agent_idx}]({self.role})'s vote_text")
        print(vote_text)
        print("\n")
        vote = json.loads(vote_text)["結論"]
        self.discussionHistory["vote"].append(vote_text["議論"])
        return json.dumps(vote,separators=(",",":"))


    def divine(self, gameTextRecords: List[str], alive:list) -> str:
        if not self.prompts_loaded:
            self.load_prompts()

        system = f"""
あなたの名前はAgent[0{self.agent_idx}]です。
{self.divine_output_rule}
"""     
        messages = []
        messages.append(f"## 役職の詳細\n{self.role_ex}")
        messages.append(f"## あなたの役職\n{self.role}")
        messages.append("## ゲーム記録"+"\n".join(gameTextRecords))
        messages.append("## 最後の自分の発言の前に考えたこと"+"\n".join(self.discussionHistory["talk"][-1]))
        messages.append(f"# 命令文（再掲）\n{system}")

        divine_text = self.chat(system, messages)
        print(f"Agent[0{self.agent_idx}]({self.role})'s divine_text")
        print(divine_text)
        print("\n")
        divine = json.loads(divine_text)["結論"]
        self.discussionHistory["divine"].append(divine_text["議論"])
        return json.dumps(divine,separators=(",",":"))


    def attack(self, gameTextRecords: List[str], alive:list) -> str:
        if not self.prompts_loaded:
            self.load_prompts()

        system = f"""
あなたの名前はAgent[0{self.agent_idx}]です
{self.attack_output_rule}
"""     
        messages = []
        messages.append(f"## 役職の詳細\n{self.role_ex}")
        messages.append(f"## あなたの役職\n{self.role}")
        messages.append("## ゲーム記録"+"\n".join(gameTextRecords))
        messages.append("## 最後の自分の発言の前に考えたこと"+"\n".join(self.discussionHistory["talk"][-1]))
        messages.append(f"# 命令文（再掲）\n{system}")

        attack_text = self.chat(system, messages)
        print(f"Agent[0{self.agent_idx}]({self.role})'s attack_text")
        print(attack_text)
        print("\n")
        attack = json.loads(attack_text)["結論"]
        self.discussionHistory["attack"].append(attack_text["議論"])  
        return json.dumps(attack,separators=(",",":"))

if __name__ == "__main__":
    agent = ChatGPTAgent()
    agent.initialize_openai_client()
    agent.set_agent_idx(1)
    agent.set_role("村人")
    agent.talk(gameTextRecords=[])