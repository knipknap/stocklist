#!/usr/bin/env python3
import os
import sys
import json
from argparse import ArgumentParser
from util import get_stocks_from_file
from nasdaq import get_nasdaq_traded_stocks, get_nasdaq_listed_stocks
from fmp import FmpCompany
from yahoo import YahooCompany
from graham import graham_filter

data_dir = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)

def fetch_symbol_data(symbol):
    """
    Retrieve the data for the given symbol from Yahoo and FMP.
    """
    fmp_company = FmpCompany(symbol)
    yahoo_company = YahooCompany(symbol)
    return {'symbol': symbol,
            'rating': fmp_company.rating,
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
        return json.load(fp)

# Parse command line options.
parser = ArgumentParser()
subparsers = parser.add_subparsers(dest="action", title='Subcommands')

# "dir" command.
dir_parser = subparsers.add_parser('dir',
                                   help='get a list of stock symbols')
dir_parser.add_argument('source', type=str,
                        choices=('nasdaq-traded', 'nasdaq-listed'),
                        help='the name of the list')

# "pull" command.
pull_parser = subparsers.add_parser('pull',
                                    help='gather fundamental data')
pull_parser.add_argument('--filename', type=str, nargs='*', default = [],
                         help='file containing a list of stock symbols')
pull_parser.add_argument('-f', '--force',
                         dest='force',
                         action='store_true',
                         help='Overwrite existing data')
pull_parser.add_argument('symbols', type=str, nargs='*',
                         help='one or more stock symbols')

# "graham" command.
graham_parser = subparsers.add_parser('graham',
        help='filter stocks by Graham analysis')
graham_parser.add_argument('--filename', type=str, nargs='*', default = [],
                           help='file containing a list of stock symbols')
graham_parser.add_argument('-f', '--force',
                           dest='force',
                           action='store_true',
                           help='Overwrite existing data')
graham_parser.add_argument('-v', '--verbose', type=int,
                           default=1, choices=range(1,6),
                           help='verbosity level (1 to 5)')
graham_parser.add_argument('symbols', type=str, nargs='*',
                           help='one or more stock symbols')

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
    symbols = args.symbols
    for filename in args.filename:
        try:
            symbols += get_stocks_from_file(filename)
        except OSError as e:
            parser.error(e)
    for symbol in symbols:
        if args.force:
            print(" Fetching fundamental data for " + symbol)
            pull(symbol)
        else:
            print(" Fundamental data for {} is cached".format(symbol))
            load(symbol)
    sys.exit(0)

elif args.action == 'graham':
    dump_successful = True if args.verbose >= 1 else False
    dump_failed = True if args.verbose >= 2 else False

    symbols = args.symbols
    for filename in args.filename:
        try:
            symbols += get_stocks_from_file(filename)
        except OSError as e:
            parser.error(e)

    for symbol in symbols:
        if args.force:
            company = pull(symbol)
        else:
            company = load(symbol)
        graham_filter(company,
                      dump_successful=dump_successful,
                      dump_failed=dump_failed)
    sys.exit(0)

else:
    parser.error('unknown action: ' + repr(args.action))
