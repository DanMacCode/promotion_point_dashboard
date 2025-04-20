import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import numpy as np
import requests
import pandas as pd
import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from dashboard_scripts.update_change_graph import create_change_graph
from dashboard_scripts.bayesian_adjustment import compute_bayesian_promotion_probability
from dashboard_scripts.predict_next_promotion import predict_next_promotion_points
import dash_bootstrap_components as dbc

from dashboard_scripts.calculate_promotion_percentage import calculate_promotion_percentage

app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootswatch@5.2.3/dist/cosmo/bootstrap.min.css",
        dbc.themes.BOOTSTRAP
    ]
)

# Load 'Coming Soon' content
coming_soon_url = "https://raw.githubusercontent.com/DanMacCode/promotion_point_dashboard/refs/heads/main/data/master/coming_soon.md"
try:
    coming_soon_text = requests.get(coming_soon_url).text
except:
    coming_soon_text = "Failed to load upcoming changes."

app.title = "Promotion Point Dashboard"
server = app.server

# Load CSV data from GitHub
csv_url = "https://raw.githubusercontent.com/DanMacCode/promotion_point_dashboard/main/data/master/master_promotion_data.csv"
try:
    df = pd.read_csv(csv_url)
    print("✅ Data successfully loaded.")
except Exception as e:
    print(f"🚨 Error loading CSV: {e}")
    df = pd.DataFrame()

# Format dates & create sorted list
df["Date"] = pd.to_datetime(df["Date"], format="%Y-%b", errors="coerce", dayfirst=False)
sorted_dates = df["Date"].dropna().sort_values().dt.strftime("%b-%Y").unique().tolist()

