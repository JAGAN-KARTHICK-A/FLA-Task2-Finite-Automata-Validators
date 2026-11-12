"""Task 2: three finite-state input validators."""
from __future__ import annotations

from automata_casebook.core.dfa import DFA, NFA


def classify_roll(char: str) -> str:
    return char if char in {"R", "A"} else ("D" if char.isascii() and char.isdigit() else "OTHER")


def classify_username(char: str) -> str:
    if char.isascii() and char.isalpha():
        return "L"
    if char.isascii() and char.isdigit():
        return "D"
    if char == "_":
        return "_"
    return "OTHER"


def classify_course(char: str) -> str:
    if char in {"A", "I", "M", "C", "S", "E"}:
        return char
    if char.isascii() and char.isdigit():
        return "D"
    return "OTHER"


def build_roll_id_dfa() -> DFA:
    """Recognise RA followed by exactly thirteen ASCII digits."""
    states = {f"q{i}" for i in range(16)} | {"qX"}
    alphabet = {"R", "A", "D", "OTHER"}
    transitions = {}
    transitions[("q0", "R")] = "q1"
    transitions[("q1", "A")] = "q2"
    for index in range(2, 15):
        transitions[(f"q{index}", "D")] = f"q{index + 1}"
    for state in states:
        for symbol in alphabet:
            if state == "qX":
                transitions[(state, symbol)] = "qX"
            elif (state, symbol) not in transitions:
                transitions[(state, symbol)] = "qX"
    return DFA(states, alphabet, transitions, "q0", {"q15"}, classify_roll, "Student roll ID")


def build_username_dfa() -> DFA:
    """First character is a letter; total length is 5..15; later chars are L/D/_."""
    states = {f"q{i}" for i in range(16)} | {"qX"}
    alphabet = {"L", "D", "_", "OTHER"}
    transitions = {}
    transitions[("q0", "L")] = "q1"
    for index in range(1, 15):
        for symbol in {"L", "D", "_"}:
            transitions[(f"q{index}", symbol)] = f"q{index + 1}"
    for state in states:
        for symbol in alphabet:
            if state == "qX":
                transitions[(state, symbol)] = "qX"
            elif (state, symbol) not in transitions:
                transitions[(state, symbol)] = "qX"
    accepting = {f"q{i}" for i in range(5, 16)}
    return DFA(states, alphabet, transitions, "q0", accepting, classify_username, "Username policy")


def build_course_code_nfa() -> NFA:
    """NFA for (AIM | CSE | ECE) followed by exactly three digits.

    The epsilon split makes the union of the three department prefixes
    explicit. All branches join the same three-digit suffix chain.
    """
    states = {
        "s", "a1", "a2", "a3", "c1", "c2", "c3", "e1", "e2", "e3",
        "d0", "d1", "d2", "d3"
    }
    alphabet = {"A", "I", "M", "C", "S", "E", "D", "OTHER"}
    transitions = {
        ("a1", "A"): {"a2"}, ("a2", "I"): {"a3"}, ("a3", "M"): {"d0"},
        ("c1", "C"): {"c2"}, ("c2", "S"): {"c3"}, ("c3", "E"): {"d0"},
        ("e1", "E"): {"e2"}, ("e2", "C"): {"e3"}, ("e3", "E"): {"d0"},
        ("d0", "D"): {"d1"}, ("d1", "D"): {"d2"}, ("d2", "D"): {"d3"},
    }
    epsilon = {"s": {"a1", "c1", "e1"}}
    return NFA(states, alphabet, transitions, "s", {"d3"}, epsilon, classify_course, "Course code NFA")


ROLL_ID_DFA = build_roll_id_dfa()
USERNAME_DFA = build_username_dfa()
COURSE_CODE_NFA = build_course_code_nfa()
COURSE_CODE_DFA = COURSE_CODE_NFA.to_dfa()

VALIDATION_EXAMPLES = {
    "roll_id": {
        "accepted": ["RA2411026050020", "RA1234567890123", "RA0000000000000", "RA9999999999999", "RA0123456789012"],
        "rejected": ["RA241102605002", "ra2411026050020", "RA24110260500200", "RA24110260A020", "RB2411026050020"],
    },
    "username": {
        "accepted": ["Jagan_24", "alpha9", "student_name", "XyZ_12345", "A_bcd", "a1234"],
        "rejected": ["2jagan", "abcd", "this_username_is_long", "name-tag", "name space", "_name1"],
    },
    "course_code": {
        "accepted": ["AIM305", "CSE201", "ECE110", "AIM000", "ECE999"],
        "rejected": ["AIM30", "AIM3000", "aim305", "AIM3X5", "EEE202", "CSE20A"],
    },
}


def validate_all() -> dict[str, dict[str, bool]]:
    return {
        "roll_id": {value: ROLL_ID_DFA.accepts(value) for value in VALIDATION_EXAMPLES["roll_id"]["accepted"] + VALIDATION_EXAMPLES["roll_id"]["rejected"]},
        "username": {value: USERNAME_DFA.accepts(value) for value in VALIDATION_EXAMPLES["username"]["accepted"] + VALIDATION_EXAMPLES["username"]["rejected"]},
        "course_code": {value: COURSE_CODE_DFA.accepts(value) for value in VALIDATION_EXAMPLES["course_code"]["accepted"] + VALIDATION_EXAMPLES["course_code"]["rejected"]},
    }
