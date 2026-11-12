# Validation and Test Evidence

## Environment

- Python 3.10 or later
- Core implementation: Python standard library
- Test runner: pytest
- Diagrams: Graphviz `dot`
- Charts: Matplotlib

## Automated checks

The test suite is made up of eight pytest test functions across two files.

| Area | Check | Coverage |
|---|---|---:|
| Task 2 | Roll-ID positive and negative cases | 7 representative samples |
| Task 2 | Username boundaries and invalid symbols | 9 representative samples plus min/max length checks |
| Task 2 | NFA, subset DFA and minimised DFA equivalence | 7 explicit cases |
| Task 2 | Course-code DFA vs independent regex | 1,111,111 strings, length 0-6 over a 10-symbol alphabet |
| Task 3 | Stack matching, string literal handling and malformed delimiters | 6 focused cases |
| Task 3 | DPDA vs CFG-derived NPDA | 1,555 bracket strings, length 0-4 |
| Task 3 | Arithmetic grammar and evaluation | Valid and invalid expression cases |
| Task 3 | Nested-array grammar and parser | Empty, nested, valid and malformed arrays |

## Reproduce

```bash
pip install -e ".[test]"
pytest -q
python tools/build_visuals.py
```

## Recorded run

```text
$ PYTHONPATH=src pytest -q
........                                                                 [100%]
8 passed
```

This result is the recorded run in the project-generation environment. Run the commands again on the submission machine to reproduce it.

## Important implementation boundary

The CFG-derived NPDA is an educational simulator. It uses breadth-first configuration exploration and a 60,000-configuration bound. It does not claim to be an optimised general-purpose parser. The recursive-descent expression and array parsers act as independent deterministic cross-checks for the selected grammars.
