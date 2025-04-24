def get_player_metrics(metric_grouping_information, row):
    '''
    Function to get metric information specific to the player based on the position they play in.

    Returns the following:
    position_group: the general grouping for position, e.g. Winger for LW and RW
    general_metrics: key metrics chosen by Metin for each position group
    lincoln_metrics: key metrics chosen by Lincoln for each position group
    comparable_positions: list of positions that are included in the player's position group
    '''
    # Find player position group
    position_group = metric_grouping_information.loc[
    (metric_grouping_information['positions_statsbomb'].apply(lambda x: row['primary_position'] in x)) &
    (metric_grouping_information['position_groups'] != 'all'),
    'position_groups'
    ].iloc[0]

    # Find corresponding statsbomb metrics
    general_metrics = metric_grouping_information.loc[
        metric_grouping_information['position_groups'] == position_group,
        'statsbomb_metrics'
    ].iloc[0]

    # # Find corresponding lincoln specific metrics
    # lincoln_metrics = metric_grouping_information.loc[
    #     metric_grouping_information['position_groups'] == position_group,
    #     'lincoln_metrics'
    # ].iloc[0]

    # Find comparable statsbomb positions in the player's position group
    comparable_positions = metric_grouping_information.loc[
        metric_grouping_information['position_groups'] == position_group,
        'positions_statsbomb'
    ].iloc[0]

    # return position_group, general_metrics, lincoln_metrics, comparable_positions
    return position_group, general_metrics, comparable_positions