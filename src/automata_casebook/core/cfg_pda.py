"""Context-free grammar utilities and a bounded CFG-to-NPDA simulator."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Sequence


@dataclass
class CFG:
    start: str
    productions: dict[str, list[tuple[str, ...]]]
    name: str = "CFG"

    @property
    def nonterminals(self) -> set[str]:
        return set(self.productions)

    def validate(self) -> None:
        if self.start not in self.productions:
            raise ValueError("Start symbol must have productions")
        for left, alternatives in self.productions.items():
            if not alternatives:
                raise ValueError(f"No productions supplied for {left}")
            for rhs in alternatives:
                if not isinstance(rhs, tuple):
                    raise TypeError("Each right-hand side must be a tuple of grammar symbols")

    def as_lines(self) -> list[str]:
        lines = []
        for left, alternatives in self.productions.items():
            right = [" ".join(rhs) if rhs else "ε" for rhs in alternatives]
            lines.append(f"{left} -> " + " | ".join(right))
        return lines


@dataclass
class PDAResult:
    accepted: bool
    explored_configurations: int
    moves: list[str]
    reason: str


class CFGPushdownSimulator:
    """Simulate the standard one-state NPDA obtained from a CFG.

    The stack is stored bottom-to-top. A nonterminal can be replaced by any
    production; a terminal on top must match the next input token. The search
    is breadth-first and bounded to keep the educational simulator safe.
    """

    def __init__(self, grammar: CFG, max_configurations: int = 60000):
        grammar.validate()
        self.grammar = grammar
        self.max_configurations = max_configurations

    def run(self, tokens: Sequence[str]) -> PDAResult:
        start_stack = (self.grammar.start,)
        start = (0, start_stack)
        queue = deque([(0, start_stack, [f"start: stack={start_stack}"])])
        visited = {start}
        explored = 0
        nonterminals = self.grammar.nonterminals

        while queue and explored < self.max_configurations:
            position, stack, moves = queue.popleft()
            explored += 1
            if position == len(tokens) and not stack:
                return PDAResult(True, explored, moves + ["accept: input consumed and stack empty"], "accepted")
            if not stack:
                continue

            top = stack[-1]
            remainder = stack[:-1]
            if top in nonterminals:
                for production in self.grammar.productions[top]:
                    new_stack = remainder + tuple(reversed(production))
                    config = (position, new_stack)
                    if config not in visited:
                        visited.add(config)
                        rhs_text = " ".join(production) if production else "ε"
                        note = f"ε: expand {top} -> {rhs_text}; stack={new_stack}"
                        queue.append((position, new_stack, moves + [note]))
            elif position < len(tokens) and top == tokens[position]:
                new_stack = remainder
                config = (position + 1, new_stack)
                if config not in visited:
                    visited.add(config)
                    note = f"read {tokens[position]}; stack={new_stack}"
                    queue.append((position + 1, new_stack, moves + [note]))

        if explored >= self.max_configurations:
            return PDAResult(False, explored, [], "configuration limit reached")
        return PDAResult(False, explored, [], "no accepting computation")


class DelimiterDPDA:
    """Deterministic stack machine for (), [] and {} with source-string awareness."""

    OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}"}

    def extract_tokens(self, source: str) -> list[str]:
        tokens: list[str] = []
        quote = None
        escaped = False
        for char in source:
            if quote is not None:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
                continue
            if char in ("'", '"'):
                quote = char
            elif char in self.OPEN_TO_CLOSE or char in self.OPEN_TO_CLOSE.values():
                tokens.append(char)
        if quote is not None:
            raise ValueError("Unterminated string literal")
        return tokens

    def run(self, source: str) -> PDAResult:
        try:
            tokens = self.extract_tokens(source)
        except ValueError as error:
            return PDAResult(False, 0, [], str(error))

        stack: list[str] = ["Z0"]
        moves = ["start: stack=[Z0]"]
        for index, token in enumerate(tokens, start=1):
            if token in self.OPEN_TO_CLOSE:
                stack.append(token)
                moves.append(f"{index}. read {token}: push {token}; stack={stack}")
            else:
                if len(stack) == 1:
                    moves.append(f"{index}. read {token}: no opener available; reject")
                    return PDAResult(False, index, moves, "closing delimiter without opener")
                opener = stack[-1]
                expected = self.OPEN_TO_CLOSE[opener]
                if token != expected:
                    moves.append(f"{index}. read {token}: expected {expected} for {opener}; reject")
                    return PDAResult(False, index, moves, "mismatched closing delimiter")
                stack.pop()
                moves.append(f"{index}. read {token}: pop {opener}; stack={stack}")

        accepted = stack == ["Z0"]
        moves.append("accept: bottom marker remains" if accepted else f"reject: unmatched opener remains; stack={stack}")
        return PDAResult(accepted, len(tokens) + 1, moves, "accepted" if accepted else "unmatched opening delimiter")
