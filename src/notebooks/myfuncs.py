# -*- coding: utf-8 -*-
import json
import datetime
from urllib.request import urlopen
import requests
import pandas as pd
import numpy as np
import pandas_datareader.data as web
from scipy.stats import circmean
from fredapi import Fred
from mykeys import fred_key, fmp_key


def num_describe(data_in):
    data_out = data_in.describe([.01,.02,.98,.99]).T
    data_out = data_out.drop(columns='count')
    data_out['skewness'] = data_in.skew()
    data_out['kurtosis'] = data_in.kurtosis()
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