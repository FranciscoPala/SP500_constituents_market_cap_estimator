# -*- coding: utf-8 -*-
import json
import datetime
import requests
import pandas as pd
import numpy as np
import pandas_datareader.data as web
import optuna
from urllib.request import urlopen
from scipy.stats import circmean
from fredapi import Fred
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer
from sklearn.linear_model import LinearRegression
from sklearn.svm import LinearSVR, SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFE
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error, 
    r2_score,
)
from mykeys import fred_key, fmp_key


def init_companies_table():
    """Wrapper for one time initializer of the creation of the unique historical
    constituents table

    Returns:
        companies: pd.DataFrame representing the initial state of the table
    """
    # read wikipedia table data & basic formatting
    current_companies = pd.read_csv('../data/raw/companies_wiki.csv')
    current_companies = current_companies.drop(columns='SEC filings')
    colnames = [
        'symbol',
        'name',
        'sector',
        'subSector',
        'hq',
        'dateFirstAdded',
        'cik',
        'founded',
    ]
    current_companies.columns = colnames
    # read time series table with constituents and convert to list
    companies_ts = pd.read_csv('../data/raw/historical_companies_TradingEvolved.csv')
    companies_ts['tickers_filtered'] = companies_ts.tickers.str.split(',')
    # get all unique constituents
    results = set()
    companies_ts.tickers_filtered.apply(results.update)
    companies = pd.DataFrame(data = results, columns = ['symbol'])
    # merge both tables
    current_companies['currentConstituent'] = True
    companies = companies.merge(current_companies, how='left')
    companies = companies.drop(columns=['dateFirstAdded'])
    companies.currentConstituent = companies.currentConstituent.fillna(False)
    # add ciks to the symbols from the time series
    ciks = pd.read_csv('../data/raw/CIK.csv', index_col = 0)
    ciks.columns = ['cik_sec_list', 'symbol', 'title']
    companies = companies.merge(ciks, how='left')
    companies.name = companies.name.fillna(companies.title)
    companies.cik = companies.cik.fillna(companies.cik_sec_list)

    return companies



def init_stays_table():
    return None


def init_statements_table():
    return None


