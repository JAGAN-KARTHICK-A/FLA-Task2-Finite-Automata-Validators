"""Generate automata diagrams, parse trees and test-summary figures."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "assets" / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def render_dot(name: str, source: str) -> None:
    dot_path = FIG / f"{name}.dot"
    dot_path.write_text(source, encoding="utf-8")
    for extension in ("png", "svg"):
        subprocess.run(["dot", f"-T{extension}", str(dot_path), "-o", str(FIG / f"{name}.{extension}")], check=True)


def automaton_style() -> str:
    return '''
      graph [bgcolor="white", pad="0.25", nodesep="0.28", ranksep="0.55", fontname="DejaVu Sans", labeljust="l"];
      node [shape=circle, style="filled", fillcolor="#EEF3FB", color="#3157A4", penwidth=1.35,
            fontname="DejaVu Sans", fontsize=10, width=0.58, height=0.58, fixedsize=true];
      edge [color="#41536F", penwidth=1.2, arrowsize=0.7, fontname="DejaVu Sans", fontsize=9];
    '''


def build_roll_id() -> None:
    body = ['digraph RollID {', automaton_style(), 'rankdir=LR;',
            'start [shape=point, width=0.12, label=""];', 'start -> q0;']
    for i in range(16):
        shape = 'doublecircle' if i == 15 else 'circle'
        body.append(f'q{i} [shape={shape}, label="q{i}"];')
    body.append('qX [label="qX", fillcolor="#FDEBE8", color="#B94738"];')
    body.extend(['q0 -> q1 [label="R"];', 'q1 -> q2 [label="A"];'])
    for i in range(2, 15):
        body.append(f'q{i} -> q{i+1} [label="D"];')
    body.extend(['q0 -> qX [label="other", color="#B94738", constraint=false];',
                 'qX -> qX [label="Σ", color="#B94738"];',
                 'label="D = ASCII digit; every unspecified transition enters qX"; labelloc=b; fontsize=9; fontcolor="#64748B";',
                 '}'])
    render_dot("task2_roll_id_dfa", "\n".join(body))


def build_username() -> None:
    body = ['digraph Username {', automaton_style(), 'rankdir=LR;',
            'start [shape=point, width=0.12, label=""];', 'start -> q0;']
    for i in range(16):
        shape = 'doublecircle' if i >= 5 else 'circle'
        body.append(f'q{i} [shape={shape}, label="q{i}"];')
    body.append('qX [label="qX", fillcolor="#FDEBE8", color="#B94738"];')
    body.append('q0 -> q1 [label="L"];')
    for i in range(1, 15):
        body.append(f'q{i} -> q{i+1} [label="L / D / _"];')
    body.extend(['q15 -> qX [label="extra char", color="#B94738"];',
                 'label="Accepting lengths: q5 through q15; L=letter, D=digit, _=underscore"; labelloc=b; fontsize=9; fontcolor="#64748B";',
                 '}'])
    render_dot("task2_username_dfa", "\n".join(body))


def build_course_nfa() -> None:
    body = ['digraph CourseCode {', automaton_style(), 'rankdir=LR;',
            'start [shape=point, width=0.12, label=""];', 'start -> s;']
    for state in ["s", "a1", "a2", "a3", "c1", "c2", "c3", "e1", "e2", "e3", "d0", "d1", "d2"]:
        body.append(f'{state} [label="{state}"];')
    body.append('d3 [shape=doublecircle, label="d3"];')
    body.extend([
        's -> a1 [label="ε"]; s -> c1 [label="ε"]; s -> e1 [label="ε"];',
        'a1 -> a2 [label="A"]; a2 -> a3 [label="I"]; a3 -> d0 [label="M"];',
        'c1 -> c2 [label="C"]; c2 -> c3 [label="S"]; c3 -> d0 [label="E"];',
        'e1 -> e2 [label="E"]; e2 -> e3 [label="C"]; e3 -> d0 [label="E"];',
        'd0 -> d1 [label="D"]; d1 -> d2 [label="D"]; d2 -> d3 [label="D"];',
        'label="D = digit. Epsilon branches select AIM, CSE or ECE before the shared 3-digit suffix."; labelloc=b; fontsize=9; fontcolor="#64748B";'
        '}'])
    render_dot("task2_course_code_nfa", "\n".join(body))


def build_bracket_dpda() -> None:
    body = ['digraph Brackets {', automaton_style(), 'rankdir=LR;',
            'start [shape=point, width=0.12, label=""];',
            'start -> qstart;',
            'qstart [label="begin", width=0.75, height=0.55, fixedsize=false];',
            'qscan [shape=box, style="rounded,filled", width=1.7, height=0.8, fixedsize=false, label="qscan\\nread next delimiter"];',
            'qf [shape=doublecircle, label="accept", width=0.75, height=0.65, fixedsize=false];',
            'qstart -> qscan;',
            'qscan -> qscan [label="opener: push\\nmatching closer: pop", minlen=3, tailport=s, headport=s];',
            'qscan -> qf [label="end of input\\nstack = Z0"];',
            'label="Mismatched closing delimiters and leftover opening delimiters reject. Stack symbols are (, [ and {."; labelloc=b; fontsize=9; fontcolor="#64748B";',
            '}']
    render_dot("task3_delimiter_dpda", "\n".join(body))


def build_cfg_pipeline() -> None:
    body = '''digraph CFGPDA {
      graph [rankdir=LR, bgcolor="white", pad="0.3", nodesep="0.35", ranksep="0.5"];
      node [shape=box, style="rounded,filled", fillcolor="#EEF3FB", color="#3157A4", fontname="DejaVu Sans", fontsize=10, margin="0.16,0.12"];
      edge [color="#41536F", penwidth=1.25, arrowsize=0.75, fontname="DejaVu Sans", fontsize=9];
      grammar [label="CFG\\nA → α | β | …"];
      stack [label="One-state NPDA\\nstart stack = S"];
      expand [label="Top is nonterminal A\\nε-expand using A → α"];
      match [label="Top is terminal t\\nread matching input token t"];
      finish [shape=doublecircle, label="Input consumed\\nand stack empty\\nACCEPT"];
      reject [fillcolor="#FDEBE8", color="#B94738", label="No valid move\\nREJECT"];
      grammar -> stack [label="standard conversion"];
      stack -> expand;
      expand -> match [label="terminal reaches top"];
      match -> expand [label="more stack symbols"];
      match -> finish [label="last symbol matched"];
      expand -> reject [label="no useful production", style=dashed, color="#B94738"];
    }'''
    render_dot("task3_cfg_to_pda_flow", body)


def build_parse_trees() -> None:
    ambiguous = '''digraph AmbiguousTrees {
      graph [bgcolor="white", rankdir=TB, pad="0.25", nodesep="0.35", ranksep="0.48", fontname="DejaVu Sans", labelloc="t", label="Two parses admitted by E → E + E | E * E | NUM"];
      node [shape=box, style="rounded,filled", fillcolor="#EEF3FB", color="#3157A4", fontname="DejaVu Sans", fontsize=10, margin="0.10,0.06"];
      edge [color="#64748B", arrowsize=0.65];
      subgraph cluster_left { label="Parse A: (2 + 3) * 4 = 20"; color="#CBD5E1"; A[label="*"]; A1[label="+"]; A2[label="4"]; A3[label="2"]; A4[label="3"]; A -> A1; A -> A2; A1 -> A3; A1 -> A4; }
      subgraph cluster_right { label="Parse B: 2 + (3 * 4) = 14"; color="#CBD5E1"; B[label="+"]; B1[label="2"]; B2[label="*"]; B3[label="3"]; B4[label="4"]; B -> B1; B -> B2; B2 -> B3; B2 -> B4; }
    }'''
    render_dot("task3_expression_ambiguity", ambiguous)

    array = '''digraph ArrayTree {
      graph [bgcolor="white", rankdir=TB, pad="0.25", nodesep="0.28", ranksep="0.48", fontname="DejaVu Sans", labelloc="t", label="Parse structure for nested array [1, [2, 3], ready, []]"];
      node [shape=box, style="rounded,filled", fillcolor="#EEF3FB", color="#3157A4", fontname="DejaVu Sans", fontsize=10, margin="0.10,0.06"];
      edge [color="#64748B", arrowsize=0.65];
      root[label="Array"]; opt[label="OptItems"]; items[label="Items"]; tail[label="Tail"]; v1[label="Value: NUM(1)"]; v2[label="Value: Array"]; v3[label="Value: STR(ready)"]; v4[label="Value: Array([])"]; nested[label="Array [2, 3]"];
      root -> opt -> items; items -> v1; items -> tail; tail -> v2; tail -> v3; tail -> v4; v2 -> nested;
    }'''
    render_dot("task3_nested_array_parse_tree", array)


def build_charts() -> None:
    # State count chart, using exact counts from the constructed code objects.
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from automata_casebook.task2.validators import ROLL_ID_DFA, USERNAME_DFA, COURSE_CODE_NFA, COURSE_CODE_DFA

    labels = ["Roll ID DFA", "Username DFA", "Course NFA", "Course DFA", "Min. course DFA"]
    values = [len(ROLL_ID_DFA.states), len(USERNAME_DFA.states), len(COURSE_CODE_NFA.states),
              len(COURSE_CODE_DFA.states), len(COURSE_CODE_DFA.minimize().states)]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.bar(labels, values)
    ax.set_title("Task 2 model sizes")
    ax.set_ylabel("Number of states")
    ax.grid(axis="y", alpha=0.25)
    ax.bar_label(bars, padding=3)
    plt.xticks(rotation=12, ha="right")
    fig.tight_layout()
    fig.savefig(FIG / "task2_state_counts.png", dpi=220)
    plt.close(fig)

    labels = ["Delimiter DPDA", "Expression CFG-NPDA", "Array CFG-NPDA"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars = ax.bar(labels, [1, 1, 1])
    ax.set_ylim(0, 1.6)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["", "single control state"])
    ax.set_title("Control-state shape of the pushdown models")
    ax.grid(axis="y", alpha=0.25)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, 1.04, "1", ha="center", va="bottom", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG / "task3_pda_control_states.png", dpi=220)
    plt.close(fig)


def main() -> None:
    build_roll_id()
    build_username()
    build_course_nfa()
    build_bracket_dpda()
    build_cfg_pipeline()
    build_parse_trees()
    build_charts()
    print(f"Generated diagrams and charts in {FIG}")


if __name__ == "__main__":
    main()
