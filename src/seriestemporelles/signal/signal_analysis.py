import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error

from seriestemporelles.signal.proporties_signal import Properties
from seriestemporelles.test.test_statistiques import TestStatistics
from sklearn.model_selection import TimeSeriesSplit
from darts import TimeSeries


class SignalAnalysis(Properties):

    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.report = super().profiling()
        self.scores = {}
        self.results = {}

    def apply_test(self, type_test: str, test_stat_name: str, *args, **kwargs):
        call_test = TestStatistics(self.data)
        test_output = call_test.statistical_test(type_test, test_stat_name, *args, **kwargs)
        self.report[type_test] = test_output
        return self.report

    def split_cv(self, timestamp, n_splits_cv=None):
        self.train_set = self.data.loc[self.data.index <= timestamp]
        self.test_set = self.data.loc[self.data.index > timestamp]
        print("Split applied on :", timestamp, '\n')

        if n_splits_cv != None:
            time_series_cross_validation = TimeSeriesSplit(n_splits=n_splits_cv)

            for fold, (train_index, test_index) in enumerate(time_series_cross_validation.split(self.train_set)):
                print("Fold: {}".format(fold))
                print("TRAIN indices:", train_index[0], " -->", train_index[-1])
                print("TEST  indices:", test_index[0], "-->", test_index[-1])
                print("\n")

            self.ts_cv = time_series_cross_validation.split(self.train_set)

    def apply_model(self, model, gridsearch=False, parameters=None):

        if gridsearch:
            best_model, best_parameters = model.gridsearch(parameters=parameters,
                                                           series=self.train_set,
                                                           start=0.5,
                                                           forecast_horizon=12)
            model = best_model

        series_train = TimeSeries.from_dataframe(self.train_set)
        model.fit(series_train)
        forecast = model.predict(len(self.test_set))
        forecast = forecast.univariate_values()

        print('model {} obtains R2 score: {:.2f}'.format(model, r2_score(self.test_set.values, forecast)), '\n')
        # print('model {} obtains RMSE score: {:.2f}'.format(model, np.sqrt(mean_squared_error(
        #                                                                      self.test_set.values, forecast)) ))

        # Save
        model_name = model.__class__.__name__
        self.scores[model_name] = {'R2_score': r2_score(self.test_set.values, forecast).round(2),
                                   'RMSE_score': np.sqrt(
                                       mean_squared_error(self.test_set.values, forecast)).round(2),
                                   }

        self.results[model_name] = {'test_set': self.test_set,
                                    'predictions': forecast,
                                    }
        return forecast



class MultiVariateSignalAnalysis(Properties):

    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.scores = {}
        self.results = {}


    def split_cv(self, timestamp, n_splits_cv=None):
        self.train_set = self.data.loc[self.data.index <= timestamp]
        self.test_set = self.data.loc[self.data.index > timestamp]
        print("Split applied on :", timestamp, '\n')

        if n_splits_cv != None:
            time_series_cross_validation = TimeSeriesSplit(n_splits=n_splits_cv)

            for fold, (train_index, test_index) in enumerate(time_series_cross_validation.split(self.train_set)):
                print("Fold: {}".format(fold))
                print("TRAIN indices:", train_index[0], " -->", train_index[-1])
                print("TEST  indices:", test_index[0], "-->", test_index[-1])
                print("\n")

            self.ts_cv = time_series_cross_validation.split(self.train_set)

    def apply_model(self, model, gridsearch=False, parameters=None):

        if gridsearch:
            best_model, best_parameters = model.gridsearch(parameters=parameters,
                                                           series=self.train_set,
                                                           start=0.5,
                                                           forecast_horizon=12)
            model = best_model


        series_train = TimeSeries.from_dataframe(self.train_set.reset_index(),
                                                 time_col='time',
                                                 value_cols=self.train_set.columns.to_list())

        model.fit(series_train)
        forecast = model.predict(len(self.test_set))
        forecast = forecast.values()

        # print('model {} obtains R2 score: {:.2f}'.format(model, r2_score(self.test_set.values, forecast)), '\n')
        # # print('model {} obtains RMSE score: {:.2f}'.format(model, np.sqrt(mean_squared_error(
        # #                                                                      self.test_set.values, forecast)) ))

        # # Save
        model_name = model.__class__.__name__
        # self.scores[model_name] = {'R2_score': r2_score(self.test_set.values, forecast).round(2),
        #                            'RMSE_score': np.sqrt(
        #                                mean_squared_error(self.test_set.values, forecast)).round(2),
        #                            }

        self.results[model_name] = {'test_set': self.test_set,
                                    'predictions': pd.DataFrame(forecast,
                                                                columns=self.train_set.columns.to_list()),
                                    }
        print("Model",model_name,"applied on train set")