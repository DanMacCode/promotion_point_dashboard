import dash
from dash import html

dash.register_page(
    __name__,
    path="/demo",
    name="Demo"
)

layout = html.Div(
    [
        # ── Video Embed ───────────────────────────────────────────
        html.Div(
            [
                html.Iframe(
                    src="https://www.youtube.com/embed/oPpEh6ny_EI?start=185",
                    style={
                        "width": "75%",
                        "maxWidth": "1200px",
                        "height": "800px",
                        "border": "none",
                        "display": "block",
                    },
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                )
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "padding": "0 30px",
            }
        ),
        html.Div(style={"flex": "1"}),

        # ── Footer ────────────────────────────────────────────────
        html.Footer(
            children=[
                html.Hr(),
                html.Div(
                    [
                        html.P(
                            "This Page Is NOT DoD Affiliated. I am just an NCO who got tired of remaking excels to speculate about points.",
                            className="mb-0"
                        ),
                        html.P("Contact: PromotionPointDashboard@gmail.com", className="mb-0"),
                        html.P("© 2025 Army Promotion Point Dashboard", className="mb-0"),
                    ],
                    className="text-center"
                ),
                html.Div(style={"height": "40px"})
            ],
            style={
                "backgroundColor": "#013220",
                "color": "yellow",
                "padding": "0px",
                "width": "100%",
            }
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "minHeight": "100vh",
        "paddingBottom": "0px",
    }
)







