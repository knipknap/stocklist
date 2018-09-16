#!/usr/bin/env python3
import os
import sys
import json
from argparse import ArgumentParser
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
            'total-debt': yahoo_company.total_debt,
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
    if not company['total-debt']:
        print(" !Incomplete data (Total Debt), skipping")
        return
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
    print(' Total Debt:', company['total-debt'])
    print(' Total Debt/Equity:', company['total-debt-equity'])
    print(' Total Assets:', company['total-assets'])
    td_ta_ratio = company['total-debt']/company['total-assets']
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

# Parse command line options.
parser = ArgumentParser()
subparsers = parser.add_subparsers(dest="action", title='Subcommands')

# "dir" command.
dir_parser = subparsers.add_parser('dir',
                                   help='get a list of stock symbols')
dir_parser.add_argument('source', type=str,
                        choices=('nasdaq-traded', 'nasdaq-listed'),
                        help='the name of the list')

# "pull" and "pull-bulk" commands.
pull_parser = subparsers.add_parser('pull',
                                    help='gather fundamental data')
pull_parser.add_argument('-f', '--force',
                         dest='force',
                         action='store_true',
                         help='Overwrite existing data')
pull_parser.add_argument('symbols', type=str,
                         nargs='+',
                         help='one or more stock symbols')

pull_bulk_parser = subparsers.add_parser('pull-bulk',
                                         help='gather data in bulk')
pull_bulk_parser.add_argument('-f', '--force',
                              dest='force',
                              action='store_true',
                              help='Overwrite existing data')
pull_bulk_parser.add_argument('filename', type=str,
                              help='file containing a list of stock symbols')

# "graham" and "graham-bulk" commands.
graham_parser = subparsers.add_parser('graham',
        help='filter stocks by Graham analysis')
graham_parser.add_argument('symbols', type=str,
                           nargs='+',
                           help='one or more stock symbols')
graham_bulk_parser = subparsers.add_parser('graham-bulk',
        help='filter stocks by Graham analysis (bulk)')
graham_bulk_parser.add_argument('filename', type=str,
                                 help='file containing a list of stock symbols')

args = sys.argv[1:]
args = parser.parse_args(args)

if args.action == 'dir':
    if args.source == 'nasdaq-traded':
        stock_list = get_nasdaq_traded_stocks()
    elif args.source == 'nasdaq-listed':
        stock_list = get_nasdaq_listed_stocks()
    else:
        parser.error('unknown source: ' + repr(args.source))
    for l in stock_list:
        print(l)
    sys.exit(0)

elif args.action == 'pull':
    for symbol in args.symbols:
        pull(symbol)
    sys.exit(0)

elif args.action == 'pull-bulk':
    try:
        stock_list = get_stocks_from_file(args.filename)
    except OSError as e:
        parser.error(e)
    for symbol in stock_list:
        pull(symbol)
    sys.exit(0)

elif args.action == 'graham':
    for symbol in args.symbols:
        run(symbol)
    sys.exit(0)

elif args.action == 'graham-bulk':
    try:
        stock_list = get_stocks_from_file(args.filename)
    except OSError as e:
        parser.error(e)
    for symbol in stock_list:
        run(symbol)
    sys.exit(0)

else:
    parser.error('unknown action: ' + repr(args.action))
