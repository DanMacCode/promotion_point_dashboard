import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_next_promotion_points(filtered_df, promotion_column):
    """
    Predicts next month's promotion points using linear regression.

    Parameters:
    - filtered_df (pd.DataFrame): The filtered dataset containing historical promotion points.
    - promotion_column (str): The column containing past cutoff points.

    Returns:
    - float: Predicted cutoff points for the next month.
    """
    # Ensure data is sorted by date
    filtered_df = filtered_df.sort_values(by="Date")

    # Drop rows with missing values in the promotion column
    filtered_df = filtered_df.dropna(subset=[promotion_column])

    if len(filtered_df) < 3:  # Need at least 3 data points for meaningful regression
        return None

    # Convert dates to numerical format (e.g., 1, 2, 3, ...)
    filtered_df["Numeric_Date"] = np.arange(len(filtered_df))

    # Prepare data for regression
    X = filtered_df[["Numeric_Date"]]
    y = filtered_df[promotion_column]

    # Train the model
    model = LinearRegression()
    model.fit(X, y)

    # Predict the next month's promotion points
    next_month_numeric = np.array([[filtered_df["Numeric_Date"].max() + 1]])
    predicted_points = model.predict(next_month_numeric)[0]

    return round(predicted_points, 2)  # Return rounded prediction