# Layout
app.layout = html.Div(
    [
        dcc.Markdown(
            """
            <style>
            .tooltip-inner {
                max-width: 1000px !important;
                width: 1000px !important;
                white-space: normal !important;
                text-align: left !important;
                padding: 10px !important;
                font-size: 14px !important;
            }
            </style>
            """,
            dangerously_allow_html=True
        )
        ,

        # Dashboard Title
        html.H1("Army Promotion Point Dashboard", style={"textAlign": "center", "color": "gold"},
                className="text-center fw-bold mt-3 mb-3"),

        # Dropdowns & Controls
        html.Div(
            [
                html.Div(
                    [
                        html.P("Load Data From:", id="label-load-data-from",
                               style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"}),
                        dcc.Dropdown(
                            id="date-range-start",
                            options=[{"label": d, "value": d} for d in sorted_dates],
                            placeholder="Select Start Month",
                            style={"width": "200px", "marginBottom": "2px", "textAlign": "center"}
                        )
                    ]
                ),
                html.Div(
                    [
                        html.P("Load Data To:", id="label-load-data-to",
                               style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"}),
                        dcc.Dropdown(
                            id="date-range-end",
                            options=[{"label": d, "value": d} for d in sorted_dates],
                            placeholder="Select End Month",
                            style={"width": "200px", "marginBottom": "2px", "textAlign": "center"}
                        )
                    ]
                ),
                html.Div(
                    [
                        html.P("Component:", id="label-component",
                               style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"}),
                        dcc.Dropdown(
                            id="component-dropdown",
                            options=[{"label": "Active", "value": "Active"}, {"label": "Reserve", "value": "Reserve"}],
                            placeholder="Select Component",
                            style={"width": "200px", "fontSize": "16px", "textAlign": "center"}
                        )
                    ]
                ),
                html.Div(
                    [
                        html.P("Cutoff Scores For:", id="label-rank",
                               style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"}),
                        dcc.Dropdown(
                            id="rank-dropdown",
                            options=[{"label": "SGT", "value": "SGT"}, {"label": "SSG", "value": "SSG"}],
                            placeholder="Select Rank",
                            style={"width": "150px", "fontSize": "16px", "textAlign": "center"}
                        )
                    ]
                ),
                html.Div(
                    [
                        html.P("MOS Code:", id="label-mos-code",
                               style={"marginBottom": "2px", "fontWeight": "bold", "textAlign": "center"}),
                        dcc.Dropdown(
                            id="mos-dropdown",
                            options=[{"label": mos, "value": mos} for mos in df["MOS"].unique()],
                            placeholder="Select MOS",
                            style={"width": "150px", "fontSize": "16px", "textAlign": "center"}
                        )
                    ]
                ),
                html.Div(
                    [
                        html.Button("Load Data", id="load-button",
                                    style={"backgroundColor": "green", "color": "white", "padding": "10px",
                                           "fontSize": "14px"}),
                        html.Button("Clear Data", id="clear-button",
                                    style={"backgroundColor": "gray", "color": "white", "padding": "10px",
                                           "fontSize": "14px", "marginLeft": "5px"}),
                        dbc.Switch(
                            id="dark-mode-switch",
                            label="Dark Mode",
                            value=False,
                            label_style={"color": "black"},
                            style={"marginLeft": "10px", "fontSize": "14px"}
                        )
                    ],
                    style={"display": "flex", "flexDirection": "row", "alignItems": "center",
                           "justifyContent": "center", "gap": "5px", "marginTop": "15px"}
                )
            ],
            style={"display": "flex", "justifyContent": "space-around", "gap": "10px", "padding": "10px",
                   "flexWrap": "wrap"}
        ),

        # Probability Statement
        html.Div(
            [
                html.P("See where you measure up. Input your promotion points:", id="label-user-prompts"),
                dcc.Dropdown(
                    id="user-points",
                    options=[{"label": str(i), "value": i} for i in range(24, 799)],
                    placeholder="Type your points",
                    style={"width": "200px", "margin": "0 auto"},
                    searchable=True,
                    clearable=True
                )
            ],
            style={"textAlign": "center", "marginBottom": "20px"}
        ),

        # Promotion Points Over Time Graph
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id="promotion-graph", style={"position": "relative"}),
                        html.Div(
                            [
                                dcc.Checklist(id="toggle-probability",
                                              options=[{"label": "Your Points", "value": "show"}],
                                              value=["show"], style={"fontSize": "10px", "lineHeight": "12px"}),
                                dcc.Checklist(id="trendline-checkbox",
                                              options=[{"label": "Show Trend", "value": "trend"}],
                                              value=[],
                                              style={"fontSize": "10px", "lineHeight": "12px", "marginBottom": "5px"}),
                                dcc.Checklist(id="volatility-checkbox",
                                              options=[{"label": "Show Volatility", "value": "volatility"}],
                                              value=[], style={"fontSize": "10px", "lineHeight": "12px"})
                            ],
                            style={"position": "absolute", "bottom": "0px", "right": "5px",
                                   "backgroundColor": "rgba(255,255,255,0.8)", "padding": "5px",
                                   "borderRadius": "5px", "boxShadow": "0px 0px 5px rgba(0,0,0,0.3)"}
                        )
                    ],
                    style={"width": "78%", "border": "1px solid #ddd", "borderRadius": "10px",
                           "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)", "padding": "15px",
                           "backgroundColor": "#ffffff", "position": "relative"}
                ),
                html.Div(
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                dcc.Markdown(coming_soon_text),style={"padding": "0.25rem 0.5rem"},
                                title="Coming Soon",
                            ),
                            dbc.AccordionItem(
                                html.P(
                                    """All data is sourced from the monthly AR 600‑8‑19 “Promotion Point Cutoff” publications. 
                                    A scraper pulled every report since August 2023, which was when secondary and primary points were unified. The PDFs
                                      (turned TXTs) are parsed into CSVs with all relevant fields mapped. The Master CSV auto-updates on the 29th, each month. 
                                    If the Army alters their format, you’ll see discrepancies until I update the logic."""
                                ), style={"padding": "0.0rem 0.0rem"},
                                title="Data Sourcing",
                                item_id="data-sourcing",
                            ),
                        ],
                        start_collapsed=True,
                        active_item="data-sourcing",
                        flush=True,
                        className="accordian"
                    ),
                    style={
                        "width": "20%",
                        "marginLeft": "2%",
                        "backgroundColor": "#f8f9fa",
                    }
                )
            ],
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start",
                   "marginBottom": "20px", "marginLeft": "2in", "marginRight": "2in"}
        ),

        # New row for predicted cutoff, promotion percentage, and limited functionality notice
        # New row for predicted cutoff, promotion percentage, and limited functionality notice
        # New row for predicted cutoff, promotion percentage, and limited functionality
        html.Div(
            [
                # Box 1: Next Month's Predicted Cutoff
                html.Div(
                    id="prediction-text",
                    children=[
                        html.Div(
                            [
                                html.H4("Next Month's Predicted Cutoff",
                                        style={"textAlign": "center", "margin": "0", "flex": "1"}),
                                html.Div(
                                    [
                                        html.Div(
                                            "ℹ️", id="info-icon",
                                            style={"fontSize": "20px", "color": "#007BFF", "cursor": "pointer"}
                                        ),
                                        dbc.Tooltip(
                                            [
                                                html.B("Reliability:"), html.Br(),
                                                "The prediction is made using Ordinary Least Squares (OLS) Linear Regression, which relies on historical data for the following month's predidiction. ",
                                                "It cannot anticipate the needs of the Army. ",
                                                "The more outliers there are for your MOS, the less accurate OLS regression will be, since one of this model's core assumptions is that the past has a linear relationship with the future.",
                                                html.Br(), html.Br(),

                                                html.B("Confidence Intervals:"), html.Br(),
                                                "Confidence intervals are the model's prediction for the upper and lower range of expected outcomes. ",
                                                "A result of the bias-variance tradeoff is such that the higher your confidence interval, the wider the range of points will be, and the lower your confidence interval, the narrower the point range will be.",
                                                html.Br(), html.Br(),

                                                html.B("Pro Tip:"), html.Br(),
                                                "Your date range informs the OLS model. Consider excluding months with outliers for more accurate predictions."
                                            ],

                                            target="info-icon",
                                            placement="right",
                                            autohide=False,
                                            className="wide-tooltip",
                                            style={"fontSize": "14px",
                                                    "width": "700px",
                                                    "whiteSpace": "normal",
                                                    "padding": "10px",
                                                    "textAlign": "left"},


                                        )
                                    ],
                                    id="info-icon-container",
                                    style={"position": "absolute", "top": "4px", "right": "4px","maxWidth": "700px"}
                                )
                            ],
                            style={"position": "relative", "display": "flex", "justifyContent": "center",
                                   "alignItems": "center"}
                        ),

                        # Predicted Cutoff Big Number
                        html.H2(
                            id="predicted-cutoff",
                            style={"textAlign": "center", "fontSize": "36px", "margin": "0", "color": "green"}
                        ),

                        # Confidence Interval Row
                        html.Div(
                            [
                                html.Span("Confidence Interval: There is a ", style={"fontSize": "20px"}),
                                dcc.Dropdown(
                                    id="ci-level-dropdown",
                                    options=[{"label": f"{i}", "value": i} for i in range(50, 100, 5)],
                                    value=95,
                                    clearable=False,
                                    style={"width": "60px", "display": "inline-block", "verticalAlign": "middle",
                                           "padding": "0"}
                                ),
                                html.Span("% chance next month's cutoff will be between ", style={"fontSize": "20px"}),
                                html.Span(id="ci-lower", style={"fontSize": "20px", "fontWeight": "bold"}),
                                html.Span(" – ", style={"fontSize": "20px"}),
                                html.Span(id="ci-upper", style={"fontSize": "20px", "fontWeight": "bold"}),
                            ],
                            style={"textAlign": "center", "marginTop": "8px", "fontSize": "20px"}
                        )
                    ],
                    style={
                        "flex": "0 0 30%",
                        "boxSizing": "border-box",
                        "border": "1px solid #ddd",
                        "borderRadius": "10px",
                        "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                        "padding": "5px",
                        "backgroundColor": "#ffffff"
                    }
                ),

                # Box 2: Soldier Promotion Percentage
                html.Div(
                    [
                        html.H4("Percentage of Soldiers Promoted", style={"textAlign": "center", "margin": "0"}),
                        html.Div(
                            id="percentage-box",
                            style={"textAlign": "center", "color": "blue", "margin": "0"}
                        )
                    ],
                    style={
                        "flex": "0 0 30%",
                        "boxSizing": "border-box",
                        "border": "1px solid #ddd",
                        "borderRadius": "10px",
                        "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                        "padding": "5px",
                        "backgroundColor": "#ffffff"
                    }
                ),

                # Box 3: Limited Functionality Notice
                html.Div(
                    [
                        html.H4("⚠️ DoD Network Limitations ⚠️",
                                style={"textAlign": "center", "color": "orange", "margin": "0"}),
                        html.P(
                            "DoD networks often prohibit write permissions. If you are on a system with these resitrictions, "
                            "you will be unable to use dark mode or check boxes on the points over time plot."
                            ,
                            style={"textAlign": "center", "fontSize": "17px", "color": "black", "margin": "0"}
                        )
                    ],
                    style={
                        "flex": "0 0 30%",
                        "boxSizing": "border-box",
                        "border": "1px solid #ddd",
                        "borderRadius": "10px",
                        "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                        "padding": "5px",
                        "backgroundColor": "#ffffff"
                    }
                )
            ],
            style={
                # Let the parent use a fixed calculated width so both rows are consistent.
                "width": "calc(100% - 4in)",  # 4in is removed for left/right margins
                "marginLeft": "2in",
                "marginRight": "2in",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "stretch",
                "gap": "4px",
                "marginTop": "20px",
                "marginBottom": "10px"
            }
        )

        ,

        # Promotion Probability (Top Row)
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(id="historical-probability-gauge",
                                          style={"width": "100%", "height": "230px"}),
                                html.Div(id="probability-text",
                                         style={"fontSize": "16px", "color": "green", "textAlign": "center",
                                                "lineHeight": "1.5", "padding": "0 10px"})
                            ],
                            style={
                                "width": "48%",
                                "border": "1px solid #ddd",
                                "borderRadius": "10px",
                                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                                "padding": "15px",
                                "backgroundColor": "#ffffff"
                            }
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id="predicted-probability-gauge",
                                    style={"width": "100%", "height": "230px"}
                                ),

                                # ─── Bayesian math info icon ───────────────────────────
                                html.Div(
                                    [
                                        html.Span(
                                            "ℹ️",
                                            id="bayes-info",
                                            style={
                                                "fontSize": "20px",
                                                "color": "blue",
                                                "cursor": "pointer",
                                                "marginLeft": "8px"
                                            }
                                        ),
                                        dbc.Tooltip(
                                            [
                                                html.B("How it works (Simplified):"), html.Br(),
                                                "1) (wins) = (months where your points ≥ cutoff)", html.Br(),
                                                "2) (base rate) = wins / (total months)", html.Br(),
                                                "3) (vol frac) = (high vol months) / (total_months)", html.Br(),
                                                html.B("Formula:"), html.Br(),
                                                "(% adjusted) = (base rate) × ((1 − vol frac) × 100)" ,html.Br(),
                                                "(For More Info: See Bayes Theorum)" ,html.Br(),

                                            ],
                                            target="bayes-info",
                                            placement="top",
                                            style={
                                                "maxWidth": "300px",
                                                "whiteSpace": "normal",
                                                "fontSize": "14px"
                                            },
                                            autohide=False
                                        )
                                    ],
                                    style={"display": "inline-flex", "alignItems": "right"}
                                ),

                                html.P(
                                    "Bayesian Probability adjusts for volatility by down‑weighting months with large jumps in promotion points. "
                                    "It calculates your historical chance, then penalizes it based on your MOS's unpredictability.",
                                    style={"textAlign": "center", "fontSize": "16px"}
                                )
                            ],
                            style={
                                "width": "48%",
                                "border": "1px solid #ddd",
                                "borderRadius": "10px",
                                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                                "padding": "15px",
                                "backgroundColor": "#ffffff"
                            }
                        ),
                    ],
                    style={"display": "flex", "justifyContent": "space-between", "gap": "4%", "flexWrap": "nowrap"}
                )
            ],
            style={"marginLeft": "2in", "marginRight": "2in", "marginTop": "40px", "marginBottom": "40px"}
        ),

        # Historical Point Fluctuation (Middle Row)
        html.Div(
            [
                dcc.Graph(id="change-graph", style={"width": "100%", "border": "1px solid #ddd", "borderRadius": "10px",
                                                    "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)", "padding": "15px",
                                                    "backgroundColor": "#ffffff", "marginBottom": "20px"})
            ],
            style={"marginLeft": "2in", "marginRight": "2in", "marginBottom": "20px"}
        ),

        # Competitiveness + Historical Soldier Selection + Details (Bottom Row)
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id="competitiveness-graph"),
                        html.P(
                            "This graph shows the ratio of promotions to eligible soldiers. A higher score indicates a less competitive MOS with more promotions relative to those eligible.",
                            style={"textAlign": "center", "fontSize": "14px"})
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "flex": "0 0 35%",
                        "border": "1px solid #ddd",
                        "borderRadius": "10px",
                        "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                        "padding": "15px",
                        "backgroundColor": "#ffffff"
                    }
                ),
                html.Div(
                    [
                        dcc.Graph(id="streamgraph"),
                        html.P(
                            "Visualize the population of those eligible for promotion versus those selected for promotion.",
                            style={"textAlign": "center", "fontSize": "14px"})
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "flex": "0 0 40%",
                        "border": "1px solid #ddd",
                        "borderRadius": "10px",
                        "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                        "padding": "15px",
                        "backgroundColor": "#ffffff"
                    }
                ),
                html.Div(
                    [
                        html.H4("Details", id="label-details-title", style={"textAlign": "center", "marginTop": "0"}),
                        html.Div(
                            [
                                html.Div(id="sidebar-details",
                                         style={"flex": 1, "overflowY": "auto", "border": "1px solid #ddd",
                                                "padding": "0px", "borderRadius": "5px", "backgroundColor": "#f8f8f8",
                                                "marginTop": "0px"})
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "border": "1px solid #ddd",
                                "borderRadius": "10px",
                                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                                "padding": "15px",
                                "backgroundColor": "#ffffff",
                                "flex": 1
                            }
                        )
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "flex": "0 0 20%"
                    }
                )
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "stretch",
                "gap": "20px",
                "marginBottom": "20px",
                "marginLeft": "2in",
                "marginRight": "2in"
            }
        ),

        html.Div(style={"flex": "1"}),

        html.Footer(
            children=[
                html.Hr(),
                html.Div(
                    [
                        html.P(
                            "This Page Is NOT DoD Affiliated. I am just an NCO who got tired of remaking excels to speculate about points.",
                            className="mb-0"),
                        html.P("Contact: PromotionPointDashboard@gmail.com", className="mb-0"),
                        html.P("© 2025 Army Promotion Point Dashboard", className="mb-0"),
                    ],
                    className="text-center"
                ),
                html.Div(style={"height": "40px"})
            ],
            style={"backgroundColor": "#013220", "color": "yellow", "padding": "0px", "width": "100%",
                   "position": "relative", "marginTop": "auto", "bottom": "0", "left": "0"}
        )
    ],
    id="page-content",
    style={"minHeight": "100vh", "display": "flex", "flexDirection": "column", "backgroundColor": "white"}
)


