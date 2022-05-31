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
    - [Best Estimator Results](#best-estimator-results)
    - [Feature Importance](#feature-importance)
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
- Created a process that, given all symbols each day since 1996, extracts information on historical constituents and their stay in the index table.
- Used information from the SEC filing dates to determine whether duplicate and other inconsistencies in 10K statements were due to amendments (10-K405 form) or change in fiscal (10-KT form).
- Concatenated the Balance Sheet, Cash Flo and Income Statements of all symbols for the dates they were in the index.
- Merged all if the above on symbol and calendar year to generate the Statements DataFrame
- Dropped duplicated columns
- Converted to Billions all currency features
- Used Core PCE to generate an inflation multiplier and adjusted all historical prices to current prices.
- For each symbol + filing date in the statement generated the target variable by: calculating the simple moving average of the daily market cap 10 days after the filing date and joining it with the filing date. Also did it for the weekly average in case there wasn't a measurement for the SMA10 on the filing date + 10 days.
- Adjusted the target variable to inflation
- Dropped null observations
- Used yoy increases in key variables like totalAssets or MarketCap to identify measurement errors in the data. Dropped the identified observations.
- Joined the economic situation variables on date. For weekly/monthly/quarterly data interpolated the missing values.
- Joined Economic situation data with the financial statements on filing date
## Future Developments
- Refactor everything.
- Change primary keys to SEC [Central Index Key](https://en.wikipedia.org/wiki/Central_Index_Key). This essential because sometimes companies will change their name and ticker but their CIK will remain. I couldn't however find a comprehensive list of all tickers and would need to do the research for about 400 of them manually.
- Get a more complete (and hopefully not too expensive) API. Right now only 609 of the 1000 constituents since 1996 have financial statements data, making the model biased towards successful companies.
- Upload everything to AWS RDS in postgreSQL and create the updating processes
# Most Viable Model
The Most Viable Model used is based on the [XGBoost Library](https://xgboost.ai) because it is a compromise between sufficient complexity (an ensemble of decision trees with regularization) and interpretability (returns a feature importance based on information gain)
## EDA
- Given the amount of modeling features (147) assessed the data programmatically by creating a function which, for every numerical feature, returns sparsity, kurtosis, skeweness, mean, standard deviation, and percentiles 0, 1, 2, 50, 98, 99, 100.
- To correct for extreme kurtosis values winsorization (if percentiles 1-99) was needed (extreme tails relative to the iqr due to measurement errors). Created a Winsorizer class which inherits from sklearn BaseEstimar and TransformerMixin.
- To correct for skeweness and normalize the features a yeo-johnson transformation was implemented using sklearn PowerTransformer class.
- Log transformed the target.
<br>

**Example of high asymmetry and wide tails for the revenue variable**

![Example of revenue Variable](https://github.com/FranciscoPala/SP500_constituents_market_cap_estimator/blob/master/readme_figures/revenue.png)
## Feature Engineering
- 
## Model Selection

[ModelsHeatmap](https://github.com/FranciscoPala/SP500_constituents_market_cap_estimator/blob/master/readme_figures/corr_modelos.jpg)
### Best Estimator Results
<br>

![Results](https://github.com/FranciscoPala/SP500_constituents_market_cap_estimator/blob/master/readme_figures/xgb_zoomed.jpg)
### Feature Importance
- The PreviousYearMarketCap feature adds up to ~50% of the average gain. It has been excluded for visualization purposes.
![Importances](https://github.com/FranciscoPala/SP500_constituents_market_cap_estimator/blob/master/readme_figures/importances_no_mcap.jpg)
# Production
## Self-Updating Processes
## Performance Monitoring