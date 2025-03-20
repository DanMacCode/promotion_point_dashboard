import numpy as np
import pandas as pd


def compute_bayesian_promotion_probability(filtered_df, promotion_column, user_points):
    """
    Computes the Bayesian Adjusted Promotion Probability.
    This considers historical volatility and directional movement in promotion points.
    """
    if user_points is None or filtered_df.empty:
        return 0  # Default to 0 if no input or data

    # ✅ Count past months where user would have been promoted
    promoted_months = sum(1 for score in filtered_df[promotion_column] if score <= user_points)
    total_months = len(filtered_df)

    # ✅ Compute baseline historical probability
    historical_probability = (promoted_months / total_months) if total_months > 0 else 0

    # ✅ Identify high-volatility months (big jumps in promotion points)
    filtered_df["Point_Change"] = filtered_df[promotion_column].diff().abs()
    volatility_threshold = filtered_df["Point_Change"].quantile(0.75)  # Top 25% of changes
    high_volatility_months = filtered_df[filtered_df["Point_Change"] > volatility_threshold]

    # ✅ Compute probability of user being affected by a volatility-driven spike
    recent_trend_factor = high_volatility_months.shape[0] / total_months if total_months > 0 else 0
    adjusted_probability = max(0, 1 - (recent_trend_factor)) * historical_probability

    return adjusted_probability * 100  # Convert to percentage
