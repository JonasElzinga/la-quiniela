#!/usr/bin/env python
import logging
import argparse
from datetime import datetime

import settings
from quiniela import models, io, preprocess_data


def parse_seasons(value):
    if value == "all":
        return "all"
    seasons = []
    for chunk in value.split(","):
        if ":" in chunk:
            try:
                start, end = map(int, chunk.split(":"))
                assert start < end
            except Exception:
                raise argparse.ArgumentTypeError(f"Unexpected format for seasons {value}")
            for i in range(start, end):
                seasons.append(f"{i}-{i+1}")
        else:
            try:
                start, end = map(int, chunk.split("-"))
                assert start == end - 1
            except Exception:
                raise argparse.ArgumentTypeError(f"Unexpected format for seasons {value}")
            seasons.append(chunk)
    return seasons


parser = argparse.ArgumentParser()
task_subparser = parser.add_subparsers(help='Task to perform', dest='task')
train_parser = task_subparser.add_parser("train")
train_parser.add_argument(
    "--training_seasons",
    default="all",
    type=parse_seasons,
    help="Seasons to use for training. Write them separated with ',' or use range with ':'. "
         "For instance, '2004:2006' is the same as '2004-2005,2005-2006'. "
         "Use 'all' to train with all seasons available in database.",
)
train_parser.add_argument(
    "--model_name",
    default="my_quiniela.model",
    help="The name to save the model with.",
)
predict_parser = task_subparser.add_parser("predict")
predict_parser.add_argument(
    "season",
    help="Season to predict",
)
predict_parser.add_argument(
    "division",
    type=int,
    choices=[1, 2],
    help="Division to predict (either 1 or 2)",
)
predict_parser.add_argument(
    "matchday",
    type=int,
    help="Matchday to predict",
)
predict_parser.add_argument(
    "--model_name",
    default="my_quiniela.model",
    help="The name of the model you want to use.",
)

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(
        filename=settings.LOGS_PATH / f"{args.task}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.log",
        format="%(asctime)s - [%(levelname)s] - %(message)s",
        level=logging.INFO,
    )
    if args.task == "train":
        logging.info(f"Training LaQuiniela model with seasons {args.training_seasons}")
        model = models.QuinielaModel()

        # get the start and end year of the training seasons
        start_year, end_year = map(int, args.training_seasons[0].split('-'))
        # get a list of the seasons to load, including 3 previous seasons that are needed for correct data extension
        load_seasons = [f"{start_year - 3}-{end_year - 3}", f"{start_year - 2}-{end_year - 2}", f"{start_year - 1}-{end_year - 1}"] + args.training_seasons
        # load the data
        training_data = io.load_historical_data(load_seasons)

        # preprocess the data by extending it
        training_data = preprocess_data.extend_data(training_data)
        # keep only the data for the training seasons, remove the 3 years used for extension
        training_data = preprocess_data.keep_data(training_data, args.training_seasons, None, None)

        model.train(training_data)
        model.save(settings.MODELS_PATH / args.model_name)
        print(f"Model succesfully trained and saved in {settings.MODELS_PATH / args.model_name}")
    if args.task == "predict":
        logging.info(f"Predicting matchday {args.matchday} in season {args.season}, division {args.division}")
        model = models.QuinielaModel.load(settings.MODELS_PATH / args.model_name)

        # get the start and end year of the testing season
        start_year, end_year = map(int, args.season.split('-'))
        # get a list of the seasons to load, including 3 previous seasons that are needed for correct data extension
        load_seasons = [f"{start_year - 3}-{end_year - 3}", f"{start_year - 2}-{end_year - 2}", f"{start_year - 1}-{end_year - 1}", args.season]
        # load the data, the complete data for the previous 3 years and the data until the matchday for the testing season
        predict_data = io.load_until_matchday(load_seasons, args.division, args.matchday)

        # preprocess the data by extending it
        predict_data = preprocess_data.extend_data(predict_data)
        # keep only the data for the mathcday to predict
        predict_data = preprocess_data.keep_data(predict_data, [args.season], [args.division], [args.matchday])

        # predict the winners for all the matches in the matchday
        predict_data["pred"] = model.predict(predict_data)

        # see how accurate the model is by getting the accuracy
        accuracy = (predict_data["pred"] == predict_data["winner"]).mean()

        # show the predictions
        predict_data = predict_data[['season', 'division', 'matchday', 'date', 'time', 'home_team', 'away_team', 'pred']]
        print(f"Matchday {args.matchday} - LaLiga - Division {args.division} - Season {args.season}")
        print("=" * 70)
        for _, row in predict_data.iterrows():
            print(f"{row['home_team']:^30s} vs {row['away_team']:^30s} --> {row['pred']}")
        # and the accuracy
        print(f"Model accuracy: {accuracy:.2f}")

        # save the predictions into the sqlite database
        io.save_predictions(predict_data)
