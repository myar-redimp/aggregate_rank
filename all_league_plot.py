import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from aggregate_rank_league_one_statsbomb import calculate_percentiles_league_one
from get_position_specific_metrics_statsbomb import get_player_metrics
from scipy.stats import rankdata
import os


def plot_distribution_all_leagues(player_df, df, metric_grouping_information, save_path):
    """
    Generate a distribution plot of player rankings in all leagues, including annotations for specific players
    with an additional focus on players under 21.

    Parameters:
    player_df (DataFrame): DataFrame containing player data.
    df (DataFrame): DataFrame with general league data.
    metric_grouping_information (dict): Dictionary containing metrics for grouping players.

    Returns:
    None. This function saves and displays the plot.

    Note:
    - This function assumes 'get_player_metrics', 'calculate_percentiles_all' are defined elsewhere.
    - The plot shows histograms with vertical lines for specific player rankings.
    """

          # Ensure axes is always iterable by wrapping single axis in a list
    fig, axes = plt.subplots(len(player_df), 1, figsize=(8, 4.5 * len(player_df)))  # Increased figure size for annotations
    if not isinstance(axes, np.ndarray):  # If only one subplot, wrap in a list
        axes = [axes]

    norm = Normalize(vmin=0, vmax=100)
    cmap = plt.get_cmap('viridis')


    for i, (index, row) in enumerate(player_df.iterrows()):

        lines_all = []
        labels_all = []

    
        season_id = row['season_id']
        season_name = row['season_name']
        competition_id = row['competition_id']
        competition_name = row['competition_name']
        player_name = row['player_name']
        player_position = row['primary_position']
        player_age = row['age']  # Assuming 'age' is in player_df


        position_group, general_metrics, comparable_positions = get_player_metrics(metric_grouping_information, row)

        # Ensure both summer and other leagues are included
        if '/' not in season_name:
            other_season_name = season_name + '/' + str(int(season_name) + 1)

        else: 
            other_season_name = season_name.split('/')[0]

        
        season_df = df[(df['season_name'] == season_name) | (df['season_name'] == other_season_name)].copy()

        # Calculate rankings
        ranking_df = calculate_percentiles_league_one(season_df, comparable_positions, general_metrics)

        # General plot
        title_general = f"{position_group.replace('_', ' ').title()}s: All Leagues, {season_name} & {other_season_name}"
        # title_general = f"{row['competition_name'].replace('_', ' ').title()}, {row['season_name']}"

        # Sort ranking_df by 'average_rank' for accurate ranking
        sorted_ranking_df = ranking_df.sort_values('average_rank', ascending=False)

        # Plot distribution of 'average_rank' for general_df
        sns.histplot(sorted_ranking_df['average_rank'], kde=True, ax=axes[i])
        axes[i].set_title(title_general)
        axes[i].set_xlabel('Player Score')
        axes[i].set_ylabel('Number of Players')

        # Highlight Lincoln City players for all players plot
        lincoln_df = sorted_ranking_df[sorted_ranking_df['team_name'] == 'lincoln_city'].copy()
        for index_1, row_1 in lincoln_df.iterrows():
            percentile = 100-sorted_ranking_df.loc[index_1, 'average_rank_percentile']
            color = cmap(norm(percentile))
            line = axes[i].axvline(sorted_ranking_df.loc[index_1, 'average_rank'], color=color, linestyle='--')
            label = f"{row_1['player_name']} ({percentile:.2f}%)"
            lines_all.append(line)
            labels_all.append((percentile, label))
        
        # Locate the row using the player_name column
        player_ranking_row = sorted_ranking_df[sorted_ranking_df['player_name'] == player_name]
        player_percentile = 100 - player_ranking_row.iloc[0]['average_rank_percentile']
        player_label = f"{player_name} ({player_percentile:.2f}%)"
        player_line = axes[i].axvline(player_ranking_row.iloc[0]['average_rank'], color='r', linestyle='--')
        
        #Add player line and label for legend
        lines_all.append(player_line)
        labels_all.append((player_percentile, player_label))

        # Add text box for player's rank information
        total_players = len(sorted_ranking_df)
        player_rank = sorted_ranking_df['average_rank'].rank(method='min', ascending=False).loc[index] - 1
        rank_percentile = sorted_ranking_df.loc[index, 'average_rank_percentile']
        general_text = f"Ranked {int(player_rank)} out of {total_players} players ({int(100-rank_percentile)}%)"

        # Add legends
        sorted_labels_all = sorted(labels_all, key=lambda x: x[0], reverse=False)
        sorted_handles_all = [lines_all[labels_all.index(item)] for item in sorted_labels_all]
        axes[i].legend(sorted_handles_all, [item[1] for item in sorted_labels_all], loc='center left', bbox_to_anchor=(1, 0.5), title=f"Percentiles: {player_name.replace('_', ' ').title()} & Lincoln Players")
        


        # Check if player is under 21, if so make second u21 legend and add text to annotation for u21 ranking
        u21_lines = []
        u21_labels = []
        if player_age < 22:
            # Filter for players under 21
            u21_df = sorted_ranking_df[sorted_ranking_df['age'] < 22]

            # Sort U21 players by rank for legend
            sorted_u21_df = u21_df.sort_values(by='average_rank', ascending=False)

            # find row for player
            u21_player_ranking_row = sorted_u21_df[sorted_u21_df['player_name'] == player_name]
            u21_player_index = u21_player_ranking_row.index[0]

            # Recalculate rank percentile for the specific U21 player
            u21_player_rank = u21_df['average_rank'].rank(method='min', ascending=False).loc[u21_player_index]
            u21_total_players = len(u21_df)
            u21_player_percentile = int(100- (u21_player_rank *100 / u21_total_players))
            u21_text = f"\nRanked {int(u21_player_rank)} out of {u21_total_players} U21 players"
            combined_text = general_text + u21_text
        else:
            combined_text = general_text

        axes[i].text(0.02, 0.95, combined_text, transform=axes[i].transAxes, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

    # # Adjust layout to prevent overlap
    plt.tight_layout()

    # Save plot as png with a player-specific filename
    full_path = f'{save_path}/{row["player_name"].replace(" ", "_")}'
    
    # Create the directory if it doesn't exist
    if not os.path.exists(full_path):
        os.makedirs(full_path)
        
    plt.savefig(f"{full_path}/all_league_year_by_year_ranking_.png)

    plt.show()


    # player_position_groups = []
    # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))  # Two subplots for all players and U21 players

    # norm = Normalize(vmin=0, vmax=100)
    # cmap = plt.get_cmap('viridis')

    # lines_all = []
    # labels_all = []
    # lines_u21 = []
    # labels_u21 = []

    # for i, (index, row) in enumerate(player_df.iterrows()):
    #     position_group, general_metrics, comparable_positions = get_player_metrics(metric_grouping_information, row)

    #     if i == 0:
    #         player_position_groups.append(position_group)
    #         general_df = calculate_percentiles_all(df, player_df, comparable_positions, general_metrics)
    #     else:
    #         if position_group not in player_position_groups:
    #             player_position_groups.append(position_group)
    #             new_df = calculate_percentiles_all(df, player_df, comparable_positions, general_metrics)
    #             general_df = pd.concat([general_df, new_df])
    #             general_df = general_df.loc[~general_df.index.duplicated(keep='first')]
    #         else:
    #             continue

    # # Plot for all players
    # sns.histplot(general_df['average_rank'], kde=True, ax=ax1)
    # ax1.set_title(f"All {position_group.replace('_', ' ').title()}s")
    # ax1.set_xlabel('Player Score')
    # ax1.set_ylabel('Number of Players')

    # if not general_df.index.is_unique:
    #   general_df = general_df.reset_index(drop=True)

    # # Highlight Lincoln City players for all players plot
    # league_one_df = general_df[general_df['competition_name'] == 'league_one'].copy()

    # # Add player if not in
    # player_name = player_df['player_name'].iloc[0]
    # if player_name not in league_one_df['player_name'].values:
    #   # find player in general_df
    #   player_df_copy = general_df[general_df['player_name'] == player_name].copy()
    #   # add player_df_copy to league_one_df
    #   league_one_df = pd.concat([league_one_df, player_df_copy])

    # # sort in descending by averank_rank
    # league_one_df = league_one_df.sort_values('average_rank', ascending=False)
    # counter = 0
    # for index, row in league_one_df.iterrows():
    #     counter += 1
    #     percentile = 100-general_df.loc[index, 'average_rank_percentile']
    #     if row['player_name'] != player_name:
    #       color = cmap(norm(percentile))
    #       line = ax1.axvline(general_df.loc[index, 'average_rank'], color=color, linestyle=':', alpha = 0.1)
    #     else:
    #       color = 'red'
    #       line = ax1.axvline(general_df.loc[index, 'average_rank'], color=color, linestyle='--', alpha = 1)
    #     label = f"{row['player_name']} {row['season_name']} ({percentile:.2f}%)"
    #     if counter < 20 or row['player_name'] == player_name:
    #       lines_all.append(line)
    #       labels_all.append((percentile, label))


    # # # Add specific player for all players plot
    # # new_player_df = general_df[general_df['player_name'] == player_df['player_name'].iloc[0]]
    # # for index, row in new_player_df.iterrows():
    # #     average_rank = new_player_df.loc[index, 'average_rank']
    # #     average_rank_percentile = new_player_df.loc[index, 'average_rank_percentile']
    # #     color = 'red'
    # #     line = ax1.axvline(average_rank, color=color, linestyle='--')
    # #     label = f"{row['player_name']} {row['season_name']} ({average_rank_percentile:.2f}%)"
    # #     lines_all.append(line)
    # #     labels_all.append((average_rank_percentile, label))

    # # Plot for U21 players
    # u21_df = general_df[general_df['age'] < 21].copy()
    # #print len u21
    # sns.histplot(general_df['average_rank'], kde=True, ax=ax2)
    # ax2.set_title(f"All {position_group.replace('_', ' ').title()}s")
    # ax2.set_xlabel('Player Score')
    # ax2.set_ylabel('Number of Players')

    # # Highlight Lincoln City U21 players and Bobby Wales
    # league_one_u21_df = u21_df[u21_df['competition_name'] == 'league_one']
    # if player_name not in league_one_u21_df['player_name'].values:
    #   league_one_u21_df = pd.concat([league_one_u21_df, player_df_copy])

    # # sort in descending order of average_rank
    # league_one_u21_df = league_one_u21_df.sort_values('average_rank', ascending=False)
    # counter = 0
    # for index, row in league_one_u21_df.iterrows():
    #         counter += 1
    #         # Use index as proxy for u21_rank
    #         u21_rank = u21_df['average_rank'].rank(method='min', ascending=False).loc[index]
    #         u21_total_players = len(u21_df)
    #         u21_percentile = ((u21_rank / u21_total_players)) * 100
    #         color = cmap(norm(u21_percentile))
    #         if row['player_name'] == 'Bobby Wales':
    #             line = ax2.axvline(u21_df.loc[index, 'average_rank'], color='red', linestyle='--', alpha = 1)
    #         else:
    #             line = ax2.axvline(u21_df.loc[index, 'average_rank'], color=color, linestyle=':', alpha= 0.3)

    #         label = f"{row['player_name']} {row['season_name']} ({u21_percentile:.2f}%)"
    #         if counter < 20 or row['player_name'] == 'Bobby Wales':
    #           lines_u21.append(line)
    #           labels_u21.append((u21_percentile, label))
    #         else:
    #           continue

    # # # Add specific U21 player if applicable
    # # new_player_u21_df = u21_df[u21_df['player_name'] == player_df['player_name'].iloc[0]]
    # # print('new_player_u21_df')
    # # print(new_player_u21_df)
    # # for index, row in new_player_u21_df.iterrows():
    # #     average_rank = new_player_u21_df.loc[index, 'average_rank']
    # #     average_rank_percentile = new_player_u21_df.loc[index, 'average_rank_percentile']
    # #     color = 'red'
    # #     line = ax2.axvline(average_rank, color=color, linestyle='--')
    # #     label = f"{row['player_name']} {row['season_name']} ({average_rank_percentile:.2f}%)"
    # #     lines_u21.append(line)
    # #     labels_u21.append((average_rank_percentile, label))

    # # Add legends
    # sorted_labels_all = sorted(labels_all, key=lambda x: x[0], reverse=False)

    # sorted_handles_all = [lines_all[labels_all.index(item)] for item in sorted_labels_all]

    # # Create new handles for legend with full alpha
    # legend_handles = [plt.Line2D([0], [0], color=h.get_color(), linestyle=h.get_linestyle(), alpha=1.0) for h in sorted_handles_all]

    # ax1.legend(legend_handles, [label[1] for label in sorted_labels_all], loc='center left', bbox_to_anchor=(1, 0.5), title=f"{player_df['player_name'].iloc[0].replace('_', ' ').title()} & Top 20 League One Player Percentiles")

    # # ax1.legend(sorted_handles_all, [item[1] for item in sorted_labels_all], loc='center left', bbox_to_anchor=(1, 0.5), title=f"{player_df['player_name'].iloc[0].replace('_', ' ').title()} & Lincoln Player Rankings")

    # sorted_labels_u21 = sorted(labels_u21, key=lambda x: x[0], reverse=False)
    # sorted_handles_u21 = [lines_u21[labels_u21.index(item)] for item in sorted_labels_u21]

    # legend_handles_u21 = [plt.Line2D([0], [0], color=h.get_color(), linestyle=h.get_linestyle(), alpha=1.0) for h in sorted_handles_u21]
    # ax2.legend(legend_handles_u21, [label[1] for label in sorted_labels_u21], loc='center left', bbox_to_anchor=(1, 0.5), title=f"U21: {player_df['player_name'].iloc[0].replace('_', ' ').title()} & Top 20 League One Percentiles")
    # # ax2.legend(sorted_handles_u21, [item[1] for item in sorted_labels_u21], loc='center left', bbox_to_anchor=(1, 0.5), title=f"U21 {player_df['player_name'].iloc[0].replace('_', ' ').title()} & Top 20 League One Rankings")

    # # get unique season_ids in general_df
    # unique_season_ids = general_df['season_id'].unique()

    # # Step 2: Find the position of each season_id in chronological_season_ids
    # # Since we can't rely on index due to potential non-sequential indexing, we use 'loc' with boolean masking
    # # Step 2: Find the position of each season_id in chronological_season_ids
    # def find_position(season_id, series):
    #     try:
    #         return series[series == season_id].index[0]
    #     except IndexError:
    #         return None  # Season ID not found in the series

    # # Create a dictionary with season_ids and their positions
    # positions = {season_id: find_position(season_id, chronological_season_ids) for season_id in unique_season_ids}

    # # Step 3: Determine the earliest and latest based on the position in chronological_season_ids
    # # Since chronological_season_ids is sorted in descending order, lowest index = latest, highest index = earliest
    # latest_position = min(positions.values()) if positions else None
    # earliest_position = max(positions.values()) if positions else None

    # # Step 4: Retrieve the corresponding season_ids
    # latest_season_id = next(season_id for season_id, pos in positions.items() if pos == latest_position) if latest_position is not None else None
    # earliest_season_id = next(season_id for season_id, pos in positions.items() if pos == earliest_position) if earliest_position is not None else None

    # # find earliest and latest season names
    # latest_season_name = general_df[general_df['season_id'] == latest_season_id]['season_name'].iloc[0]
    # earliest_season_name = general_df[general_df['season_id'] == earliest_season_id]['season_name'].iloc[0]

    # fig.suptitle(f"Ranking in All Leagues: {earliest_season_name} - {latest_season_name}", fontsize=16, x=0.45)

    # plt.tight_layout(rect=[0, 0, 0.85, 0.95])
    # plt.savefig(f'{save_path}all_league_ranking_{player_df["player_name"].iloc[0].replace(" ", "_")}.png')
    # plt.show()