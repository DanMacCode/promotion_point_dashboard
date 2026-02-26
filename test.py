# test.py
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from dashboard_scripts.update_change_graph import create_change_graph
from dashboard_scripts.bayesian_adjustment import compute_bayesian_promotion_probability
from dashboard_scripts.predict_next_promotion import predict_next_promotion_points
from dashboard_scripts.calculate_promotion_percentage import calculate_promotion_percentage
from dash import callback_context


# ── Initialize Dash with Pages turned on ───────────────────────
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,  # ✅ ADD THIS LINE
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootswatch@5.2.3/dist/cosmo/bootstrap.min.css",
        dbc.themes.BOOTSTRAP,
    ],
)

server = app.server
app.title = "Army Promotion Point Dashboard"

# ── Load your master CSV and Coming Soon text ──────────────────
csv_url = (
    "https://raw.githubusercontent.com/"
    "DanMacCode/promotion_point_dashboard/main/data/master/master_promotion_data.csv"
)
try:
    df = pd.read_csv(csv_url)
except Exception:
    df = pd.DataFrame()

df["Date"] = pd.to_datetime(df["Date"], format="%Y-%b", errors="coerce")
sorted_dates = df["Date"].dropna().sort_values().dt.strftime("%b-%Y").unique().tolist()

coming_soon_url = (
    "https://raw.githubusercontent.com/DanMacCode/"
    "promotion_point_dashboard/refs/heads/main/data/master/coming_soon.md"
)
try:
    coming_soon_text = requests.get(coming_soon_url).text
except Exception:
    coming_soon_text = "Failed to load upcoming changes."

# ── App layout with all your styling & nav ─────────────────────
app.layout = html.Div(
    [
        # ── HEADER ────────────────────────────────────────────────
        html.Div(
            [
                # Tooltip CSS
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
                    dangerously_allow_html=True,
                ),

                # Title
                html.H1(
                    "Army Promotion Point Dashboard",
                    style={"textAlign": "center", "color": "gold"},
                    className="text-center fw-bold mt-3 mb-3",
                ),
                dbc.Checklist(
                    id="dashboard-dark-mode-switch",
                    options=[{"label": "Dark Mode", "value": True}],
                    value=[],
                    switch=True,
                    inline=True,
                    style={
                        "marginLeft": "20px",  # same indent as your “Home” link
                        "marginBottom": "0"  # tighten up vertical spacing
                    },
                ),


                dbc.Checklist(
                    id="hidden-dark-mode-switch",
                    options=[{"label": "🌙 Dark Mode", "value": True}],
                    value=[],
                    switch=True,
                    inline=True,
                    style={"display": "none"}
                ),

                # Nav links (Home / About / Demo / Privacy)
                html.Div(
                    [
                        dcc.Link(
                            "Home",
                            href="/",
                            style={
                                "marginRight": "20px",
                                "fontSize": "18px",
                                "color": "green",
                                "textDecoration": "none",
                            },
                        ),
                        dcc.Link(
                            "About",
                            href="/about",
                            style={
                                "marginRight": "20px",
                                "fontSize": "18px",
                                "color": "green",
                                "textDecoration": "none",
                            },
                        ),
                        dcc.Link(
                            "Demo",
                            href="/demo",
                            style={
                                "marginRight": "20px",
                                "fontSize": "18px",
                                "color": "green",
                                "textDecoration": "none",
                            },
                        ),
                        dcc.Link(
                            "Privacy Policy",
                            href="/privacy_policy",
                            style={
                                "fontSize": "18px",
                                "color": "green",
                                "textDecoration": "none",
                            },
                        ),


                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "marginLeft": "20px",
                        "padding": "10px 0",
                    },

                ),
                html.Div(
                    style={
                        "height": "3px",
                        "backgroundColor": "gold",
                        "boxShadow": "0px 4px 4px rgba(0, 0, 0, 0.25)",
                        "marginTop": "0px",
                        "marginBottom": "20px",
                    }
                ),
            ],
            id="header-container",
            style={"backgroundColor": "white"},
        ),
        dcc.Store(id="dark-mode-store", storage_type="local", data=False),
        # inject the router + page container together, as a list of children
        html.Div(
            [
                dcc.Location(id="url", refresh=False),
                dash.page_container
            ],
            id="page-content",
            style={
                "minHeight": "100vh",
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "white"
            },
        ),

    ],
    id="dashboard-page-wrapper",
    className="",
    style={
        "minHeight": "100vh",
        "backgroundColor": "transparent",  # not "white"
        "flex": 1,
        "display": "flex",
        "flexDirection": "column",
    },
)

