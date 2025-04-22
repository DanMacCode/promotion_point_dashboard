# pages/about.py
import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(
    __name__,
    path="/about",
    name="About"
)

# this Div will hold all of your H1/H2/P text, with left/right gutters
body = html.Div(id="about-body-content", style={
    "flex": "1",               # take all available vertical space
    "marginLeft": "4in",
    "marginRight": "4in",
    "paddingTop": "30px",
    "paddingBottom": "30px",
    "fontFamily": "Arial, sans-serif",
})

# footer lives outside of the gutters, at 100% width
footer = html.Footer(
    children=[
        html.Hr(style={"margin": "0"}),
        html.Div(
            [
                html.P(
                    "This Page Is NOT DoD Affiliated. "
                    "I am just an NCO who got tired of remaking excels to speculate about points.",
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
        "color": "gold",
        "padding": "10px 0",
        "width": "100%",
        "flex": "none"           # prevents this from growing
    }
)

# outer wrapper: flex column, full viewport height
layout = html.Div(
    [ body, footer ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "minHeight": "100vh",
    }
)


@callback(
    Output("about-body-content", "children"),
    Input("dark-mode-store", "data"),
    allow_duplicate=True
)
def update_about_text(is_dark):
    text_color = "white" if is_dark else "black"
    return [
        html.H1(
            "About The Army Promotion Point Dashboard",
            style={
                "color": "gold",
                "textAlign": "center",
                "fontFamily": "Georgia, serif",
                "marginBottom": "0.5em"
            }
        ),
        html.H2(
            "My Mission",
            style={
                "color": "green",
                "marginTop": "2em",
                "fontFamily": "Georgia, serif"
            }
        ),
        html.P(
            "My mission is to provide soldiers with information, real-time insights into Army "
            "promotion point trends, and equip them with the tools to better plan their careers and advancement goals.",
            style={
                "fontSize": "18px",
                "marginBottom": "1.5em",
                "lineHeight": "1.5",
                "color": text_color
            }
        ),
        # … all your other H2/P …
        html.H2(
            "About The Author",
            style={
                "color": "green",
                "marginTop": "2em",
                "fontFamily": "Georgia, serif"
            }
        ),
        html.P(
            [
                "I’m a Staff Sergeant with five years of Active Component service, now dual‑hatted alongside an East "
                "Coast National Guard unit. I’m also completing an M.S. in Data Analytics and Policy at Johns Hopkins "
                "University, concentrating in statistical analysis.",

            ],
            style={
                "fontSize": "18px",
                "marginBottom": "2em",
                "lineHeight": "1.5",
                "color": text_color
            }
        ),
        html.P(
            [
                "I’ve always believed in two things: relentless self‑development, and lifting others as you climb. After"
                " wrestling with Excel every month to predict my own promotion points, I realized I could build a tool that "
                "spares every soldier that hassle. I hope the sum of my developing efforts helps you not only achieve "
                "your goals but also generates your own itch, encouraging you to look around, find the gaps in your "
                "organization, and build solutions that lift not only yourself, but those around you as well. If even "
                "a handful of you find it useful, it’s worth every line of code. ",
            ],
            style={
                "fontSize": "18px",
                "marginBottom": "2em",
                "lineHeight": "1.5",
                "color": text_color
            }
        ),

        html.H2(
            "My Philosophy",
            style={
                "color": "green",
                "marginTop": "2em",
                "fontFamily": "Georgia, serif"
            }
        ),
        html.P(
            [
                "The Army is a cornfield: you have a goal in mind, but the stalks obscure and befuddle your path. My aim"
                " is not only to reach the destination myself but to cut a trail that makes the journey smoother for everyone "
                "who follows.",
            ],
            style={
                "fontSize": "18px",
                "marginBottom": "2em",
                "lineHeight": "1.5",
                "color": text_color
            }
        ),

        html.P(
            [
                "If you take anything from this site, take two things. One: use the insights provided to gauge and "
                "improve your standing for promotion. Two: identify problems and create solutions that help not only yourself, but "
                "those around you as well.",
            ],
            style={
                "fontSize": "18px",
                "marginBottom": "2em",
                "lineHeight": "1.5",
                "color": text_color
            }
        ),
        html.P(
            [
                "And yes, you may still have to wrestle with one more Army tool that looks like its stuck in the "
                "2000s, but at least this one doesn't require a CAC.",
            ],
            style={
                "fontSize": "18px",
                "marginBottom": "2em",
                "lineHeight": "1.5",
                "color": text_color
            }
        ),
        html.P(
            [
                "Cheers! And go get your promotions!",
            ],
            style={
                "fontSize": "18px",
                "marginBottom": "2em",
                "lineHeight": "1.5",
                "color": text_color
            }
        ),
        html.H2(
            "Contact Me",
            style={
                "color": "green",
                "marginTop": "2em",
                "fontFamily": "Georgia, serif"
            }
        ),
        html.P([
            "All feedback, suggestions, and input are welcome. Reach out at ",
            html.A(
                "promotionpointdashboard@gmail.com",
                href="mailto:promotionpointdashboard@gmail.com",
                style={"color": "green", "textDecoration": "underline"}
            ),
            "."
        ],
            style={"fontSize": "18px", "marginBottom": "2em",
                   "lineHeight": "1.5", "color": text_color}
        ),
    ]
