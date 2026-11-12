"""Task 3: CFG/PDA models for delimiters, expressions and nested arrays."""
from __future__ import annotations

from automata_casebook.core.cfg_pda import CFG, CFGPushdownSimulator, DelimiterDPDA


BRACKET_GRAMMAR = CFG("S", {
    "S": [("(", "S", ")", "S"), ("[", "S", "]", "S"), ("{", "S", "}", "S"), ()],
}, "Balanced delimiters")

EXPRESSION_GRAMMAR = CFG("E", {
    "E": [("T", "E2")],
    "E2": [("+", "T", "E2"), ("-", "T", "E2"), ()],
    "T": [("F", "T2")],
    "T2": [("*", "F", "T2"), ("/", "F", "T2"), ()],
    "F": [("(", "E", ")"), ("NUM",)],
}, "Arithmetic expressions with precedence")

ARRAY_GRAMMAR = CFG("Array", {
    "Array": [("[", "OptItems", "]")],
    "OptItems": [("Items",), ()],
    "Items": [("Value", "Tail")],
    "Tail": [(",", "Value", "Tail"), ()],
    "Value": [("NUM",), ("STR",), ("Array",)],
}, "Nested array literals")

BRACKET_NPDA = CFGPushdownSimulator(BRACKET_GRAMMAR)
EXPRESSION_NPDA = CFGPushdownSimulator(EXPRESSION_GRAMMAR)
ARRAY_NPDA = CFGPushdownSimulator(ARRAY_GRAMMAR)
BRACKET_DPDA = DelimiterDPDA()


def expression_tokens(source: str) -> list[str]:
    """Tokenise a restricted arithmetic expression into grammar terminals."""
    source = source.strip()
    import re
    pattern = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|([()+\-*/]))")
    tokens: list[str] = []
    position = 0
    while position < len(source):
        match = pattern.match(source, position)
        if not match:
            raise ValueError(f"Unexpected character at position {position}: {source[position]!r}")
        number, operator = match.groups()
        tokens.append("NUM" if number is not None else operator)
        position = match.end()
    return tokens


def array_tokens(source: str) -> list[str]:
    """Tokenise integer, quoted-string and nested-array literal syntax."""
    source = source.strip()
    import re
    pattern = re.compile(r'\s*(?:(\d+)|("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|([\[\],]))')
    tokens: list[str] = []
    position = 0
    while position < len(source):
        match = pattern.match(source, position)
        if not match:
            raise ValueError(f"Unexpected character at position {position}: {source[position]!r}")
        number, string, punctuation = match.groups()
        tokens.append("NUM" if number is not None else "STR" if string is not None else punctuation)
        position = match.end()
    return tokens


def check_with_cfg(case: str, tokens: list[str]):
    simulators = {"brackets": BRACKET_NPDA, "expression": EXPRESSION_NPDA, "arrays": ARRAY_NPDA}
    return simulators[case].run(tokens)
