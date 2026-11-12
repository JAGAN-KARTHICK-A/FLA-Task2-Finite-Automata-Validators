"""Predictive parser and evaluator for the precedence-aware expression grammar."""
from __future__ import annotations

from dataclasses import dataclass
from automata_casebook.task3.cases import expression_tokens


@dataclass
class Token:
    kind: str
    value: str


class ExpressionParser:
    def __init__(self, source: str):
        source = source.strip()
        self.source = source
        import re
        pattern = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|([()+\-*/]))")
        self.tokens: list[Token] = []
        position = 0
        while position < len(source):
            match = pattern.match(source, position)
            if not match:
                raise ValueError(f"Invalid token at position {position}")
            number, operator = match.groups()
            self.tokens.append(Token("NUM", number) if number else Token(operator, operator))
            position = match.end()
        self.index = 0

    def current(self) -> str:
        return self.tokens[self.index].kind if self.index < len(self.tokens) else "EOF"

    def consume(self, expected: str) -> Token:
        if self.current() != expected:
            raise ValueError(f"Expected {expected}, found {self.current()}")
        token = self.tokens[self.index]
        self.index += 1
        return token

    def parse(self):
        tree = self.parse_expression()
        if self.current() != "EOF":
            raise ValueError(f"Unexpected token {self.current()} after expression")
        return tree

    def parse_expression(self):
        node = self.parse_term()
        while self.current() in {"+", "-"}:
            operator = self.current()
            self.consume(operator)
            node = (operator, node, self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current() in {"*", "/"}:
            operator = self.current()
            self.consume(operator)
            node = (operator, node, self.parse_factor())
        return node

    def parse_factor(self):
        if self.current() == "NUM":
            return ("num", float(self.consume("NUM").value))
        if self.current() == "(":
            self.consume("(")
            node = self.parse_expression()
            self.consume(")")
            return node
        raise ValueError(f"Expected a number or '(', found {self.current()}")


def evaluate(tree):
    if tree[0] == "num":
        return tree[1]
    operator, left, right = tree
    a, b = evaluate(left), evaluate(right)
    return {"+": lambda: a + b, "-": lambda: a - b,
            "*": lambda: a * b, "/": lambda: a / b}[operator]()


def parse_and_evaluate(source: str):
    tree = ExpressionParser(source).parse()
    return tree, evaluate(tree)
