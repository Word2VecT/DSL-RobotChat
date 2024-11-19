"""DSL Interpreter Module.

This module defines a DSLInterpreter class for interpreting a custom Domain-Specific Language (DSL)
and generating responses based on predefined rules. It also includes a DSLTransformer class
to convert parsed DSL grammar into Python dictionaries for easier manipulation.

The DSL interpreter uses the Lark library for parsing and supports dynamic variable substitution
in responses based on user input.

Classes:
    - DSLTransformer: Custom transformer to process DSL grammar and rules.
    - DSLInterpreter: Interpreter to manage the DSL rules, process user input, and generate replies.

Usage:
    Initialize the DSLInterpreter with paths to the grammar file and DSL file. Call `get_response`
    with user input to generate a reply based on the current state and rules.

Example:
    dsl_interpreter = DSLInterpreter("path/to/dsl.txt", "path/to/grammar.lark")
    response = dsl_interpreter.get_response("some user input")
    print(response)

"""

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
    """Custom Transformer for parsing DSL rules.

    This class converts parsed DSL rules into Python dictionaries
    for easier processing in the interpreter.
    """

    def start(self, rules: list) -> dict:
        """Transform the start rule of the grammar.

        Converts all rules into a dictionary where the key is the state
        and the value is a list of associated rules.
        """
        return {rule["state"]: rule["rules"] for rule in rules}

    def rule(self, items: list) -> dict:
        """Transform a rule in the grammar.

        Each rule contains a state and its associated statements.
        """
        return {"state": items[0], "rules": items[1:]}

    def state(self, token: list) -> str:
        """Extract state name.

        Returns the state name as a string.
        """
        return str(token[0])

    def statements(self, cases: list) -> list:
        """Transform statements into a list of cases.

        Returns a list of all parsed cases.
        """
        return cases

    def case(self, items: list) -> dict:
        """Parse a case with conditions, reply, and next state.

        Conditions include initial and 'or' conditions.
        Reply and next state are extracted from the case structure.
        """
        initial_condition = items[0] if items else None
        or_conditions = [c for c in items[1:] if isinstance(c, str)]  # Combine 'or' conditions
        reply = next((x for x in items[1:] if isinstance(x, dict) and "reply" in x), None)
        next_state = next((x for x in items[1:] if isinstance(x, dict) and "next_state" in x), None)

        # Combine condition list
        conditions = [initial_condition, *or_conditions] if initial_condition else or_conditions

        return {
            "conditions": conditions,
            "reply": reply if isinstance(reply, str) else (reply.get("reply") if reply else None),
            "next_state": next_state
            if isinstance(next_state, str)
            else (next_state.get("next_state") if next_state else "INIT"),
        }

    def or_condition(self, items: list) -> str:
        """Extract 'or' condition value.

        Returns the value of the condition.
        """
        return items[0]

    def default_case(self, items: list) -> dict:
        """Handle the default case in the rule.

        Extracts reply and next state, using "INIT" as default next state.
        """
        reply = items[0] if items and len(items) > 0 else None
        next_state = items[1] if len(items) > 1 else "INIT"

        return {
            "default": True,
            "reply": reply if isinstance(reply, str) else (reply.get("reply") if reply else None),
            "next_state": next_state
            if isinstance(next_state, str)
            else (next_state.get("next_state") if next_state else "INIT"),
        }

    def reply_case(self, items: list) -> dict:
        """Parse a reply case with optional next state.

        Returns a dictionary with the reply and the next state.
        """
        reply = items[0] if items else None
        next_state = items[1] if len(items) > 1 else "INIT"

        return {
            "reply": reply if isinstance(reply, str) else (reply.get("reply") if reply else None),
            "next_state": next_state
            if isinstance(next_state, str)
            else (next_state.get("next_state") if next_state else "INIT"),
        }

    def condition(self, token: list) -> str:
        """Parse a condition.

        Removes quotes from the condition string and returns it.
        """
        return token[0][1:-1]

    def reply(self, token: list) -> dict:
        """Parse a reply string.

        Removes quotes and returns the reply value as a dictionary.
        """
        return {"reply": token[0][1:-1]}

    def next_state(self, token: list) -> dict:
        """Parse the next state.

        Returns the state name, defaulting to 'INIT' if not specified.
        """
        return {"next_state": str(token[0])}


class DSLInterpreter:
    """DSL Interpreter for processing custom-defined rules.

    This class parses a given DSL file and processes user input to
    generate appropriate responses based on defined rules.
    """

    def __init__(self, dsl_file_path: str, grammar_file_path: str) -> None:
        """Initialize the DSL Interpreter.

        Reads the grammar and DSL files, parses the rules, and sets up
        the initial state and default message.

        :param dsl_file_path: Path to the DSL file.
        :param grammar_file_path: Path to the grammar file.
        """
        with Path(grammar_file_path).open(encoding="utf-8") as f:
            grammar = f.read()
        self.parser = Lark(grammar, start="start", parser="lalr", transformer=DSLTransformer())
        with Path(dsl_file_path).open(encoding="utf-8") as f:
            dsl_text = f.read()
        self.tree = self.parser.parse(dsl_text)
        self.rules = DSLTransformer().transform(self.tree)
        self.current_state = "INIT"
        self.default_message = self.rules["DEFAULT"][0][0]["reply"]
        self.id = None

    def get_variable(self, message: str) -> str:
        """Replace placeholders in the message with actual values.

        Supports replacing placeholders such as `{ids}`, `{id}`, and `{id.price}`
        with corresponding values from `example_data`.

        :param message: Message containing placeholders.
        :return: Updated message with placeholders replaced.
        """
        ids = "\n" + "\n".join(str(data["id"]) for data in example_data)
        message = message.replace("{ids}", ids)

        if self.id:
            message = message.replace("{id}", str(self.id))

        for data in example_data:
            if self.id and data["id"] == self.id:
                message = message.replace("{id.price}", str(data["price"]))
                break
        return message

    def process_case(self, case: dict) -> str:
        """Process a case and generate a reply."""
        if self.current_state.startswith("VAR"):
            self.current_state = case.get("next_state")
            return self.get_variable(case["reply"])
        self.current_state = case.get("next_state")
        if self.current_state.startswith("VAR"):
            return self.get_variable(case["reply"])
        return case["reply"]

    def get_response(self, user_message: str) -> str:
        """Generate a response based on user input and update state.

        Processes user input to find matching rules for the current state,
        updates the state, and returns the corresponding reply.

        :param user_message: User's input message.
        :return: Generated response message.
        """
        # Default initialization for state
        if not self.current_state or self.current_state == "None":
            self.current_state = "INIT"

        rules_for_state = self.rules.get(self.current_state, [])
        logger.info("Current state: %s", self.current_state)

        # Handle variable state
        if self.current_state.startswith("VAR") and user_message.isdigit():
            self.id = int(user_message)
            logger.info(self.id)
            if any(data["id"] == self.id for data in example_data):
                user_message = "{id}"

        # Process rules
        for rule_set in rules_for_state:
            for case in rule_set:
                if "conditions" in case and any(cond in user_message for cond in case["conditions"]):
                    return self.process_case(case)
                if "default" in case:
                    return self.process_case(case)

        # Fallback to default state and message
        self.current_state = "INIT"
        return self.default_message
