from backend.dsl_interpreter import DSLInterpreter

# Mock data for testing
grammar_file = "dsl_grammar.lark"
dsl_file = "rules.dsl"


# Test cases
def test_dsl_interpreter():
    dsl_interpreter = DSLInterpreter(dsl_file_path=dsl_file, grammar_file_path=grammar_file)

    assert "请输入您要查询的产品 id" in dsl_interpreter.get_response("产品")
    assert dsl_interpreter.get_response("123") == "产品123的价格为200"
