# pages/dashboard.py
import dash
from dash import html, dcc
import pandas as pd
import requests
import dash_bootstrap_components as dbc

from dash import Input, Output, callback

from dashboard_scripts.update_change_graph import create_change_graph
from dashboard_scripts.bayesian_adjustment import compute_bayesian_promotion_probability
from dashboard_scripts.predict_next_promotion import predict_next_promotion_points
from dashboard_scripts.calculate_promotion_percentage import calculate_promotion_percentage

dash.register_page(__name__, path="/", name="Home", order=0)

csv_url = "https://raw.githubusercontent.com/DanMacCode/promotion_point_dashboard/main/data/master/master_promotion_data.csv"
try:
    df = pd.read_csv(csv_url)
except Exception:
    df = pd.DataFrame()

if not df.empty and "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%b", errors="coerce")
    sorted_dates = df["Date"].dropna().sort_values().dt.strftime("%b-%Y").unique().tolist()
else:
    sorted_dates = []

coming_soon_url = "https://raw.githubusercontent.com/DanMacCode/promotion_point_dashboard/refs/heads/main/data/master/coming_soon.md"
try:
    coming_soon_text = requests.get(coming_soon_url).text
except Exception:
    coming_soon_text = "Failed to load upcoming changes."

PAGE_CONTAINER_STYLE = {
    "maxWidth": "1280px",
    "margin": "0 auto",
    "paddingLeft": "16px",
    "paddingRight": "16px",
}

CARD_STYLE = {
    "border": "1px solid #ddd",
    "borderRadius": "10px",
    "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
    "padding": "15px",
    "backgroundColor": "#ffffff",
}

CARD_STRETCH_STYLE = {
    **CARD_STYLE,
    "height": "100%",
    "display": "flex",
    "flexDirection": "column",
}

# Bottom row must NOT let Details decide the row height.
# We set a fixed card height for all 3 so they align,
# and the Details table scrolls inside its panel.
BOTTOM_ROW_CARD_HEIGHT = "520px"
BOTTOM_ROW_CARD_STYLE = {
    **CARD_STRETCH_STYLE,
    "height": BOTTOM_ROW_CARD_HEIGHT,
}

# Legend placement target for the streamgraph figure.
# Apply this in the callback that builds the streamgraph figure:
# fig.update_layout(legend=STREAMGRAPH_LEGEND_LAYOUT)
STREAMGRAPH_LEGEND_LAYOUT = {
    "orientation": "h",
    "x": 0.5,
    "xanchor": "center",
    "y": -0.25,
    "yanchor": "top",
}

