def get_last_results(row):
    season = row['season']
    division = row['division']
    matchday = row['matchday']
    team = row['team']
    
    filtered = final_result[
        (final_result['season'] == season) &
        (final_result['division'] == division) &
        (final_result['matchday'] <= matchday) &
        (final_result['matchday'] >= max(1, matchday - 4)) &
        (final_result['team'] == team)
    ]
    return filtered['result'].tolist()[-5:]


df_filtered = df.dropna(subset=['home_score', 'away_score', 'winner'])


home_grouped = df_filtered.groupby(['season', 'division', 'matchday', 'home_team']).agg(
    GF=('home_score', 'sum'),
    GA=('away_score', 'sum'),
    W=('winner', lambda x: (x == 1).sum()),
    L=('winner', lambda x: (x == 2).sum()),
    T=('winner', lambda x: (x == 'X').sum())
).reset_index()


away_grouped = df_filtered.groupby(['season', 'division', 'matchday', 'away_team']).agg(
    GF=('away_score', 'sum'),
    GA=('home_score', 'sum'),
    W=('winner', lambda x: (x == 2).sum()),
    L=('winner', lambda x: (x == 1).sum()),
    T=('winner', lambda x: (x == 'X').sum())
).reset_index()


away_grouped.rename(columns={'away_team': 'team'}, inplace=True)


combined = pd.concat([home_grouped.rename(columns={'home_team': 'team', 'result': 'home_result'}),
                      away_grouped.rename(columns={'away_team': 'team', 'result': 'away_result'})]).fillna(0)


combined['result'] = combined.apply(
    lambda row: 'W' if row['W'] > 0 else ('L' if row['L'] > 0 else 'T'), axis=1
)


combined['GD'] = combined['GF'] - combined['GA']
combined['Pts'] = combined['W'] * 3 + combined['T']


final_result = combined.groupby(['season', 'division', 'matchday', 'team']).agg(
    GF=('GF', 'sum'),
    GA=('GA', 'sum'),
    GD=('GD', 'sum'),
    W=('W', 'sum'),
    L=('L', 'sum'),
    T=('T', 'sum'),
    Pts=('Pts', 'sum'),
    result = ('result', 'first')
).reset_index()


final_result = final_result.sort_values(by=['season', 'division', 'matchday', 'team'])
final_result[['GF', 'GA', 'GD', 'W', 'L', 'T', 'Pts']] = final_result.groupby(['season', 'division', 'team'])[
    ['GF', 'GA', 'GD', 'W', 'L', 'T', 'Pts']
].cumsum()


final_result = final_result.sort_values(by=['season', 'division', 'matchday', 'Pts', 'GD', 'GF'], ascending=[True, True, True, False, False, False])
final_result['rank'] = final_result.groupby(['season', 'division', 'matchday']).cumcount() + 1
final_result = final_result.sort_values(by=['season', 'division', 'matchday', 'rank'], ascending=[False, True, True, True]).reset_index(drop=True)


final_result = final_result[['season', 'division', 'matchday', 'rank', 'team', 'GF', 'GA', 'GD', 'W', 'L', 'T', 'Pts', 'result']]

final_result['last_5'] = final_result.apply(get_last_results, axis=1)

final_result.to_excel('results.xlsx', index=False)
