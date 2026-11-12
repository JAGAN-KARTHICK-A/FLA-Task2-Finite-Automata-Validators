"""Recursive-descent parser for a small nested-array language."""
from __future__ import annotations

import ast
import re


class ArrayParser:
    def __init__(self, source: str):
        source = source.strip()
        self.source = source
        token_pattern = re.compile(r'\s*(?:(\d+)|("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|([\[\],]))')
        self.tokens: list[tuple[str, str]] = []
        position = 0
        while position < len(source):
            match = token_pattern.match(source, position)
            if not match:
                raise ValueError(f"Invalid array token at position {position}")
            number, string, punctuation = match.groups()
            if number is not None:
                self.tokens.append(("NUM", number))
            elif string is not None:
                self.tokens.append(("STR", string))
            else:
                self.tokens.append((punctuation, punctuation))
            position = match.end()
        self.index = 0

    def current(self):
        return self.tokens[self.index][0] if self.index < len(self.tokens) else "EOF"

    def take(self, kind: str):
        if self.current() != kind:
            raise ValueError(f"Expected {kind}, found {self.current()}")
        token = self.tokens[self.index]
        self.index += 1
        return token[1]

    def parse(self):
        value = self.parse_array()
        if self.current() != "EOF":
            raise ValueError(f"Unexpected trailing token: {self.current()}")
        return value

    def parse_array(self):
        self.take("[")
        values = []
        if self.current() != "]":
            values.append(self.parse_value())
            while self.current() == ",":
                self.take(",")
                values.append(self.parse_value())
        self.take("]")
        return values

    def parse_value(self):
        if self.current() == "NUM":
            return int(self.take("NUM"))
        if self.current() == "STR":
            return ast.literal_eval(self.take("STR"))
        if self.current() == "[":
            return self.parse_array()
        raise ValueError(f"Expected a number, string or nested array; found {self.current()}")


def parse_array(source: str):
    return ArrayParser(source).parse()