layout = html.Div(
    [
        html.Div(
            [
                # ─────────────────────────────────────────────────────────
                # Selection controls row
                # ─────────────────────────────────────────────────────────
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    "Load Data From:",
                                    id="label-load-data-from",
                                    style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"},
                                ),
                                dcc.Dropdown(
                                    id="date-range-start",
                                    options=[{"label": d, "value": d} for d in sorted_dates],
                                    placeholder="Select Start Month",
                                    style={"width": "200px", "marginBottom": "2px", "textAlign": "center"},
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.P(
                                    "Load Data To:",
                                    id="label-load-data-to",
                                    style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"},
                                ),
                                dcc.Dropdown(
                                    id="date-range-end",
                                    options=[{"label": d, "value": d} for d in sorted_dates],
                                    placeholder="Select End Month",
                                    style={"width": "200px", "marginBottom": "2px", "textAlign": "center"},
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.P(
                                    "Component:",
                                    id="label-component",
                                    style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"},
                                ),
                                dcc.Dropdown(
                                    id="component-dropdown",
                                    options=[{"label": "Active", "value": "Active"}, {"label": "Reserve", "value": "Reserve"}],
                                    placeholder="Select Component",
                                    style={"width": "200px", "fontSize": "16px", "textAlign": "center"},
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.P(
                                    "Cutoff Scores For:",
                                    id="label-rank",
                                    style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"},
                                ),
                                dcc.Dropdown(
                                    id="rank-dropdown",
                                    options=[{"label": "SGT", "value": "SGT"}, {"label": "SSG", "value": "SSG"}],
                                    placeholder="Select Rank",
                                    style={"width": "150px", "fontSize": "16px", "textAlign": "center"},
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.P(
                                    "MOS Code:",
                                    id="label-mos-code",
                                    style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"},
                                ),
                                dcc.Dropdown(
                                    id="mos-dropdown",
                                    options=[{"label": mos, "value": mos} for mos in df["MOS"].unique()]
                                    if (not df.empty and "MOS" in df.columns)
                                    else [],
                                    placeholder="Select MOS",
                                    style={"width": "150px", "fontSize": "16px", "textAlign": "center"},
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Button(
                                    "Load Data",
                                    id="load-button",
                                    style={"backgroundColor": "green", "color": "white", "padding": "10px", "fontSize": "14px"},
                                ),
                                html.Button(
                                    "Clear Data",
                                    id="clear-button",
                                    style={
                                        "backgroundColor": "gray",
                                        "color": "white",
                                        "padding": "10px",
                                        "fontSize": "14px",
                                        "marginLeft": "5px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "row",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "gap": "5px",
                                "marginTop": "15px",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-around",
                        "gap": "10px",
                        "padding": "10px",
                        "flexWrap": "wrap",
                    },
                ),

                # ─────────────────────────────────────────────────────────
                # User points input
                # ─────────────────────────────────────────────────────────
                html.Div(
                    [
                        html.P("See where you measure up. Input your promotion points:", id="label-user-prompts"),
                        dcc.Dropdown(
                            id="user-points",
                            options=[{"label": str(i), "value": i} for i in range(24, 799)],
                            placeholder="Input Your Points",
                            style={"width": "220px", "margin": "0 auto"},
                            searchable=True,
                            clearable=True,
                        ),
                    ],
                    style={"textAlign": "center", "marginBottom": "20px"},
                ),

                # ─────────────────────────────────────────────────────────
                # Top chart row: responsive and height-aligned
                # ─────────────────────────────────────────────────────────
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(
                                        dcc.Graph(id="promotion-graph", style={"position": "relative"}),
                                        style={"flex": "1"},
                                    ),
                                    html.Div(
                                        [
                                            dcc.Checklist(
                                                id="toggle-probability",
                                                options=[{"label": "Your Points", "value": "show"}],
                                                value=["show"],
                                                style={"fontSize": "10px", "lineHeight": "12px"},
                                            ),
                                            dcc.Checklist(
                                                id="trendline-checkbox",
                                                options=[{"label": "Show Trend", "value": "trend"}],
                                                value=[],
                                                style={"fontSize": "10px", "lineHeight": "12px", "marginBottom": "5px"},
                                            ),
                                            dcc.Checklist(
                                                id="volatility-checkbox",
                                                options=[{"label": "Show Volatility", "value": "volatility"}],
                                                value=[],
                                                style={"fontSize": "10px", "lineHeight": "12px"},
                                            ),
                                        ],
                                        id="points-trend-controls",
                                        style={
                                            "position": "absolute",
                                            "bottom": "0px",
                                            "right": "5px",
                                            "backgroundColor": "rgba(255,255,255,0.8)",
                                            "padding": "5px",
                                            "borderRadius": "5px",
                                            "boxShadow": "0px 0px 5px rgba(0,0,0,0.3)",
                                        },
                                    ),
                                ],
                                style={**CARD_STRETCH_STYLE, "position": "relative"},
                            ),
                            xs=12,
                            lg=9,
                        ),
                        dbc.Col(
                            html.Div(
                                dbc.Accordion(
                                    [
                                        dbc.AccordionItem(
                                            html.Div(
                                                dcc.Markdown(coming_soon_text),
                                                id="features-list",
                                                style={"paddingLeft": "1rem", "marginTop": "0.5rem"},
                                            ),
                                            title="Coming Soon",
                                        ),
                                        dbc.AccordionItem(
                                            html.P(
                                                """All data is sourced from the monthly AR 600-8-19 “Promotion Point Cutoff” publications.
A scraper pulled every report since August 2023, which was when secondary and primary points were unified. The PDFs
(turned TXTs) are parsed into CSVs with all relevant fields mapped. The Master CSV auto-updates on the 29th, each month.
If the Army alters their format, you will see discrepancies until I update the logic."""
                                            ),
                                            id="data-sourcing-text",
                                            style={"padding": "0.0rem 0.0rem"},
                                            title="Data Sourcing",
                                            item_id="data-sourcing",
                                        ),
                                    ],
                                    start_collapsed=True,
                                    active_item="data-sourcing",
                                    flush=True,
                                    className="accordian",
                                ),
                                style={
                                    **CARD_STRETCH_STYLE,
                                    "backgroundColor": "#f8f9fa",
                                    "padding": "10px",
                                },
                            ),
                            xs=12,
                            lg=3,
                        ),
                    ],
                    className="g-3",
                    align="stretch",
                    style={"marginBottom": "20px"},
                ),

                # ─────────────────────────────────────────────────────────
                # KPI cards row: responsive and height-aligned
                # ─────────────────────────────────────────────────────────
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                id="prediction-text",
                                children=[
                                    html.Div(
                                        [
                                            html.H4(
                                                "Next Month's Predicted Cutoff",
                                                style={"textAlign": "center", "margin": "0", "flex": "1"},
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        "ℹ️",
                                                        id="info-icon",
                                                        style={"fontSize": "20px", "color": "#007BFF", "cursor": "pointer"},
                                                    ),
                                                    dbc.Tooltip(
                                                        [
                                                            html.B("Reliability:"),
                                                            html.Br(),
                                                            "The prediction is made using Ordinary Least Squares (OLS) Linear Regression, which relies on historical data for the following month's prediction. ",
                                                            "It cannot anticipate the needs of the Army. ",
                                                            "The more outliers there are for your MOS, the less accurate OLS regression will be, since one of this model's core assumptions is that the past has a linear relationship with the future.",
                                                            html.Br(),
                                                            html.Br(),
                                                            html.B("Confidence Intervals:"),
                                                            html.Br(),
                                                            "Confidence intervals are the model's prediction for the upper and lower range of expected outcomes. ",
                                                            "A result of the bias-variance tradeoff is such that the higher your confidence interval, the wider the range of points will be, and the lower your confidence interval, the narrower the point range will be.",
                                                            html.Br(),
                                                            html.Br(),
                                                            html.B("Pro Tip:"),
                                                            html.Br(),
                                                            "Your date range informs the OLS model. Consider excluding months with outliers for more accurate predictions.",
                                                        ],
                                                        target="info-icon",
                                                        placement="right",
                                                        autohide=False,
                                                        className="wide-tooltip",
                                                        style={
                                                            "fontSize": "14px",
                                                            "width": "700px",
                                                            "whiteSpace": "normal",
                                                            "padding": "10px",
                                                            "textAlign": "left",
                                                        },
                                                    ),
                                                ],
                                                id="info-icon-container",
                                                style={"position": "absolute", "top": "4px", "right": "4px", "maxWidth": "700px"},
                                            ),
                                        ],
                                        style={
                                            "position": "relative",
                                            "display": "flex",
                                            "justifyContent": "center",
                                            "alignItems": "center",
                                        },
                                    ),
                                    html.H2(
                                        id="predicted-cutoff",
                                        style={"textAlign": "center", "fontSize": "36px", "margin": "0", "color": "green"},
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Confidence Interval: There is a ", style={"fontSize": "16px"}),
                                            dcc.Dropdown(
                                                id="ci-level-dropdown",
                                                options=[{"label": f"{i}", "value": i} for i in range(50, 100, 5)],
                                                value=95,
                                                clearable=False,
                                                style={"width": "80px", "display": "inline-block", "verticalAlign": "middle"},
                                            ),
                                            html.Span("% chance next month's cutoff will be between ", style={"fontSize": "16px"}),
                                            html.Span(id="ci-lower", style={"fontSize": "16px", "fontWeight": "bold"}),
                                            html.Span(" - ", style={"fontSize": "16px"}),
                                            html.Span(id="ci-upper", style={"fontSize": "16px", "fontWeight": "bold"}),
                                        ],
                                        style={"textAlign": "center", "marginTop": "8px"},
                                    ),
                                ],
                                style={**CARD_STRETCH_STYLE, "padding": "12px"},
                            ),
                            xs=12,
                            md=6,
                            lg=4,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H4(
                                        "Percentage of Soldiers Promoted",
                                        id="percentage-title",
                                        style={"textAlign": "center", "margin": "0"},
                                    ),
                                    html.Div(id="percentage-box", style={"textAlign": "center", "margin": "0"}),
                                ],
                                style={**CARD_STRETCH_STYLE, "padding": "12px"},
                            ),
                            xs=12,
                            md=6,
                            lg=4,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H4(
                                        "⚠️ DoD Network Limitations ⚠️",
                                        style={"textAlign": "center", "color": "orange", "margin": "0"},
                                    ),
                                    html.P(
                                        "DoD networks often prohibit write permissions. If you are on a system with these restrictions, you will be unable to use dark mode, type your promotion points, or check boxes on the points over time plot.",
                                        style={"textAlign": "center", "fontSize": "14px", "margin": "0"},
                                    ),
                                ],
                                className="warning-box",
                                style={**CARD_STRETCH_STYLE, "padding": "12px"},
                            ),
                            xs=12,
                            md=12,
                            lg=4,
                        ),
                    ],
                    className="g-3",
                    align="stretch",
                    style={"marginTop": "16px", "marginBottom": "10px"},
                ),

                # ─────────────────────────────────────────────────────────
                # Probability gauges row: responsive and height-aligned
                # ─────────────────────────────────────────────────────────
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(
                                        dcc.Graph(id="historical-probability-gauge", style={"width": "100%", "height": "230px"}),
                                        style={"flex": "1"},
                                    ),
                                    html.Div(
                                        id="probability-text",
                                        style={
                                            "fontSize": "16px",
                                            "color": "green",
                                            "textAlign": "center",
                                            "lineHeight": "1.5",
                                            "padding": "0 10px",
                                        },
                                    ),
                                ],
                                style=CARD_STRETCH_STYLE,
                            ),
                            xs=12,
                            lg=6,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(
                                        dcc.Graph(id="predicted-probability-gauge", style={"width": "100%", "height": "230px"}),
                                        style={"flex": "1"},
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                "ℹ️",
                                                id="bayes-info",
                                                style={
                                                    "fontSize": "20px",
                                                    "color": "blue",
                                                    "cursor": "pointer",
                                                    "marginLeft": "8px",
                                                },
                                            ),
                                            dbc.Tooltip(
                                                [
                                                    html.B("How it works (Simplified):"),
                                                    html.Br(),
                                                    "1) (wins) = (months where your points ≥ cutoff)",
                                                    html.Br(),
                                                    "2) (base rate) = wins / (total months)",
                                                    html.Br(),
                                                    "3) (vol frac) = (high vol months) / (total months)",
                                                    html.Br(),
                                                    html.B("Formula:"),
                                                    html.Br(),
                                                    "(% adjusted) = (base rate) × ((1 - vol frac) × 100)",
                                                ],
                                                target="bayes-info",
                                                placement="top",
                                                style={"maxWidth": "300px", "whiteSpace": "normal", "fontSize": "14px"},
                                                autohide=False,
                                            ),
                                        ],
                                        style={"display": "inline-flex", "justifyContent": "center", "width": "100%", "marginTop": "6px"},
                                    ),
                                    html.P(
                                        "Evidence weighting adjusts for volatility by down-weighting months with large jumps in promotion points. It calculates your historical chance, then penalizes it based on your MOS's unpredictability.",
                                        id="bayes-text",
                                        style={"textAlign": "center", "fontSize": "16px"},
                                    ),
                                ],
                                className="white-box",
                                style=CARD_STRETCH_STYLE,
                            ),
                            xs=12,
                            lg=6,
                        ),
                    ],
                    className="g-3",
                    align="stretch",
                    style={"marginTop": "24px", "marginBottom": "24px"},
                ),

                # ─────────────────────────────────────────────────────────
                # Change graph row: wrap graph in a card container
                # ─────────────────────────────────────────────────────────
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="change-graph", style={"width": "100%"})],
                            style={
                                "border": "1px solid #ddd",
                                "borderRadius": "10px",
                                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                                "padding": "15px",
                                "backgroundColor": "#ffffff",
                            },
                        )
                    ],
                    style={"marginBottom": "20px"},
                ),

                # ─────────────────────────────────────────────────────────
                # Bottom row: fixed height so Details never stretches the plots
                # ─────────────────────────────────────────────────────────
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(dcc.Graph(id="competitiveness-graph"), style={"flex": "1", "minHeight": "0"}),
                                    html.P(
                                        "This graph shows the ratio of promotions to eligible soldiers. The higher the score the less competitive.",
                                        id="competitiveness-text",
                                        style={"textAlign": "center", "fontSize": "14px", "marginBottom": "0"},
                                    ),
                                ],
                                style=BOTTOM_ROW_CARD_STYLE,
                            ),
                            xs=12,
                            md=6,
                            lg=4,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(dcc.Graph(id="streamgraph"), style={"flex": "1", "minHeight": "0"}),
                                    html.P(
                                        "Visualize the population of those eligible for promotion versus those selected for promotion.",
                                        id="streamgraph-text",
                                        style={"textAlign": "center", "fontSize": "14px", "marginBottom": "0"},
                                    ),
                                ],
                                style=BOTTOM_ROW_CARD_STYLE,
                            ),
                            xs=12,
                            md=6,
                            lg=5,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H4("Details", id="label-details-title", style={"textAlign": "center", "marginTop": "0"}),
                                    html.Div(
                                        id="sidebar-details",
                                        style={
                                            "flex": "1",
                                            "minHeight": "0",
                                            "overflowY": "auto",
                                            "border": "1px solid #ddd",
                                            "padding": "0px",
                                            "borderRadius": "5px",
                                            "backgroundColor": "#f8f8f8",
                                        },
                                    ),
                                ],
                                style=BOTTOM_ROW_CARD_STYLE,
                            ),
                            xs=12,
                            md=12,
                            lg=3,
                        ),
                    ],
                    className="g-3",
                    align="stretch",
                    style={"marginBottom": "20px"},
                ),
            ],
            style=PAGE_CONTAINER_STYLE,
        ),

        html.Footer(
            children=[
                html.Hr(),
                html.Div(
                    [
                        html.P(
                            "This Page Is NOT DoD Affiliated. I am just an NCO who got tired of remaking excels to speculate about points.",
                            className="mb-0",
                        ),
                        html.P("Contact: PromotionPointDashboard@gmail.com", className="mb-0"),
                        html.P("© 2025 Army Promotion Point Dashboard", className="mb-0"),
                    ],
                    className="text-center",
                ),
                html.Div(style={"height": "40px"}),
            ],
            style={"backgroundColor": "#013220", "color": "yellow", "padding": "0px", "width": "100%"},
        ),
    ],
    id="home-page-wrapper",
    style={
        "minHeight": "100vh",
        "display": "flex",
        "flexDirection": "column",
    },
)

# NOTE ON STREAMGRAPH LEGEND
# The legend position (side vs below) is controlled by the Plotly figure layout,
# not by the dcc.Graph component. To move the legend below the streamgraph,
# update the callback that creates the streamgraph figure with:
#
# fig.update_layout(legend=STREAMGRAPH_LEGEND_LAYOUT)
#
# If you paste the callback that outputs the "streamgraph" figure, I will modify it safely
# without changing the data logic or any IDs.