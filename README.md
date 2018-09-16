# Stocklist

## Summary

This is a personal experiment only. The repo contains functions I use
for stock data collection and analysis.

Data sources are all completely free, no sign up required:
- NASDAQ symbol directory
- Yahoo finance (web scraping, no API)
- Financial Modelling Prep API (to collect a rating for each stock)

## Requirements

You'll need Python 3 with the modules listed in requirements.txt.

## Supported Operations

### Pull a list of stock symbols from NASDAQ

```
./stocklist.py pull nasdaq-traded > nasdaq_traded.txt
./stocklist.py pull nasdaq-listed > nasdaq_listed.txt
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

To check for one or more symbols for Benjamin Graham's 7 criteria:

```
./stocklist.py graham AAPL LHA.DE
```

The same, but reading the symbols from a file:

```
./stocklist.py grahamlist nasdaq_listed.txt
```
