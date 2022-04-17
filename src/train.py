from pathlib import Path
import pickle
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer
from xgboost import XGBRegressor
from utils.myclasses import Windsorizer

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
xgb_pipe.fit(features, target)
with open(cwd/'src'/'model'/'my_model.pickle', 'wb') as f:
    pickle.dump(xgb_pipe, f)