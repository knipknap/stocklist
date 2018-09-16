# Stocklist

## Summary

This is a personal experiment only. The repo contains functions I use
for stock data collection and analysis.

Data sources are all completely free, no sign up required:
- NASDAQ symbol directory
- Yahoo finance API
- Financial Modelling Prep API (to collect a rating for each stock)

## Usage

Pull a list of stock symbols from NASDAQ:

```
./stocklist.py pull nasdaq-traded > nasdaq_traded.txt
./stocklist.py pull nasdaq-listed > nasdaq_listed.txt
```

Check one or more symbols for Benjamin Graham's 7 criteria.

```
./stocklist.py graham AAPL LHA.DE
```

The same, but reading the symbols from a file:

```
./stocklist.py grahamlist nasdaq_listed.txt
```
