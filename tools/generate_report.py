"""Create the individual CLA-2 report in DOCX format."""
from pathlib import Path
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "assets" / "figures"
OUT = ROOT / "report" / "CLA2_Tasks_2_3_A_Jagan_Karthick.docx"
OUT.parent.mkdir(parents=True, exist_ok=True)

NAVY = "1E3557"
BLUE = "3157A4"
PALE = "EAF0F8"
GREY = "667085"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text, bold=False, color=None, size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = "Times New Roman"
    r.font.size = Pt(size)
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_table(doc, headers, rows, widths=None, font_size=8.6):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = False
    for i, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], header, bold=True, color="FFFFFF", size=font_size)
        shade(table.rows[0].cells[i], NAVY)
    set_repeat_table_header(table.rows[0])
    for row_idx, row in enumerate(rows):
        cells = table.add_row().cells
        for col_idx, value in enumerate(row):
            set_cell_text(cells[col_idx], value, size=font_size)
            if row_idx % 2 == 1:
                shade(cells[col_idx], "F4F7FB")
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Inches(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_para(doc, text="", bold_lead=None, italic=False, size=10.5, align=None, after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.08
    if align is not None:
        p.alignment = align
    if bold_lead and text.startswith(bold_lead):
        r = p.add_run(bold_lead)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(size)
        rest = p.add_run(text[len(bold_lead):])
        rest.font.name = "Times New Roman"
        rest.font.size = Pt(size)
        if italic:
            rest.italic = True
    else:
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(size)
        r.italic = italic
    return p


def heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8 if level == 1 else 5)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(14 if level == 1 else 11.5)
    r.font.color.rgb = RGBColor.from_string(NAVY if level == 1 else BLUE)
    return p


def code_block(doc, text):
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.cell(0, 0)
    shade(cell, "F2F5F9")
    cell.text = ""
    for i, line in enumerate(text.splitlines()):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(line)
        r.font.name = "Consolas"
        r.font.size = Pt(8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def figure(doc, filename, caption, width=6.35):
    path = FIG / filename
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(1)
    p.add_run().add_picture(str(path), width=Inches(width))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_after = Pt(6)
    r = cp.add_run(caption)
    r.italic = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor.from_string(GREY)


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.03
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    return p


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("A. Jagan Karthick  |  RA2411026050020  |  Page ")
    run.font.name = "Times New Roman"
    run.font.size = Pt(8)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    paragraph._p.append(fld)


doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)
section.top_margin = Inches(0.68)
section.bottom_margin = Inches(0.68)
section.left_margin = Inches(0.78)
section.right_margin = Inches(0.78)
section.header_distance = Inches(0.3)
section.footer_distance = Inches(0.32)

styles = doc.styles
styles["Normal"].font.name = "Times New Roman"
styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
styles["Normal"].font.size = Pt(10.5)

# First-page header/footer intentionally blank; regular pages get a running header and footer.
section.different_first_page_header_footer = True
header = section.header
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
hr = hp.add_run("21CSC301T - FORMAL LANGUAGE AND AUTOMATA  |  CLA-2")
hr.bold = True
hr.font.name = "Times New Roman"
hr.font.size = Pt(8)
hr.font.color.rgb = RGBColor.from_string(GREY)
footer = section.footer
add_page_number(footer.paragraphs[0])

# COVER PAGE
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(30)
r = p.add_run("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY")
r.bold = True; r.font.name = "Times New Roman"; r.font.size = Pt(15); r.font.color.rgb = RGBColor.from_string(NAVY)
for line, size, bold in [
    ("TIRUCHIRAPPALLI", 12, True),
    ("SCHOOL OF COMPUTING", 11, True),
    ("FACULTY OF ENGINEERING AND TECHNOLOGY", 10, False),
]:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(2)
    rr = p.add_run(line); rr.bold = bold; rr.font.name = "Times New Roman"; rr.font.size = Pt(size)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(42); p.paragraph_format.space_after = Pt(12)
r = p.add_run("FINITE AUTOMATA, CONTEXT-FREE GRAMMARS\nAND STACK MACHINES FOR INPUT VALIDATION\nAND STRUCTURED SYNTAX")
r.bold = True; r.font.name = "Times New Roman"; r.font.size = Pt(17); r.font.color.rgb = RGBColor.from_string(NAVY)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(8)
r = p.add_run("A COURSE ASSIGNMENT REPORT")
r.bold = True; r.font.name = "Times New Roman"; r.font.size = Pt(12)
add_para(doc, "submitted for the course", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
add_para(doc, "21CSC301T - FORMAL LANGUAGE AND AUTOMATA", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=12).runs[0].bold = True
add_para(doc, "CLA-2 ASSESSMENT TASKS 2 AND 3 (INDIVIDUAL WORK)", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=18)

add_para(doc, "Submitted by", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
p = add_para(doc, "A. JAGAN KARTHICK", size=13, align=WD_ALIGN_PARAGRAPH.CENTER, after=1); p.runs[0].bold = True
p = add_para(doc, "RA2411026050020", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=18); p.runs[0].bold = True
add_para(doc, "Under the guidance of", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=3)
p = add_para(doc, "Dr. C. GUNASUNDARI", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=1); p.runs[0].bold = True
add_para(doc, "Assistant Professor, Department of AIML", size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, after=18)
add_para(doc, "III Year / V Semester", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
add_para(doc, "B.Tech. Artificial Intelligence and Machine Learning", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
add_para(doc, "SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
add_para(doc, "TIRUCHIRAPPALLI - 621105", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
add_para(doc, "NOVEMBER 2026", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)

doc.add_page_break()

# TASK 2 - PAGE 2
heading(doc, "Task 2: Finite Automata for Real-Time Input Validation", 1)
add_para(doc, "Reference implementation scope: https://github.com/Vaishakkr/FLA-Task2-Finite-Automata-Validators", size=8.5, italic=True, after=5)
heading(doc, "1. Problem and approach", 2)
add_para(doc, "Registration portals and course systems reject malformed identifiers before using them. I represented three such checks as regular languages: a student roll identifier, a username policy and a course code. Each implementation consumes the input from left to right and records only the finite state needed to decide whether the string follows the selected rule.")
add_para(doc, "The models deliberately separate syntax from meaning. A correctly shaped roll ID does not prove that the student is enrolled, and an allowed course-code pattern does not prove that the course is offered. Those decisions need records maintained by the application.")
heading(doc, "2. Application 1: Student roll identifier", 2)
add_para(doc, "The language consists of the literal prefix RA followed by exactly thirteen decimal digits. The alphabet is grouped into R, A, D (ASCII digit) and OTHER. q0 reads R, q1 reads A, and q2 through q14 count the thirteen digits. q15 is the only accepting state; qX is a trap state for every invalid or excess character.")
code_block(doc, "L_roll = { RAx : x ∈ {0,1,...,9}^13 }\nExample: RA2411026050020  -> ACCEPT")
figure(doc, "task2_roll_id_dfa.png", "Fig. 1. DFA for the fixed RA prefix and thirteen-digit suffix.", width=6.35)
heading(doc, "3. Application 2: Username rule", 2)
add_para(doc, "A username must contain between five and fifteen characters. Its first symbol must be an English letter; subsequent symbols may be letters, digits or underscores. States q1 through q15 record the number of consumed characters. q5 through q15 accept, while qX rejects an unsupported character or a sixteenth character.")
code_block(doc, "L_user = { w : 5 ≤ |w| ≤ 15, first(w) ∈ L, later(w) ∈ L ∪ D ∪ {_} }\nAccepted: Jagan_24     Rejected: 2jagan, name-tag")
figure(doc, "task2_username_dfa.png", "Fig. 2. Length-bounded username DFA; double circles represent valid lengths.", width=6.35)
add_para(doc, "Representative test data (the assignment asks for at least five accepted and five rejected examples per application):", size=9.2, after=3)
add_table(doc, ["Application", "Accepted examples", "Rejected examples"], [
    ["Roll ID", "RA2411026050020; RA1234567890123; RA0000000000000; RA9999999999999; RA0123456789012", "RA241102605002; ra2411026050020; RA24110260500200; RA24110260A020; RB2411026050020"],
    ["Username", "Jagan_24; alpha9; student_name; XyZ_12345; A_bcd; a1234", "2jagan; abcd; this_username_is_long; name-tag; name space; _name1"],
    ["Course code", "AIM305; CSE201; ECE110; AIM000; ECE999", "AIM30; AIM3000; aim305; AIM3X5; EEE202; CSE20A"],
], widths=[0.9, 2.9, 2.8], font_size=7.0)

# TASK 2 - PAGE 3
p = heading(doc, "Task 2: NFA Construction, Testing and Interpretation", 1); p.paragraph_format.page_break_before = True
heading(doc, "4. Application 3: Course-code validator", 2)
add_para(doc, "The accepted pattern is one of the three uppercase department prefixes AIM, CSE or ECE, followed by exactly three digits. I first represented the union of the prefixes using an epsilon-NFA. Three epsilon branches leave the start state and join the same digit-suffix chain after the selected prefix has been consumed.")
code_block(doc, "L_code = {AIM, CSE, ECE}{0,1,...,9}^3\nAccepted: AIM305, CSE201, ECE110     Rejected: AIM30, EEE202")
figure(doc, "task2_course_code_nfa.png", "Fig. 3. Epsilon-NFA with three prefix branches and a shared three-digit suffix.", width=6.1)
add_para(doc, "The subset construction forms a deterministic state for each reachable epsilon-closed subset. The generated NFA contains 14 states, the subset DFA contains 12 reachable subsets (including the empty subset), and partition refinement minimises that DFA to 11 states.")
figure(doc, "task2_state_counts.png", "Fig. 4. State counts read directly from the generated machines.", width=5.9)
add_table(doc, ["Model", "States", "Meaning"], [
    ["Roll-ID DFA", "17", "16 progress states and trap"],
    ["Username DFA", "17", "16 length states and trap"],
    ["Course-code NFA", "14", "Three prefix paths and shared suffix"],
    ["Subset DFA / minimal DFA", "12 / 11", "Reachable subsets; equivalent states merged"],
], widths=[1.55, 0.7, 4.2], font_size=8.3)
heading(doc, "5. Validation and observations", 2)
add_para(doc, "Positive and negative examples are exercised in the test suite. The course-code NFA, subset DFA and minimised DFA are compared against one another. An independent regular-expression rule is also used for all 1,111,111 strings of length zero through six over a ten-symbol test alphabet. The tests confirm agreement for this bounded set.")
add_para(doc, "Finite automata are appropriate because the rules need only bounded length information and a finite set of character classes. They do not check whether a username is available, whether a student record exists, or whether a course is open for registration. These are semantic checks performed after syntactic acceptance.")

# TASK 3 - PAGE 4
p = heading(doc, "Task 3: Context-Free Grammars and Pushdown Automata", 1); p.paragraph_format.page_break_before = True
add_para(doc, "Reference implementation scope: https://github.com/Vaishakkr/FLA-Task3-PDA-CFG-Case-Studies", size=8.5, italic=True, after=5)
heading(doc, "1. Why a stack is required", 2)
add_para(doc, "A finite automaton has a fixed number of states and cannot count an arbitrary nesting depth. Consider L = { an opening parenthesis repeated n times, followed by a closing parenthesis repeated n times : n ≥ 0 }. Let p be a proposed pumping length and choose a string with p opening parentheses followed by p closing parentheses. Since |xy| ≤ p, the non-empty segment y lies entirely among the opening parentheses. Pumping y adds opening parentheses but leaves the closing half unchanged, so the resulting string is not balanced. This contradiction shows that the language is not regular.")
add_para(doc, "A pushdown automaton adds a last-in-first-out stack. The stack stores opening delimiters until matching closing delimiters arrive. The same idea supports recursive arithmetic expressions and nested arrays.")
heading(doc, "2. Case study A: Balanced delimiters", 2)
add_para(doc, "The target alphabet contains (, ), [, ], { and }. The grammar is S → (S)S | [S]S | {S}S | ε. It allows empty content, nested groups and concatenated balanced groups. The application includes a small lexical pass that skips characters inside single- and double-quoted strings, so a bracket-like character in a string does not affect the stack.")
figure(doc, "task3_delimiter_dpda.png", "Fig. 5. DPDA control flow. Opening symbols are pushed; matching closing symbols pop the stack.", width=5.8)
add_para(doc, "For the input ({[]}), the stack is initialised with Z0. The top of the stack is shown at the right in the table.")
add_table(doc, ["Input", "Stack operation", "Stack after step"], [
    ["Start", "Initialise bottom marker", "Z0"],
    ["(", "Push (", "Z0 ("],
    ["{", "Push {", "Z0 ({"],
    ["[", "Push [", "Z0 ({["],
    ["]", "Match and pop [", "Z0 ({"],
    ["}", "Match and pop {", "Z0 ("],
    [")", "Match and pop (", "Z0"],
    ["End", "Only bottom marker remains", "ACCEPT"],
], widths=[1.0, 2.6, 2.8], font_size=8.2)
add_para(doc, "The sequence ([)] rejects at the closing parenthesis because the top symbol is [. An unmatched closer or an opening symbol left at end-of-input also causes rejection.")

# TASK 3 - PAGE 5
p = heading(doc, "Task 3: Arithmetic Expression Parsing", 1); p.paragraph_format.page_break_before = True
heading(doc, "3. Case study B: Arithmetic expressions", 2)
add_para(doc, "A compact grammar E → E + E | E * E | (E) | NUM accepts basic expressions but does not establish operator precedence. For the token sequence 2 + 3 * 4, one parse groups the addition first and gives (2 + 3) * 4 = 20. Another groups multiplication first and gives 2 + (3 * 4) = 14. The same input therefore has two different parse trees and values under the ambiguous grammar.")
figure(doc, "task3_expression_ambiguity.png", "Fig. 6. Two parse trees for 2 + 3 * 4 under the ambiguous operator grammar.", width=5.7)
heading(doc, "4. Precedence-aware grammar", 2)
code_block(doc, "E  → T E2\nE2 → + T E2 | - T E2 | ε\nT  → F T2\nT2 → * F T2 | / F T2 | ε\nF  → ( E ) | NUM")
add_para(doc, "The E level handles addition and subtraction; the T level handles multiplication and division; F handles a number or parenthesised expression. Since multiplication is placed at a lower grammar level, it binds more tightly. The grammar is simulated by the generic CFG-derived NPDA and independently parsed by a recursive-descent evaluator.")
add_para(doc, "Worked input: 2 + 3 * (4 - 1). The parenthesised factor evaluates to 3, multiplication produces 9, and the remaining addition produces 11. The deterministic parser returns the same result as the intended precedence rule.")
figure(doc, "task3_cfg_to_pda_flow.png", "Fig. 7. CFG-to-PDA simulation: expand a nonterminal, match a terminal, and accept on empty stack.", width=6.2)

# TASK 3 - PAGE 6
p = heading(doc, "Task 3: Nested Array Syntax and Validation", 1); p.paragraph_format.page_break_before = True
heading(doc, "5. Case study C: Nested arrays", 2)
add_para(doc, "The final case study models a small array-literal language. An array may be empty or contain comma-separated values. A value can be an integer, a quoted string or another array. Recursion is needed because an array may contain another array at any depth.")
code_block(doc, "Array    → [ OptItems ]\nOptItems → Items | ε\nItems    → Value Tail\nTail     → , Value Tail | ε\nValue    → NUM | STR | Array")
figure(doc, "task3_nested_array_parse_tree.png", "Fig. 8. Parse structure for [1, [2, 3], \"ready\", []].", width=4.7)
add_para(doc, "For [1, [2, 3], \"ready\", []], the parser returns a nested Python list containing two integer values in the inner array, a string value, and an empty array. Inputs such as [1,,2], [1 2], [1,] and [1, [2] are rejected because they violate the element or closing-bracket productions.")
heading(doc, "6. Test cases", 2)
add_table(doc, ["Case study", "Accepted examples", "Rejected examples"], [
    ["Delimiters", "(), [], {}, ([{}]), {[()]}", "([)], ((), )(, {[}, ())"],
    ["Expressions", "2+3*4, (8-2)/3, 7*5-2, 12, (1+2)*(3+4)", "2+, +2, (2+3, 2+*3, 2 3"],
    ["Arrays", "[], [1,2], [1,[2,3],\"ready\"], [\"x\"], [7,[8],[]]", "[1,,2], [1 2], [1,], [1,[2], 1,2"],
], widths=[1.0, 2.9, 2.6], font_size=7.2)
add_para(doc, "The explicit delimiter DPDA and CFG-derived NPDA are compared for all 1,555 delimiter strings of length zero through four over the six-symbol bracket alphabet. The expression and array grammars are also checked by the CFG-derived NPDA and their independent recursive-descent implementations.")

# SUMMARY AND CONTRIBUTIONS - PAGE 7
p = heading(doc, "7. Determinism, Practical Boundaries and Conclusion", 1); p.paragraph_format.page_break_before = True
add_table(doc, ["Case study", "Formal model", "Practical parser", "Boundary"], [
    ["Delimiters", "CFG / PDA", "Deterministic stack machine", "Full language lexing needs comments and string rules."],
    ["Expressions", "CFG / CFG-derived NPDA", "Recursive-descent parser", "No unary operators, names, functions or type rules."],
    ["Nested arrays", "CFG / CFG-derived NPDA", "Recursive-descent parser", "Only integers and quoted strings are scalar values."],
], widths=[1.0, 1.45, 1.65, 2.5], font_size=7.8)
add_para(doc, "The grammar-to-PDA construction is nondeterministic in general because a nonterminal may have several productions. In the implementation, breadth-first exploration is bounded at 60,000 configurations to avoid unbounded search. The selected expression and array grammars are right-recursive and small. Separate recursive-descent parsers demonstrate deterministic processing for these chosen rule sets.")
add_para(doc, "The work demonstrates the distinction between regular input checks and nested syntax. Finite automata are suitable for fixed-format identifiers, bounded usernames and course codes. A stack is needed for recursive structure such as nested delimiters, arithmetic parentheses and array literals. The corrected expression grammar resolves the precedence ambiguity shown by the initial grammar.")
heading(doc, "Individual contribution", 2)
add_para(doc, "This is an individual submission. I defined the languages and grammar productions, designed the automata, implemented the DFA/NFA and CFG/PDA utilities, wrote the validators and parsers, prepared the test cases, ran the verification suite, generated the diagrams and charts, and assembled the report and demonstration interface.")
add_table(doc, ["Work area", "Contribution"], [
    ["Task 2", "Roll-ID and username DFAs; course-code NFA, subset construction and minimisation."],
    ["Task 3", "Delimiter DPDA; arithmetic and nested-array CFGs; CFG-derived NPDA and parsers."],
    ["Verification", "Positive/negative and boundary tests; bounded exhaustive equivalence checks."],
    ["Documentation", "Automata diagrams, parse trees, state-count chart, CLI/browser demo and report."],
], widths=[1.25, 5.2], font_size=8.1)

# REFERENCES - PAGE 8
p = heading(doc, "References", 1); p.paragraph_format.page_break_before = True
references = [
    "[1] J. E. Hopcroft, R. Motwani and J. D. Ullman, Introduction to Automata Theory, Languages, and Computation, 3rd ed., Pearson, 2007.",
    "[2] A. V. Aho, M. S. Lam, R. Sethi and J. D. Ullman, Compilers: Principles, Techniques, and Tools, 2nd ed., Pearson, 2007.",
    "[3] M. Sipser, Introduction to the Theory of Computation, 3rd ed., Cengage Learning, 2012.",
    "[4] SRM Institute of Science and Technology, Tiruchirappalli, Continuous Learning Assessment - 2: Course Assignment Instructions with Rubrics, 21CSC301T - Formal Language and Automata, AY 2026-2027, Tasks 2 and 3.",
    "[5] Vaishakkr, FLA-Task2-Finite-Automata-Validators, GitHub repository, https://github.com/Vaishakkr/FLA-Task2-Finite-Automata-Validators (consulted for task scope and demonstration ideas).",
    "[6] Vaishakkr, FLA-Task3-PDA-CFG-Case-Studies, GitHub repository, https://github.com/Vaishakkr/FLA-Task3-PDA-CFG-Case-Studies (consulted for task scope and case-study expectations).",
]
for item in references:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.18)
    p.paragraph_format.first_line_indent = Inches(-0.18)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.12
    r = p.add_run(item)
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
heading(doc, "Project execution record", 2)
add_para(doc, "The accompanying repository contains the complete Python source, unit tests, generated diagrams and charts, technical notes, command-line demonstration, optional Flask interface and reproducibility instructions. The recorded verification run completed with eight pytest test functions passing.")
add_para(doc, "Student: A. Jagan Karthick  |  Register number: RA2411026050020", size=10, bold_lead="Student:", after=2)

# Metadata
doc.core_properties.title = "CLA-2 Tasks 2 and 3 - Formal Language and Automata"
doc.core_properties.subject = "Finite automata, context-free grammars and pushdown automata"
doc.core_properties.author = "A. Jagan Karthick"
doc.core_properties.keywords = "Formal Language and Automata, DFA, NFA, CFG, PDA, CLA-2"

doc.save(OUT)
print(OUT)
