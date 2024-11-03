import sqlite3

import pandas as pd

import settings


def load_until_matchday(season, division, matchday):
    """
    Load all data until the matchday for the given seasons and division.

    :param season: seasons to load.
    :param division: division to load.
    :param matchday: matchday to load until.

    :return: data: DataFrame with the data loaded.
    """
    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        data = pd.read_sql(f"""
            SELECT * FROM Matches
                WHERE season IN {tuple(season)}
                AND division = {division}
        """, conn)
    if data.empty:
        raise ValueError("There is no matchday data for the values given")

    # keep the full data for the seasons before the last one (maximum 3, less if less are found)
    # keep only the data until matchday for the last season
    temp_data = data[data["season"] == season[-1]]
    temp_data = temp_data[temp_data["matchday"] <= matchday]

    data = pd.concat([data[data["season"] != season[-1]], temp_data])
    return data


def load_historical_data(seasons):
    """
    Load all data for the given seasons.

    :param seasons: seasons to load.
    """
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
