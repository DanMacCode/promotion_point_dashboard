# dashboard_scripts/calculate_promotion_percentage.py

def calculate_promotion_percentage(filtered_df, promotions_col, eligibles_col):
    """
    Calculate the overall percentage of promoted soldiers given a filtered DataFrame.
    Returns a float (percentage), or 0 if there are no eligible soldiers.
    """
    total_promoted = filtered_df[promotions_col].sum()
    total_eligible = filtered_df[eligibles_col].sum()
    if total_eligible > 0:
        return (total_promoted / total_eligible) * 100
    return 0
