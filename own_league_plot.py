import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap
from get_position_specific_metrics_statsbomb import get_player_metrics
from aggregate_rank_statsbomb import calculate_percentiles
from scipy.stats import rankdata
import os

def plot_stacked_distribution_u21_flag(player_df, df, metric_grouping_information, save_path):

    """
    Generate a distribution plot of player rankings in their own league, including annotations for specific players
    with an additional focus on players under 21.

    Parameters:
    player_df (DataFrame): DataFrame containing player data.
    df (DataFrame): DataFrame with general league data.
    metric_grouping_information (dict): Dictionary containing metrics for grouping players.

    Returns:
    None. This function saves and displays the plot.

    Note:
    - This function assumes 'get_player_metrics', 'calculate_percentiles' are defined elsewhere.
    - The plot shows histograms with vertical lines for specific player rankings.
    """
    

    # Ensure axes is always iterable by wrapping single axis in a list
    fig, axes = plt.subplots(len(player_df), 1, figsize=(8, 4.5 * len(player_df)))  # Increased figure size for annotations
    if not isinstance(axes, np.ndarray):  # If only one subplot, wrap in a list
        axes = [axes]

    for i, (index, row) in enumerate(player_df.iterrows()):
        season_id = row['season_id']
        competition_id = row['competition_id']
        competition_name = row['competition_name']
        player_name = row['player_name']
        player_position = row['primary_position']
        player_age = row['age']  # Assuming 'age' is in player_df


        position_group, general_metrics, comparable_positions = get_player_metrics(metric_grouping_information, row)


        # Calculate rankings
        general_df = calculate_percentiles(df, season_id, competition_id, comparable_positions, general_metrics)


        column_list = general_df.columns.tolist()

        # Check if 'season' is in any column name
        season_columns = [col for col in general_df.columns if 'season' in col]

        # General plot
        title_general = f"{position_group.replace('_', ' ').title()}s: {row['competition_name'].replace('_', ' ').title()}, {row['season_name']}"
        # title_general = f"{row['competition_name'].replace('_', ' ').title()}, {row['season_name']}"

        # Sort general_df by 'average_rank' for accurate ranking
        sorted_general_df = general_df.sort_values('average_rank', ascending=False)

        # Plot distribution of 'average_rank' for general_df
        sns.histplot(sorted_general_df['average_rank'], kde=True, ax=axes[i])
        axes[i].set_title(title_general)
        axes[i].set_xlabel('Player Score')
        axes[i].set_ylabel('Number of Players')

        # Plot distribution of 'average_rank' for general_df
        # sns.histplot(sorted_general_df['average_rank'], kde=True, ax=axes[i])
        # axes[i].set_title(title_general)
        # axes[i].set_xlabel('Player Score')
        # axes[i].set_ylabel('Number of Players')

        # # Set custom x-axis labels to plot ten percentile values
        # percentiles = np.linspace(0, 100, 10)
        # axes[i].set_xticks(np.linspace(sorted_general_df['average_rank'].min(), sorted_general_df['average_rank'].max(), 10))
        # axes[i].set_xticklabels([f'{p:.0f}%' for p in percentiles])

        # Draw vertical line for the player's average_rank for general_df - Bobby Wales in red
        axes[i].axvline(sorted_general_df.loc[index, 'average_rank'], color='r', linestyle='--', label=player_name)

        # Add text box for player's rank information
        total_players = len(sorted_general_df)
        player_rank = sorted_general_df['average_rank'].rank(method='min', ascending=False).loc[index] - 1
        rank_percentile = sorted_general_df.loc[index, 'average_rank_percentile']
        general_text = f"Ranked {int(player_rank)} out of {total_players} players ({int(100-rank_percentile)}%)"

        # Check if player is under 21
        if player_age < 22:
            # Filter for players under 21
            u21_df = sorted_general_df[sorted_general_df['age'] < 22]

            # Define color mapping for U21 players based on rank
            cmap = get_cmap('viridis')
            norm = Normalize(vmin=u21_df['average_rank'].rank(method='min', ascending=False).min(),
                             vmax=u21_df['average_rank'].rank(method='min', ascending=False).max())

            # Sort U21 players by rank for legend
            sorted_u21_df = u21_df.sort_values(by='average_rank', ascending=False)

            lines = []
            labels = []

            for u21_index, u21_row in sorted_u21_df.iterrows():
                u21_player_rank = u21_df['average_rank'].rank(method='min', ascending=False).loc[u21_index]
                u21_total_players = len(u21_df)
                u21_player_name = u21_row['player_name']

                # Use red for Bobby Wales, otherwise use color based on rank
                if u21_player_name == player_name:
                    color = 'red'
                else:
                    color = cmap(norm(u21_df['average_rank'].rank(method='min', ascending=False).loc[u21_index]))

                line = axes[i].axvline(u21_row['average_rank'], color=color, linestyle=':', alpha=0.5)
                # axes[i].annotate(f"{u21_player_name}\nU21 Rank: {int(u21_player_rank)}/{u21_total_players}",
                #                  xy=(u21_row['average_rank'], axes[i].get_ylim()[1] * 0.8),
                #                  xytext=(5, 5), textcoords='offset points',
                #                  ha='center', va='bottom',
                #                  fontsize=8, color=color, alpha=0.8)
                lines.append(line)
                # labels.append(f"{u21_player_name} (U21 Rank: {int(u21_player_rank)})")
                labels.append(f"{u21_player_name} (Percentile: {int(100-u21_row['average_rank_percentile'])})")
                # labels.append(f"{u21_player_name}")

            # Recalculate rank percentile for the specific U21 player
            u21_player_rank = u21_df['average_rank'].rank(method='min', ascending=False).loc[index] if index in u21_df.index else "Not in U21"
            u21_total_players = len(u21_df)
            u21_text = f"\nRanked {int(u21_player_rank)} out of {u21_total_players} U21 players"
            combined_text = general_text + u21_text

            # Sort legend by rank in ascending order
            # sorted_handles_labels = sorted(zip(lines, labels), key=lambda x: float(x[1].split('Rank: ')[1].split(')')[0]))
            sorted_handles_labels = sorted(zip(lines, labels), key=lambda x: float(x[1].split(': ')[1].split(')')[0]))
            sorted_lines, sorted_labels = zip(*sorted_handles_labels)
            # only keep part before .split('Rank: ')[1] in sorted labels
            # sorted_labels = [label.split('(')[0] for label in sorted_labels]

            axes[i].legend(sorted_lines, sorted_labels, loc='center left', bbox_to_anchor=(1, 0.5), title=f"U21 Percentiles: {player_name.replace('_', ' ').title()} & {competition_name.replace('_', ' ').title()} Players")
        else:
            # combined_text = general_text + "\nPlayer is not under 21."
            combined_text = general_text
            axes[i].legend(loc='center left', bbox_to_anchor=(1, 0.5), title = f"{player_name.replace('_', ' ').title()}")

        axes[i].text(0.02, 0.95, combined_text, transform=axes[i].transAxes, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Save plot as png with a player-specific filename
    full_path = f'{save_path}/{row["player_name"].replace(" ", "_")}'
    
    # Create the directory if it doesn't exist
    if not os.path.exists(full_path):
        os.makedirs(full_path)
        
    plt.savefig(f"{full_path}/own_league_year_by_year_ranking_.png")

    plt.show()

# def get_player_metrics(metric_grouping_information, row):
#     '''
#     Function to get metric information specific to the player based on the position they play in.

#     Returns the following:
#     position_group: the general grouping for position, e.g. Winger for LW and RW
#     general_metrics: key metrics chosen by Metin for each position group
#     lincoln_metrics: key metrics chosen by Lincoln for each position group
#     comparable_positions: list of positions that are included in the player's position group
#     '''
#     # Find player position group
#     position_group = metric_grouping_information.loc[
#     (metric_grouping_information['positions_statsbomb'].apply(lambda x: row['primary_position'] in x)) &
#     (metric_grouping_information['position_groups'] != 'all'),
#     'position_groups'
#     ].iloc[0]

#     # Find corresponding statsbomb metrics
#     general_metrics = metric_grouping_information.loc[
#         metric_grouping_information['position_groups'] == position_group,
#         'statsbomb_metrics'
#     ].iloc[0]

#     # # Find corresponding lincoln specific metrics
#     # lincoln_metrics = metric_grouping_information.loc[
#     #     metric_grouping_information['position_groups'] == position_group,
#     #     'lincoln_metrics'
#     # ].iloc[0]

#     # Find comparable statsbomb positions in the player's position group
#     comparable_positions = metric_grouping_information.loc[
#         metric_grouping_information['position_groups'] == position_group,
#         'positions_statsbomb'
#     ].iloc[0]

#     # return position_group, general_metrics, lincoln_metrics, comparable_positions
#     return position_group, general_metrics, comparable_positions