# Callback to clear dropdowns and input
@app.callback(
    [
        Output("date-range-start", "value"),
        Output("date-range-end", "value"),
        Output("component-dropdown", "value"),
        Output("rank-dropdown", "value"),
        Output("mos-dropdown", "value"),
        Output("user-points", "value"),
        Output("trendline-checkbox", "value"),
        Output("volatility-checkbox", "value"),
        Output("toggle-probability", "value")
    ],
    Input("clear-button", "n_clicks"),
    prevent_initial_call=True
)
def clear_inputs(n_clicks):
    return None, None, None, None, None, None, [], [], ["show"]


# Main callback to update figures and texts
@app.callback(
    [
        Output("promotion-graph", "figure"),
        Output("historical-probability-gauge", "figure"),
        Output("predicted-probability-gauge", "figure"),
        Output("change-graph", "figure"),
        Output("competitiveness-graph", "figure"),
        Output("streamgraph", "figure"),
        Output("probability-text", "children"),
        Output("predicted-cutoff", "children"),
        Output("ci-lower", "children"),
        Output("ci-upper", "children"),
        Output("percentage-box", "children")
    ],
    [
        Input("load-button", "n_clicks"),
        Input("ci-level-dropdown",  "value"),
        Input("user-points", "value"),
        Input("trendline-checkbox", "value"),
        Input("volatility-checkbox", "value"),
        Input("toggle-probability", "value")
    ],
    [
        State("date-range-start", "value"),
        State("date-range-end", "value"),
        State("component-dropdown", "value"),
        State("rank-dropdown", "value"),
        State("mos-dropdown", "value")
    ],
    prevent_initial_call=True
)
def update_graphs(n_clicks, ci_level, user_points, trendline, volatility, toggle_probability,
                  start_month, end_month, component, rank, mos):


    ctx = dash.callback_context
    empty_fig = px.line(title="No Data Available")
    # Check if all required inputs are provided.
    if not n_clicks or not start_month or not end_month or not rank or not mos or not component:
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "", "", ""

    # Filter the DataFrame based on dates and selections.
    filtered_df = df.copy()
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], format="%Y-%b", errors="coerce")
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(start_month, format="%b-%Y")) &
        (filtered_df["Date"] <= pd.to_datetime(end_month, format="%b-%Y"))
        ].sort_values(by="Date")
    if component:
        filtered_df = filtered_df[filtered_df["Component"].str.upper() == component.upper()]
    if mos:
        filtered_df = filtered_df[filtered_df["MOS"] == mos]
    if filtered_df.empty:
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "", "", ""

    promotion_column = "Cutoff_SGT" if rank == "SGT" else "Cutoff_SSG"
    promotions_col = "Promotions_SGT" if rank == "SGT" else "Promotions_SSG"
    eligibles_col = "Eligibles_SGT" if rank == "SGT" else "Eligibles_SSG"

    # Compute historical promotion probability.
    if user_points is not None:
        promoted_months = sum(1 for score in filtered_df[promotion_column] if score <= user_points)
    else:
        promoted_months = 0
    total_months = len(filtered_df)
    historical_probability = (promoted_months / total_months) * 100 if total_months > 0 else 0

    if user_points is not None and total_months > 0:
        failure_months = sum(1 for score in filtered_df[promotion_column] if user_points < score)
        adjusted_probability = (1 - (failure_months / total_months)) * 100 if total_months > 0 else 0
    else:
        adjusted_probability = 0
    adjusted_probability = compute_bayesian_promotion_probability(filtered_df, promotion_column, user_points)
    y_pred, (ci_lower, ci_upper) = predict_next_promotion_points(
        filtered_df, promotion_column, ci_level=ci_level
    )



    # Create Promotion Graph.
    fig1 = px.line(filtered_df, x="Date", y=promotion_column, title="Promotion Points Over Time", markers=True,
                   color_discrete_sequence=["green"], labels={promotion_column: "MOS Cutoffs"})
    fig1.update_traces(name="MOS Cutoff Points", showlegend=True)
    if "trend" in trendline:
        x_vals = np.arange(len(filtered_df))
        y_vals = filtered_df[promotion_column].dropna()
        if len(y_vals) > 1:
            trend_poly = np.polyfit(x_vals, y_vals, 1)
            trend_line = np.poly1d(trend_poly)(x_vals)
            fig1.add_scatter(x=filtered_df["Date"], y=trend_line, mode="lines", line=dict(color="gold", dash="solid"),
                             name="Trend Line")
    if "volatility" in volatility:
        filtered_df["Rolling_StdErr"] = filtered_df[promotion_column].rolling(window=3, min_periods=1).std()
        upper_bound = (filtered_df[promotion_column] + filtered_df["Rolling_StdErr"]).clip(upper=798)
        lower_bound = (filtered_df[promotion_column] - (0.5 * filtered_df["Rolling_StdErr"])).clip(lower=0)
        fig1.add_traces([
            go.Scatter(
                x=filtered_df["Date"].tolist() + filtered_df["Date"].tolist()[::-1],
                y=upper_bound.tolist() + lower_bound.tolist()[::-1],
                fill="toself",
                fillcolor="rgba(0, 128, 0, 0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Volatility Range",
                showlegend=True
            )
        ])
    if "show" in toggle_probability and user_points is not None:
        fig1.add_hline(y=user_points, line_dash="dash", line_color="red", annotation_text=f"Your Points: {user_points}",
                       annotation_position="top right", name="Your Points")

    fig2 = create_change_graph(filtered_df, promotion_column)
    filtered_df["Competitiveness"] = filtered_df[promotions_col] / filtered_df[eligibles_col]
    fig3 = px.bar(filtered_df, x="Date", y="Competitiveness", title="Competitiveness Score",
                  color_discrete_sequence=["green"])

    probability_text = html.Span(
        [
            f'Given the date range of {start_month} to {end_month}, with your promotion points at {user_points}, ',
            f'you would have promoted {promoted_months} out of {total_months} months. ',
            f'If the past is an indicator, you would have a {historical_probability:.1f}% chance of promoting next month.',
            html.Br()
        ],
        style={'color': 'red' if historical_probability < 50 else 'orange' if historical_probability < 80 else 'green'}
    ) if user_points is not None else ""

    filtered_df["Not_Promoted"] = (filtered_df[eligibles_col] - filtered_df[promotions_col]).clip(lower=0)
    filtered_df["Eligible_Total"] = filtered_df[eligibles_col]
    filtered_df = filtered_df.sort_values(by="Date")
    fig4 = go.Figure()
    fig4.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Not_Promoted"],
            fill='tozeroy',
            mode='none',
            name="Eligible not Promoted",
            fillcolor="green",
            opacity=0.6,
            hovertemplate=(
                "<b>Date</b>: %{x}<br>"
                "<b>Not Promoted</b>: %{y}"
                "<extra></extra>"
            )
        )
    )
    promoted_series = filtered_df[promotions_col]
    fig4.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Eligible_Total"],
            fill='tonexty',
            mode='none',
            name="Promoted",
            fillcolor="gold",
            opacity=0.9,
            customdata=promoted_series,
            hovertemplate=(
                "<b>Date</b>: %{x}<br>"
                "<b>Promoted</b>: %{customdata}"
                "<extra></extra>"
            )
        )
    )
    fig4.update_layout(
        title="Historical Soldier Selection",
        xaxis_title="Date",
        yaxis_title="# of Soldiers",
        showlegend=True,
        legend=dict(traceorder="normal")
    )

    fig5 = go.Figure(go.Indicator(mode="gauge+number", value=historical_probability,
                                  title={"text": "Historical Promotion Probability"},
                                  gauge={"axis": {"range": [0, 100]},
                                         "bar": {
                                             "color": "green" if historical_probability > 80 else "orange" if historical_probability > 50 else "red"}}))
    fig5.update_layout(margin=dict(t=45, b=25, l=35, r=35))

    fig6 = go.Figure(go.Indicator(mode="gauge+number", value=adjusted_probability,
                                  title={"text": "Bayesian Adjusted Promotion Probability"},
                                  gauge={"axis": {"range": [0, 100]},
                                         "bar": {
                                             "color": "green" if adjusted_probability > 80 else "orange" if adjusted_probability > 50 else "red"}}))
    fig6.update_layout(margin=dict(t=45, b=25, l=35, r=35))

    total_promoted = filtered_df[promotions_col].sum()
    total_eligible = filtered_df[eligibles_col].sum()
    if total_eligible > 0:
        soldier_promoted_pct = (total_promoted / total_eligible) * 100
    else:
        soldier_promoted_pct = 0
    percentage_text = html.Div([
        html.H2(
            f"{soldier_promoted_pct:.1f}%",
            style={"textAlign": "center", "fontSize": "36px", "margin": "0", "color": "green"}
        ),
        html.P(
            f"Between {start_month} and {end_month}, {soldier_promoted_pct:.1f}% "
            f"of eligible {mos} soldiers were selected for promotion.",
            style={"textAlign": "center", "fontSize": "20px", "margin": "0","color": "black"}
        )
    ])

    return (
        fig1, fig5, fig6, fig2, fig3, fig4, probability_text,
        f"{y_pred}", str(ci_lower), str(ci_upper),
        percentage_text
    )


