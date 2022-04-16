# input features for modeling
input_features = [
    'symbol', # symbol of the ticker, needed for yoy calculations
    'calendarYear', # year of the financial statement, needed for yoy calcualtions
    # Balance Sheet
    # Current Assets
    'cashAndCashEquivalents', # YES
    'shortTermInvestments', # YES current marketable securities
    #'cashAndShortTermInvestments', NO, linear combination
    'netReceivables', # YES, accounts receivable + vendor non-trade receivables
    'inventory', # YES, products manufactured not yet sold
    'otherCurrentAssets', # NO
    #'totalCurrentAssets',
    'propertyPlantEquipmentNet', # YES, how capital intensive an industry is
    #'goodwill', # NO, not relevant to the functioning of a company
    'intangibleAssets', # YES
    #'goodwillAndIntangibleAssets', # NO linear combination
    'longTermInvestments', # YES, Marketable securities
    #'taxAssets', # NO
    'otherNonCurrentAssets', # YES
    #'totalNonCurrentAssets', # NO, linear combination
    #'otherAssets', # NO
    'totalAssets', # YES. Normalizer
    'accountPayables', # YES, goods the company has recieved and hasn't yet paid
    'shortTermDebt', # YES, Commercial paper and Term debt
    #'taxPayables', # NO, not relevant to the functioning of a company
    'deferredRevenue', # YES, subsriptions. Revenue the company has received withou haveing given teh service
    'otherCurrentLiabilities', # YES
    # 'totalCurrentLiabilities', # NO linear combination of other features
    'longTermDebt', # YES, debt longer than 12 months
    # 'deferredRevenueNonCurrent', # NO, sparse
    # 'deferredTaxLiabilitiesNonCurrent', NO
    'otherNonCurrentLiabilities', # YES
    # 'totalNonCurrentLiabilities',
    # 'otherLiabilities', # percentile 90 is 0
    # 'capitalLeaseObligations', 16% non-zero values
    # 'totalLiabilities', # linear combination
    # 'preferredStock',
    # 'commonStock',
    'retainedEarnings',
    # 'accumulatedOtherComprehensiveIncomeLoss',
    # 'othertotalStockholdersEquity',
    'totalStockholdersEquity',
    # 'totalLiabilitiesAndStockholdersEquity',
    # 'minorityInterest',
    # 'totalEquity',
    # 'totalLiabilitiesAndTotalEquity',
    # 'totalInvestments', # 30% 0
    'totalDebt', # Comercial paper + current&noncurrent debt
    # 'netDebt', # Recalculated to include Non-current Marketable Securities
    # Income
    'revenue',
    'costOfRevenue',
    'grossProfit',
    #'grossProfitRatio',
    'researchAndDevelopmentExpenses',
    # 'generalAndAdministrativeExpenses',
    # 'sellingAndMarketingExpenses',
    'sellingGeneralAndAdministrativeExpenses',
    #'otherExpenses', beyond normal operation of company
    # 'operatingExpenses',
    # 'costAndExpenses', Linear Combination
    # 'interestIncome',
    # 'interestExpense',
    'depreciationAndAmortization',
    'ebitda',
    # 'ebitdaratio',
    'operatingIncome', # EBIT
    # 'operatingIncomeRatio',
    # 'totalOtherIncomeExpensesNet',
    # 'incomeBeforeTax',
    # 'incomeBeforeTaxRatio',
    # 'incomeTaxExpense',
    'netIncome',
    # 'netIncomeRatio',
    # 'eps',
    # 'epsdiluted',
    # 'weightedAverageShsOut',
    # 'weightedAverageShsOutDil',
    #'date',
    #'reportedCurrency',
    #'cik',
    #'fillingDate',
    #'acceptedDate',
    #'period',
    # 'deferredIncomeTax',
    'stockBasedCompensation',
    'changeInWorkingCapital',
    # 'accountsReceivables',
    # 'accountsPayables',
    # 'otherWorkingCapital',
    # 'otherNonCashItems',
    # 'netCashProvidedByOperatingActivities', # Cash Flow From Operations
    # 'investmentsInPropertyPlantAndEquipment',
    'acquisitionsNet',
    'purchasesOfInvestments',
    # 'salesMaturitiesOfInvestments',
    # 'otherInvestingActivites',
    # 'netCashUsedForInvestingActivites', # Cash Flow From Investments
    # 'debtRepayment',
    'commonStockIssued',
    'commonStockRepurchased',
    'dividendsPaid',
    # 'otherFinancingActivites',
    # 'netCashUsedProvidedByFinancingActivities', # Cash Flow Financing
    'effectOfForexChangesOnCash',
    'netChangeInCash',
    # 'cashAtEndOfPeriod',
    # 'cashAtBeginningOfPeriod',
    # 'operatingCashFlow',
    'capitalExpenditure',
    'freeCashFlow',
    #'link',
    #'finalLink',
    #'month',
    #'inflationMultiplier',
    #'mcapDate',
    #'mcapYear',
    #'mcapWeek',
    'target',
 ]

