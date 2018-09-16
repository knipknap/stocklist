from datetime import datetime
from itertools import islice
from collections import OrderedDict
from util import get_soup_from_url, resolve_value

yahoo_key_stats_url = 'https://finance.yahoo.com/quote/%s/key-statistics/?guccounter=1'
yahoo_income_statement_url = 'https://finance.yahoo.com/quote/%s/financials/'
yahoo_balance_sheet_url = 'https://finance.yahoo.com/quote/%s/balance-sheet/'
yahoo_analysis_url = 'https://finance.yahoo.com/quote/%s/analysis/'

class YahooCompany(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self._yahoo_key_stats = None
        self._yahoo_income_statement = None
        self._yahoo_balance_sheet = None
        self._yahoo_analysis = None

    @property
    def yahoo_key_stats(self):
        if self._yahoo_key_stats is not None:
            return self._yahoo_key_stats
        soup = get_soup_from_url(yahoo_key_stats_url % self.symbol)

        # The stock price is only included in the javascript, making extraction hairy...
        price = None
        for n, scr in enumerate(soup.find_all('script')):
            scr = scr.string
            if not scr:
                continue
            try:
                idx = scr.index('regularMarketPrice')
                idx = idx + scr[idx:].index('"raw":')
            except ValueError:
                continue
            length = scr[idx+6:].find(',')
            price = scr[idx+6:idx+6+length]

        pet_label = soup.find("span", string="Trailing P/E")
        pef_label = soup.find("span", string="Forward P/E")
        pbv_label = soup.find("span", string="Price/Book")
        td_label = soup.find("span", string="Total Debt")
        tde_label = soup.find("span", string="Total Debt/Equity")
        fw_dividend_label = soup.find("span", string="Forward Annual Dividend Rate")
        cr_label = soup.find("span", string="Current Ratio")
        try:
            total_debt = td_label.parent.nextSibling.text
        except AttributeError:
            total_debt = None
        try:
            total_debt_equity = tde_label.parent.nextSibling.text
        except AttributeError:
            total_debt_equity = None
        try:
            pe_trailing = pet_label.parent.nextSibling.text
        except AttributeError:
            pe_trailing = None
        try:
            pe_forward = pef_label.parent.nextSibling.text
        except AttributeError:
            pe_forward = None
        try:
            pbv = pbv_label.parent.nextSibling.text
        except AttributeError:
            pbv = None
        try:
            dividend_forward = fw_dividend_label.parent.nextSibling.text
        except AttributeError:
            dividend_forward = None
        try:
            cr = cr_label.parent.nextSibling.text
        except AttributeError:
            cr = None
        result = {'price': resolve_value(price),
                  'total-debt': resolve_value(total_debt),
                  'total-debt-equity': resolve_value(total_debt_equity),
                  'pe-trailing': resolve_value(pe_trailing),
                  'pe-forward': resolve_value(pe_forward),
                  'p-bv': resolve_value(pbv),
                  'dividend-forward': resolve_value(dividend_forward),
                  'current-ratio': resolve_value(cr)}
        self._yahoo_key_stats = result
        return self._yahoo_key_stats

    @property
    def yahoo_income_statement(self):
        if self._yahoo_income_statement is not None:
            return self._yahoo_income_statement
        soup = get_soup_from_url(yahoo_income_statement_url % self.symbol)

        # Find some entry points in the HTML.
        re_label = soup.find("span", string="Revenue")
        try:
            re_spans = re_label.parent.parent.select('td > span')[1:]
        except AttributeError:
            re_spans = []

        ni_label = soup.find("span", string="Net Income Applicable To Common Shares")
        try:
            ni_spans = ni_label.parent.parent.select('td > span')[1:]
        except AttributeError:
            ni_spans = []

        tre_label = soup.find("span", string="Total Revenue")
        gp_label = soup.find("span", string="Gross Profit")

        # Extract dates for each year.
        dates = []
        for span in re_spans:
            date = datetime.strptime(span.text, "%m/%d/%Y").strftime('%Y-%m-%d')
            dates.append(date)

        # Annual net income.
        try:
            ni = OrderedDict()
            for date, span in zip(dates, ni_spans):
                ni[date] = resolve_value(span.text)
        except AttributeError:
            print(" !Warning: failed to look up net income for %s" % date)

        # Total revenue.
        try:
            tre = tre_label.parent.nextSibling.find('span').text + 'k'
        except AttributeError:
            tre = '-'

        # Gross profit.
        try:
            gp = gp_label.parent.nextSibling.find('span').text + 'k'
        except AttributeError:
            gp = '-'

        result = {'net-income': ni,
                  'total-revenue': resolve_value(tre),
                  'gross-profit': resolve_value(gp)}
        self._yahoo_income_statement = result
        return self._yahoo_income_statement

    @property
    def yahoo_balance_sheet(self):
        if self._yahoo_balance_sheet is not None:
            return self._yahoo_balance_sheet
        soup = get_soup_from_url(yahoo_balance_sheet_url % self.symbol)
        ta_label = soup.find("span", string="Total Assets")
        try:
            ta = ta_label.parent.nextSibling.find('span').text + 'k'
        except AttributeError:
            ta = '-'
        result = {'total-assets': resolve_value(ta)}
        self._yahoo_balance_sheet = result
        return self._yahoo_balance_sheet

    @property
    def yahoo_analysis(self):
        if self._yahoo_analysis is not None:
            return self._yahoo_analysis
        soup = get_soup_from_url(yahoo_analysis_url % self.symbol)
        result = {}
        self._yahoo_analysis = result
        return self._yahoo_analysis

    @property
    def total_debt(self):
        """
        Total dept.
        """
        return self.yahoo_key_stats['total-debt']

    @property
    def total_debt_equity(self):
        """
        Total dept/equity.
        """
        return self.yahoo_key_stats['total-debt-equity']

    @property
    def pe_trailing(self):
        """
        Price to earnings per share (trailing)
        """
        return self.yahoo_key_stats['pe-trailing']

    @property
    def pe_forward(self):
        """
        Price to earnings per share (trailing)
        """
        return self.yahoo_key_stats['pe-forward']

    @property
    def p_bv(self):
        """
        Price to book value (mrq)
        """
        return self.yahoo_key_stats['p-bv']

    @property
    def dividend_forward(self):
        """
        Forward Annual Dividend Rate
        """
        return self.yahoo_key_stats['dividend-forward']

    @property
    def total_assets(self):
        return self.yahoo_balance_sheet['total-assets']

    @property
    def current_ratio(self):
        return self.yahoo_key_stats['current-ratio']

    @property
    def net_income(self):
        '''
        Returns net income of stock in the past twelve months.
        '''
        try:
            ni = next(islice(self.yahoo_income_statement.get('net-income').values(), 1))
            return int(ni)
        except (KeyError, ValueError, StopIteration):
            return None

    def get_net_income_series(self):
        '''
        Returns net income of stock.
        Returns a dict mapping month to income, e.g.::
        
            {"2017-08": 10}
        '''
        ni = self.yahoo_income_statement.get('net-income')
        if not ni:
            return None
        try:
            return dict((k, int(v)*1000000) for (k, v) in ni.items())
        except ValueError:
            return None

    @property
    def revenue(self):
        '''Returns revenue of stock in
        the past twelve months'''
        return self.yahoo_income_statement['total-revenue']

    @property
    def gross_profit(self):
        '''Returns gross profit of stock in
        the past twelve months'''
        return self.yahoo_income_statement['gross-profit']

    @property
    def share_price(self):
        '''Returns current stock price'''
        return self.yahoo_key_stats['price']
