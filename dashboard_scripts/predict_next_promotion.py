import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.stats import norm


def predict_next_promotion_points(df, promotion_column, ci_level=95):
    """
    Predict next month's promotion cutoff and return a confidence interval at the given level.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain a datetime column "Date" and the numeric column named promotion_column.
    promotion_column : str
        Name of the column holding historical cutoff scores.
    ci_level : int, optional (default=95)
        Confidence level in percent (e.g. 90, 95, 99).

    Returns
    -------
    predicted_cutoff : int
        Rounded prediction for next month's cutoff.
    (ci_lower, ci_upper) : tuple of ints
        Lower and upper bounds of the confidence interval, clamped to [24, 798].
    """

    # 1. Prepare data
    df = df.dropna(subset=[promotion_column]).sort_values(by="Date")
    if len(df) < 3:
        return None, None

    # 2. Convert dates to ordinal for regression
    df["Date_Ordinal"] = df["Date"].map(pd.Timestamp.toordinal)
    X = df["Date_Ordinal"].values.reshape(-1, 1)
    y = df[promotion_column].values

    # 3. Fit linear model
    model = LinearRegression().fit(X, y)

    # 4. Predict for next month
    next_month = df["Date"].max() + pd.DateOffset(months=1)
    next_ordinal = next_month.toordinal()
    y_pred = model.predict([[next_ordinal]])[0]

    # 5. Compute residual standard error
    y_fit = model.predict(X)
    residuals = y - y_fit
    stderr = np.sqrt(np.sum(residuals**2) / (len(y) - 2))

    # 6. Compute standard error of the prediction
    mean_x = np.mean(X)
    SE_pred = stderr * np.sqrt(
        1
        + 1/len(X)
        + ((next_ordinal - mean_x)**2 / np.sum((X - mean_x)**2))
    )

    # 7. Convert ci_level to z‑score
    alpha = 1 - ci_level/100
    z = norm.ppf(1 - alpha/2)

    # 8. Build confidence interval, clamp to valid range
    ci_lower = max(24, round(y_pred - z * SE_pred))
    ci_upper = min(798, round(y_pred + z * SE_pred))

    # 9. Return rounded prediction and bounds
    return max(0, round(y_pred)), (ci_lower, ci_upper)

