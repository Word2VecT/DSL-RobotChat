# dsl_interpreter.py

from lark import Lark, Transformer
import logging

logger = logging.getLogger(__name__)


class DSLInterpreter:
    def __init__(self, dsl_file_path, grammar_file_path):
        # 读取语法文件
        with open(grammar_file_path, "r", encoding="utf-8") as f:
            grammar = f.read()
        self.parser = Lark(grammar, start="start", parser="lalr")
        # 解析 DSL 文件并存储规则
        with open(dsl_file_path, "r", encoding="utf-8") as f:
            dsl_text = f.read()
        parse_tree = self.parser.parse(dsl_text)
        self.rules = self.transform(parse_tree)

    def transform(self, parse_tree):
        # 将解析树转换为规则列表
        class TreeToRules(Transformer):
            def start(self, rules):
                return rules

            def rule(self, items):
                condition_list = items[0]
                action_list = items[1]
                return {"conditions": condition_list, "actions": action_list}

            def condition_list(self, items):
                return items

            def condition_expr(self, items):
                return ("contains", items[0])

            def action_list(self, items):
                return items

            def action_expr(self, items):
                return ("reply", items[0])

            def STRING(self, s):
                return str(s)[1:-1]  # 去除引号

            def contains(self, items):
                return items[0]

            def reply(self, items):
                return items[0]

        transformer = TreeToRules()
        rules = transformer.transform(parse_tree)
        return rules

    def get_response(self, user_message):
        # 遍历规则，检查条件
        for rule in self.rules:
            conditions_met = True
            for condition in rule["conditions"]:
                if condition[0] == "contains":
                    keyword = condition[1]
                    if keyword.lower() not in user_message.lower():
                        conditions_met = False
                        break
                else:
                    conditions_met = False
                    break
            if conditions_met:
                # 执行动作
                for action in rule["actions"]:
                    if action[0] == "reply":
                        response = action[1]
                        return response
        # 如果没有匹配的规则，返回默认响应
        return "抱歉，我没有理解您的意思。"
