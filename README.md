# Stocklist

## Summary

Disclaimer: If you plan on using this tool for making actual financial
decisions in production, there is something wrong with you.
Use it on your own risk.

This project is purely experimental. The repo contains functions I use
for stock data collection and analysis.

## Supported Operations

### Get a list of stock symbols from NASDAQ

```
./stocklist.py dir nasdaq-traded > nasdaq_traded.txt
./stocklist.py dir nasdaq-listed > nasdaq_listed.txt
```

### Pull fundamental data for a list of stock symbols

```
./stocklist.py pull AAPL LHA.DE
./stocklist.py pull --filename nasdaq-listed.txt
```

### Graham filter

The tool can filter for stocks matching Benjamin Graham's seven criteria to identify
strong value stocks. The criteria are:

- Look for a quality rating that is average or better
- Total Debt to Current Asset ratios of less than 1.10
- Current Ratio over 1.50
- Positive earnings per share growth during the past five years with no earnings deficits
- Price to earnings per share (P/E) ratios of 9.0 or less
- Price to book value (P/BV) ratios less than 1.20
- Must currently be paying dividends

To check one or more symbols for Benjamin Graham's 7 criteria:

```
./stocklist.py graham AAPL LHA.DE
```

The same, but reading the symbols from a file:

```
./stocklist.py graham --filename nasdaq_listed.txt
```

Example output for a stock considered undervalued:

```
$ ./stocklist.py graham LEO.DE

LEO.DE:
 Using cached version
 !Warning: No rating found, assuming 3
 Rating: 3 -> Ok
 Share Price: 34.77
 Total Debt: 7159500000
 Total Debt/Equity: 65.31
 Total Assets: 31263100000
 Total Debt to Total Asset ratio: 0.22900799984646436 -> Ok
 Current Ratio: 1.06 -> Ok
 Net Income: 145022 -> Ok
 P/E (trailing): 8.52 -> Ok
 P/E (forward): 7.61 -> Ok
 Price to Book Value: 1.04 -> Ok
 Dividend (forward): 1.4 -> Ok
 -> Passed Graham filter
```

### More options

There's always `--help`:

```
$ ./stocklist.py --help
```

This also provides more options for sub-commands:

```
$ ./stocklist.py graham --help
```

## Data Sources

The data sources are all completely free (as in money), with no sign up required:
- NASDAQ symbol directory
- Yahoo finance (web scraping, no API)
- Financial Modelling Prep API (to collect a rating for each stock)

## Requirements

You'll need Python 3 with the modules listed in requirements.txt.