def generate_features(data):
    """Generates features from input data

    Args:
        data (pd.DataFrame): _input data

    Returns:
        pd.DataFrame: Datafraeme with the features
    """
    # sort for increases
    data = data.sort_values(by=['symbol', 'calendarYear'])
    # pd.DataFrame to return
    features = pd.DataFrame()
    # target
    features['target'] = data.target
    # needed for increases & check results
    features['symbol'] = data.symbol
    features['calendarYear'] = data.calendarYear
    features['fillingDate'] = data.fillingDate
    # add .000001 to denominators
    data['totalAssets'] = data.totalAssets + 0.001001
    data['revenue'] = data.revenue + 0.001001
    data['freeCashFlow'] = data.freeCashFlow + 0.001001
    data['ebitda'] = data.ebitda + 0.001001
    data['totalStockholdersEquity'] = data.totalStockholdersEquity + 0.001001

    # Economic Conditions
    economic_features = [
        'brent',
        'chicagoFedFinancialConditions',
        'consumerSentiment',
        'corePCE',
        'GDP',
        'interest10Y',
        'interest10Y3M',
        'interest10YIInflationAdjusted',
        'interest20Y',
        'interest3M',
        'inventorySalesRatio',
        'leadingIndex',
        'monthlySupplyHouses',
        'moodysAaa20Y',
        'moodysBaa20Y',
        'mortgage30Y',
        'nasdaq',
        'stlouisFredFinancialStress',
        'unemployment',
        'volatility',
        'wilshire5000',
        'wti'
    ]
    for col in economic_features:
        features[col] = data[col]
    # Growth
    for col in economic_features:
        yoy_name = col + 'YearOverYear'
        features[yoy_name] = features.groupby('symbol')[col].pct_change(1)
    # Trend
    for col in economic_features:
        trend_name = col + 'SMA3'
        features[trend_name] = features.groupby('symbol', as_index=False)[col].rolling(window=3, min_periods=1).mean()[col]

    # Mcap Features
    features['previousMarketCap'] = data.groupby('symbol')['target'].shift(1)
    # companies with only 1 year
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'MRNA'), 'previousMarketCap'] = 58.56302555472
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'NXPI'), 'previousMarketCap'] = 53.11789218
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'TRMB'), 'previousMarketCap'] = 18.495856
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'CRL'), 'previousMarketCap'] = 14.03994341
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'PTC'), 'previousMarketCap'] = 11.4132228607542
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'SEDG'), 'previousMarketCap'] = 13.5400336411
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'MTCH'), 'previousMarketCap'] = 45.5847188219078
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'ENPH'), 'previousMarketCap'] = 26.752206558546
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'PENN'), 'previousMarketCap'] = 18.192836484350003
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'MPWR'), 'previousMarketCap'] = 17.6892658073466
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'BRO'), 'previousMarketCap'] = 12.5013695457742
    features.loc[(features.calendarYear == 2021) & (features.symbol == 'EPAM'), 'previousMarketCap'] = 22.005622872
    features['previousMarketCap'].fillna(method='bfill', inplace=True)
    features['targetYoY'] = features.groupby('symbol')['target'].pct_change(1)

    # Absolute Values
    features['totalAssets'] = data.totalAssets
    true_cash = data.cashAndCashEquivalents + data.shortTermInvestments + data.longTermInvestments
    total_debt = data.shortTermDebt  + data.longTermDebt
    features['netDebt'] = (total_debt - true_cash)
    features['revenue'] = data.revenue
    features['freeCashFlow'] = data.freeCashFlow
    # Absolute Values Growth
    features['revenueYoY'] = features.groupby('symbol')['revenue'].pct_change(1)
    features['revenueYoYSMA3'] = features.groupby('symbol', as_index=False)['revenueYoY'].rolling(window=3, min_periods=1).mean()['revenueYoY']
    features['netDebtYoY'] = features.groupby('symbol')['netDebt'].pct_change(1)
    features['netDebtYoYSMA3'] = features.groupby('symbol', as_index=False)['netDebtYoY'].rolling(window=3, min_periods=1).mean()['netDebtYoY']
    features['freeCashFlowYoY'] = features.groupby('symbol')['freeCashFlow'].pct_change(1)
    features['freeCashFlowYoYSMA3'] = features.groupby('symbol', as_index=False)['freeCashFlowYoY'].rolling(window=3, min_periods=1).mean()['freeCashFlowYoY']
    
    # Balance Ratios
    balance_features = [
        # Assets
        'cashAndCashEquivalents',
        'shortTermInvestments',
        'netReceivables',
        'inventory',
        'otherCurrentAssets',
        'propertyPlantEquipmentNet',
        'intangibleAssets',
        'longTermInvestments',
        'otherNonCurrentAssets',
        # Liabilities
        'accountPayables',
        'shortTermDebt',
        'deferredRevenue',
        'otherCurrentLiabilities',
        'longTermDebt',
        'otherNonCurrentLiabilities',
        # Equity
        'retainedEarnings',
        'totalStockholdersEquity',
    ]
    # Balance Vertical (ratio to Total Assets)
    for col in balance_features:
        feature_name = col+'ToAssets'
        features[feature_name] = data[col]/data.totalAssets
    # Aditional Balance Ratios
    true_cash = data.cashAndCashEquivalents + data.shortTermInvestments + data.longTermInvestments
    total_debt = data.shortTermDebt  + data.longTermDebt
    features['netDebtToAssets'] = (total_debt - true_cash) / data.totalAssets
    
    # Income Ratios
    income_features = [
        'costOfRevenue',
        'researchAndDevelopmentExpenses',
        'sellingGeneralAndAdministrativeExpenses',
        'ebitda',
        'operatingIncome',
        'netIncome',
    ]
    for col in income_features:
        feature_name = col+'ToRevenue'
        features[feature_name] = data[col]/data.revenue
    # Income Horizontal
    for col in income_features:
        colname = col+'ToRevenue'
        yoy_name = colname + 'YearOverYear'
        features[yoy_name] = features.groupby('symbol')[colname].pct_change(1)
    # Income Trend
    for col in income_features:
        colname = col+'ToRevenueYearOverYear'
        trend_name = colname + 'SMA3'
        features[trend_name] = features.groupby('symbol', as_index=False)[colname].rolling(window=3, min_periods=1).mean()[colname]

    # Cash Flow Ratios
    cflow_features = [
        'stockBasedCompensation',
        'depreciationAndAmortization',
        'changeInWorkingCapital',
        'freeCashFlow',
        'capitalExpenditure',
        'acquisitionsNet',
        'purchasesOfInvestments',
        'dividendsPaid',
    ]
    # Cash Flow Vertical
    for col in cflow_features:
        feature_name = col+'ToRevenue'
        features[feature_name] = data[col]/data.revenue
    # Aditional Cash Flow Ratios
    net_shares = abs(data.commonStockRepurchased) - data.commonStockIssued
    features['netSharesRepurchasedToRevenue'] = net_shares/data.revenue
    # Cash Flow Horizontal
    for col in cflow_features:
        colname = col+'ToRevenue'
        yoy_name = colname + 'YearOverYear'
        features[yoy_name] = features.groupby('symbol')[colname].pct_change(1)
    # Cash Flow Trend
    for col in cflow_features:
        colname = col+'ToRevenueYearOverYear'
        trend_name = colname + 'SMA3'
        features[trend_name] = features.groupby('symbol', as_index=False)[colname].rolling(window=3, min_periods=1).mean()[colname]

    # Mixed Values
    features['freeCashFlowGivenToShareholders'] = (net_shares + abs(data.dividendsPaid)) / data.freeCashFlow # careful negative cash flow issuing stock
    features['PPEtoSales'] = data.propertyPlantEquipmentNet / data.revenue
    features['netDebtToEBITDA'] = (data.totalDebt - true_cash) / data.ebitda
    features['roe'] = data.netIncome / data.totalStockholdersEquity
    
    # cleaning before return
    # infinity to NaN
    features.replace([np.inf, -np.inf], np.nan, inplace=True)
    # null policy: set to 0
    features = features.fillna(0)
    return features


