"""Start the optional Flask browser demonstration: python serve_demo.py."""
from automata_casebook.web.app import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
