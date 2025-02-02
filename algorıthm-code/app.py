# app.py
from dash import Dash
from demo_interface import create_interface
import demo_callbacks  # This registers the callbacks


app = Dash(__name__)
app.title = "Time-Dependent QAP Solver Demo"
app.layout = create_interface()


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8051)
