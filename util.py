import re
import requests
from bs4 import BeautifulSoup

def get_stocks_from_file(filename):
    with open(filename) as fp:
        return [l.rstrip() for l in fp.readlines()]

def get_soup_from_url(url):
    """
    Returns the JSON from the given financialmodelingprep.com URL.
    """
    request = requests.get(url)
    data_html = request.text
    return BeautifulSoup(data_html, 'html.parser')

def resolve_value(value):
    """
    Convert "1k" to 1 000, "1m" to 1 000 000, etc.
    """
    tens = dict(k=10e3, m=10e6, b=10e9, t=10e12)
    value = value.replace(',', '')
    match = re.match(r'(-?\d+\.?\d*)([kmbt]?)$', value, re.I)
    if not match:
        return None
    factor, exp = match.groups()
    if not exp:
        return float(factor)
    return int(float(factor)*tens[exp.lower()])
