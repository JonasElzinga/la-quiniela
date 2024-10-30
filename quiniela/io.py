import sqlite3

import pandas as pd

import settings


def load_until_matchday(season, division, matchday):
    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        data = pd.read_sql(f"""
            SELECT * FROM Matches
                WHERE season IN {tuple(season)}
                AND division = {division}
        """, conn)
    if data.empty:
        raise ValueError("There is no matchday data for the values given")

    # keep the full data for season[0], season[1], season[2], and keep only the data until matchday for season[3]
    temp_data = data[data["season"] == season[3]]
    temp_data = temp_data[temp_data["matchday"] <= matchday]

    data = pd.concat([data[data["season"] != season[3]], temp_data])
    return data


def load_historical_data(seasons):
    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        if seasons == "all":
            data = pd.read_sql("SELECT * FROM Matches", conn)
        else:
            data = pd.read_sql(f"""
                SELECT * FROM Matches
                    WHERE season IN {tuple(seasons)}
            """, conn)
    if data.empty:
        raise ValueError(f"No data for seasons {seasons}")
    return data


def save_predictions(predictions):
    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        predictions.to_sql(name="Predictions", con=conn, if_exists="append", index=False)
