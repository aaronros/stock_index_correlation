# stock_index_correlation

The idea of this project is to see how correlated 
stock prices are in a given index, and if they are 
strongly correlated, write a trading alorithm that
goes long on stocks that are under performing the 
index (or other stocks that it is strngly correlated
with) and short the ones that are overperforming

Time series of the stock prices are scrapped from
finance.google.com, which has split-adjusted stock
prices. The indices and holdings are from ETF daily

Concerns
- indices change holdings, so the index correlations 
will not be reflective of true industry correlations
- survivorship bias: only companies that live will be 
in the current indices
- need lots of data: we can't look at any correlations in
new industries, such as tech or biotech, because there isn't 
enough time to look at correlations



