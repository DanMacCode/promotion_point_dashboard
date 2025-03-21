import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import numpy as np
import requests
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dashboard_scripts.update_change_graph import create_change_graph
from dashboard_scripts.bayesian_adjustment import compute_bayesian_promotion_probability
from dashboard_scripts.predict_next_promotion import predict_next_promotion_points







# ✅ Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootswatch@5.2.3/dist/cosmo/bootstrap.min.css"])


server = app.server

# ✅ Public direct raw GitHub link
csv_url = "https://raw.githubusercontent.com/DanMacCode/promotion_point_dashboard/main/data/master/master_promotion_data.csv"

try:
    df = pd.read_csv(csv_url)
    print("✅ Data successfully loaded.")
    print(df.head())  # Print sample data for verification
except Exception as e:
    print(f"🚨 Error loading CSV: {e}")
    df = pd.DataFrame()  # Load empty DataFrame if there's an issue

# ✅ Ensure proper sorting and formatting
df["Date"] = pd.to_datetime(df["Date"], format="%Y-%b", errors="coerce", dayfirst=False)
print(df[["Date"]].dropna().head())  # Ensure dates are parsed correctly
sorted_dates = df["Date"].dropna().sort_values().dt.strftime("%b-%Y").unique().tolist()

app.layout = html.Div([
    # ✅ Dashboard Title
    html.H1("Army Promotion Point Dashboard", style={"textAlign": "center", "color": "gold"}, className="text-center fw-bold mt-3 mb-3")
,

    # ✅ Dropdowns & Controls
    html.Div([
        dcc.Dropdown(id="date-range-start",
                     options=[{"label": d, "value": d} for d in sorted_dates],
                     placeholder="Select Start Month",
                     style={"width": "200px", "fontSize": "16px", "textAlign": "center"}),

        dcc.Dropdown(id="date-range-end",
                     options=[{"label": d, "value": d} for d in sorted_dates],
                     placeholder="Select End Month",
                     style={"width": "200px", "fontSize": "16px", "textAlign": "center"}),

        dcc.Dropdown(id="component-dropdown",
                     options=[{"label": "Active", "value": "Active"}, {"label": "Reserve", "value": "Reserve"}],
                     placeholder="Select Component",
                     style={"width": "200px", "fontSize": "16px", "textAlign": "center"}),

        dcc.Dropdown(id="rank-dropdown",
                     options=[{"label": "SGT", "value": "SGT"}, {"label": "SSG", "value": "SSG"}],
                     placeholder="Select Rank",
                     style={"width": "150px", "fontSize": "16px", "textAlign": "center"}),

        dcc.Dropdown(id="mos-dropdown",
                     options=[{"label": mos, "value": mos} for mos in df["MOS"].unique()],
                     placeholder="Select MOS",
                     style={"width": "150px", "fontSize": "16px", "textAlign": "center"}),

        html.Button("Load Data", id="load-button",
                    style={"backgroundColor": "green", "color": "white", "padding": "10px", "fontSize": "14px"}),

        html.Button("Clear Data", id="clear-button",
                    style={"backgroundColor": "gray", "color": "white", "padding": "10px", "fontSize": "14px"})
    ], style={"display": "flex", "justifyContent": "space-around", "gap": "10px", "padding": "10px"}),

    # ✅ Probability Statement
    html.Div([
        html.P("See where you measure up. Input your promotion points:"),
        dcc.Input(id='user-points', type='number', min=0, max=800, step=1, style={'marginBottom': '10px'}),
        html.Div(id='probability-text', style={'fontSize': '18px', 'marginTop': '10px'})
    ], style={"textAlign": "center", "marginBottom": "20px"}),



    # ✅ Promotion Points Over Time Graph (Below Probability)
    html.Div([
        html.Div([
            dcc.Graph(id="promotion-graph", style={"position": "relative"}),

            # ✅ Floating Checkboxes (Bottom Right)
            html.Div([
                dcc.Checklist(
                    id="toggle-probability",
                    options=[{"label": "Your Points", "value": "show"}],
                    value=["show"],
                    style={"fontSize": "10px", "lineHeight": "12px"}
                ),
                dcc.Checklist(
                    id="trendline-checkbox",
                    options=[{"label": "Show Trend", "value": "trend"}],
                    value=[],
                    style={"fontSize": "10px", "lineHeight": "12px", "marginBottom": "5px"}
                ),
                dcc.Checklist(
                    id="volatility-checkbox",
                    options=[{"label": "Show Volatility", "value": "volatility"}],
                    value=[],
                    style={"fontSize": "10px", "lineHeight": "12px"}
                )

            ], style={
                "position": "absolute",
                "bottom": "0px",
                "right": "05px",
                "backgroundColor": "rgba(255,255,255,0.8)",
                "padding": "5px",
                "borderRadius": "5px",
                "boxShadow": "0px 0px 5px rgba(0,0,0,0.3)"
            })

        ], style={"position": "relative","border": "1px solid #ddd",
                "borderRadius": "10px",
                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                "padding": "15px",
                "backgroundColor": "#ffffff",
                "marginBottom": "20px"}),

    html.Div(id="prediction-text"),
    # ✅ Promotion Probability (Top Row)
        html.Div([
            html.Div([
                dcc.Graph(id="historical-probability-gauge", style={"width": "100%"})
            ], style={
                "border": "1px solid #ddd",
                "borderRadius": "10px",
                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                "padding": "15px",
                "backgroundColor": "#ffffff",
                "marginBottom": "20px",
                "marginTop": "20px"
            }),

            html.Div([
                dcc.Graph(id="predicted-probability-gauge", style={"width": "100%"})
            ], style={
                "border": "1px solid #ddd",
                "borderRadius": "10px",
                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                "padding": "15px",
                "backgroundColor": "#ffffff",
                "marginBottom": "20px",
                "marginTop": "20px"
            })
        ], style={"display": "flex", "justifyContent": "center", "gap": "20px"})
        ,

        # ✅ Historical Point Fluctuation (Middle Row)
    dcc.Graph(id="change-graph", style={"width": "100%","border": "1px solid #ddd",
                "borderRadius": "10px",
                "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",
                "padding": "15px",
                "backgroundColor": "#ffffff",
                "marginBottom": "20px"})

    ], style={"marginLeft": "2in", "marginRight": "2in", "marginBottom": "20px",
                }),

        # ✅ Competitiveness + Historical Soldier Selection + Details (Bottom Row)
        html.Div([
            html.Div([
                dcc.Graph(id="competitiveness-graph"),
                html.P(
                    "This chart shows the ratio of promotions to eligible soldiers. "
                    "A higher score indicates a less competitive MOS with more promotions relative to those eligible.",
                    style={"textAlign": "center", "fontSize": "14px", "marginTop": "5px"}
                )
            ], style={"width": "35%", "display": "inline-block",
                        "border": "1px solid #ddd",  # Light gray border
                        "borderRadius": "10px",  # Rounded edges
                        "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",  # Soft shadow
                        "padding": "15px",  # Padding inside the box
                        "backgroundColor": "#ffffff",  # White background
                        "marginBottom": "20px"}),  # 🔹 Competitiveness Score (LEFT)

        html.Div([
            dcc.Graph(id="streamgraph")
        ], style={"width": "40%", "display": "inline-block", "verticalAlign": "top",
                    "border": "1px solid #ddd",  # Light gray border
                    "borderRadius": "10px",  # Rounded edges
                    "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",  # Soft shadow
                    "padding": "15px",  # Padding inside the box
                    "backgroundColor": "#ffffff",  # White background
                    "marginBottom": "20px"}),  # 🔹 Historical Soldier Selection (CENTER)

        html.Div([
            html.H4("Details", style={"textAlign": "center"}),
            html.Div([
                html.Div(id="sidebar-details", style={
                    "maxHeight": "400px",
                    "overflowY": "auto",
                    "width": "100%",
                    "border": "1px solid #ddd",
                    "padding": "0px",
                    "borderRadius": "5px",
                    "backgroundColor": "#f8f8f8",
                    "marginTop": "0px"
                })
            ], style={
                "width": "100%",
                "display": "inline-block",
                "verticalAlign": "top",
                "border": "1px solid #ddd",  # Light gray border
                    "borderRadius": "10px",  # Rounded edges
                    "boxShadow": "0px 4px 8px rgba(0,0,0,0.1)",  # Soft shadow
                    "padding": "15px",  # Padding inside the box
                    "backgroundColor": "#ffffff",  # White background
                    "marginBottom": "20px"
            })

        ])  # 🔹 Details Box (RIGHT)
    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "20px", "marginLeft": "2in", "marginRight": "2in"}),

    html.Div(style={"flex": "1"}),

    html.Footer(               # <- Put this at the end
            children=[
                html.Hr(),
                html.Div([
                    html.P("This Page Is NOT DoD Affiliated. I am just an NCO who got tired of remaking excels to speculate about points.", className="mb-0"),
                    html.P("Contact: PromotionPointDashboard@gmail.com", className="mb-0"),
                    html.P("© 2025 Army Promotion Point Dashboard", className="mb-0"),
                ], className="text-center"),
                html.Div(style={"height": "40px"})
            ],
            style={
                "backgroundColor": "#013220",
                "color": "yellow",
                "padding": "0px",
                "width": "100%",  # Ensure full width
                "position": "absolute",
                "position": "relative",  # Keeps it below content naturally
                "marginTop": "auto",  # Stick to bottom
                "bottom": "0",  # Anchor to bottom
                "left": "0"  # Ensure it starts from the left edge
            }
        )

], style={"minHeight": "100vh", "display": "flex", "flexDirection": "column"})

