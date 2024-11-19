import pprint
from pathlib import Path

from lark import Lark, Transformer


class RuleTransformer(Transformer):
    def start(self, rules):
        # 将所有的 rule 转换为字典，key 是 state，value 是 rules
        return {rule["state"]: rule["rules"] for rule in rules}

    def rule(self, items):
        # 每个 rule 包括 state 和 statements
        return {"state": items[0], "rules": items[1:]}

    def state(self, token):
        # 返回状态名称
        return str(token[0])

    def statements(self, cases):
        # 返回 cases 列表
        return cases

    def case(self, items):
        # 提取条件和其他信息
        initial_condition = items[0] if items else None
        or_conditions = [c for c in items[1:] if isinstance(c, str)]  # 合并多个 or_condition
        reply = next((x for x in items[1:] if isinstance(x, dict) and "reply" in x), None)
        next_state = next((x for x in items[1:] if isinstance(x, dict) and "next_state" in x), None)

        # 合并条件列表
        conditions = [initial_condition, *or_conditions] if initial_condition else or_conditions

        return {
            "conditions": conditions,
            "reply": reply if isinstance(reply, str) else (reply.get("reply") if reply else None),
            "next_state": next_state
            if isinstance(next_state, str)
            else (next_state.get("next_state") if next_state else "INIT"),
        }

    def or_condition(self, items):
        # 返回 "or" 条件的值
        return items[0]  # condition 的值

    def default_case(self, items):
        # 提取回复和下一状态，处理 None 情况
        reply = items[0] if items and len(items) > 0 else None
        next_state = items[1] if len(items) > 1 else "INIT"

        return {
            "default": True,
            "reply": reply if isinstance(reply, str) else (reply.get("reply") if reply else None),
            "next_state": next_state
            if isinstance(next_state, str)
            else (next_state.get("next_state") if next_state else "INIT"),
        }

    def reply_case(self, items):
        reply = items[0] if items else None
        next_state = items[1] if len(items) > 1 else "INIT"

        return {
            "reply": reply if isinstance(reply, str) else (reply.get("reply") if reply else None),
            "next_state": next_state
            if isinstance(next_state, str)
            else (next_state.get("next_state") if next_state else "INIT"),
        }

    def condition(self, token):
        # 去掉条件字符串的引号
        return token[0][1:-1]

    def reply(self, token):
        # 返回去掉引号的 reply 字符串
        return {"reply": token[0][1:-1]}

    def next_state(self, token):
        # 返回状态名称，默认返回 'INIT'
        return {"next_state": str(token[0])}


file_path = Path("/Users/tang/Course/程序设计实践/chatbot/backend/dsl_grammar.lark")  # 替换为你的文件路径
with file_path.open(encoding="utf-8") as f:
    dsl_grammar = f.read()

parser = Lark(dsl_grammar, start="start", parser="lalr")

# 从文件中读取 DSL 脚本
file_path = Path("/Users/tang/Course/程序设计实践/chatbot/backend/rules.dsl")  # 替换为你的文件路径
try:
    with file_path.open(encoding="utf-8") as f:
        dsl_script = f.read()

    tree = parser.parse(dsl_script)
    print(tree.pretty())
    transformer = RuleTransformer()
    res = transformer.transform(tree)
    pprint.pp(res)
except FileNotFoundError:
    pprint.pp(f"错误: 找不到文件 {file_path}")
except Exception as e:
    pprint.pp(f"解析错误: {e}")
