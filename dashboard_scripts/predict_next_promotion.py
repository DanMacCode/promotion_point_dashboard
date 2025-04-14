import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_next_promotion_points(df, promotion_column):
    """Predict next month's promotion cutoff and provide a 95% confidence interval."""

    df = df.dropna(subset=[promotion_column])
    df = df.sort_values(by="Date")

    if len(df) < 3:
        return None, None  # Return a tuple for consistency

    df["Date_Ordinal"] = df["Date"].map(pd.Timestamp.toordinal)

    X = df["Date_Ordinal"].values.reshape(-1, 1)
    y = df[promotion_column].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict next month's ordinal date
    next_month_date = df["Date"].max() + pd.DateOffset(months=1)
    next_month_ordinal = next_month_date.toordinal()
    X_pred = np.array([[next_month_ordinal]])
    y_pred = model.predict(X_pred)[0]

    # Compute residual standard error
    y_fit = model.predict(X)
    residuals = y - y_fit
    stderr = np.sqrt(np.sum(residuals ** 2) / (len(y) - 2))

    # Compute standard error of the prediction
    mean_x = np.mean(X)
    SE_pred = stderr * np.sqrt(
        1 + (1 / len(X)) + ((next_month_ordinal - mean_x) ** 2 / np.sum((X - mean_x) ** 2))
    )

    # 95% confidence interval
    ci_lower = max(24, round(y_pred - 1.96 * SE_pred))
    ci_upper = min(798, round(y_pred + 1.96 * SE_pred))

    return max(0, round(y_pred)), (ci_lower, ci_upper)