# ✅ Now define your callbacks
@app.callback(
    [
        Output("promotion-graph", "figure"),
        Output("historical-probability-gauge", "figure"),
        Output("predicted-probability-gauge", "figure"),
        Output("change-graph", "figure"),
        Output("competitiveness-graph", "figure"),
        Output("streamgraph", "figure"),
        Output("probability-text", "children"),
        Output("prediction-text", "children")
    ],
    [
        Input("load-button", "n_clicks"),
        Input("clear-button", "n_clicks"),
        Input("date-range-start", "value"),
        Input("date-range-end", "value"),
        Input("component-dropdown", "value"),
        Input("rank-dropdown", "value"),
        Input("mos-dropdown", "value"),
        Input("trendline-checkbox", "value"),
        Input("volatility-checkbox", "value"),
        Input("user-points", "value"),
        Input("toggle-probability", "value")
    ]
)
def update_graphs(load_clicks, clear_clicks, start_month, end_month, component, rank, mos, trendline, volatility,
                  user_points, toggle_probability):
    ctx = dash.callback_context
    if ctx.triggered_id == "clear-button":
        return px.line(title="No Data Available"), px.line(title="No Data Available"), px.bar(
            title="No Data Available"), ""

    if not load_clicks or not start_month or not end_month:
        return px.line(title="No Data Available"), px.line(title="No Data Available"), px.bar(
            title="No Data Available"), ""

    # ✅ Filter Data and Sort Chronologically
    filtered_df = df.copy()
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], format="%Y-%b", errors="coerce")

    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(start_month, format="%b-%Y")) &
        (filtered_df["Date"] <= pd.to_datetime(end_month, format="%b-%Y"))
        ].sort_values(by="Date")  # 🔹 Ensuring chronological order

    if component:
        filtered_df = filtered_df[filtered_df["Component"].str.upper() == component.upper()]
    if mos:
        filtered_df = filtered_df[filtered_df["MOS"] == mos]

    if filtered_df.empty:
        return px.line(title="No Data Available"), px.line(title="No Data Available"), px.line(
            title="No Data Available"), px.line(title="No Data Available")

    # ✅ Define column names based on rank
    promotion_column = "Cutoff_SGT" if rank == "SGT" else "Cutoff_SSG"
    promotions_col = "Promotions_SGT" if rank == "SGT" else "Promotions_SSG"
    eligibles_col = "Eligibles_SGT" if rank == "SGT" else "Eligibles_SSG"

    # ✅ Compute Historical Promotion Probability
    if user_points is not None:
        promoted_months = sum(1 for score in filtered_df[promotion_column] if score <= user_points)
    else:
        promoted_months = 0

    total_months = len(filtered_df)
    historical_probability = (promoted_months / total_months) * 100 if total_months > 0 else 0

    # ✅ Compute Bayesian Adjusted Probability using Historical Data
    if user_points is not None and total_months > 0:
        failure_months = sum(1 for score in filtered_df[promotion_column] if user_points < score)
        adjusted_probability = (1 - (failure_months / total_months)) * 100 if total_months > 0 else 0
    else:
        adjusted_probability = 0  # Default to 0 if no user input

    adjusted_probability = compute_bayesian_promotion_probability(filtered_df, promotion_column, user_points)
    # ✅ Predict Next Month's Promotion Points
    predicted_promotion_points = predict_next_promotion_points(filtered_df, promotion_column)

    # ✅ Define the Prediction Text for Next Month's Promotion Points
    if predicted_promotion_points is not None:
        prediction_text = html.Div([
            html.H4("Next Month's Predicted Cutoff", style={"textAlign": "center"}),
            html.P(f"Predicted Promotion Points: {predicted_promotion_points}",
                   style={"fontSize": "16px", "textAlign": "center", "color": "blue"})
        ], style={
            "border": "1px solid #ddd",
            "padding": "10px",
            "borderRadius": "5px",
            "backgroundColor": "#f8f8f8",
            "width": "300px",
            "margin": "auto",
            "marginTop": "10px",
            "marginBottom": "10px"
        })
    else:
        prediction_text = html.P("Not enough data for prediction.", style={
            "textAlign": "center", "fontSize": "16px", "color": "gray"
        })

    # ✅ Create Promotion Graph
    fig1 = px.line(filtered_df, x="Date", y=promotion_column, title="Promotion Points Over Time", color="MOS",
                   markers=True)

    # ✅ Add Trend Line if selected
    if "trend" in trendline:
        x_vals = np.arange(len(filtered_df))
        y_vals = filtered_df[promotion_column].dropna()
        if len(y_vals) > 1:
            trend_poly = np.polyfit(x_vals, y_vals, 1)
            trend_line = np.poly1d(trend_poly)(x_vals)
            fig1.add_scatter(
                x=filtered_df["Date"],
                y=trend_line,
                mode="lines",
                line=dict(color="gold", dash="solid"),
                name="Trend Line"
            )

    # ✅ Add Volatility Overlay if selected
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

    # ✅ LIVE UPDATE: Add User's Promotion Points as a Horizontal Line
    if "show" in toggle_probability and user_points is not None:
        fig1.add_hline(
            y=user_points, line_dash="dash", line_color="red",
            annotation_text=f"Your Points: {user_points}",
            annotation_position="top right",
            name="Your Points"
        )

    # ✅ Compute Change Over Time and Competitiveness Score
    fig2 = create_change_graph(filtered_df, promotion_column)

    # ✅ Competitiveness Score
    filtered_df["Competitiveness"] = filtered_df[promotions_col] / filtered_df[eligibles_col]
    fig3 = px.bar(filtered_df, x="Date", y="Competitiveness", title="Competitiveness Score")

    # ✅ Compute Probability Text Output
    probability_text = html.Span([
        f'Given the date range of {start_month} to {end_month}, with your promotion points at {user_points}, ',
        f'you would have promoted {promoted_months} out of {total_months} months. ',
        f'If the past is an indicator, you would have a {historical_probability:.1f}% chance of promoting next month.',
        html.Br(),
        html.Span("However, the Army’s promotion point system is more needs-based than statistically driven.",
                  style={"color": "gray", "fontSize": "10px"})
    ], style={
        'color': 'red' if historical_probability < 50 else 'orange' if historical_probability < 80 else 'green'}) if user_points is not None else ""

    # ✅ Compute Data for Streamgraph
    filtered_df["Not_Promoted"] = (filtered_df[eligibles_col] - filtered_df[promotions_col]).fillna(0)

    # ✅ Ensure Sorting for Streamgraph
    filtered_df = filtered_df.sort_values(by="Date")

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df[promotions_col],
        fill='tonexty',
        mode='none',
        name="Promoted",
        fillcolor="gold",
        opacity=0.8
    ))

    fig4.add_trace(go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df["Not_Promoted"],
        fill='tonexty',
        mode='none',
        name="Eligible not Promoted",
        fillcolor="green",
        opacity=0.6
    ))

    fig4.update_layout(
        title="Historical Soldier Selection",
        xaxis_title="Date",
        yaxis_title="# of Soldiers",
        showlegend=True
    )

    # ✅ Create Probability Gauges
    fig5 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=historical_probability,
        title={"text": "Historical Promotion Probability"},
        gauge={"axis": {"range": [0, 100]},
               "bar": {
                   "color": "green" if historical_probability > 80 else "orange" if historical_probability > 50 else "red"}}
    ))

    fig6 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=adjusted_probability,
        title={"text": "Bayesian Adjusted Promotion Probability"},
        gauge={"axis": {"range": [0, 100]},
               "bar": {
                   "color": "green" if adjusted_probability > 80 else "orange" if adjusted_probability > 50 else "red"}}
    ))
    # ✅ Define the Prediction Text for Next Month's Promotion Points
    # ✅ Define the Prediction Text for Next Month's Promotion Points
    if predicted_promotion_points is not None:
        prediction_text = html.Div([
            html.H4("Next Month's Predicted Cutoff", style={"textAlign": "center"}),
            html.P(f"Predicted Promotion Points: {predicted_promotion_points}",
                   style={"fontSize": "16px", "textAlign": "center", "color": "blue"})
        ], style={
            "border": "1px solid #ddd",
            "padding": "10px",
            "borderRadius": "5px",
            "backgroundColor": "#f8f8f8",
            "width": "300px",
            "margin": "auto",
            "marginTop": "10px"
        })
    else:
        prediction_text = html.P("Not enough data for prediction.", style={
            "textAlign": "center", "fontSize": "16px", "color": "gray"
        })

    return fig1, fig5, fig6, fig2, fig3, fig4, probability_text, prediction_text




