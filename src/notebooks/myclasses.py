import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class Winsorizer(BaseEstimator, TransformerMixin):
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


class FeatureSelector(BaseEstimator,TransformerMixin):
    def fit(self, data, y=None):
        return self
        
    def transform(self, data, y=None):
        return None