@app.callback(
    Output("sidebar-details", "children"),
    [
        Input("load-button", "n_clicks"),
        Input("date-range-start", "value"),
        Input("date-range-end", "value"),
        Input("component-dropdown", "value"),
        Input("rank-dropdown", "value"),
        Input("mos-dropdown", "value")
    ]
)
def update_sidebar(load_clicks, start_month, end_month, component, rank, mos):
    if not load_clicks or not start_month or not end_month:
        return html.P("No Data Available")
    if not rank:
        return html.P("No Rank Selected")
    filtered_df = df.copy()
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], format="%Y-%b", errors="coerce")
    start_month = pd.to_datetime(start_month, format="%b-%Y", errors="coerce")
    end_month = pd.to_datetime(end_month, format="%b-%Y", errors="coerce")
    filtered_df = filtered_df[(filtered_df["Date"] >= start_month) & (filtered_df["Date"] <= end_month)]
    if component:
        filtered_df = filtered_df[filtered_df["Component"].str.upper() == component.upper()]
    if mos:
        filtered_df = filtered_df[filtered_df["MOS"] == mos]
    if filtered_df.empty:
        return html.P("No Data Available")
    eligibles_column = "Eligibles_SGT" if rank == "SGT" else "Eligibles_SSG"
    promotions_column = "Promotions_SGT" if rank == "SGT" else "Promotions_SSG"
    table_header = html.Thead(html.Tr([
        html.Th("Date",
                style={"position": "sticky", "top": 0, "backgroundColor": "#f8f8f8", "zIndex": 2, "padding": "0px",
                       "margin": "0", "textAlign": "left"}),
        html.Th("Eligible",
                style={"position": "sticky", "top": 0, "backgroundColor": "#f8f8f8", "zIndex": 2, "padding": "0px",
                       "margin": "0", "textAlign": "center"}),
        html.Th("Promotions",
                style={"position": "sticky", "top": 0, "backgroundColor": "#f8f8f8", "zIndex": 2, "padding": "0px",
                       "margin": "0", "textAlign": "center"})
    ]))
    table_rows = html.Tbody([
        html.Tr([
            html.Td(row["Date"].strftime("%b-%Y")),
            html.Td(int(row[eligibles_column]) if pd.notna(row[eligibles_column]) else "N/A"),
            html.Td(int(row[promotions_column]) if pd.notna(row[promotions_column]) else "N/A")
        ]) for _, row in filtered_df.sort_values(by="Date").iterrows()
    ])
    return html.Table([table_header, table_rows],
                      style={"width": "100%", "borderCollapse": "collapse", "margin": "0", "padding": "0"})