# ── CALLBACKS ──────────────────────────────────────────────────
# 1) Clear all inputs
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
        Output("toggle-probability", "value"),
    ],
    Input("clear-button", "n_clicks")
)
def clear_inputs(n_clicks):
    return None, None, None, None, None, None, [], [], ["show"]


# 2) Main callback: update all graphs, gauges, text, etc.
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
        Output("percentage-box", "children"),
    ],
    [
        Input("load-button", "n_clicks"),
        Input("ci-level-dropdown", "value"),
        Input("user-points", "value"),
        Input("trendline-checkbox", "value"),
        Input("volatility-checkbox", "value"),
        Input("toggle-probability", "value"),
    ],
    [
        State("date-range-start", "value"),
        State("date-range-end", "value"),
        State("component-dropdown", "value"),
        State("rank-dropdown", "value"),
        State("mos-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def update_graphs(
    n_clicks,
    ci_level,
    user_points,
    trendline,
    volatility,
    toggle_probability,
    start_month,
    end_month,
    component,
    rank,
    mos,
):
    # copied exactly from your working version...
    empty_fig = px.line(title="No Data Available")
    if not n_clicks or not start_month or not end_month or not rank or not mos or not component:
        return [empty_fig] * 6 + ["", "", "", ""]

    filtered_df = df.copy()
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], format="%Y-%b", errors="coerce")
    filtered_df = (
        filtered_df[
            (filtered_df["Date"] >= pd.to_datetime(start_month, format="%b-%Y"))
            & (filtered_df["Date"] <= pd.to_datetime(end_month, format="%b-%Y"))
        ]
        .sort_values(by="Date")
    )

    if component:
        filtered_df = filtered_df[filtered_df["Component"].str.upper() == component.upper()]
    if mos:
        filtered_df = filtered_df[filtered_df["MOS"] == mos]
    if filtered_df.empty:
        return [empty_fig] * 6 + ["", "", "", ""]

    promotion_column = "Cutoff_SGT" if rank == "SGT" else "Cutoff_SSG"
    promotions_col = "Promotions_SGT" if rank == "SGT" else "Promotions_SSG"
    eligibles_col = "Eligibles_SGT" if rank == "SGT" else "Eligibles_SSG"

    # Predicted cutoff
    y_pred, (ci_lower, ci_upper) = predict_next_promotion_points(
        filtered_df, promotion_column, ci_level=ci_level
    )
    # Historical probability
    historical_probability = (
        sum(score <= user_points for score in filtered_df[promotion_column]) / len(filtered_df) * 100
        if user_points is not None
        else 0
    )
    # Bayesian adjusted
    adjusted_probability = compute_bayesian_promotion_probability(
        filtered_df, promotion_column, user_points
    )

    # Promotion Points Over Time
    fig1 = px.line(
        filtered_df,
        x="Date",
        y=promotion_column,
        title="Promotion Points Over Time",
        markers=True,
        color_discrete_sequence=["green"],
        labels={promotion_column: "MOS Cutoffs"},
    )
    fig1.update_traces(name="MOS Cutoff Points", showlegend=True)

    if "trend" in trendline:
        x_vals = np.arange(len(filtered_df))
        y_vals = filtered_df[promotion_column].dropna()
        if len(y_vals) > 1:
            poly = np.polyfit(x_vals, y_vals, 1)
            line = np.poly1d(poly)(x_vals)
            fig1.add_scatter(x=filtered_df["Date"], y=line, mode="lines",
                             line=dict(color="gold", dash="solid"), name="Trend Line")

    if "volatility" in volatility:
        filtered_df["SE"] = filtered_df[promotion_column].rolling(3, min_periods=1).std()
        upper = (filtered_df[promotion_column] + filtered_df["SE"]).clip(upper=798)
        lower = (filtered_df[promotion_column] - 0.5 * filtered_df["SE"]).clip(lower=0)
        fig1.add_traces(
            go.Scatter(
                x=list(filtered_df["Date"]) + list(filtered_df["Date"])[::-1],
                y=list(upper) + list(lower)[::-1],
                fill="toself",
                fillcolor="rgba(0,128,0,0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Volatility Range",
                showlegend=True,
            )
        )

    if "show" in toggle_probability and user_points is not None:
        fig1.add_hline(
            y=user_points,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Your Points: {user_points}",
            annotation_position="top right",
        )

    # Change graph
    fig2 = create_change_graph(filtered_df, promotion_column)
    # Competitiveness
    filtered_df["Competitiveness"] = filtered_df[promotions_col] / filtered_df[eligibles_col]
    fig3 = px.bar(filtered_df, x="Date", y="Competitiveness", title="Competitiveness Score",
                  color_discrete_sequence=["green"])

    # Streamgraph
    filtered_df["Not_Promoted"] = (filtered_df[eligibles_col] - filtered_df[promotions_col]).clip(lower=0)
    fig4 = go.Figure()

    # First: Promoted
    fig4.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df[promotions_col],
            fill="tozeroy",
            mode="none",
            name="Promoted",
            fillcolor="gold",
            opacity=0.9,
            hovertemplate="<b>Date</b>: %{x}<br><b>Promoted</b>: %{y}<extra></extra>"
        )
    )

    # Second: Eligible (stacked *on top* of Promoted)
    fig4.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Not_Promoted"],
            fill="tonexty",
            mode="none",
            name="Eligible not Promoted",
            fillcolor="green",
            opacity=0.6,
            hovertemplate="<b>Date</b>: %{x}<br><b>Eligible (Not promoted)</b>: %{y}<extra></extra>"
        )
    )

    fig4.update_layout(
        title="Historical Soldier Selection",
        xaxis_title="Date",
        yaxis_title="# of Soldiers",
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.25,
            yanchor="top",
            traceorder="normal",
        ),
        margin=dict(t=60, r=20, l=40, b=95),
    )

    # Gauges
    fig5 = go.Figure(go.Indicator(
        mode="gauge+number", value=historical_probability,
        title={"text": "Historical Promotion Probability"},
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": "green" if historical_probability > 80 else "orange" if historical_probability > 50 else "red"}},
    ))
    fig5.update_layout(margin=dict(t=45, b=25, l=35, r=35))

    fig6 = go.Figure(go.Indicator(
        mode="gauge+number", value=adjusted_probability,
        title={"text": "Evidence Weighted Promotion Probability"},
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": "green" if adjusted_probability > 80 else "orange" if adjusted_probability > 50 else "red"}},
    ))
    fig6.update_layout(margin=dict(t=45, b=25, l=35, r=35))

    # Promotion percentage
    tot_prom = filtered_df[promotions_col].sum()
    tot_elig = filtered_df[eligibles_col].sum()
    pct = (tot_prom / tot_elig * 100) if tot_elig else 0
    percentage_text = html.Div([
        html.H2(f"{pct:.1f}%", style={"textAlign": "center", "fontSize": "36px", "color": "green"}),
        html.P(
            f"Between {start_month} and {end_month}, {pct:.1f}% of eligible {mos} soldiers were selected for promotion.",
            style={"textAlign": "center", "fontSize": "20px"},
        ),
    ])

    # Probability text
    prob_text = html.Span([
        f"Given the date range of {start_month} to {end_month}, with your promotion points at {user_points}, "
        f"you would have promoted {int(historical_probability/100*len(filtered_df))} out of {len(filtered_df)} months. "
        f"You would have a {historical_probability:.1f}% chance next month.",
        html.Br(),
    ], style={"color": "green" if historical_probability > 80 else "orange" if historical_probability > 50 else "red"})

    return fig1, fig5, fig6, fig2, fig3, fig4, prob_text, f"{y_pred}", str(ci_lower), str(ci_upper), percentage_text


