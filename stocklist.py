#!/usr/bin/env python3
import os
import sys
import json
from argparse import ArgumentParser
from util import get_stocks_from_file
from nasdaq import get_nasdaq_traded_stocks, get_nasdaq_listed_stocks
from fmp import FmpCompany
from yahoo import YahooCompany
from colorama import Fore, Back, Style

FAIL = Fore.RED+'-> Failed'+Style.RESET_ALL
OK = Fore.GREEN+'-> Ok'+Style.RESET_ALL

data_dir = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)

def check_net_income(company):
    net_income_dict = company['net-income']
    first = None
    for month, ni in sorted(net_income_dict.items()):
        if first is None:
            first = ni
        if ni < 0:
            return ' -> Negative net income in '+month+': '+str(ni)
    if ni <= first:
        return ' -> Net income did not rise over five years'
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

def run(symbol, dump_successful=True, dump_failed=True, force=False):
    output = [symbol+':']
    if force:
        company = pull(symbol)
    else:
        company = load(symbol)

    # Sanity checks.
    if not company['rating']:
        output.append(" !Warning: No rating found, assuming 3")
        company['rating'] = 3
    if not company['total-debt']:
        output.append(" !Incomplete data (Total Debt), skipping")
        return
    if not company['total-assets']:
        output.append(" !Incomplete data (Total Assets), skipping")
        return
    if not company['current-ratio']:
        output.append(" !Incomplete data (Current Ratio), skipping")
        return
    if not company['p-bv']:
        output.append(" !Incomplete data (Price to Book Value ratio), skipping")
        return
    if not company['latest-net-income']:
        output.append(" !Incomplete data (Net Income), skipping")
        return
    if not company['net-income']:
        output.append(' !Incomplete data, not net income data found')
        return
    pe = company['pe-forward'] if company['pe-forward'] else company['pe-trailing']
    if not pe:
        output.append(" !Incomplete data (P/E), skipping")
        return

    # Filter and dump results to stdout...
    results = []

    results.append(FAIL if company['rating'] > 3 else OK)
    output.append(' Rating: {} {}'.format(company['rating'], results[-1]))

    output.append(' Share Price: {}'.format(company['share-price']))
    output.append(' Total Debt: {}'.format(company['total-debt']))
    output.append(' Total Debt/Equity: {}'.format(company['total-debt-equity']))
    output.append(' Total Assets: {}'.format(company['total-assets']))

    td_ta_ratio = company['total-debt']/company['total-assets']
    results.append(FAIL if td_ta_ratio > 1.10 else OK)
    output.append(' Total Debt to Total Asset ratio: {} {}'.format(td_ta_ratio, results[-1]))

    results.append(FAIL if company['current-ratio'] > 1.50 else OK)
    output.append(' Current Ratio: {} {}'.format(company['current-ratio'], results[-1]))

    result = check_net_income(company)
    results.append(OK if check_net_income(company) is True else FAIL)
    output.append(' Net Income: {} {}'.format(company['latest-net-income'], results[-1]))
    if result is not True:
        output.append(result)

    results.append(FAIL if company['pe-trailing'] and pe > 9 else OK)
    output.append(' P/E (trailing): {} {}'.format(company['pe-trailing'], results[-1]))

    results.append(FAIL if company['pe-forward'] and pe > 9 else OK)
    output.append(' P/E (forward): {} {}'.format(company['pe-forward'], results[-1]))

    results.append(FAIL if company['p-bv'] >= 1.2 else OK)
    output.append(' Price to Book Value: {} {}'.format(company['p-bv'], results[-1]))

    results.append(OK if company['dividend-forward'] else FAIL)
    output.append(' Dividend (forward): {} {}'.format(company['dividend-forward'], results[-1]))

    if FAIL in results:
        output.append(" -> "+Back.RED+Fore.WHITE+"Failed Graham filter"+Style.RESET_ALL)
        if dump_failed:
            print("\n"+"\n".join(output))
        return output
    output.append(" -> "+Back.GREEN+"Passed Graham filter"+Style.RESET_ALL)
    if dump_successful:
        print("\n"+"\n".join(output))
    return output

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
        print(" Fetching fundamental data for " + symbol)
        if args.force:
            pull(symbol)
        else:
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
        run(symbol,
            dump_successful=dump_successful,
            dump_failed=dump_failed,
            force=args.force)
    sys.exit(0)

else:
    parser.error('unknown action: ' + repr(args.action))
