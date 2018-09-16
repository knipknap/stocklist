#!/usr/bin/env python3
import os
import sys
import json
from optparse import OptionParser
from util import get_stocks_from_file, resolve_value
from nasdaq import get_nasdaq_traded_stocks, get_nasdaq_listed_stocks
from fmp import FmpCompany
from yahoo import YahooCompany

data_dir = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)

def check_net_income(company):
    net_income_dict = company['net-income']
    if not net_income_dict:
        print(' !Incomplete data, not net income data found')
        return False
    first = None
    for month, ni in sorted(net_income_dict.items()):
        if first is None:
            first = ni
        if ni < 0:
            print(' -> Negative net income in', month)
            return False
    if ni <= first:
        print(' -> Net income did not rise over five years')
        return False
    return True

def fetch_symbol_data(symbol):
    """
    Retrieve the data for the given symbol from Yahoo and FMP.
    """
    fmp_company = FmpCompany(symbol)
    yahoo_company = YahooCompany(symbol)
    return {'rating': fmp_company.rating,
            'share-price': yahoo_company.share_price,
            'total-debt-equity': yahoo_company.total_debt_equity,
            'pe-trailing': yahoo_company.pe_trailing,
            'pe-forward': yahoo_company.pe_forward,
            'p-bv': yahoo_company.p_bv,
            'dividend-forward': yahoo_company.dividend_forward,
            'current-ratio': yahoo_company.current_ratio,
            'latest-net-income': yahoo_company.net_income,
            'net-income': yahoo_company.get_net_income_series(),
            'total-revenue': yahoo_company.revenue,
            'gross-profit': yahoo_company.gross_profit,
            'total-assets': yahoo_company.total_assets}

def pull(symbol):
    """
    Like fetch(), but also stores the result on the file system.
    """
    print(" Fetching fundamental data for " + symbol)
    company = fetch_symbol_data(symbol)
    filename = os.path.join(data_dir, symbol + '.json')
    with open(filename, 'w') as fp:
        json.dump(company, fp)
    return company

def load(symbol):
    """
    Like pull(), but uses already stored version from file system,
    if available.
    """
    filename = os.path.join(data_dir, symbol + '.json')
    if not os.path.isfile(filename):
        return pull(symbol)
    with open(filename) as fp:
        print(" Using cached version")
        return json.load(fp)

def run(symbol):
    print()
    print(symbol + ':')
    company = load(symbol)

    # Sanity checks.
    if not company['rating']:
        print(" !Warning: No rating found, assuming 3")
        company['rating'] = 3
    if not company['total-debt-equity']:
        print(" !Incomplete data (Total Debt/Equity), skipping")
        return
    if not company['total-assets']:
        print(" !Incomplete data (Total Assets), skipping")
        return
    if not company['current-ratio']:
        print(" !Incomplete data (Current Ratio), skipping")
        return
    if not company['latest-net-income']:
        print(" !Incomplete data (Net Income), skipping")
        return

    # Dump some info...
    print(' Rating:', company['rating'])
    print(' Total Debt/Equity:', company['total-debt-equity'])
    print(' Total Assets:', company['total-assets'])
    td_ta_ratio = company['total-debt-equity']/company['total-assets']
    print(' Total Debt to Total Asset ratio:', td_ta_ratio)
    print(' Current Ratio:', company['current-ratio'])
    print(' Net Income:', company['latest-net-income'])
    print(' Share Price:', company['share-price'])
    print(' P/E (trailing):', company['pe-trailing'])
    print(' P/E (forward):', company['pe-forward'])
    print(' Price to Book Value:', company['p-bv'])
    print(' Dividend (forward):', company['dividend-forward'])

    pe = company['pe-forward'] if company['pe-forward'] else company['pe-trailing']
    if not pe:
        print(" !Incomplete data (P/E), skipping")
        return

    # Graham filters.
    if company['rating'] > 3:
        print(' -> Bad rating')
        return
    if td_ta_ratio > 1.10:
        print(' -> Exceeds Total Debt to Current Asset ratio')
        return
    if company['current-ratio'] > 1.50:
        print(' -> Exceeds Current Ratio (current assets divided by current liabilities)')
        return
    if not check_net_income(company):
        pass
        return
    if pe > 9:
        print(' -> Exceeds P/E')
        return
    if company['p-bv'] >= 1.2:
        print(' -> Exceeds Price/Book Value')
        return
    if not company['dividend-forward']:
        print(' -> No dividends')
        return
    print(" ", symbol, "is looking good")

usage  = '%prog [options] action [action-options ...]'
parser = OptionParser(usage=usage)
options, args = parser.parse_args(sys.argv)
args.pop(0)

try:
    action = args.pop(0)
except IndexError:
    parser.error('missing action argument')

if action == 'dir':
    try:
        source = args.pop(0)
    except IndexError:
        parser.error('missing data source argument')
    if source == 'nasdaq-traded':
        stock_list = get_nasdaq_traded_stocks()
    elif source == 'nasdaq-listed':
        stock_list = get_nasdaq_listed_stocks()
    else:
        parser.error('unknown source: ' + repr(source))
    for l in stock_list:
        print(l)
    sys.exit(0)

elif action == 'pull':
    if not args:
        parser.error('need at least one symbol')
    for arg in args:
        pull(arg)
    sys.exit(0)

elif action == 'pull-bulk':
    try:
        filename = args.pop(0)
    except IndexError:
        parser.error('missing filename argument')
    try:
        stock_list = get_stocks_from_file(filename)
    except OSError:
        parser.error('error: ' + repr(filename))
    for symbol in stock_list:
        pull(symbol)
    sys.exit(0)

elif action == 'graham':
    if not args:
        parser.error('need at least one symbol')
    for arg in args:
        run(arg)
    sys.exit(0)

elif action == 'graham-bulk':
    try:
        filename = args.pop(0)
    except IndexError:
        parser.error('missing filename argument')
    try:
        stock_list = get_stocks_from_file(filename)
    except OSError:
        parser.error('error: ' + repr(filename))
    for symbol in stock_list:
        run(symbol)
    sys.exit(0)

else:
    parser.error('unknown action: ' + repr(action))