to_billions_features = [
    # 'symbol',
    # 'calendarYear',
    'cashAndCashEquivalents',
    'shortTermInvestments',
    'cashAndShortTermInvestments',
    'netReceivables',
    'inventory',
    'otherCurrentAssets',
    'totalCurrentAssets',
    'propertyPlantEquipmentNet',
    'goodwill',
    'intangibleAssets',
    'goodwillAndIntangibleAssets',
    'longTermInvestments',
    'taxAssets',
    'otherNonCurrentAssets',
    'totalNonCurrentAssets',
    'otherAssets',
    'totalAssets',
    'accountPayables',
    'shortTermDebt',
    'taxPayables',
    'deferredRevenue',
    'otherCurrentLiabilities',
    'totalCurrentLiabilities',
    'longTermDebt',
    'deferredRevenueNonCurrent',
    'deferredTaxLiabilitiesNonCurrent',
    'otherNonCurrentLiabilities',
    'totalNonCurrentLiabilities',
    'otherLiabilities',
    'capitalLeaseObligations',
    'totalLiabilities',
    'preferredStock',
    'commonStock',
    'retainedEarnings',
    'accumulatedOtherComprehensiveIncomeLoss',
    'othertotalStockholdersEquity',
    'totalStockholdersEquity',
    'totalLiabilitiesAndStockholdersEquity',
    'minorityInterest',
    'totalEquity',
    'totalLiabilitiesAndTotalEquity',
    'totalInvestments',
    'totalDebt',
    'netDebt',
    'revenue',
    'costOfRevenue',
    'grossProfit',
    'grossProfitRatio',
    'researchAndDevelopmentExpenses',
    'generalAndAdministrativeExpenses',
    'sellingAndMarketingExpenses',
    'sellingGeneralAndAdministrativeExpenses',
    'otherExpenses',
    'operatingExpenses',
    'costAndExpenses',
    'interestIncome',
    'interestExpense',
    'depreciationAndAmortization',
    'ebitda',
    'ebitdaratio',
    'operatingIncome',
    'operatingIncomeRatio',
    'totalOtherIncomeExpensesNet',
    'incomeBeforeTax',
    'incomeBeforeTaxRatio',
    'incomeTaxExpense',
    'netIncome',
    'netIncomeRatio',
    'eps',
    'epsdiluted',
    'weightedAverageShsOut',
    'weightedAverageShsOutDil',
    # 'date',
    # 'reportedCurrency',
    # 'cik',
    # 'fillingDate',
    # 'acceptedDate',
    # 'period',
    'deferredIncomeTax',
    'stockBasedCompensation',
    'changeInWorkingCapital',
    'accountsReceivables',
    'accountsPayables',
    'otherWorkingCapital',
    'otherNonCashItems',
    'netCashProvidedByOperatingActivities',
    'investmentsInPropertyPlantAndEquipment',
    'acquisitionsNet',
    'purchasesOfInvestments',
    'salesMaturitiesOfInvestments',
    'otherInvestingActivites',
    'netCashUsedForInvestingActivites',
    'debtRepayment',
    'commonStockIssued',
    'commonStockRepurchased',
    'dividendsPaid',
    'otherFinancingActivites',
    'netCashUsedProvidedByFinancingActivities',
    'effectOfForexChangesOnCash',
    'netChangeInCash',
    'cashAtEndOfPeriod',
    'cashAtBeginningOfPeriod',
    'operatingCashFlow',
    'capitalExpenditure',
    'freeCashFlow',
    # 'link',
    # 'finalLink'
]
