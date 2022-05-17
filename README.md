- [Market Capitalization Estimator for the Constituents on the SP500](#market-capitalization-estimator-for-the-constituents-on-the-sp500)
  - [Overview](#overview)
  - [Code and Resources](#code-and-resources)
  - [Building a Database](#building-a-database)
    - [Data Gathering](#data-gathering)
      - [API Endpoints](#api-endpoints)
      - [Web Scrapping](#web-scrapping)
    - [Data Cleaning](#data-cleaning)
      - [Tables Description](#tables-description)
    - [ER Diagram](#er-diagram)
  - [Model Build](#model-build)
    - [EDA](#eda)
    - [Feature Engineering](#feature-engineering)
    - [Performance Metrics](#performance-metrics)
    - [Model Selection](#model-selection)
  - [Production](#production)
    - [Database Update](#database-update)
    - [Performance Monitoring](#performance-monitoring)
# Market Capitalization Estimator for the Constituents on the SP500
## Overview
## Code and Resources
**Python Version:** 3.8.10.  
**Packages:** numpy, pandas, scipy, matplotlib, seaborn, sklearn, xgboost, optuna, sqlalchemy, requests, pathlib, pickle, fredapi.  
**Data Sources:** Securities Exchange Commission, Federal Reserve Bank of St. Louis, Financial Modeling Prep, Wikipedia.  
## Building a Database
Relational database in PostrgreSQL with information on:
- Unique historical constituents since 1996.
- Dates those constituents were on the SP500.
- Yearly (10K) Financial Statements of said constituents.
- Daily Market Capitalization of said constituents.
- Economic conditions of the US economy since 1996.
### Data Gathering

#### API Endpoints
#### Web Scrapping
### Data Cleaning
- Joined 
#### Tables Description
### ER Diagram
## Model Build
### EDA
### Feature Engineering
### Performance Metrics
### Model Selection
## Production
### Database Update
### Performance Monitoring