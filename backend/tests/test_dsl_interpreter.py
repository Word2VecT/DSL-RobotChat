import re
import logging
from lark import Lark, Transformer, v_args

# 配置日志
logging.basicConfig(level=logging.DEBUG)  # 设置为 DEBUG 以获取详细信息
logger = logging.getLogger(__name__)


# 从外部 .lark 文件读取 DSL 语法
def load_grammar(grammar_file_path):
    try:
        with open(grammar_file_path, "r", encoding="utf-8") as f:
            grammar = f.read()
            logger.debug(f"Loaded grammar from {grammar_file_path}:\n{grammar}")
            return grammar
    except FileNotFoundError:
        logger.error(f"Grammar file not found: {grammar_file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading grammar file: {e}")
        raise


# 定义 DSL 的语法文件路径
grammar_file = "dsl_grammar.lark"

# 加载 DSL 语法
dsl_grammar = load_grammar(grammar_file)


# 实现 Transformer 类
class DSLTransformer(Transformer):
    def start(self, rules):
        return rules

    @v_args(inline=True)  # 确保方法接收单独的参数
    def rule(self, name, pattern, response):
        logger.debug(f"Transforming rule: {name}, {pattern}, {response}")
        return {"name": name, "pattern": pattern, "response": response}

    def pattern(self, items):
        # items 是一个包含所有模式字符串的列表
        patterns = [self._strip_quotes(item) for item in items]
        logger.debug(f"Parsed patterns: {patterns}")
        return patterns

    def response(self, items):
        # items 是一个包含单个字符串的列表
        if len(items) != 1:
            logger.error(f"Expected single response but got: {items}")
            return self._strip_quotes(items)
        response = self._strip_quotes(items[0])
        logger.debug(f"Parsed response: {response}")
        return response

    def _strip_quotes(self, s):
        # 去除字符串两端的引号
        if isinstance(s, list):
            # 防止传入列表
            logger.error(f"Expected string but got list: {s}")
            return "".join(s)  # 或根据需求处理
        if s.startswith('"') and s.endswith('"'):
            return s[1:-1]
        if s.startswith("'") and s.endswith("'"):
            return s[1:-1]
        return s


# 定义 Rule 类
class Rule:
    def __init__(self, name, patterns, response):
        self.name = name
        self.patterns = patterns  # List of compiled regex patterns
        self.response = response


# 定义 DSLInterpreter 类
class DSLInterpreter:
    def __init__(self, dsl_file_path, grammar_file_path):
        self.rules = []
        self.default_rule = None
        self.load_dsl(dsl_file_path, grammar_file_path)

    def load_dsl(self, dsl_path, grammar_path):
        try:
            with open(dsl_path, "r", encoding="utf-8") as file:
                content = file.read()
                logger.debug(f"DSL内容:\n{content}")
        except FileNotFoundError:
            logger.error(f"DSL文件未找到: {dsl_path}")
            return
        except Exception as e:
            logger.error(f"读取DSL文件时出错: {e}")
            return

        # 创建 Lark 解析器，从外部语法文件读取语法
        try:
            parser = Lark(
                dsl_grammar,
                parser="lalr",
                transformer=DSLTransformer(),
                maybe_placeholders=False,
            )
            parsed_rules = parser.parse(content)
            logger.debug(f"Parsed rules: {parsed_rules}")
        except Exception as e:
            logger.error(f"解析DSL文件时出错: {e}")
            return

        # 处理解析后的规则
        for rule_dict in parsed_rules:
            rule_name = rule_dict["name"]
            patterns = rule_dict["pattern"]
            response = rule_dict["response"]

            # 转换为正则表达式
            regex_patterns = []
            for p in patterns:
                if p == "*":
                    regex_patterns.append(r".*")
                else:
                    # 添加通配符以允许部分匹配
                    regex_patterns.append(re.escape(p))

            # 编译正则表达式，确保完全匹配
            compiled_patterns = [
                re.compile(rf"^{pattern}$", re.IGNORECASE) for pattern in regex_patterns
            ]

            rule = Rule(rule_name, compiled_patterns, response)
            self.rules.append(rule)
            logger.info(f"加载规则: {rule_name}, 模式: {patterns}, 响应: {response}")

            # 如果是默认规则，单独存储
            if rule_name.lower() == "default":
                self.default_rule = rule

    def get_response(self, user_message):
        logger.info(f"用户输入: {user_message}")
        for rule in self.rules:
            if rule.name.lower() == "default":
                continue  # 默认规则稍后处理
            for pattern in rule.patterns:
                if pattern.fullmatch(user_message):
                    logger.info(f"匹配规则: {rule.name}")
                    return rule.response
        # 如果没有匹配到任何规则，返回默认响应
        if self.default_rule:
            logger.info("匹配到默认规则")
            return self.default_rule.response
        return "抱歉，我无法理解您的意思。"


# 示例使用
if __name__ == "__main__":
    # 假设 DSL 文件名为 rules.dsl，语法文件为 dsl_grammar.lark
    dsl_file = "rules.dsl"
    grammar_file = "dsl_grammar.lark"

    # 创建 DSLInterpreter 实例
    interpreter = DSLInterpreter(dsl_file, grammar_file)

    # 输出解析后的规则
    logger.info("解析后的规则:")
    for rule in interpreter.rules:
        logger.info(
            f"规则名称: {rule.name}, 模式: {[p.pattern for p in rule.patterns]}, 响应: {rule.response}"
        )

    # 匹配函数示例
    user_inputs = ["hello", "hi", "需要帮助", "支持", "再见", "退出", "未知的输入"]

    for input_text in user_inputs:
        response = interpreter.get_response(input_text)
        print(f"用户: {input_text}\n机器人: {response}\n")
