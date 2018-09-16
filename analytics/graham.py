from colorama import Fore, Back, Style

FAIL = Fore.RED+'-> Failed'+Style.RESET_ALL
OK = Fore.GREEN+'-> Ok'+Style.RESET_ALL

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

def graham_filter(company, dump_successful=True, dump_failed=True):
    output = [company['symbol']+':']

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
