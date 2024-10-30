import pandas as pd

def count_points(last_5):
    if last_5 == 0:
        return 0

    count = 0
    for i in last_5:
        if i == 'W':
            count += 3
        elif i == 'T':
            count += 1
    return count


def extend_data(input_data):
    # clean the inputted dataframe
    # make a copy of the data so the original dataframe does not change
    data = input_data.copy()

    # drop NaN values (there are only NaN values left in the "score" column)
    data.dropna(inplace=True)

    # create two new columns, one for the score of the home team, and one for the score of the away team, drop the score column
    data[['home_score', 'away_score']] = data['score'].str.split(':', expand=True).astype(int)
    data.drop(columns=['score'], inplace=True)

    # create a new column to show which team won (1 for home team, 2 for away team and 'X' for a draw)
    data['winner'] = data.apply(
        lambda row: 1 if row['home_score'] > row['away_score'] else 2 if row['home_score'] < row['away_score'] else 'X',
        axis=1)

    # use the code from exercise 10 to gather more data for the matches
    # make a copy of the data dataframe so the original dataframe does not change
    data_copy = data

    # calculate, for every unique group of season, division, matchday and home_team, how many goals the team made (GF) and got against (GA)
    # and if the team won (W=1), lost (L=1) or tied (T=1)
    home_stats = data_copy.groupby(['season', 'division', 'matchday', 'home_team']).agg(
        GF=('home_score', 'sum'), GA=('away_score', 'sum'),
        W=('winner', lambda x: (x == 1).sum()),
        L=('winner', lambda x: (x == 2).sum()),
        T=('winner', lambda x: (x == 'X').sum())
    ).reset_index().rename(columns={'home_team': 'team', 'result': 'home_result'})

    # calculate, for every unique group of season, division, matchday and away_team, how many goals the team made (GF) and got against (GA)
    # and if the team won (W=1), lost (L=1) or tied (T=1)
    away_stats = data_copy.groupby(['season', 'division', 'matchday', 'away_team']).agg(
        GF=('away_score', 'sum'), GA=('home_score', 'sum'),
        W=('winner', lambda x: (x == 2).sum()),
        L=('winner', lambda x: (x == 1).sum()),
        T=('winner', lambda x: (x == 'X').sum())
    ).reset_index().rename(columns={'away_team': 'team', 'result': 'away_result'})

    # add the statestics for the home teams and the away teams together
    combined_stats = pd.concat([home_stats, away_stats]).fillna(0)
    # calculate the goal difference for each row, a negative goal difference means the team got more goals against then that it made
    combined_stats['GD'] = combined_stats['GF'] - combined_stats['GA']
    # calculate the amount of points for each row, a win is worth 3 points, and a tie 1
    combined_stats['Pts'] = combined_stats['W'] * 3 + combined_stats['T']
    # create a result column that contains "W" if the team one the match, 'L' if the team lost the match and "T" if the team tied the match
    combined_stats['result'] = combined_stats.apply(lambda row: 'W' if row['W'] > 0 else ('L' if row['L'] > 0 else 'T'),
                                                    axis=1)

    # sort the combined statistics so they are in the right order
    results = combined_stats.sort_values(by=['season', 'division', 'matchday', 'Pts', 'GD', 'GF'])
    # cumulative sum 'GF', 'GA', 'GD', 'W', 'L', 'T' and 'Pts', so that it is updated for every matchday
    results[['GF', 'GA', 'GD', 'W', 'L', 'T', 'Pts']] = results.groupby(['season', 'division', 'team'])[
        ['GF', 'GA', 'GD', 'W', 'L', 'T', 'Pts']].cumsum()

    # sort the dataframe again so that the rank can be calculated
    results = results.sort_values(by=['season', 'division', 'matchday', 'Pts', 'GD', 'GF'],
                                  ascending=[True, True, True, False, False, False])
    # calculate the rank
    results['rank'] = results.groupby(['season', 'division', 'matchday']).cumcount() + 1
    # sort the dataframe so everything is in the right order
    results = results.sort_values(by=['season', 'division', 'matchday', 'rank'],
                                  ascending=[False, True, True, True]).reset_index(drop=True)

    # create a column with the last 5 results of the team in the same season and division
    results['last_5'] = results.apply(lambda row: results[
                                                      (results['season'] == row['season']) &
                                                      (results['division'] == row['division']) &
                                                      (results['matchday'] <= row['matchday']) &
                                                      (results['matchday'] >= max(1, row['matchday'] - 4)) &
                                                      (results['team'] == row['team'])
                                                      ]['result'].tolist()[-5:], axis=1)

    # count the amount of points the last 5 results would total to
    results['last_5'] = results['last_5'].apply(lambda x: count_points(x))

    # the final result dataframe
    results = results[
        ['season', 'division', 'matchday', 'rank', 'team', 'GF', 'GA', 'GD', 'W', 'L', 'T', 'Pts', 'result', 'last_5']]

    # shift the results dataframe so that it can be combined with the data dataframe later
    # make a copy of the results dataframe so the original dataframe does not change
    results_shifted = results.copy()
    # shift the matchday up by 1 so that the results dataframe will merge good with the data dataframe
    results_shifted['matchday'] += 1

    # rename the columns so that that values are clear, the values are from just before the matchday where they are shown started
    results_shifted = results_shifted.rename(columns={
        'rank': 'prev_rank',
        'GF': 'prev_GF', 'GA': 'prev_GA', 'GD': 'prev_GD',
        'W': 'prev_W', 'L': 'prev_L', 'T': 'prev_T', 'Pts': 'prev_Pts',
        'result': 'prev_result', 'last_5': 'prev_last_5'
    })

    # merge the data dataframe with the shifted results dataframe, first only for the home teams
    data = data.merge(results_shifted,
                      how='left',
                      left_on=['season', 'division', 'matchday', 'home_team'],
                      right_on=['season', 'division', 'matchday', 'team']).fillna(0)

    # drop the team column that was created
    data.drop(columns=['team'], inplace=True)

    # merge the data dataframe again with the shifted results dataframe, now for the away teams, and ensure the prefixes are correct
    data = data.merge(results_shifted,
                      how='left',
                      left_on=['season', 'division', 'matchday', 'away_team'],
                      right_on=['season', 'division', 'matchday', 'team'],
                      suffixes=('_home', '_away')).fillna(0)

    # drop the team column that was created
    data.drop(columns=['team'], inplace=True)

    # space to add extra data to the data dataframe or change existing data
    data['winner'] = data.apply(lambda row: 1 if row['winner'] == 1 else 2 if row['winner'] == 2 else 0, axis=1)

    # Create a helper column to represent team pairs in an unordered manner
    data['team_pair'] = data.apply(lambda row: frozenset([row['home_team'], row['away_team']]), axis=1)

    # Group by 'team_pair' instead of separate home and away teams to include all matches between the two teams
    data['head_to_head_last_5'] = data.groupby('team_pair')['winner'].transform(
        lambda x: x.rolling(5, 1).apply(lambda y: sum(y == 1) / 5, raw=True)
    )

    # 1. Head-to-Head Draw Ratio in the last 5 matches
    data['head_to_head_draw_ratio'] = data.groupby('team_pair')['winner'].transform(
        lambda x: x.rolling(5, 1).apply(lambda y: sum(y == 'X') / 5, raw=True)
    )

    # 2. Head-to-Head Average Goals Scored by Home Team in the last 5 matches
    data['head_to_head_avg_goals_home'] = data.groupby('team_pair')['home_score'].transform(
        lambda x: x.rolling(5, 1).mean()
    )

    # 3. Head-to-Head Average Goals Scored by Away Team in the last 5 matches
    data['head_to_head_avg_goals_away'] = data.groupby('team_pair')['away_score'].transform(
        lambda x: x.rolling(5, 1).mean()
    )

    # 4. Head-to-Head Goal Difference (Home Goals - Away Goals) in the last 5 matches
    data['head_to_head_goal_diff'] = data.groupby('team_pair').apply(
        lambda x: (x['home_score'] - x['away_score']).rolling(5, 1).mean()
    ).reset_index(level=0, drop=True)

    # Drop the helper column to clean up the dataframe
    data.drop(columns=['team_pair'], inplace=True)

    return data

def keep_data(data, season = None, divsion = None, matchday = None):
    # keep the seasons that are given, if season is None, keep all seasons
    if season is None:
        season = data['season'].unique()
    # keep the divisions that are given, if division is None, keep all divisions
    if divsion is None:
        divsion = data['division'].unique()
    # keep the matchdays that are given, if matchday is None, keep all matchdays
    if matchday is None:
        matchday = data['matchday'].unique()

    # keep only the seasons that are in the seasons list
    data = data[data['season'].isin(season)]
    # keep only the divisions that are in the divisions list
    data = data[data['division'].isin(divsion)]
    # keep only the matchdays that are in the matchdays list
    data = data[data['matchday'].isin(matchday)]

    return data
