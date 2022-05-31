- [Overview](#overview)
- [Code and Resources](#code-and-resources)
- [Building a Database](#building-a-database)
  - [Tables Description](#tables-description)
  - [Data Gathering](#data-gathering)
  - [Data Cleaning](#data-cleaning)
  - [Future Developments](#future-developments)
- [Most Viable Model](#most-viable-model)
  - [EDA](#eda)
  - [Feature Engineering](#feature-engineering)
  - [Model Selection](#model-selection)
- [Production](#production)
  - [Self-Updating Processes](#self-updating-processes)
  - [Performance Monitoring](#performance-monitoring)
# Overview
# Code and Resources
**Python Version:** 3.8.10.  
**Packages:** numpy, pandas, scipy, matplotlib, seaborn, sklearn, xgboost, optuna, sqlalchemy, requests, pathlib, pickle, fredapi.  
**Data Sources:** [Securities Exchange Commission](https://www.sec.gov/edgar/searchedgar/companysearch.html) (SEC), Federal Reserve Bank of St. Louis (https://fred.stlouisfed.org/) (FRED), [Financial Modeling Prep API](https://site.financialmodelingprep.com/developer/docs/), Wikipedia.  
# Building a Database
## Tables Description
The result of all the gathering and cleaning processes are a series of tables, deployed to a database via PostgreSQL:
1. A table with information on all **unique historical constituents** of the SP500 since 1996 such as trading symbol (primary key), company name, sector, subsector, date it was founded, if its currently in the index, etc.
2. Table with the start and end date of **each constituent stay** in the index. The main columns are symbol, start date and end date. The primary key of this table is an id which is a concatenation of the `symbol` and `date_added` columns.
3. Yearly (10K) Financial Statements of all constituents. The primary keys are the symbol and the year. The columns are the features which make up a company's balance sheet, income statement and cash flow statement.
4. Daily Market Capitalization of all constituents. The primary keys are date and symbol.
5. Economic conditions of the US economy since 1996. The primary key is the date, includes variables related to interest rates, consumption, commodities and prices.
## Data Gathering
- Scrapped the current constituents and former constituents from Wikipedia.
- Got a list of the daily symbols since 1996 from [Here](https://www.followingthetrend.com/trading-evolved/)
- Gathered the CIK keys from the SEC.
- Called the Balance Sheet, Cash Flow and Income Statements API endpoints for every symbol gathered from Wikipedia.
- Called the Daily Market Cap API endpoint as well.
- Called the Federal Reserve of Saint Louis API to get all the relevant economic series.
- Called the SEC Fillings API to get the filling dates of the 10k Statements.
## Data Cleaning
- 
## Future Developments
- Refactor everything.
- Change primary keys to SEC [Central Index Key](https://en.wikipedia.org/wiki/Central_Index_Key)
- Get a more complete (and hopefully not too expensive) API. Right now only 609 of the 1000 constituents since 1996 have financial statements data, making the model biased towards successful companies.
# Most Viable Model
The Most Viable Model used is based on the [XGBoost Library](https://xgboost.ai) because it is a compromise between sufficient complexity (an ensemble of decision trees with regularization) and interpretability (returns a feature importance based on information gain)
## EDA
## Feature Engineering
## Model Selection
![Results](https://github.com/FranciscoPala/SP500_constituents_market_cap_estimator/blob/master/readme_figures/xgb_zoomed.jpg)
# Production
## Self-Updating Processes
## Performance Monitoring