@app.callback(
    Output("sidebar-details", "children"),
    [
        Input("load-button", "n_clicks"),
        Input("date-range-start", "value"),
        Input("date-range-end", "value"),
        Input("component-dropdown", "value"),
        Input("rank-dropdown", "value"),
        Input("mos-dropdown", "value"),
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

    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_month) & (filtered_df["Date"] <= end_month)
    ]

    if component:
        filtered_df = filtered_df[filtered_df["Component"].str.upper() == component.upper()]

    if mos:
        filtered_df = filtered_df[filtered_df["MOS"] == mos]

    if filtered_df.empty:
        return html.P("No Data Available")

    eligibles_column = "Eligibles_SGT" if rank == "SGT" else "Eligibles_SSG"
    promotions_column = "Promotions_SGT" if rank == "SGT" else "Promotions_SSG"

    # Clearly defined table header
    table_header = html.Thead(html.Tr([
        html.Th("Date", style={
            "position": "sticky",
            "top": 0,
            "backgroundColor": "#f8f8f8",
            "zIndex": 2,
            "padding": "0px",
            "margin": "0",
            "textAlign": "left",

        }),
        html.Th("Eligible", style={
            "position": "sticky",
            "top": 0,
            "backgroundColor": "#f8f8f8",
            "zIndex": 2,
            "padding": "0px",
            "margin": "0",
            "textAlign": "center",

        }),
        html.Th("Promotions", style={
            "position": "sticky",
            "top": 0,
            "backgroundColor": "#f8f8f8",
            "zIndex": 2,
            "padding": "0px",
            "margin": "0",
            "textAlign": "center",

        }),
    ]))

    # Clearly defined table rows
    table_rows = html.Tbody([
        html.Tr([
            html.Td(row["Date"].strftime("%b-%Y")),
            html.Td(int(row[eligibles_column]) if pd.notna(row[eligibles_column]) else "N/A"),
            html.Td(int(row[promotions_column]) if pd.notna(row[promotions_column]) else "N/A")
        ]) for _, row in filtered_df.sort_values(by="Date").iterrows()
    ])

    # Return the complete table directly (without extra [])
    return html.Table([table_header, table_rows], style={"width": "100%", "borderCollapse": "collapse", "margin":"0", "padding": "0"})




    return html.Table(table_header + [html.Tbody(table_body)], style={"width": "100%"})




# ✅ Start Dash Server
if __name__ == "__main__":
    app.run(debug=True)

