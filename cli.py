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

        start_year, end_year = map(int, args.training_seasons[0].split('-'))
        load_seasons = [f"{start_year - 3}-{end_year - 3}", f"{start_year - 2}-{end_year - 2}", f"{start_year - 1}-{end_year - 1}"] + args.training_seasons
        training_data = io.load_historical_data(load_seasons)

        training_data = preprocess_data.extend_data(training_data)
        training_data = preprocess_data.keep_data(training_data, args.training_seasons, None, None)

        model.train(training_data)
        model.save(settings.MODELS_PATH / args.model_name)
        print(f"Model succesfully trained and saved in {settings.MODELS_PATH / args.model_name}")
    if args.task == "predict":
        logging.info(f"Predicting matchday {args.matchday} in season {args.season}, division {args.division}")
        model = models.QuinielaModel.load(settings.MODELS_PATH / args.model_name)

        start_year, end_year = map(int, args.season.split('-'))
        load_seasons = [f"{start_year - 3}-{end_year - 3}", f"{start_year - 2}-{end_year - 2}", f"{start_year - 1}-{end_year - 1}", args.season]
        predict_data = io.load_until_matchday(load_seasons, args.division, args.matchday)

        predict_data = preprocess_data.extend_data(predict_data)
        predict_data = preprocess_data.keep_data(predict_data, [args.season], [args.division], [args.matchday])

        print(predict_data[['home_team', 'away_team', 'winner']])

        predict_data["pred"] = model.predict(predict_data)
        predict_data = predict_data[['season', 'division', 'matchday', 'date', 'time', 'home_team', 'away_team', 'pred']]
        print(f"Matchday {args.matchday} - LaLiga - Division {args.division} - Season {args.season}")
        print("=" * 70)
        for _, row in predict_data.iterrows():
            print(f"{row['home_team']:^30s} vs {row['away_team']:^30s} --> {row['pred']}")
        io.save_predictions(predict_data)
