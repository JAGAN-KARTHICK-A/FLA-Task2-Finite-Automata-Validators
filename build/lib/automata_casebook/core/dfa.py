"""Small, dependency-free DFA and NFA toolkit used by both assignments."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet, Hashable, Iterable, Mapping, Optional, Sequence, Set, Tuple

State = Hashable
Symbol = str
DEAD = "__DEAD__"


@dataclass
class DFA:
    states: Set[State]
    alphabet: Set[Symbol]
    transitions: Dict[Tuple[State, Symbol], State]
    start: State
    accepting: Set[State]
    classifier: Optional[Callable[[str], Symbol]] = None
    name: str = "DFA"

    def _classify(self, char: str) -> Symbol:
        symbol = self.classifier(char) if self.classifier else char
        if symbol not in self.alphabet and "OTHER" in self.alphabet:
            return "OTHER"
        return symbol

    def next_state(self, state: State, char: str) -> State:
        symbol = self._classify(char)
        return self.transitions.get((state, symbol), DEAD)

    def trace(self, text: str) -> list[dict]:
        state = self.start
        rows = [{"index": 0, "character": "START", "class": "-", "state": state}]
        for index, char in enumerate(text, start=1):
            symbol = self._classify(char)
            state = self.transitions.get((state, symbol), DEAD)
            rows.append({"index": index, "character": char, "class": symbol, "state": state})
        return rows

    def accepts(self, text: str) -> bool:
        rows = self.trace(text)
        return rows[-1]["state"] in self.accepting

    def complete(self) -> "DFA":
        """Return an equivalent total DFA, adding a sink when necessary."""
        states = set(self.states)
        transitions = dict(self.transitions)
        needs_dead = False
        for state in list(states):
            for symbol in self.alphabet:
                if (state, symbol) not in transitions:
                    needs_dead = True
                    transitions[(state, symbol)] = DEAD
        if needs_dead or DEAD in states:
            states.add(DEAD)
            for symbol in self.alphabet:
                transitions[(DEAD, symbol)] = DEAD
        return DFA(states, set(self.alphabet), transitions, self.start, set(self.accepting), self.classifier, self.name)

    def minimize(self) -> "DFA":
        """Partition-refinement minimisation for a complete deterministic machine."""
        machine = self.complete()
        accepting = set(machine.accepting)
        rejecting = set(machine.states) - accepting
        partitions = [part for part in (accepting, rejecting) if part]

        changed = True
        while changed:
            changed = False
            refined: list[set] = []
            for block in partitions:
                buckets: dict[tuple, set] = {}
                for state in block:
                    signature = tuple(
                        next((i for i, part in enumerate(partitions)
                              if machine.transitions[(state, symbol)] in part), -1)
                        for symbol in sorted(machine.alphabet)
                    )
                    buckets.setdefault(signature, set()).add(state)
                refined.extend(buckets.values())
                if len(buckets) > 1:
                    changed = True
            partitions = refined

        state_to_block = {state: i for i, block in enumerate(partitions) for state in block}
        new_states = set(range(len(partitions)))
        new_start = state_to_block[machine.start]
        new_accepting = {state_to_block[state] for state in machine.accepting}
        new_transitions: dict[tuple, int] = {}
        for i, block in enumerate(partitions):
            representative = next(iter(block))
            for symbol in machine.alphabet:
                target = machine.transitions[(representative, symbol)]
                new_transitions[(i, symbol)] = state_to_block[target]
        return DFA(new_states, set(machine.alphabet), new_transitions, new_start, new_accepting,
                   machine.classifier, f"minimal({self.name})")

    def product(self, other: "DFA", *, name: str = "product") -> "DFA":
        """Reachable product DFA recognising the intersection of two languages."""
        if self.alphabet != other.alphabet:
            raise ValueError("Product construction requires identical alphabets")
        left, right = self.complete(), other.complete()
        start = (left.start, right.start)
        queue = deque([start])
        seen = {start}
        transitions: dict[tuple, tuple] = {}
        accepting: set[tuple] = set()
        while queue:
            pair = queue.popleft()
            if pair[0] in left.accepting and pair[1] in right.accepting:
                accepting.add(pair)
            for symbol in left.alphabet:
                target = (left.transitions[(pair[0], symbol)], right.transitions[(pair[1], symbol)])
                transitions[(pair, symbol)] = target
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return DFA(seen, set(left.alphabet), transitions, start, accepting, None, name)


@dataclass
class NFA:
    states: Set[State]
    alphabet: Set[Symbol]
    transitions: Dict[Tuple[State, Symbol], Set[State]]
    start: State
    accepting: Set[State]
    epsilon: Dict[State, Set[State]]
    classifier: Optional[Callable[[str], Symbol]] = None
    name: str = "NFA"

    def _classify(self, char: str) -> Symbol:
        symbol = self.classifier(char) if self.classifier else char
        if symbol not in self.alphabet and "OTHER" in self.alphabet:
            return "OTHER"
        return symbol

    def _closure(self, seeds: Iterable[State]) -> FrozenSet[State]:
        closure = set(seeds)
        todo = list(closure)
        while todo:
            state = todo.pop()
            for target in self.epsilon.get(state, set()):
                if target not in closure:
                    closure.add(target)
                    todo.append(target)
        return frozenset(closure)

    def accepts(self, text: str) -> bool:
        current = self._closure({self.start})
        for char in text:
            symbol = self._classify(char)
            targets: set[State] = set()
            for state in current:
                targets.update(self.transitions.get((state, symbol), set()))
            current = self._closure(targets)
        return bool(current & self.accepting)

    def to_dfa(self) -> DFA:
        """Subset construction, including the empty subset as a sink state."""
        start = self._closure({self.start})
        queue = deque([start])
        seen = {start}
        transitions: dict[tuple, FrozenSet[State]] = {}
        accepting: set[FrozenSet[State]] = set()
        while queue:
            subset = queue.popleft()
            if subset & self.accepting:
                accepting.add(subset)
            for symbol in self.alphabet:
                targets: set[State] = set()
                for state in subset:
                    targets.update(self.transitions.get((state, symbol), set()))
                target_subset = self._closure(targets)
                transitions[(subset, symbol)] = target_subset
                if target_subset not in seen:
                    seen.add(target_subset)
                    queue.append(target_subset)
        return DFA(seen, set(self.alphabet), transitions, start, accepting,
                   self.classifier, f"subset({self.name})")
