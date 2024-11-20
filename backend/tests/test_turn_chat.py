from backend.dsl_interpreter import DSLInterpreter

# Mock data for testing
grammar_file = "dsl_grammar.lark"
dsl_file = "rules.dsl"


# Test cases
def test_dsl_interpreter():
    dsl_interpreter = DSLInterpreter(dsl_file_path=dsl_file, grammar_file_path=grammar_file)
    # # Test price
    assert dsl_interpreter.get_response("价格") == "我们的产品售价是99美元。"
    assert dsl_interpreter.get_response("查询") == "请问您想查询什么信息？"
    assert dsl_interpreter.get_response("123") == "目前仅能查询手机"
    assert dsl_interpreter.get_response("手机") == "我们的手机售价是99美元。"
