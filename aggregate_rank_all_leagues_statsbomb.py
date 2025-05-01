def calculate_percentiles_all(df, player_df, comparable_positions, general_metrics):
    from scipy.stats import rankdata

    # Define function to calculate percentiles (ranking): all leagues

    # Filter for primary_position in comparable_positions
    filtered_df = df[df['primary_position'].isin(comparable_positions)]

    general_df = filtered_df.copy()

    # Convert each metric to percentile in filtered_df using ther rankdata function
    for metric in general_metrics:

        # Create a mask for NaN values
        nan_mask = general_df[metric].isna()
        
        # Filter out NaN values for ranking
        non_nan_values = general_df.loc[~nan_mask, metric]
        
        # Rank the non-NaN values and convert to percentage
        ranked_percentages = rankdata(non_nan_values, method='average') / len(non_nan_values) * 100

        #assign rank to new column, with 50 given to those who didnt record anything 
        general_df[f'{metric}_percentile'] = 50.0
        general_df.loc[~nan_mask, f'{metric}_percentile'] = ranked_percentages.astype(np.float64)

    # Create average rank column (mean across percentile columns)
    general_df['average_rank'] = general_df[[f'{metric}_percentile' for metric in general_metrics]].mean(axis=1)

    # Convert the average rank to a percentile
    general_df['average_rank_percentile'] = rankdata(general_df['average_rank'], method='average') / len(general_df) * 100

    return general_df