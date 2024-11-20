from backend.dsl_interpreter import DSLInterpreter

# Mock data for testing
grammar_file = "dsl_grammar.lark"
dsl_file = "rules.dsl"


# Test cases
def test_dsl_interpreter():
    dsl_interpreter = DSLInterpreter(dsl_file_path=dsl_file, grammar_file_path=grammar_file)

    # Test initial greetings
    assert dsl_interpreter.get_response("hello") == "您好！请问有什么可以帮助您？"
    assert dsl_interpreter.get_response("hi") == "嗨"

    # Test laugh
    assert dsl_interpreter.get_response("哈哈") == "笑啥呢"
    assert dsl_interpreter.get_response("嘿嘿") == "笑啥呢"

    # Test inappropriate language
    assert dsl_interpreter.get_response("fu") == "请文明用语"
    assert dsl_interpreter.get_response("bitch") == "请文明用语"

    # Test unknown message
    assert dsl_interpreter.get_response("unknown") == "不能理解，请换种说法。"
