import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect("../laliga.sqlite")
df_matches = pd.read_sql_query("SELECT * from Matches", con)
df_predictions = pd.read_sql_query("SELECT * from Predictions", con)

con.close()


def split_score(score):
    if score is None:
        return None

    score_split = score.split(":")

    if score_split[0] > score_split[1]:
        return 1
    elif score_split[0] < score_split[1]:
        return 2
    else:
        return 'X'


df_matches['winner'] = df_matches.apply(lambda row: split_score(row['score']),
                                        axis=1)

count_home_wins = df_matches[df_matches['winner'] == 1].shape[0]
count_away_wins = df_matches[df_matches['winner'] == 2].shape[0]
count_draws = df_matches[df_matches['winner'] == 'X'].shape[0]
total_wins = count_home_wins + count_away_wins + count_draws

y = np.array([count_home_wins, count_away_wins, count_draws])
labels = ['Home Wins', 'Away Wins', 'Draws']

plt.pie(y, labels=labels, autopct="%1.1f%%")
plt.show()

df_rank = pd.concat([df_matches[df_matches['division']==1][['home_team', 'home_score']].groupby(['home_team']).agg(['sum']), df_matches[df_matches['division']==1][['away_team', 'away_score']].groupby(['away_team']).agg(['sum'])], axis=1)

df_rank['total'] = df_rank['home_score'] + df_rank['away_score']

top_10 = df_rank[['total']].sort_values('total', ascending=False).head(10)

plt.barh(list(top_10.index)[::-1],list(top_10['total'])[::-1])
plt.show()

df_concede = pd.concat([df_matches[df_matches['division']==1][['home_team', 'away_score']].groupby(['home_team']).agg(['sum']), df_matches[df_matches['division']==1][['away_team', 'home_score']].groupby(['away_team']).agg(['sum'])], axis=1)
df_concede['total'] = df_concede['home_score'] + df_concede['away_score']
top_10_concede = df_concede[['total']].sort_values('total', ascending=False).head(10)

plt.barh(list(top_10_concede.index)[::-1],list(top_10_concede['total'])[::-1])
plt.show()

df_matches['difference'] = abs(df_matches['home_score'] - df_matches['away_score'])
df_matches[['date', 'home_team', 'away_team', 'score', 'difference']].sort_values('difference', ascending=False).head(10)
