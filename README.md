# Automata Casebook

**Course:** 21CSC301T - Formal Language and Automata  
**Assessment:** CLA-2, Tasks 2 and 3  
**Student:** A. Jagan Karthick (RA2411026050020)  
**Programme:** B.Tech. AIML, SRM Institute of Science and Technology, Tiruchirappalli

A compact Python workbench containing finite automata, context-free grammars and pushdown-machine demonstrations. The design is an independent implementation and uses different validation examples and project organisation from the reference work.

## Included work

### Task 2 - Finite automata for input validation

1. **Student roll identifier:** `RA` followed by exactly thirteen ASCII digits.
2. **Username policy:** 5-15 characters; first character must be a letter; remaining characters may be letters, digits or underscores.
3. **Course code:** one of `AIM`, `CSE` or `ECE`, followed by exactly three digits. The model is first expressed as an epsilon-NFA, then converted to a DFA through subset construction and minimised.

The examples demonstrate fixed-length recognition, length-bounded state tracking, NFA union and subset construction. All are syntax checks. The roll-ID validator does not confirm enrolment, and a course code is not checked against a live catalogue.

### Task 3 - CFG and PDA case studies

1. **Nested delimiters:** a deterministic stack machine validates `()`, `[]` and `{}`. It ignores delimiter-like characters inside quoted strings.
2. **Arithmetic expressions:** a precedence-aware CFG is simulated as a CFG-derived NPDA and independently processed by a recursive-descent evaluator.
3. **Nested arrays:** a CFG recognises arrays containing integers, quoted strings and further arrays. A recursive-descent parser returns the parsed value.

The expression section also contrasts an ambiguous operator grammar with a corrected grammar that gives multiplication higher precedence than addition.

## Project layout

```text
src/automata_casebook/core/       DFA, NFA, CFG and PDA engines
src/automata_casebook/task2/      finite-state validators
src/automata_casebook/task3/      grammars, stack cases and parsers
src/automata_casebook/web/        optional Flask demonstration
 tests/                           regression and bounded exhaustive tests
 tools/                            diagram and evidence generation
 assets/figures/                   PNG/SVG automata, parse trees and charts
 docs/                             theory notes and validation evidence
 report/                           editable report and PDF report
```

## Run locally

Python 3.10 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\\Scripts\\activate
pip install -e ".[test,demo,visuals,report]"
python -m automata_casebook.cli all
python -m automata_casebook.cli task2
python -m automata_casebook.cli task3
python -m automata_casebook.cli --trace RA2411026050020
pytest -q
```

Start the interactive browser demonstration:

```bash
python serve_demo.py
```

Open `http://127.0.0.1:5050`. The Flask component is optional; the core models and CLI do not depend on Flask.

Rebuild diagrams and summary charts (requires Graphviz `dot` on your PATH):

```bash
python tools/build_visuals.py
```

## Interpreting the models

- A DFA remembers a finite state; its transition depends on the current state and next input class.
- The course-code NFA uses epsilon branching to express a union of department prefixes. The subset construction produces an equivalent deterministic machine.
- A PDA has a stack, which supplies unbounded last-in-first-out memory for nested structures.
- The CFG-to-PDA simulator explores nondeterministic grammar expansions with a configuration cap. It is an educational recogniser, not a production parser generator.
- The recursive-descent expression and array parsers provide deterministic implementations for the selected grammars.

## Reproducibility and evidence

`pytest -q` checks representative positive/negative cases, edge conditions, NFA/DFA equivalence, bounded short-string agreement for delimiters, and agreement between CFG-PDA recognisers and the application parsers. The generated test log and figures are stored in `docs/` and `assets/figures/`. Rebuild the report with `python tools/generate_report.py` after installing the `report` extra.

## Academic integrity note

This package is an independent study implementation. The submitted student should inspect the grammar definitions, run the examples, and be prepared to explain each transition, stack operation and limitation during the demonstration. Replace or supplement the sample cases with any additional rules specified by the faculty.
