import re
from ftplib import FTP
from io import StringIO

def get_nasdaq_stocks(filename):
    ftp = FTP('ftp.nasdaqtrader.com')
    ftp.login()
    ftp.cwd('SymbolDirectory')
    lines = StringIO()
    ftp.retrlines('RETR '+filename, lambda x: lines.write(str(x)+'\n'))
    ftp.quit()
    lines.seek(0)
    result = [l.split('|')[1] for l in lines.readlines()]
    return [l for l in result if re.match(r'^[A-Z]+$', l)]

def get_nasdaq_traded_stocks():
    return get_nasdaq_stocks('nasdaqtraded.txt')

def get_nasdaq_listed_stocks():
    return get_nasdaq_stocks('nasdaqlisted.txt')
