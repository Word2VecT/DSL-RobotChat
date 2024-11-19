from doctest import Example
import logging
from pathlib import Path

from lark import Lark, Transformer

logger = logging.getLogger(__name__)

example_data = [
    {
        "id": 123,
        "price": 200,
    },
    {
        "id": 456,
        "price": 100,
    },
]


class DSLTransformer(Transformer):
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
        # 返回状态名称, 默认返回 'INIT'
        return {"next_state": str(token[0])}


class DSLInterpreter:
    def __init__(self, dsl_file_path, grammar_file_path) -> None:
        # 读取语法文件
        with Path(grammar_file_path).open(encoding="utf-8") as f:
            grammar = f.read()
        self.parser = Lark(grammar, start="start", parser="lalr", transformer=DSLTransformer())
        # 解析 DSL 文件并存储规则
        with Path(dsl_file_path).open(encoding="utf-8") as f:
            dsl_text = f.read()
        self.tree = self.parser.parse(dsl_text)
        self.rules = DSLTransformer().transform(self.tree)
        self.current_state = "INIT"
        self.default_message = self.rules["DEFAULT"][0][0]["reply"]
        self.id = None

    def get_variable(self, message):
        ids = "\n" + "\n".join(str(data["id"]) for data in example_data)
        message = message.replace("{ids}", ids)

        if self.id:
            message = message.replace("{id}", str(self.id))

        for data in example_data:
            if self.id and data["id"] == self.id:
                message = message.replace("{id.price}", str(data["price"]))
                break
        return message

    def get_response(self, user_message):
        """根据用户输入生成回复, 并更新状态.

        :param user_message: 用户的输入消息
        :return: 回复消息
        """
        # 获取当前状态的规则列表
        if not self.current_state or self.current_state == "None":
            self.current_state = "INIT"
        rules_for_state = self.rules.get(self.current_state, [])
        logger.info("Current state: %s", self.current_state)

        if self.current_state.startswith("VAR") and user_message.isdigit():
            self.id = int(user_message)
            logger.info(self.id)
            if any(data["id"] == self.id for data in example_data):
                user_message = "{id}"

        # 遍历规则, 寻找匹配的条件
        for rule_set in rules_for_state:  # rules_for_state 是一个列表
            for case in rule_set:  # 每个规则集内有多个 case
                # 检查条件是否匹配
                if "conditions" in case and any(cond in user_message for cond in case["conditions"]):
                    # 匹配成功, 返回回复并更新状态
                    if self.current_state.startswith("VAR"):
                        self.current_state = case.get("next_state")
                        return self.get_variable(case["reply"])
                    self.current_state = case.get("next_state")
                    if self.current_state.startswith("VAR"):
                        return self.get_variable(case["reply"])
                    return case["reply"]

                # 检查默认分支
                if "default" in case:
                    if self.current_state.startswith("VAR"):
                        self.current_state = case.get("next_state")
                        return self.get_variable(case["reply"])
                    self.current_state = case.get("next_state")
                    if self.current_state.startswith("VAR"):
                        return self.get_variable(case["reply"])
                    return case["reply"]

        self.current_state = "INIT"
        return self.default_message