def num_describe(data_in):
    """returns a better vesion of describe

    Args:
        data_in (pd.DataFrame): input pandas DataFrame

    Returns:
        pd.DataFrame: output dataframe
    """
    # get extra percentiles
    data_out = data_in.describe([.01,.02,.98,.99]).T
    data_out = data_out.drop(columns='count')
    data_out.insert(0,'skewness', data_in.skew())
    data_out.insert(0,'kurtosis', data_in.kurtosis())
    data_out.insert(0,'sparsity', (data_in==0).sum()/len(data_in))
    data_out.insert(0,'nulls', (data_in.isna()).sum()/len(data_in))
    return data_out


def get_fred(series_name, alt_name=''):
    fred = Fred(api_key=fred_key)
    data = fred.get_series(series_name)
    data = data.reset_index()
    if len(alt_name) == 0:
        data.columns = ['date', series_name]
    else:
        data.columns = ['date', alt_name]
    data['date'] = pd.to_datetime(data['date'])
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['day'] = data['date'].dt.day
    return data


def get_fred_pdr(series_names, year = 1980):
    """Gets the ser"""
    start = datetime.datetime(year, 1, 1)
    end = datetime.date.today()

    for i, name in enumerate(series_names):
        if i == 0:
            df = web.DataReader(name, data_source = 'fred', start=start, end = end)
        else:
            series = web.DataReader(name, data_source = 'fred', start=start, end = end)
            df = pd.concat([df, series], axis = 1)
    return df


def get_submissions(CIK):
    # reformat CIK
    submissions_key = '{:010d}'.format(CIK)
    # API adress
    url = 'https://data.sec.gov/submissions/CIK{}.json'.format(submissions_key)
    headers = {
        'User-Agent': 'Freelance data scientist testing the API for learning purposes. francisco.palab@gmail.com',
        }
    # request get
    r = requests.get(url, headers=headers)
    r.encoding = 'UTF-8'
    data_json = json.loads(r.content)
    # last 1000 submissions to a dict
    data = data_json['filings']['recent']
    # for every older filing
    for older_filing in data_json['filings']['files']:
        # generate its url
        url = 'https://data.sec.gov/submissions/' + older_filing['name']
        # request get
        r = requests.get(url, headers=headers)
        r.encoding = 'UTF-8'
        older_json = json.loads(r.content)
        # extend json
        for key,list_values in data.items():
            list_values.extend(older_json.get(key, []))
    return data


def call_fmp_api(endpoint, ticker=None, periods=None):
    """"""
    def get_jsonparsed_data(url):
        response = urlopen(url)
        data = response.read().decode("utf-8")
        return json.loads(data)
    # open json with urls
    with open('./urls.json', 'rb') as f:
        urls = json.load(f)
    # get the url from the endpoint
    url = urls['fmp'][endpoint].format(ticker, periods, fmp_key)
    data_json = get_jsonparsed_data(url)  
    df = pd.DataFrame(data_json)
    return df


