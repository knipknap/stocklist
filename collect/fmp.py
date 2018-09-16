import json
from .util import get_soup_from_url

stock_list_url = 'https://financialmodelingprep.com/api/stock/losers'
profile_url = 'https://financialmodelingprep.com/public/api/company/profile/%s'
income_statement_url = 'https://financialmodelingprep.com/api/financials/income-statement/%s'
rating_url = 'https://financialmodelingprep.com/api/company/rating/%s'
balance_sheet_url = 'https://financialmodelingprep.com/api/financials/balance-sheet-statement/%s'
cash_flow_url = 'https://financialmodelingprep.com/api/financials/cash-flow-statement/%s'

def get_from_fmp_url(url):
    """
    Returns the JSON from the given financialmodelingprep.com URL.
    """
    soup = get_soup_from_url(url)
    data_json = soup.pre.get_text()
    return json.loads(data_json)

def get_stock_list_from_url(url):
    """
    Pull a list of stocks from financialmodelingprep.com.
    Returns a dict mapping stock symbol to basic data, like the company name
    and the price.
    """
    return get_from_fmp_url(url)

class FmpCompany(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self._profile = None
        self._rating = None
        self._income_statement = None
        self._balance_sheet = None
        self._cash_flow = None

    @property
    def profile(self):
        if self._profile is not None:
            return self._profile
        data = get_from_fmp_url(profile_url % symbol)
        self._profile = data[symbol]
        return self._profile

    @property
    def rating(self):
        """
        Returns the rating as an integer:
        5 = sell
        4 = underperform
        3 = hold
        2 = buy
        1 = strong buy
        0 = unrated?
        """
        if self._rating is not None:
            return self._rating
        try:
            data = get_from_fmp_url(rating_url % self.symbol)
        except AttributeError:
            return None
        try:
            self._rating = int(data[self.symbol]['rating'])
        except ValueError:
            return None
        return self._rating

    @property
    def income_statement(self):
        if self._income_statement is not None:
            return self._income_statement
        data = get_from_fmp_url(income_statement_url % self.symbol)
        self._income_statement = data[self.symbol]
        return self._income_statement

    @property
    def balance_sheet(self):
        if self._balance_sheet is not None:
            return self._balance_sheet
        self._balance_sheet = get_from_fmp_url(balance_sheet_url % self.symbol)
        return self._balance_sheet

    @property
    def cash_flow(self):
        if self._cash_flow is not None:
            return self._cash_flow
        data = get_from_fmp_url(cash_flow_url % self.symbol)
        self._cash_flow = data[self.symbol]
        return self._cash_flow

    @property
    def number_of_outstanding_shares(self):
        return int(self.profile['MktCap']) / self.share_price
