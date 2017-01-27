
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
Function: get_month
Usage: month = get_month(date)
---
For a given date, we extract the month. Raises
an error if the month is in the wrong form
'''
def get_month(date):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month = date[0:3]
    
    #assert month in months
    #return month
    if month in months: return month
    else: 
        raise ValueError('Incorrect date input')

'''
Function: get_day
Usage: day = get_day(date)
---
For a given date, we extract the day. Raises
an error if the day is in the wrong form
'''
def get_day(date):
    days = range(1,32)
    day = date[4]
    if not date[5] == ' ': day += date[5]
    day = int(day)
    if day in days: return day
    else:
        raise ValueError('Incorrect date input')

'''
Function: get_year
Usage: year = get_year(date)
---
For a given date, we extract the year. Raises
an error if the year is in the wrong form
'''    
def get_year(date):
    years = range(1900,2017)
    year = int(date[len(date)-4:len(date)])
    if year in years: return year
    else:
        raise ValueError('Incorrect year input')

'''
Function: get_date_form
Usage: date_form = get_date_form(date)
---
For a given date, we extract the date form. Raises
an error if the date is in the wrong form
'''   
def get_date_form(date):
    month = get_month(date)
    day = str(get_day(date))
    year = str(get_year(date))
    return month + '+' + day + '%2C' + '+' + year

'''
Function: get_TS_NASDAQ
Usage: df = get_TS_NASDAQ('AAPL', 'Jan 1 1990', 'Dec 1 2016')
---
Returns a dataframe of the price time series for a given ticker. 
'''
def get_TS_NASDAQ(tick, start_date, end_date):
    tick = str(tick)
    url_name = 'https://www.google.com/finance/historical?q=NASDAQ%3A' + tick
    url_start_date = '&ei=WmRhWLHJDITCjAGDlJnoCw&startdate=' + get_date_form(start_date)
    url_end_date = '&enddate=' + get_date_form(end_date)
    url_output = '&output=csv'    
    url_csv = url_name + url_start_date + url_end_date + url_output
    
    try:
        df = pd.read_csv(url_csv)
    except:
        return pd.DataFrame()
    return df

'''
Function: get_TS_NYSE
Usage: df = get_TS_NYSE('XOM', 'Jan 1 1990', 'Dec 1 2016')
---
Returns a dataframe of the price time series for a given ticker. 
'''
def get_TS_NYSE(tick, start_date, end_date):
    tick = str(tick)
    url_name = 'https://www.google.com/finance/historical?q=NYSE%3A' + tick
    url_start_date = '&ei=c51oWPH6Osyw2Aa9363wCA&startdate=' + get_date_form(start_date)
    url_end_date = '&enddate=' + get_date_form(end_date)
    url_output = '&output=csv'    
    url_csv = url_name + url_start_date + url_end_date + url_output
    
    try:
        df = pd.read_csv(url_csv)
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
def get_TS(tick, start_date, end_date):
    if str(tick) == 'nan': return pd.DataFrame()
    
    df = get_TS_NASDAQ(tick, start_date, end_date)
    if df.empty == True: 
        df = get_TS_NYSE(tick, start_date, end_date)
        if df.empty == True:
            print('Warning: ' + tick + ' could not be found in the NASDAQ or NYSE')
            return pd.DataFrame()
    
    df = df.convert_objects(convert_numeric=True)
    df.columns = ['Date', tick,'High','Low','Close','Vol']
    df = df[['Date',tick]]
    df.set_index('Date',inplace = True)
    df = df.iloc[::-1]
    df.replace({0: 'nan'})
    df.dropna(inplace = True)    
    
    df_price = df
    df_perc_chn = df.copy(deep= True)
    df_perc_chn[tick] = (df_perc_chn[tick] - df_perc_chn[tick][0]) / df_perc_chn[tick][0] * 100.0
    
    return df_price, df_perc_chn 

def get_largest_TS(holdings, start_date, end_date, ncounter = 10):
    if len(holdings) == 0: raise EmptyIndex('No holdings passed to function')
    count = 0
    for tick in holdings:
        count += 1
        print(tick)
        tick_larg = ''
        rows_larg = 0
        df_price, df_perc_chn = get_TS(tick, start_date, end_date)
        rows_tick = len(df_price)
        if rows_tick > rows_larg:
            rows_larg = rows_tick
            tick_larg = tick
        if count >= ncounter: break
    return tick_larg

'''
Function: get_holdings
Usage: holdings = get_holdings('SPY')
---
This function returns a dataframe of the holdings for a given etf
where the etf itself is the first entry. The index of the data frame 
is time and the data is the stock price
'''
def get_holdings(etf, start_date = 'Jan 1 1990', end_date = 'Dec 1 2016', nstocks = 30, include_index = True):

    # find all holdings
    url_holdings = 'http://etfdailynews.com/etf/' + etf
    df_hold = pd.read_html(url_holdings)
    df_hold = df_hold[1]['Symbol']


    # now loop through the tickers in df_hold and create dataframes for 
    # each of the stock prices.
    if include_index:
        df_index_price, df_index_perc_chn  = get_TS(etf, start_date, end_date)
        df_full_price = df_index_price.copy(deep= True)
        df_full_perc_chn = df_index_perc_chn.copy(deep= True)
    
    counter = 0
    
    
#    print(type(df_hold))
#    df_largest = get_largest_TS(df_hold,start_date, end_date)
#    print(df_largest)



    for tick in df_hold:
        counter += 1
        print(tick)
        df_tick_price, df_tick_perc_chn = get_TS(tick, start_date, end_date)
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
    
    return df_full_price

df_full_price = get_holdings('IYR',start_date='Jan 1 1990', end_date= 'Dec 1 2016', nstocks= 10, include_index=False)



