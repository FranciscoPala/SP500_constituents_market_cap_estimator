# -*- coding: utf-8 -*-
from urllib.request import urlopen
from scipy.stats import circmean
import requests
import json
import pandas as pd
import datetime
import pandas_datareader.data as web
from fredapi import Fred
from keys import fred_key, fmp_key


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


def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def call_fmp_api(endpoint, ticker=None, periods=None):
    """Calls the financial modeling prep API.
    
    Args:
        endpoint: possible endpoints.
        'income_quarterly', 'income_yearly', 'income_yoy',
        'balance_quarterly', 'balance_yearly', 'income_yoy'
        'cflow_quarterly', 'cflow_yearly', 'cflow_yoy'
        'metrics_quarterly'
        'market_cap'
        ticker: company ticker
        periods: if rquired, number of periods to get
    """

    # Income Statements
    if endpoint == 'income_quarterly':
       url ="https://financialmodelingprep.com/api/v3/income-statement/{}?period=quarter&limit={}&apikey={}".format(ticker, periods, fmp_key)
    elif endpoint == 'income_yearly':
       url ="https://financialmodelingprep.com/api/v3/income-statement/{}?limit={}&apikey={}".format(ticker, periods, fmp_key)
    elif endpoint == 'income_yoy':
       url ="https://financialmodelingprep.com/api/v3/income-statement-growth/{}?limit={}&apikey={}".format(ticker, periods, fmp_key)
    # Balance Sheet
    elif endpoint == 'balance_quarterly':
        url ="https://financialmodelingprep.com/api/v3/balance-sheet-statement/{}?period=quarter&limit={}&apikey={}".format(ticker, periods, fmp_key)
    elif endpoint == 'balance_yearly':
        url ="https://financialmodelingprep.com/api/v3/balance-sheet-statement/{}?limit={}&apikey={}".format(ticker, periods, fmp_key)
    elif endpoint == 'balance_yoy':
        url ="https://financialmodelingprep.com/api/v3/balance-sheet-statement-growth/{}?limit={}&apikey={}".format(ticker, periods, fmp_key)
    # Cash Flow 
    elif endpoint == 'cflow_quarterly':
        url = "https://financialmodelingprep.com/api/v3/cash-flow-statement/{}?period=quarter&limit={}&apikey={}".format(ticker, periods, fmp_key)
    elif endpoint == 'cflow_yearly':
        url ="https://financialmodelingprep.com/api/v3/cash-flow-statement/{}?limit={}&apikey={}".format(ticker, periods, fmp_key)
    elif endpoint == 'cflow_yoy':
        url ="https://financialmodelingprep.com/api/v3/cash-flow-statement-growth/{}?limit={}&apikey={}".format(ticker, periods, fmp_key)
    # Metrics
    elif endpoint == 'metrics_quarterly':
        url = "https://financialmodelingprep.com/api/v3/key-metrics/{}?period=quarter&limit={}&apikey={}".format(ticker, periods, fmp_key)
    # Daily Market Cap
    elif endpoint == 'market_cap':
        url = url = "https://financialmodelingprep.com/api/v3/historical-market-capitalization/{}?limit={}&apikey={}".format(ticker, periods, fmp_key)
    data_json = get_jsonparsed_data(url)  
    df = pd.DataFrame(data_json)
    return df


def check_duplicates(df, colnames):
    """Checks for duplicates along a list of columns and returns the dataframe with all the duplicates"""
    mask = df[colnames].duplicated(keep=False)
    return df[mask]


def explore_numerical(df):
    """Given a list of features, returns an exploration of its moset relevant 
    features"""
    features = df.select_dtypes(include=['int', 'float']).columns
    return_data = []
    for feature in features:
        # nulls
        nulls = df[feature].isna().sum()
        # null pct
        nulls_pct = nulls/df.shape[0]
        # notna mask
        notna = df[feature].notna()
        # distribution
        min = df.loc[notna,feature].min()
        max = df.loc[notna,feature].max()
        p5 = df.loc[notna,feature].quantile(0.05)
        p4 = df.loc[notna,feature].quantile(0.04)
        p3 = df.loc[notna,feature].quantile(0.03)
        p2 = df.loc[notna,feature].quantile(0.02)
        p1 = df.loc[notna,feature].quantile(0.01)
        p95 = df.loc[notna,feature].quantile(0.95)
        p96 = df.loc[notna,feature].quantile(0.96)
        p97 = df.loc[notna,feature].quantile(0.97)
        p98 = df.loc[notna,feature].quantile(0.98)
        p99 = df.loc[notna,feature].quantile(0.99)
        mean = df.loc[notna,feature].mean()
        median = df.loc[notna,feature].median()
        std = df.loc[notna,feature].std()
        var = df.loc[notna, feature].var()
        # append everything to data
        return_data.append([
            nulls,
            nulls_pct,
            min,
            p1,
            p2,
            p3,
            p4,
            p5,
            mean,
            median,
            p95,
            p96,
            p97,
            p98,
            p99,
            max,
            std,
            var,
        ])
    index = [
        'nulls',
        'nulls_pct',
        'min',
        '1%',
        '2%',
        '3%',
        '4%',
        '5%',
        'mean',
        'median',
        '95%',
        '96%',
        '97%',
        '98%',
        '99%',
        'max',
        'std',
        'var',
        ]
    # create a DataFrame fro all computations
    return pd.DataFrame(return_data, columns=index, index=features)


def check_duplicates(df, colnames):
    """Checks for duplicates along a list of columns and returns the dataframe with all the duplicates"""
    mask = df[colnames].duplicated(keep=False)
    return df[mask]


def dates_processing(df, *date_colnames):
    """Converts date columns to number and extracts month info.
    
    Keyword Arguments:
    df -- dataframe to manipulate
    date_colnames -- names of the columns to manipulate
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


def circ_distance(v1, v2, low, high):
    """Returns absolut distance between two cyclical values. Seems to work 
    buut double check
    """
    # minmax scale to 0-2pi rad
    v1_rad = ((v1-low)/(high-low))*(2*np.pi)
    v2_rad = ((v2-low)/(high-low))*(2*np.pi)
    # sin and cos for coordinates in the unit circle 
    sin_v1, cos_v1 = np.sin(v1_rad), np.cos(v1_rad)
    sin_v2, cos_v2 = np.sin(v2_rad), np.cos(v2_rad)
    # dot product is the arccos of alpha
    angle = np.arccos(np.dot([cos_v1, sin_v1],[cos_v2, sin_v2]))
    # convert back to initial units
    angle = angle*(high-low)/(2*np.pi) + low
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