def dates_processing(df, *date_colnames):
    """
    """
    # convert dates to numbers
    for colname in date_colnames:
        # new feature names
        num_colname = colname + '_int'
        month_colname = colname + '_month'
        year_colname = colname + '_year'
        yday_colname = colname + '_yday'
        # create new features
        # convert to datetime
        df.loc[:, colname] = pd.to_datetime(df.loc[:,colname])
        # changes date to int as yyyymmdd
        df.loc[:, num_colname] = df[colname].dt.strftime("%Y%m%d").astype(int)
        # extract the month as int
        df.loc[:, month_colname] = df[colname].dt.month
        # extract year as int
        df.loc[:, year_colname] = df[colname].dt.year
        # estract day of year
        df.loc[:, yday_colname] = df[colname].dt.dayofyear
        df.loc[:, yday_colname] = np.clip(df.loc[:, yday_colname], a_min=1, a_max=365)
    return df


def grouped_circmean(df, column, low, high, levels):
    """Implementation of a groupby and circmean for a column"""
    # calculate the circular mean of the yday for each symbol and period using scipy
    cir_mean = lambda x: circmean(x, high = high, low=low)
    df_means = df.groupby(levels)[column].apply(cir_mean).reset_index()
    dict_means = df_means.pivot(levels[:-1], levels[-1], column).to_dict('index')
    return dict_means


def circ_distance(value_1, value_2, low, high):
    """Returns distance bweteen two cyclical values

    Args:
        value_1 (int,float): first value
        value_2 (int,float): second value
        low (int,float): _description_
        high (int,float): _description_

    Returns:
        float: distance between two values
    """
    # minmax scale to 0-2pi rad
    value_1_rad = ((value_1-low)/(high-low))*(2*np.pi)
    value_2_rad = ((value_2-low)/(high-low))*(2*np.pi)
    # sin and cos for coordinates in the unit circle 
    sin_value_1, cos_value_1 = np.sin(value_1_rad), np.cos(value_1_rad)
    sin_value_2, cos_value_2 = np.sin(value_2_rad), np.cos(value_2_rad)
    # dot product is the arccos of alpha
    angle = np.arccos(np.dot([cos_value_1, sin_value_1],[cos_value_2, sin_value_2]))
    # convert back to initial units
    angle = angle*(high-low)/(2*np.pi) + low
    # return distance
    return round(angle,3)


def infer_period(symbol_observation, yday_observation, ref_dict):
    """Infers the period of an observation based on the distance to the average 
    yearday for each period for each symbol
    """
    # the maximum possible distance is 365 days
    best_distance = 365
    # infered period defaults to nan
    infered_period = np.nan
    # check with the dicitonary of references
    for period,value in ref_dict[symbol_observation].items():
        # get the circular distance between the two days
        distance = circ_distance(yday_observation, value, 0, 365)
        if distance < best_distance:
            # update best distance with the best new value
            best_distance = distance
            # update infered period with its coresponding period
            infered_period = period
    return infered_period


def print_regression_metrics(model, X_train, X_test, y_train, y_test):
    train_preds = model.predict(X_train)
    test_preds = model.predict(X_test)
    # mean absolute error
    print('train mae: ', mean_absolute_error(y_true=y_train, y_pred=train_preds))
    print('test mae: ', mean_absolute_error(y_true=y_test, y_pred=test_preds))
    # mean sqared error
    print('train mse: ', mean_squared_error(y_true=y_train, y_pred=train_preds))
    print('test mse: ', mean_squared_error(y_true=y_test, y_pred=test_preds))
    # r2
    print('train r2: ', r2_score(y_true=y_train, y_pred=train_preds))
    print('test r2: ', r2_score(y_true=y_test, y_pred=test_preds))
    return None


def do_linear_regression(pipe, X_train, X_test, y_train, y_test=None):
    pipe.steps.append(('linear_regression', LinearRegression()))
    pipe.fit(X_train, y_train)
    preds_test = pipe.predict(X_test)
    preds_train = pipe.predict(X_train)
    mse_test = mean_squared_error(y_true=np.exp(y_test), y_pred=np.exp(preds_test))
    mse_train = mean_squared_error(y_true=np.exp(y_train), y_pred=np.exp(preds_train))
    print('mse train:', mse_train)
    print('mse test: ', mse_test)
    print('rmse test: ', np.sqrt(mse_test))


def do_poly_regression(pipe, X_train, X_test, y_train, y_test=None, degree = 2):
    pipe.steps.append(('poly_transform', PolynomialFeatures(degree=degree)))
    pipe.steps.append(('regression', LinearRegression()))
    pipe.fit(X_train, y_train)
    preds_test = pipe.predict(X_test)
    preds_train = pipe.predict(X_train)
    mse_test = mean_squared_error(y_true=np.exp(y_test), y_pred=np.exp(preds_test))
    mae_test = mean_absolute_error(y_true=np.exp(y_test), y_pred=np.exp(preds_test))
    mse_train = mean_squared_error(y_true=np.exp(y_train), y_pred=np.exp(preds_train))
    print('mse train:', mse_train)
    print('mse test: ', mse_test)
    print('mae test: ', mae_test)
    print('rmse test: ', np.sqrt(mse_test))
    return pipe


