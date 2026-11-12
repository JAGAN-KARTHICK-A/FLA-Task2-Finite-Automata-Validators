"""Command-line demonstrations for both CLA-2 assignments."""
from __future__ import annotations

import argparse
import json

from automata_casebook.task2.validators import (
    ROLL_ID_DFA, USERNAME_DFA, COURSE_CODE_NFA, COURSE_CODE_DFA,
    VALIDATION_EXAMPLES,
)
from automata_casebook.task3.cases import (
    BRACKET_DPDA, BRACKET_NPDA, EXPRESSION_NPDA, ARRAY_NPDA,
    expression_tokens, array_tokens,
)
from automata_casebook.task3.expression import parse_and_evaluate
from automata_casebook.task3.arrays import parse_array


def show_task2() -> None:
    print("\nTASK 2 | FINITE-STATE VALIDATORS")
    print("=" * 72)
    machines = {"roll_id": ROLL_ID_DFA, "username": USERNAME_DFA, "course_code": COURSE_CODE_DFA}
    for name, machine in machines.items():
        print(f"\n{name.replace('_', ' ').title()} | states={len(machine.states)} | accepting={len(machine.accepting)}")
        examples = VALIDATION_EXAMPLES[name]
        for label in ("accepted", "rejected"):
            for value in examples[label]:
                verdict = "ACCEPT" if machine.accepts(value) else "REJECT"
                print(f"  {verdict:6}  {value}")
    print(f"\nCourse-code NFA states: {len(COURSE_CODE_NFA.states)}")
    print(f"Subset DFA states: {len(COURSE_CODE_DFA.states)}")
    print(f"Minimised subset DFA states: {len(COURSE_CODE_DFA.minimize().states)}")


def show_task3() -> None:
    print("\nTASK 3 | CFG AND PDA CASE STUDIES")
    print("=" * 72)

    source = "call({items[0]}, \"ignore ] inside string\")"
    result = BRACKET_DPDA.run(source)
    print(f"\n1. Delimiter DPDA: {source!r} -> {'ACCEPT' if result.accepted else 'REJECT'}")
    for move in result.moves:
        print("  " + move)
    for candidate in ["([{}])", "([)]", "(()"]:
        tokens = BRACKET_DPDA.extract_tokens(candidate)
        check = BRACKET_NPDA.run(tokens)
        print(f"  CFG/PDA cross-check {candidate!r}: {'ACCEPT' if check.accepted else 'REJECT'}")

    expression = "2 + 3 * (4 - 1)"
    tokens = expression_tokens(expression)
    pda = EXPRESSION_NPDA.run(tokens)
    _, value = parse_and_evaluate(expression)
    print(f"\n2. Expression: {expression} -> {value:g}")
    print(f"   CFG-derived NPDA: {'ACCEPT' if pda.accepted else 'REJECT'} ({pda.explored_configurations} configurations)")

    array_source = '[1, [2, 3], "ready", []]'
    array_toks = array_tokens(array_source)
    array_result = ARRAY_NPDA.run(array_toks)
    parsed = parse_array(array_source)
    print(f"\n3. Nested array: {array_source} -> {parsed}")
    print(f"   CFG-derived NPDA: {'ACCEPT' if array_result.accepted else 'REJECT'} ({array_result.explored_configurations} configurations)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Formal Language and Automata assignment workbench")
    parser.add_argument("task", nargs="?", choices=["all", "task2", "task3"], default="all")
    parser.add_argument("--trace", help="show a DFA trace for a student roll ID")
    args = parser.parse_args()
    if args.task in ("all", "task2"):
        show_task2()
    if args.task in ("all", "task3"):
        show_task3()
    if args.trace is not None:
        print("\nROLL-ID DFA TRACE")
        print(json.dumps(ROLL_ID_DFA.trace(args.trace), indent=2))


if __name__ == "__main__":
    main()
