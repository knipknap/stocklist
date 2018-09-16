#!/usr/bin/env python3
import sys
from optparse import OptionParser
from util import get_stocks_from_file, resolve_value
from nasdaq import get_nasdaq_traded_stocks, get_nasdaq_listed_stocks
from fmp import FmpCompany
from yahoo import YahooCompany

def check_net_income(company):
    net_income_dict = company.get_net_income_series()
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

def run(stock_list):
    for symbol in stock_list:
        print()
        fmp_company = FmpCompany(symbol)
        company = YahooCompany(symbol)
        print(symbol + ':')
        rating = fmp_company.rating
        if rating is None:
            print(" !Warning: No rating found, assuming 3")
            rating = 3

        # Sanity checks.
        try:
            company.total_debt_equity
        except AttributeError:
            print(" !Failed to collect Total Debt/Equity data, skipping")
            continue
        if not company.total_debt_equity:
            print(" !Incomplete data (Total Debt/Equity), skipping")
            continue
        if not company.total_assets:
            print(" !Incomplete data (Total Assets), skipping")
            continue
        if not company.current_ratio:
            print(" !Incomplete data (Current Ratio), skipping")
            continue
        if not company.net_income:
            print(" !Incomplete data (Net Income), skipping")
            continue

        # Dump some info...
        print(' Rating:', rating)
        print(' Total Debt/Equity:', company.total_debt_equity)
        print(' Total Assets:', company.total_assets)
        td_ta_ratio = company.total_debt_equity/company.total_assets
        print(' Total Debt to Total Asset ratio:', td_ta_ratio)
        print(' Current Ratio:', company.current_ratio)
        print(' Net Income:', company.net_income)
        print(' Share Price:', company.share_price)
        print(' P/E (trailing):', company.pe)
        print(' P/E (forward):', company.pe_forward)
        print(' Price to Book Value:', company.p_bv)
        print(' Dividend (forward):', company.dividend_forward)

        if not company.pe:
            print(" !Incomplete data (P/E), using forward P/E instead")
        pe = company.pe if company.pe else company.pe_forward
        if not pe:
            print(" !Incomplete data (P/E), skipping")
            continue

        # Graham filters.
        if rating > 3:
            print(' -> Bad rating')
            continue
        if td_ta_ratio > 1.10:
            print(' -> Exceeds Total Debt to Current Asset ratio')
            continue
        if company.current_ratio > 1.50:
            print(' -> Exceeds Current Ratio (current assets divided by current liabilities)')
            continue
        if not check_net_income(company):
            pass
            continue
        if pe > 9:
            print(' -> Exceeds P/E')
            continue
        if company.p_bv >= 1.2:
            print(' -> Exceeds Price/Book Value')
            continue
        if not company.dividend_forward:
            print(' -> No dividends')
            continue
        print(" ", company.symbol, "is looking good")

usage  = '%prog [options] action [action-options ...]'
parser = OptionParser(usage=usage)
options, args = parser.parse_args(sys.argv)
args.pop(0)

try:
    action = args.pop(0)
except IndexError:
    parser.error('missing action argument')

if action == 'pull':
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

elif action == 'grahamlist':
    try:
        filename = args.pop(0)
    except IndexError:
        parser.error('missing filename argument')
    try:
        stock_list = get_stocks_from_file(filename)
    except OSError:
        parser.error('error: ' + repr(filename))
    run(stock_list)
    sys.exit(0)

elif action == 'graham':
    if not args:
        parser.error('need at least one symbol')
    run(args)
    sys.exit(0)

else:
    parser.error('unknown action: ' + repr(action))
