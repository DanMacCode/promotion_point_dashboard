def update_graphs(load_clicks, clear_clicks, start_month, end_month, component, rank, mos, trendline, volatility,
                  user_points, toggle_probability):

    ctx = dash.callback_context
    if ctx.triggered_id == "clear-button":
        return px.line(title="No Data Available"), px.line(title="No Data Available"), px.bar(title="No Data Available"), ""

    if not load_clicks or not start_month or not end_month:
        return px.line(title="No Data Available"), px.line(title="No Data Available"), px.bar(title="No Data Available"), ""

    print("🔎 Initial Data Sample:")
    print(df.head(10))  # Show first 10 rows
    print("Unique Dates in Data:", df["Date"].unique())

    # ✅ Filter Data
    filtered_df = df.copy()
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], format="%Y-%b", errors="coerce")

    # ✅ Ensure filtering actually selects data
    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_month, format="%b-%Y")) &
        (df["Date"] <= pd.to_datetime(end_month, format="%b-%Y"))
    ]

    if component:
        filtered_df = filtered_df[filtered_df["Component"].str.upper() == component.upper()]
    if mos:
        filtered_df = filtered_df[filtered_df["MOS"] == mos]

    if filtered_df.empty:
        return px.line(title="No Data Available"), px.line(title="No Data Available"), px.line(
            title="No Data Available"), px.line(title="No Data Available")

    # ✅ Define proper column names based on rank
    promotion_column = "Cutoff_SGT" if rank == "SGT" else "Cutoff_SSG"
    promotions_col = "Promotions_SGT" if rank == "SGT" else "Promotions_SSG"
    eligibles_col = "Eligibles_SGT" if rank == "SGT" else "Eligibles_SSG"

    # ✅ Compute Historical Promotion Probability
    if user_points is not None:
        promoted_months = sum(1 for score in filtered_df[promotion_column] if score <= user_points)
    else:
        promoted_months = 0  # Default to zero if no input

    total_months = len(filtered_df)
    historical_probability = (promoted_months / total_months) * 100 if total_months > 0 else 0

    # ✅ Compute Bayesian Adjusted Probability using Standard Deviation
    std_dev = filtered_df[promotion_column].std()
    if std_dev > 0 and total_months > 0:
        adjusted_probability = (promoted_months / (total_months + std_dev)) * 100
    else:
        adjusted_probability = historical_probability  # Fallback if std_dev is undefined

    # ✅ Create Promotion Graph
    fig1 = px.line(filtered_df, x="Date", y=promotion_column, title="Promotion Points Over Time", color="MOS", markers=True)

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
        filtered_df["Rolling_StdErr"] = (
            filtered_df[promotion_column].rolling(window=3, min_periods=1).std()
        )
        upper_bound = (filtered_df[promotion_column] + filtered_df["Rolling_StdErr"]).clip(upper=798)
        lower_bound = filtered_df[promotion_column] - (0.5 * filtered_df["Rolling_StdErr"])

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

    filtered_df["Competitiveness"] = filtered_df[promotions_col] / filtered_df[eligibles_col]
    fig3 = px.bar(filtered_df, x="Date", y="Competitiveness", title="Competitiveness Score")

    # ✅ Compute Probability Text Output
    probability_text = ""
    if user_points is not None:
        probability = (promoted_months / total_months) * 100 if total_months > 0 else 0
        color = 'red' if probability < 50 else 'orange' if probability < 80 else 'green'

        probability_text = html.Span([
            f'Given the date range of {start_month} to {end_month}, with your promotion points at {user_points}, ',
            f'you would have promoted {promoted_months} out of {total_months} months. ',
            f'If the past is an indicator, you would have a {probability:.1f}% chance of promoting next month.',
            html.Br(),
            html.Span("However, the Army’s promotion point system is more needs-based than statistically driven.",
                      style={"color": "gray", "fontSize": "10px"})
        ], style={'color': color})

    # ✅ Compute Data for Streamgraph
    filtered_df["Not_Promoted"] = (filtered_df[eligibles_col] - filtered_df[promotions_col]).fillna(0)

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
               "bar": {"color": "green" if historical_probability > 80 else "orange" if historical_probability > 50 else "red"}}
    ))

    fig6 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=adjusted_probability,
        title={"text": "Bayesian Adjusted Promotion Probability"},
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": "green" if adjusted_probability > 80 else "orange" if adjusted_probability > 50 else "red"}}
    ))

    return fig1, fig5, fig6, fig2, fig3, fig4, probability_text
