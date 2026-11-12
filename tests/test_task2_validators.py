import itertools
import re

from automata_casebook.task2.validators import (
    ROLL_ID_DFA, USERNAME_DFA, COURSE_CODE_NFA, COURSE_CODE_DFA,
    VALIDATION_EXAMPLES,
)


def test_roll_id_examples_and_fixed_width():
    for value in VALIDATION_EXAMPLES["roll_id"]["accepted"]:
        assert ROLL_ID_DFA.accepts(value)
    for value in VALIDATION_EXAMPLES["roll_id"]["rejected"]:
        assert not ROLL_ID_DFA.accepts(value)
    assert len(ROLL_ID_DFA.trace("RA2411026050020")) == 16


def test_username_examples_and_boundaries():
    for value in VALIDATION_EXAMPLES["username"]["accepted"]:
        assert USERNAME_DFA.accepts(value)
    for value in VALIDATION_EXAMPLES["username"]["rejected"]:
        assert not USERNAME_DFA.accepts(value)
    assert USERNAME_DFA.accepts("abcde")
    assert USERNAME_DFA.accepts("a" * 15)
    assert not USERNAME_DFA.accepts("a" * 16)


def test_course_nfa_subset_dfa_and_minimized_machine_agree():
    machine = COURSE_CODE_DFA.minimize()
    samples = ["AIM305", "CSE201", "ECE110", "aim305", "AIM30", "EEE202", "AIM3000"]
    for sample in samples:
        expected = COURSE_CODE_NFA.accepts(sample)
        assert COURSE_CODE_DFA.accepts(sample) == expected
        assert machine.accepts(sample) == expected


def test_short_subject_code_strings_against_regular_expression():
    alphabet = "AIMCSE012X"
    reference = re.compile(r"(?:AIM|CSE|ECE)[0-9]{3}\Z")
    for length in range(7):
        for chars in itertools.product(alphabet, repeat=length):
            value = "".join(chars)
            assert COURSE_CODE_DFA.accepts(value) == bool(reference.fullmatch(value))
