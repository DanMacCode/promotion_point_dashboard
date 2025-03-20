import plotly.graph_objects as go
import pandas as pd

def create_change_graph(filtered_df, promotion_column):
    """
    Creates a bar chart showing historical point fluctuation.

    Args:
        filtered_df (pd.DataFrame): Filtered dataset containing promotion data.
        promotion_column (str): Column name for promotion points.

    Returns:
        go.Figure: Plotly bar chart showing changes in promotion points.
    """

    # Ensure the DataFrame is sorted by Date
    filtered_df = filtered_df.sort_values(by="Date")

    # Compute month-to-month change in promotion points
    filtered_df["Point_Change"] = filtered_df[promotion_column].diff()

    # Create figure
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=filtered_df["Date"],
        y=filtered_df["Point_Change"],
        marker_color=[
            "green" if val > 0 else "red" for val in filtered_df["Point_Change"]
        ],
        name="Points Change"
    ))

    # Update layout
    fig.update_layout(
        title="Historical Point Fluctuation",
        xaxis_title="Date",
        yaxis_title="Points Change",
        showlegend=False
    )

    return fig
