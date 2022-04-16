import numpy as np
import pandas as pd
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


class FeatureGenerator(BaseEstimator,TransformerMixin):
    def fit(self, data, y=None):
        return self
        
    def transform(self, data, y=None):
        features = pd.DataFrame()
        # add .000001 to denominators
        data['totalAssets'] = data.totalAssets + 0.001001
        data['totalDebt'] = data.totalDebt + 0.001001
        data['revenue'] = data.revenue + 0.001001
        data['freeCashFlow'] = data.freeCashFlow + 0.001001
        data['ebitda'] = data.ebitda + 0.001001
        data['totalStockholdersEquity'] = data.totalStockholdersEquity + 0.001001

        # Assets
        features['cashAndEquivalentsToAssets'] = data.cashAndCashEquivalents/data.totalAssets
        features['shortTermInvestmentsToAssets'] = data.shortTermInvestments/data.totalAssets
        features['netReceivablesToAssets'] = data.netReceivables/data.totalAssets
        features['inventoryToAssets'] = data.inventory/data.totalAssets
        features['otherCurrentAssetsToAssets'] = data.otherCurrentAssets/data.totalAssets
        features['propertyPlantEquipmentNetToAssets'] = data.propertyPlantEquipmentNet/data.totalAssets
        features['intangibleAssetsToAssets'] = data.intangibleAssets/data.totalAssets
        features['longTermInvestmentsToAssets'] = data.longTermInvestments/data.totalAssets
        features['otherNonCurrentAssetsToAssets'] = data.otherNonCurrentAssets/data.totalAssets
        # Liabilities
        features['accountPayablesToAssets'] = data.accountPayables/data.totalAssets
        features['shortTermDebtToAssets'] = data.shortTermDebt/data.totalAssets
        features['deferredRevenueToAssets'] = data.deferredRevenue/data.totalAssets
        features['otherCurrentLiabilitiesToAssets'] = data.otherCurrentLiabilities/data.totalAssets
        features['longTermDebtToAssets'] = data.longTermDebt/data.totalAssets
        features['otherNonCurrentLiabilitiesToAssets'] = data.otherNonCurrentLiabilities/data.totalAssets
        true_cash = data.cashAndCashEquivalents + data.shortTermInvestments + data.longTermInvestments
        total_debt = data.shortTermDebt  + data.longTermDebt + 0.001001
        features['netDebtToTotalDebt'] = (total_debt - true_cash) / total_debt
        # Equity
        features['retainedEarningsToAssets'] = data.retainedEarnings / data.totalAssets
        features['totalStockholdersEquityToAssets'] = data.totalStockholdersEquity / data.totalAssets
        # Income
        features['costOfRevenueToRevenue'] = data.costOfRevenue / data.revenue
        features['researchAndDevelopmentExpensesToRevenue'] = data.researchAndDevelopmentExpenses / data.revenue
        features['sellingGeneralAndAdministrativeExpensesToRevenue'] = data.sellingGeneralAndAdministrativeExpenses / data.revenue
        features['ebitdaToRevenue'] = data.ebitda / data.revenue
        features['operatingIncomeToRevenue'] = data.operatingIncome / data.revenue
        features['netIncomeToRevenue'] = data.netIncome / data.revenue
        # Cash Flow
        features['stockBasedCompensationToRevenue'] = data.stockBasedCompensation/data.revenue
        features['depreciationAndAmortizationToRevenue'] = data.depreciationAndAmortization/data.revenue
        features['changeInWorkingCapitalToRevenue'] = data.changeInWorkingCapital/data.revenue
        features['freeCashFlowToRevenue'] = data.freeCashFlow/data.revenue
        features['capitalExpenditureToRevenue'] = data.capitalExpenditure/data.revenue
        features['acquisitionsNetToRevenue'] = data.acquisitionsNet/data.revenue
        features['purchasesOfInvestmentsToRevenue'] = data.purchasesOfInvestments/data.revenue
        net_shares = abs(data.commonStockRepurchased) - data.commonStockIssued
        features['netSharesRepurchasedToRevenue'] = net_shares/data.revenue
        features['dividendsPaidToRevenue'] = abs(data.dividendsPaid)/data.revenue
        features['freeCashFlowGivenToShareholders'] = (net_shares + abs(data.dividendsPaid)) / data.freeCashFlow

        # Absolute Values
        features['totalAssets'] = data.totalAssets
        features['revenue'] = data.revenue

        # Mixed Values
        features['PPEtoSales'] = data.propertyPlantEquipmentNet / data.revenue
        features['netDebtToEBITDA'] = (data.totalDebt - true_cash) / data.ebitda
        features['roe'] = data.netIncome / data.totalStockholdersEquity
        return features