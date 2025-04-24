def remove_duplicate_rows(df):
    # Function to remove duplicate rows after concatenating legacy ccfc and subscribed lcfc statsbomb data
    # Sort by player_id, season_id, competition_id, team_name, and minutes.
    # Keep the row with the highest minutes when duplicates exist for the same player, season, competition, and team.
    df = df.sort_values(by=['player_id', 'season_id', 'competition_id', 'team_name', 'minutes'],
                        ascending=[True, True, True, True, False])
    df = df.drop_duplicates(subset=['player_id', 'season_id', 'competition_id', 'team_name'], keep='first')
    return df