
# coding: utf-8

'''
Created 2016-12-30

The goal is to see how stocks in a certain sector correlate with
other stocks in the sector and broader indexes. Ideally, we would
see a strong correlation between a stock and a certain index over long
periods of time allowing us to go long or short when stocks are overweight
or underweight with respect to the index

Data
- The stock and ETF data is split adjusted from finance.google.com
- The current holdings of the index is found by etfdailynews.com
- For now, indexes are inputed by hand, but there will be automation in the future

Plan
- For a given index, find all the holdings
- For each of the holdings (and the index itself), import the the stock prices with time
- create a large dataframe of the stock prices for a ticker and correlate them
'''


'''
Import packages
'''
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (10.0, 8.0)


'''
Initialize contants and global variables
'''
etf_sect = ['IBB','IYW','IYH','IYF','ITA','IGF','IXJ','IYE','ITB',
                'IGE','IYG','IYJ','IHI','IYM','IHE','IYZ','IYR']
etf_broad = ['SPY','DIA','QQQ','GLD']
url_holdings = 'http://etfdailynews.com/etf/'


'''
Helper functions
'''

'''
Exception objects
'''
class ValueError(Exception):
    pass
class EmptyIndex(Exception):
    pass

'''
Function: get_raw_TS
Usage: df = get_raw_TS('AAPL', 'Jan 1 1990', 'Dec 1 2016')
---
Returns a dataframe of the price time series for a given ticker. 
'''
def get_raw_TS(tick, start_year, end_year):
    tick = str(tick)
    url_name = 'http://chart.finance.yahoo.com/table.csv?s=' + tick
    url_date = '&a=0&b=01&c=' + str(start_year) + '&d=0&e=01&f=' + str(end_year)
    url_csv = '&g=d&ignore=.csv'
    url = url_name + url_date + url_csv
    
    try:
        df = pd.read_csv(url)
    except:
        return pd.DataFrame()
    return df
    

'''
Function: get_TS
Usage: df_price, df_perc_chn = get_TS('XOM', 'Jan 1 1990', 'Dec 1 2016')
---
Wrapper function for NYSE and NASDAQ TS functions
Returns a dataframe of the price time series for a given ticker. 
Returns a dataframe of the price and the percent change
'''
def get_TS(tick, start_year, end_year):
    if str(tick) == 'nan': return pd.DataFrame()
    
    df = get_raw_TS(tick, start_year, end_year)
    if df.empty == True: 
        print('Warning: ' + tick + ' could not be found in the NASDAQ or NYSE')
        return pd.DataFrame()
    
    
    df = df.convert_objects(convert_numeric=True)
    df.columns = ['Date', 'Open','High','Low','Close','Vol', tick] # tick is technically adjusted close
    df = df[['Date', tick]]
    df.set_index('Date',inplace = True)
    df = df.iloc[::-1]
    df.replace({0: 'nan'})
    df.dropna(inplace = True)    
    
    df_price = df
    df_perc_chn = df.copy(deep= True)
    df_perc_chn[tick] = (df_perc_chn[tick] - df_perc_chn[tick][0]) / df_perc_chn[tick][0] * 100.0
    
    return df_price, df_perc_chn 
 

'''
Function: get_holdings
Usage: holdings = get_holdings('SPY')
---
This function returns a dataframe of the holdings for a given etf
where the etf itself is the first entry. The index of the data frame 
is time and the data is the stock price
'''
def get_holdings(etf, start_year = 1990, end_year = 2016, nstocks = 30, include_index = True):

    # find all holdings
    url_holdings = 'http://etfdailynews.com/etf/' + etf
    df_hold = pd.read_html(url_holdings)
    df_hold = df_hold[1]['Symbol']


    # now loop through the tickers in df_hold and create dataframes for 
    # each of the stock prices. THis if statement is used if we want to
    # include the index
    if include_index:
        df_index_price, df_index_perc_chn  = get_TS(etf, start_year, end_year)
        df_full_price = df_index_price.copy(deep= True)
        df_full_perc_chn = df_index_perc_chn.copy(deep= True)
    
    counter = 0

    for tick in df_hold:
        counter += 1
        print(tick)
        df_tick_price, df_tick_perc_chn = get_TS(tick, start_year, end_year)
        if not df_tick_perc_chn.empty and not str(tick) == 'nan':
            if counter == 1 and include_index == False:
                df_full_price = df_tick_price.copy(deep = True)
                df_full_perc_chn = df_tick_perc_chn.copy(deep = True)  
            else:
                df_full_price = df_full_price.join(df_tick_price)   
                df_full_perc_chn = df_full_perc_chn.join(df_tick_perc_chn)   
        if counter == nstocks: break

    df_corr = df_full_perc_chn.corr()

    fig, ax = plt.subplots(facecolor='white')
    df_full_perc_chn.plot(legend = False, ax= ax)
    
    return df_full_price, df_corr

df_full_price, df_corr = get_holdings('IYH',start_year =1950, end_year= 2016, nstocks= 10, include_index=True)



# for two different df columns, 
plt.close('all')

tick1 = 'IYH'
tick2 = 'JNJ'

rolling_corr = pd.rolling_corr(df_full_price[tick1], df_full_price[tick2], 30*5)
fig = plt.figure(facecolor = 'white')
ax1 = plt.subplot2grid((2,1),(0,0))
ax2 = plt.subplot2grid((2,1),(1,0), sharex = ax1)

df_full_price[tick1].plot(ax = ax1, label = tick1)
df_full_price[tick2].plot(ax = ax1, label = tick2)

ax1.legend(loc = 2)
rolling_corr.plot(ax=ax2, label = 'Rolling corr')

plt.legend(loc = 2)
plt.show()




'''
trading ideas

If correlation goes below -0.5 (or some threshold to be determined), buy the 
low and short the high (how to determine which is low and high?). Hold until
correlation is 0.5 (some other threshold), in which case dump all the two
positions

- how to do this for more than 2 stocks? AAPL is correlated with MSFT, FB and
much more. 

- maybe within an index, take the stocks that are 0.9 correlated and correlate
them all in time with each other to get an average. Then buy/short
'''