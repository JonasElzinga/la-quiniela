clasico = df_matches[((df_matches['home_team']=='Barcelona')| (df_matches['home_team']=='Real Madrid')) & ((df_matches['away_team']=='Barcelona')| (df_matches['away_team']=='Real Madrid'))]

clasico_wins = clasico.groupby(['home_team','winner']).size()
Barcelona_wins = clasico_wins[('Barcelona',1)] + clasico_wins[('Real Madrid',2)]
RMadrid_wins = clasico_wins[('Barcelona',2)] + clasico_wins[('Real Madrid',1)]

def labelpie(pct, allvals, param):
    absolute = int(np.round(pct/100.*np.sum(allvals)))
    return f"{pct:.1f}%\n({absolute:d} {param})"

clasico_wins_data = [Barcelona_wins, RMadrid_wins]
plt.pie(clasico_wins_data, labels=['Barcelona' , 'Real Madrid'], autopct=lambda pct: labelpie(pct, clasico_wins_data, 'wins' ))
plt.show()

#BREAK

clasico_score = clasico[['home_team' , 'home_score' , 'away_score']]
Barcelona_score = clasico_score[clasico_score["home_team"]=="Barcelona"]["home_score"].sum() + clasico_score[clasico_score["home_team"]=="Real Madrid"]["away_score"].sum()
RMadrid_score = clasico_score[clasico_score["home_team"]=="Real Madrid"]["home_score"].sum() + clasico_score[clasico_score["home_team"]=="Barcelona"]["away_score"].sum()

clasico_scores_data = [Barcelona_score, RMadrid_score]
plt.pie(clasico_scores_data, labels=['Barcelona' , 'Real Madrid'], autopct=lambda pct: labelpie(pct, clasico_scores_data, 'goals' ))
plt.show()

#BREAK

def plot_direct_confrontations_stats(team1, team2):
    confrontation = df_matches[((df_matches['home_team'] == team1)| (df_matches['home_team']== team2 )) & ((df_matches['away_team']== team1 )| (df_matches['away_team']== team2 ))]

    confrontation_wins = confrontation.groupby(['home_team','winner']).size()
    team1_wins = confrontation_wins[( team1 ,1)] + confrontation_wins[( team2 ,2)]
    team2_wins = confrontation_wins[( team1 ,2)] + confrontation_wins[( team2 ,1)]

    fig, ax = plt.subplots(1,2)
    confrontation_wins_data = [team1_wins, team2_wins]
    ax[0].pie(confrontation_wins_data, labels=[ team1  ,  team2 ], autopct=lambda pct: labelpie(pct, confrontation_wins_data, 'wins' ))
    ax[0].set_title("Total wins comparison")

    confrontation_score = confrontation[['home_team' , 'home_score' , 'away_score']]
    team1_score = confrontation_score[confrontation_score["home_team"]== team1 ]["home_score"].sum() + confrontation_score[confrontation_score["home_team"]== team2 ]["away_score"].sum()
    team2_score = confrontation_score[confrontation_score["home_team"]== team2 ]["home_score"].sum() + confrontation_score[confrontation_score["home_team"]== team1 ]["away_score"].sum()

    confrontation_scores_data = [team1_score, team2_score]
    ax[1].pie(confrontation_scores_data, labels=[ team1  ,  team2 ], autopct=lambda pct: labelpie(pct, confrontation_scores_data, 'goals' ))
    ax[1].set_title("Total scored goals comparison")

    return ax

#BREAK

ax = plot_direct_confrontations_stats('Real Betis', 'Sevilla FC')
plt.show()