def calculate_percentiles_all(df, player_df, comparable_positions, general_metrics):
    from scipy.stats import rankdata

    # Define function to calculate percentiles (ranking): all leagues

    # Filter for primary_position in comparable_positions
    filtered_df = df[df['primary_position'].isin(comparable_positions)]

    general_df = filtered_df.copy()

    # Convert each metric to percentile in filtered_df using ther rankdata function
    for metric in general_metrics:
      general_df[metric] = general_df[metric].fillna(0) # Fill missing values with nan
      general_df[f'{metric}_percentile'] = rankdata(general_df[metric], method='average') / len(general_df) * 100

    # Create average rank column (mean across percentile columns)
    general_df['average_rank'] = general_df[[f'{metric}_percentile' for metric in general_metrics]].mean(axis=1)

    # Convert the average rank to a percentile
    general_df['average_rank_percentile'] = rankdata(general_df['average_rank'], method='average') / len(general_df) * 100

    return general_df