from pathlib import Path
import pickle
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer
from xgboost import XGBRegressor
from sklearn.base import BaseEstimator, TransformerMixin

class Windsorizer(BaseEstimator, TransformerMixin):
    """_summary_

    Args:
        BaseEstimator (class): sklearn BaseEstimator
        TransformerMixin (class): _description_
    """
    def __init__(
        self,
        columns = None,
        clip_values = None,
        lower_percentile = .01,
        upper_percentile = .99
    ):
        """ Constructor for the Windsorizer"""
        self.lower_percentile = lower_percentile
        self.upper_percentile = upper_percentile
        self.columns = columns
        self.clip_values = clip_values

    def fit(self, data_in, y=None):
        if self.clip_values is None:
            self.clip_values = {}
        if self.columns is None:
            self.columns = data_in.columns.tolist()
        for col in self.columns:
            lower_value, upper_value = np.nanquantile(
                a = data_in[col],
                q =[self.lower_percentile, self.upper_percentile])
            boundaries = (lower_value, upper_value)
            self.clip_values[col] = self.clip_values.get(col, boundaries)
        return self

    def transform(self, data_in, y=None):

        transformed = data_in.copy()
        for col in self.columns:
            lower_value, upper_value = self.clip_values[col]
            transformed[col].clip(lower=lower_value, upper=upper_value, axis=0, inplace=True)
        return transformed


cwd = Path.cwd()
data = pd.read_csv(cwd/'src'/'data'/'processed'/'train.csv')
features = data.drop(columns=['target', 'symbol', 'calendarYear', 'filingDate'])
target = data.target

params = {
    'alpha': 0.005431704895799771,
    'colsample_bytree': 0.7063898876659078,
    'eta': 0.08220319061595308,
    'max_depth': 10,
    'min_child_weight': 58,
    'subsample': 0.9724863280502848
    }
xgb_pipe = Pipeline(
        steps = [
            ('feature_clipper', Windsorizer()),
            ('normalizer', PowerTransformer()),
            ('xgb', XGBRegressor(**params)),
        ])
xgb_pipe.fit(features, np.log(target))
with open(cwd/'src'/'model'/'my_model.pickle', 'wb') as f:
    pickle.dump(xgb_pipe, f)