@app.callback(
    [
        Output("page-content", "style"),
        Output("label-load-data-from", "style"),
        Output("label-load-data-to", "style"),
        Output("label-component", "style"),
        Output("label-rank", "style"),
        Output("label-mos-code", "style"),
        Output("label-user-prompts", "style"),
        Output("label-details-title", "style"),
        Output("dark-mode-switch", "label_style")
    ],
    Input("dark-mode-switch", "value")
)
def update_dark_mode(is_dark_mode):
    page_style = {
        "minHeight": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "backgroundColor": "#2F2F2F" if is_dark_mode else "white"
    }
    base_label_style = {
        "marginBottom": "2px",
        "fontWeight": "bold",
        "textAlign": "center",
        "color": "white" if is_dark_mode else "black"
    }
    switch_label_style = {
        "color": "white" if is_dark_mode else "black",
        "marginLeft": "10px",
        "fontSize": "14px"
    }
    return (
        page_style,
        base_label_style,
        base_label_style,
        base_label_style,
        base_label_style,
        base_label_style,
        base_label_style,
        base_label_style,
        switch_label_style
    )


def update_page_background(dark_mode_value):
    base_style = {
        "minHeight": "100vh",
        "display": "flex",
        "flexDirection": "column",
    }
    if "dark" in dark_mode_value:
        base_style["backgroundColor"] = "#2F2F2F"
    else:
        base_style["backgroundColor"] = "white"
    return base_style


if __name__ == "__main__":
    app.run(debug=True)
