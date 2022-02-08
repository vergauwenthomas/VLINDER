#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 09:03:29 2021

@author: thoverga
"""

import pandas as pd

#%%
inputfile = "/home/thoverga/Documents/VLINDER_github/VLINDER/eurocordex_extractor_vlinder/vlinder01_cordexbe_data.csv"





#%%
df = pd.read_csv(inputfile)

#%%
columns_of_interest = ['datetime', 'temperature_rcp26', 'temperature_rcp45', 'temperature_rcp85',
                       'relative_humidity_rcp26', 'relative_humidity_rcp45', 'relative_humidity_rcp85',
                       'N-wind_rcp26', 'N-wind_rcp45', 'N-wind_rcp85', 'E-wind_rcp26', 'E-wind_rcp45', 'E-wind_rcp85',
                       'station', 'lat', 'lon']
newdf = df[columns_of_interest]


newdf['datetime'] = pd.to_datetime(newdf['datetime'])
newdf.set_index(newdf['datetime'], inplace=True)



newdf.drop(columns=['datetime'], inplace=True)

keep_hours = [0, 6, 12, 18]


newdf = newdf[newdf.index.hour.isin(keep_hours)]
#%%

plot_columns = ['temperature_rcp26', 'temperature_rcp45', 'temperature_rcp85']

plotdf = newdf[plot_columns]

plotdf.plot.line()