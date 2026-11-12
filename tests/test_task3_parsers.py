import itertools

import pytest

from automata_casebook.task3.cases import (
    BRACKET_DPDA, BRACKET_NPDA, EXPRESSION_NPDA, ARRAY_NPDA,
    expression_tokens, array_tokens,
)
from automata_casebook.task3.expression import parse_and_evaluate
from automata_casebook.task3.arrays import parse_array


def test_delimiter_pda_examples_and_string_literal_handling():
    assert BRACKET_DPDA.run('call({items[0]}, "ignore ]")').accepted
    assert BRACKET_DPDA.run("f(') ignored', [a, b])").accepted
    assert not BRACKET_DPDA.run("([)]").accepted
    assert not BRACKET_DPDA.run("(()").accepted
    assert not BRACKET_DPDA.run(")(").accepted
    assert not BRACKET_DPDA.run('print("unfinished)').accepted


def test_bracket_dpda_and_cfg_npda_agree_for_bounded_strings():
    alphabet = "()[]{}"
    for length in range(5):
        for chars in itertools.product(alphabet, repeat=length):
            source = "".join(chars)
            dpda = BRACKET_DPDA.run(source).accepted
            npda = BRACKET_NPDA.run(list(source)).accepted
            assert dpda == npda


def test_expression_precedence_and_validation():
    _, value = parse_and_evaluate("2 + 3 * 4")
    assert value == 14
    _, nested_value = parse_and_evaluate("2 + 3 * (4 - 1)")
    assert nested_value == 11
    for source in ["2 + 3 * 4", "(8-2)/3", "7*5-2", "12", "(1+2)*(3+4)"]:
        assert EXPRESSION_NPDA.run(expression_tokens(source)).accepted
    for source in ["2+", "+2", "(2+3", "2 3", "2+*3"]:
        with pytest.raises(ValueError):
            parse_and_evaluate(source)
        try:
            accepted = EXPRESSION_NPDA.run(expression_tokens(source)).accepted
        except ValueError:
            accepted = False
        assert not accepted


def test_nested_array_parser_and_cfg_pda():
    source = '[1, [2, 3], "ready", []]'
    assert parse_array(source) == [1, [2, 3], "ready", []]
    assert ARRAY_NPDA.run(array_tokens(source)).accepted
    assert parse_array("[]") == []
    assert ARRAY_NPDA.run(array_tokens("[]")).accepted
    for valid in ["[1,2]", "[1,[2,3],\"ready\"]", "[\"x\"]", "[7,[8],[]]"]:
        assert ARRAY_NPDA.run(array_tokens(valid)).accepted
        parse_array(valid)
    for invalid in ["[1,,2]", "[1 2]", "[1,]", "1,2", "[1, [2]"]:
        with pytest.raises(ValueError):
            parse_array(invalid)
        try:
            accepted = ARRAY_NPDA.run(array_tokens(invalid)).accepted
        except ValueError:
            accepted = False
        assert not accepted