def do_linear_svm_regression(pipe, X_train, X_test, y_train, y_test=None):
    pipe.steps.append(('linear_svm', LinearSVR(C=0.02, max_iter=1000)))
    pipe.fit(X_train, y_train)
    preds_test = pipe.predict(X_test)
    preds_train = pipe.predict(X_train)
    mse_test = mean_squared_error(y_true=np.exp(y_test), y_pred=np.exp(preds_test))
    mse_train = mean_squared_error(y_true=np.exp(y_train), y_pred=np.exp(preds_train))
    print('mse train:', mse_train)
    print('mse test: ', mse_test)
    print('rmse test: ', np.sqrt(mse_test))


def do_svm_regression(pipe, C, epsilon, X_train, X_test, y_train, y_test=None):
    pipe.steps.append(('rbf_svm', SVR(kernel = 'rbf', C=C, epsilon=epsilon)))
    pipe.fit(X_train, y_train)
    preds_test = pipe.predict(X_test)
    preds_train = pipe.predict(X_train)
    mse_test = mean_squared_error(y_true=np.exp(y_test), y_pred=np.exp(preds_test))
    mse_train = mean_squared_error(y_true=np.exp(y_train), y_pred=np.exp(preds_train))
    print('mse train:', mse_train)
    print('mse test: ', mse_test)
    print('rmse test: ', np.sqrt(mse_test))
    return pipe


def do_neighbors(X_train, X_test, y_train, y_test=None):
    def objective(trial):
        n_features_to_select = trial.suggest_int("n_features_to_select", 1, 10)
        knn_params = {
            "n_neighbors": trial.suggest_int("n_neighbors", 1, 10),
        }
        pipe = Pipeline(steps=[
            ('RFE', RFE(estimator = LinearRegression(), n_features_to_select=n_features_to_select)),
            ('KNN', KNeighborsRegressor(**knn_params)),
        ])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        mae = mean_absolute_error(y_true=np.exp(y_test), y_pred=np.exp(preds))
        return mae
    minutes = 10
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, timeout=(60*minutes))
    results = study.trials_dataframe()
    return results, study


def search_forest(X_train, X_test, y_train, y_test):
    def objective(trial):
        params={
            "min_samples_leaf": trial.suggest_float("min_samples_leaf", 1e-4, 0.1, log=True),
            "min_samples_split": trial.suggest_float("min_samples_split", 1e-4, 0.1, log=True),
            "max_depth" : trial.suggest_int("max_depth", 5, 10),
            }
        pipe = Pipeline(steps=[
            ('scaler', PowerTransformer()),
            ('forest', RandomForestRegressor(**params)),
            ])
        pipe.fit(X_train,y_train)
        preds = pipe.predict(X_test)
        mae = mean_absolute_error(y_true=np.exp(y_test), y_pred=np.exp(preds))
        return mae
    minutes = 10
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, timeout=(60*minutes))
    results = study.trials_dataframe()
    return results, study


def search_boosting(pipe, X_train, X_test, y_train, y_test):
    def objective(trial):
        params={
            "objective": "reg:squarederror",
            "eval_metric": "rmse",
            "booster": "gbtree",
            "min_child_weight": trial.suggest_int("min_child_weight", 20, 500),
            "alpha": trial.suggest_float("alpha", 1e-6, 1.0, log=True),
            "max_depth" : trial.suggest_int("max_depth", 5, 10),
            "colsample_bytree" : trial.suggest_float("colsample_bytree", 0.4, 1),
            "subsample" : trial.suggest_float("subsample", 0.5, 1),
            "eta" : trial.suggest_float("eta", 1e-2, 0.2, log=True)
            }
        pipe = Pipeline(steps=[
            ('scaler', PowerTransformer()),
            ('xgb', xgboost.XGBRegressor(**params)),
            ])
        pipe.fit(X_train,y_train)
        preds = pipe.predict(X_test)
        mae = mean_absolute_error(y_true=np.exp(y_test), y_pred=np.exp(preds))
        return mae

    minutes = 10
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, timeout=(60*minutes))
    results = study.trials_dataframe()
    return results, study
