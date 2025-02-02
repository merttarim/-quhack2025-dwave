# demo_interface.py
from dash import html, dcc


def create_interface():
    return html.Div(
        id="app-container",
        style={
            "maxWidth": "1200px",
            "margin": "0 auto",
            "padding": "2rem",
            "fontFamily": "Arial, sans-serif",
            "textAlign": "center"
        },
        children=[
            html.H1("Time-Dependent QAP Solver"),
            html.P(
                "Set the number of time steps and the relocation cost weight (λ), then click 'Run Optimization' to solve the time-dependent QAP."
            ),
            html.Div(
                [
                    html.Label("Number of Time Steps:"),
                    dcc.Slider(
                        id="time-steps-slider",
                        min=1,
                        max=10,
                        step=1,
                        value=3,
                        marks={i: str(i) for i in range(1, 11)},
                        tooltip={"placement": "bottom", "always_visible": True},
                    )
                ],
                style={"margin": "1rem 0"}
            ),
            html.Div(
                [
                    html.Label("Relocation Cost Weight (λ):"),
                    dcc.Slider(
                        id="lambda-slider",
                        min=0,
                        max=10,
                        step=0.5,
                        value=2.0,
                        marks={i: str(i) for i in range(0, 11)},
                        tooltip={"placement": "bottom", "always_visible": True},
                    )
                ],
                style={"margin": "1rem 0"}
            ),
            html.Button(
                "Run Optimization",
                id="run-button",
                n_clicks=0,
                style={"fontSize": "1.2rem", "padding": "0.5rem 1rem", "marginTop": "1rem"}
            ),
            html.Div(id="output-container", style={"marginTop": "2rem"})
        ]
    )
