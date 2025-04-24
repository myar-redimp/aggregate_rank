def preprocess_df(df):

  # pre-processing

  # Clean col names
  df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()

  # Remove 'player_season' from any column names that include it
  df.rename(columns=lambda x: x.replace('player_season_', ''), inplace=True)

  # # Filter df for rows with minutes > 900
  df = df[df['minutes'] > 700]

  # Strip and lowercase and add underscores where spaces exists between words for values in 'primary_position'
  df['primary_position'] = df['primary_position'].str.strip().str.lower().str.replace(' ', '_')

  # Strip and lowercase values in competition_name, also replace spaces with '_'
  df['competition_name'] = df['competition_name'].str.strip().str.lower().str.replace(' ', '_')

  # Team name-clean
  df['team_name'] = df['team_name'].str.strip().str.lower().str.replace(' ', '_')

  # Create goals - Xg fetaure
  df['np_goals_less_xg_90'] = df['npga_90']-df['assists_90']-df['np_xg_90']

  # Invert some metrics
  metrics_to_invert = ['dribbled_past_90','errors_90']

  # Invert metrics
  df[metrics_to_invert] = df[metrics_to_invert].apply(lambda x: -x)

  # calculate age from season_name.split('/')[0] - datetime(birth_date)
  df['age'] = df['season_name'].str.split('/').str[0].astype(int) - df['birth_date'].str.split('-').str[0].astype(int)

  return df