# 3) Sidebar details (exactly your old code)
@app.callback(
    Output("sidebar-details", "children"),
    [
        Input("load-button", "n_clicks"),
        Input("date-range-start", "value"),
        Input("date-range-end", "value"),
        Input("component-dropdown", "value"),
        Input("rank-dropdown", "value"),
        Input("mos-dropdown", "value"),
    ],
)
def update_sidebar(load_clicks, start_month, end_month, component, rank, mos):
    if not load_clicks or not start_month or not end_month:
        return html.P("No Data Available")
    if not rank:
        return html.P("No Rank Selected")

    dff = df.copy()
    dff["Date"] = pd.to_datetime(dff["Date"], format="%Y-%b", errors="coerce")
    start = pd.to_datetime(start_month, format="%b-%Y", errors="coerce")
    end = pd.to_datetime(end_month, format="%b-%Y", errors="coerce")
    dff = dff[(dff["Date"] >= start) & (dff["Date"] <= end)]
    if component:
        dff = dff[dff["Component"].str.upper() == component.upper()]
    if mos:
        dff = dff[dff["MOS"] == mos]
    if dff.empty:
        return html.P("No Data Available")

    elig = "Eligibles_SGT" if rank == "SGT" else "Eligibles_SSG"
    prom = "Promotions_SGT" if rank == "SGT" else "Promotions_SSG"

    header = html.Thead(html.Tr([
        html.Th("Date", style={"position":"sticky","top":0,"backgroundColor":"#f8f8f8"}),
        html.Th("Eligible", style={"position":"sticky","top":0,"backgroundColor":"#f8f8f8"}),
        html.Th("Promoted", style={"position":"sticky","top":0,"backgroundColor":"#f8f8f8"}),
    ]))
    rows = []
    for _, row in dff.sort_values("Date").iterrows():
        rows.append(html.Tr([
            html.Td(row["Date"].strftime("%b-%Y")),
            html.Td(int(row[elig]) if pd.notna(row[elig]) else "N/A"),
            html.Td(int(row[prom]) if pd.notna(row[prom]) else "N/A"),
        ]))
    body = html.Tbody(rows)
    return html.Table([header, body], style={"width":"100%","borderCollapse":"collapse"})


