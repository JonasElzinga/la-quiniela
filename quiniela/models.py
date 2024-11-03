import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression


class QuinielaModel:

    def train(self, train_data):
        """
        Trains the model with the training data.
        Here we assume that the training data is already preprocessed by using the cli.py script.
        The model is a Logistic Regression model with the hyperparameters C=1, class_weight="balanced", max_iter=1000, solver="lbfgs" and uses
        the features we selected to get the best results. They are:
        - prev_GF_away
        - prev_GF_home_avg
        - prev_W_away
        - prev_rank_away
        - prev_Pts_home
        - prev_GF_away_avg
        - prev_W_home

        :param train_data: DataFrame with the preprocessed training data
        """
        # balance the training data
        balanced_data = self.balance(train_data)

        # define the features and the target
        features = ['prev_GF_away', 'prev_GF_home_avg', 'prev_W_away', 'prev_rank_away', 'prev_Pts_home',
                    'prev_GF_away_avg', 'prev_W_home']
        target = 'winner'

        # create X and y
        X = balanced_data[features]
        y = balanced_data[target]

        # train the model
        self.model = LogisticRegression(C=1, class_weight="balanced", max_iter=1000, solver="lbfgs")
        self.model.fit(X, y)

    def predict(self, predict_data):
        """
        Predicts the winner of the matches in the predict_data DataFrame.

        :param predict_data: DataFrame with the preprocessed data to predict.
        :return: predictions: array with the predictions.
        """
        # define the features
        features = ['prev_GF_away', 'prev_GF_home_avg', 'prev_W_away', 'prev_rank_away', 'prev_Pts_home',
                    'prev_GF_away_avg', 'prev_W_home']

        # create X
        X = predict_data[features]

        # predict the winner
        predictions = self.model.predict(X)

        return predictions

    def balance(self, data):
        """
        Balances the training data by subsampling the majority classes to match the minority class.

        :param data: DataFrame with the training data.

        :return: balanced_data: DataFrame with the balanced training data.
        """
        # find the minority catagory in the winner column
        minority_cat = min(data['winner'].value_counts())

        # seperate each class
        df_class_0 = data[data['winner'] == 0]
        df_class_1 = data[data['winner'] == 1]
        df_class_2 = data[data['winner'] == 2]

        # subsample for each class if necessary
        df_class_0_subsampled = df_class_0.sample(minority_cat, random_state=42)
        df_class_1_subsampled = df_class_1.sample(minority_cat, random_state=42)
        df_class_2_subsampled = df_class_2.sample(minority_cat, random_state=42)

        # concat each class into a final balanced training dataset
        balanced_data = pd.concat([df_class_0_subsampled, df_class_1_subsampled, df_class_2_subsampled]).reset_index(drop=True)

        return balanced_data

    @classmethod
    def load(cls, filename):
        """ Load model from file """
        with open(filename, "rb") as f:
            model = pickle.load(f)
            assert isinstance(model, cls)
        return model

    def save(self, filename):
        """ Save a model in a file """
        with open(filename, "wb") as f:
            pickle.dump(self, f)
