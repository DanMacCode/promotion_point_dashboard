import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_next_promotion_points(df, promotion_column):
    """Predict the next month's promotion cutoff points using a simple linear regression."""

    df = df.dropna(subset=[promotion_column])  # Drop rows with missing promotion points
    df = df.sort_values(by="Date")  # Ensure chronological order

    if len(df) < 3:  # Not enough data to make a meaningful prediction
        return None

    # Convert dates into numerical values for regression
    df["Date_Ordinal"] = df["Date"].map(pd.Timestamp.toordinal)

    # Train simple linear regression model
    X = df["Date_Ordinal"].values.reshape(-1, 1)
    y = df[promotion_column].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict the next month's promotion points
    next_month_date = df["Date"].max() + pd.DateOffset(months=1)
    next_month_ordinal = np.array([[next_month_date.toordinal()]])

    predicted_points = model.predict(next_month_ordinal)[0]

    return max(0, round(predicted_points))  # Ensure it doesn't go below 0
