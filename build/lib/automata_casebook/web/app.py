"""Optional Flask interface for trying the validators and PDA parsers."""
from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from automata_casebook.task2.validators import ROLL_ID_DFA, USERNAME_DFA, COURSE_CODE_DFA
from automata_casebook.task3.cases import BRACKET_DPDA, EXPRESSION_NPDA, ARRAY_NPDA, expression_tokens, array_tokens
from automata_casebook.task3.expression import parse_and_evaluate
from automata_casebook.task3.arrays import parse_array

app = Flask(__name__, template_folder="templates", static_folder="static")

VALIDATORS = {
    "roll_id": ("Student roll ID", ROLL_ID_DFA),
    "username": ("Username", USERNAME_DFA),
    "course_code": ("Course code", COURSE_CODE_DFA),
}

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/check")
def check():
    payload = request.get_json(silent=True) or {}
    mode = payload.get("mode", "roll_id")
    value = str(payload.get("value", ""))
    try:
        if mode in VALIDATORS:
            label, machine = VALIDATORS[mode]
            trace = machine.trace(value)
            return jsonify({"label": label, "accepted": trace[-1]["state"] in machine.accepting,
                            "trace": trace, "note": "Formal syntax check only; semantic checks require application data."})
        if mode == "brackets":
            result = BRACKET_DPDA.run(value)
            return jsonify({"label": "Balanced delimiters", "accepted": result.accepted,
                            "trace": result.moves, "note": result.reason})
        if mode == "expression":
            tokens = expression_tokens(value)
            pda = EXPRESSION_NPDA.run(tokens)
            tree, answer = parse_and_evaluate(value)
            return jsonify({"label": "Arithmetic expression", "accepted": pda.accepted,
                            "trace": pda.moves, "note": f"Evaluated value: {answer:g}; configurations: {pda.explored_configurations}"})
        if mode == "array":
            tokens = array_tokens(value)
            pda = ARRAY_NPDA.run(tokens)
            parsed = parse_array(value)
            return jsonify({"label": "Nested array literal", "accepted": pda.accepted,
                            "trace": pda.moves, "note": f"Parsed value: {parsed}; configurations: {pda.explored_configurations}"})
        return jsonify({"error": "Unknown validation mode"}), 400
    except (ValueError, ZeroDivisionError) as error:
        return jsonify({"label": mode, "accepted": False, "trace": [], "note": str(error)})
