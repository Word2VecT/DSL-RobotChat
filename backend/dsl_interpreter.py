import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Rule:
    def __init__(self, name, patterns, response):
        self.name = name
        self.patterns = patterns  # List of regex patterns
        self.response = response


class DSLInterpreter:
    def __init__(self, dsl_file_path):
        self.rules = []
        self.load_dsl(dsl_file_path)

    def load_dsl(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
        except FileNotFoundError:
            logger.error(f"DSL文件未找到: {path}")
            return

        rule_blocks = re.split(r"\n\s*\n", content)  # 按空行分割规则块
        for block in rule_blocks:
            lines = block.strip().split("\n")
            if not lines:
                continue
            header = lines[0]
            match = re.match(r"rule\s+(\w+):", header)
            if not match:
                logger.warning(f"无法解析规则头部: {header}")
                continue
            rule_name = match.group(1)
            patterns = []
            response = ""
            for line in lines[1:]:
                pattern_match = re.match(r"\s*pattern:\s*(.+)", line)
                response_match = re.match(r'\s*response:\s*"(.+)"', line)
                if pattern_match:
                    pattern_str = pattern_match.group(1)
                    # 去除引号并分割
                    patterns = [
                        p.strip().strip('"').strip("'") for p in pattern_str.split("|")
                    ]
                elif response_match:
                    response = response_match.group(1)
            # 转换为正则表达式
            regex_patterns = []
            for p in patterns:
                if p == "*":
                    regex_patterns.append(r".*")
                else:
                    # 添加通配符以允许部分匹配
                    regex_patterns.append(re.escape(p))
            # 编译正则表达式
            compiled_patterns = [
                re.compile(rf"{pattern}", re.IGNORECASE) for pattern in regex_patterns
            ]
            self.rules.append(Rule(rule_name, compiled_patterns, response))
            logger.info(f"加载规则: {rule_name}, 模式: {patterns}, 响应: {response}")

    def get_response(self, user_message):
        logger.info(f"用户输入: {user_message}")
        for rule in self.rules:
            for pattern in rule.patterns:
                if pattern.search(user_message):
                    logger.info(f"匹配规则: {rule.name}")
                    return rule.response
        # 如果没有匹配到任何规则，返回默认响应
        default_rule = next((r for r in self.rules if r.name == "default"), None)
        if default_rule:
            logger.info("匹配到默认规则")
            return default_rule.response
        return "抱歉，我无法理解您的意思。"