# 4) Dark‑mode toggle (now includes header)
# in test.py
# only one dark‑mode callback in test.py

@app.callback(
    Output("dark-mode-store", "data"),
    Input("dashboard-dark-mode-switch", "value"),
    prevent_initial_call=True
)
def update_dark_mode_switch(dashboard_value):
    return True if dashboard_value else False


@app.callback(
    Output("hidden-dark-mode-switch", "value"),
    Output("dashboard-dark-mode-switch", "value"),
    Input("dashboard-dark-mode-switch", "value"),
    Input("hidden-dark-mode-switch", "value"),
    prevent_initial_call=True,
    allow_duplicate=True
)
def sync_switches(vis, hid):
    ctx_id = callback_context.triggered[0]["prop_id"].split('.')[0]
    if ctx_id == "dashboard-dark-mode-switch":
        # user toggled the visible switch
        return ([True] if vis else []), vis
    else:
        # user toggled (programmatically) the hidden switch
        return hid, (True if hid else False)



from dash import callback_context



# NEW CALLBACK: Update dark-mode-store from hidden switch
# Sync dashboard switch to hidden switch

from dash import Input, Output

from dash import Input, Output
@app.callback(
    [
        Output("header-container",     "style"),
        Output("page-content",         "style"),
        Output("dashboard-page-wrapper","className"),
        # your 7 labels:
        Output("label-load-data-from", "style"),
        Output("label-load-data-to",   "style"),
        Output("label-component",      "style"),
        Output("label-rank",           "style"),
        Output("label-mos-code",       "style"),
        Output("label-user-prompts",   "style"),
        Output("label-details-title",  "style"),
        # the switch labelStyle:
        Output("dashboard-dark-mode-switch", "labelStyle"),
        # all your dropdown/input controls:
        Output("date-range-start",    "style"),
        Output("date-range-end",      "style"),
        Output("component-dropdown",  "style"),
        Output("rank-dropdown",       "style"),
        Output("mos-dropdown",        "style"),
        Output("user-points",         "style"),
    ],
    Input("dark-mode-store", "data"),
    prevent_initial_call=True,
)
def apply_dark_mode(is_dark):
    DARK_BG = "#2E2E2E"
    LIGHT_BG = "white"

    # 1) Page chrome
    header_style = {"backgroundColor": DARK_BG if is_dark else LIGHT_BG}
    page_style   = {
        "backgroundColor": DARK_BG if is_dark else LIGHT_BG,
        "minHeight":       "100vh",
        "display":         "flex",
        "flexDirection":   "column",
    }
    wrapper_class = "dark-mode" if is_dark else ""

    # 2) Labels
    label_common = {
        "marginBottom": "2px",
        "fontWeight":   "bold",
        "textAlign":    "center",
        "color":        "white" if is_dark else "black",
    }
    labels = [label_common] * 7

    # 3) Switch label
    switch_label = {
        "marginLeft":   "20px",
        "marginBottom": "0",
        "fontSize":     "18px",
        "color":        "white" if is_dark else "black",
    }

    # 4) Always‐white dropdowns & inputs
    dropdown_style = {
        "backgroundColor": "white",
        "color": "black",
        "textAlign": "center",
        "width": "200px",
        "margin": "0 auto 10px",
    }
    small_dd = {**dropdown_style, "width": "150px"}
    user_pts_style = dropdown_style.copy()

    return (
        header_style,
        page_style,
        wrapper_class,
        *labels,
        switch_label,
        dropdown_style,  # date-range-start
        dropdown_style,  # date-range-end
        dropdown_style,  # component-dropdown
        small_dd,        # rank-dropdown
        small_dd,        # mos-dropdown
        user_pts_style   # user-points
    )


from dash import Input, Output

@app.callback(
    Output("dashboard-dark-mode-switch", "style"),
    Input("url", "pathname"),
    prevent_initial_call=False
)
def toggle_switch_visibility(pathname):
    return {"display": "inline-block"} if pathname in ("/", "") else {"display": "none"}


# near the bottom of test.py, replace your existing swap_all_backgrounds with:




if __name__ == "__main__":
    app.run(debug=True)
