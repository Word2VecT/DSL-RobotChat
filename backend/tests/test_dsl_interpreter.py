# backend/tests/test_dsl_interpreter.py

import pytest
from backend.dsl_interpreter import DSLInterpreter

# 定义一个临时的DSL内容，用于测试
TEST_DSL_CONTENT = """
rule greet:
    pattern: "hello" | "hi" | "hey"
    response: "您好！有什么可以帮您的吗？"

rule help:
    pattern: "帮助" | "支持" | "需要帮助"
    response: "当然，我在这里帮助您。您需要什么帮助？"

rule farewell:
    pattern: "再见" | "拜拜" | "退出"
    response: "再见！祝您有美好的一天！"

rule default:
    pattern: "*"
    response: "抱歉，我不太明白您的意思。您能换种说法吗？"
"""


@pytest.fixture
def dsl_file(tmp_path):
    """
    创建一个临时的DSL文件，并返回其路径。
    """
    dsl_path = tmp_path / "bot_rules.dsl"
    dsl_path.write_text(TEST_DSL_CONTENT, encoding="utf-8")
    return str(dsl_path)


@pytest.fixture
def interpreter(dsl_file):
    """
    创建一个DSLInterpreter实例，使用临时DSL文件。
    """
    return DSLInterpreter(dsl_file)


def test_load_rules(interpreter):
    """
    测试DSL规则是否正确加载。
    """
    assert len(interpreter.rules) == 4, "应该加载4条规则"

    rule_names = [rule.name for rule in interpreter.rules]
    expected_names = ["greet", "help", "farewell", "default"]
    assert set(rule_names) == set(
        expected_names
    ), "规则名称应包含greet, help, farewell, default"

    # 检查每条规则的响应
    responses = {rule.name: rule.response for rule in interpreter.rules}
    assert responses["greet"] == "您好！有什么可以帮您的吗？"
    assert responses["help"] == "当然，我在这里帮助您。您需要什么帮助？"
    assert responses["farewell"] == "再见！祝您有美好的一天！"
    assert responses["default"] == "抱歉，我不太明白您的意思。您能换种说法吗？"


def test_get_response_greet(interpreter):
    """
    测试greet规则的响应。
    """
    test_messages = ["hello", "Hi", "HEY", "HeLLo"]
    expected_response = "您好！有什么可以帮您的吗？"
    for msg in test_messages:
        response = interpreter.get_response(msg)
        assert (
            response == expected_response
        ), f"输入 '{msg}' 应返回 '{expected_response}'"


def test_get_response_help(interpreter):
    """
    测试help规则的响应。
    """
    test_messages = ["我需要帮助", "请给我支持", "需要帮助"]
    expected_response = "当然，我在这里帮助您。您需要什么帮助？"
    for msg in test_messages:
        response = interpreter.get_response(msg)
        assert (
            response == expected_response
        ), f"输入 '{msg}' 应返回 '{expected_response}'"


def test_get_response_farewell(interpreter):
    """
    测试farewell规则的响应。
    """
    test_messages = ["再见", "拜拜", "我要退出", "退出程序"]
    expected_response = "再见！祝您有美好的一天！"
    for msg in test_messages:
        response = interpreter.get_response(msg)
        assert (
            response == expected_response
        ), f"输入 '{msg}' 应返回 '{expected_response}'"


def test_get_response_default(interpreter):
    """
    测试默认规则的响应。
    """
    test_messages = ["不知道说什么", "这是一个测试", "随机输入"]
    expected_response = "抱歉，我不太明白您的意思。您能换种说法吗？"
    for msg in test_messages:
        response = interpreter.get_response(msg)
        assert response == expected_response, f"输入 '{msg}' 应返回默认响应"


def test_case_insensitivity(interpreter):
    """
    测试规则匹配的大小写不敏感性。
    """
    test_messages = ["HELLO", "Hi", "HeY", "再见", "拜拜"]
    expected_responses = [
        "您好！有什么可以帮您的吗？",
        "您好！有什么可以帮您的吗？",
        "您好！有什么可以帮您的吗？",
        "再见！祝您有美好的一天！",
        "再见！祝您有美好的一天！",
    ]
    for msg, expected in zip(test_messages, expected_responses):
        response = interpreter.get_response(msg)
        assert response == expected, f"输入 '{msg}' 应返回 '{expected}'"


def test_missing_default_rule(tmp_path):
    """
    测试在没有default规则时的行为。
    """
    dsl_content = """
rule greet:
    pattern: "hello"
    response: "Hello!"
    """
    # 创建一个临时DSL文件
    dsl_path = tmp_path / "bot_rules.dsl"
    dsl_path.write_text(dsl_content, encoding="utf-8")
    interpreter = DSLInterpreter(str(dsl_path))
    response = interpreter.get_response("unknown input")
    assert response == "抱歉，我无法理解您的意思。", "缺少default规则时应返回默认消息"


def test_rule_with_wildcard(interpreter):
    """
    测试带有通配符的规则。
    """
    test_messages = ["任何输入都可以", "随机内容", "测试通配符"]
    expected_response = "抱歉，我不太明白您的意思。您能换种说法吗？"
    for msg in test_messages:
        response = interpreter.get_response(msg)
        assert response == expected_response, f"输入 '{msg}' 应返回默认响应"
