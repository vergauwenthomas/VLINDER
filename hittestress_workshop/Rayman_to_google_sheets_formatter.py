#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 15:07:22 2022

@author: thoverga
"""

import pandas as pd
import datetime 

#%% IO

input_folder = '/home/thoverga/Documents/VLINDER_github/VLINDER/hittestress_workshop/Rayman_output'

filename = 'Vlinder_57.txt'

Textfiles = [os.path.join(input_folder, filename)]


labels = ['VLINDER 57'] #the name of the vlinder stations, in the same order as the data files!!








#%%

total_df = pd.DataFrame()
for station_index in range(len(Textfiles)): 
    
    #PET file
    file = Textfiles[station_index]
    
    #Read data and skip the first lines
    
    df = pd.read_csv(file, delimiter='\t', skiprows=[0,1,2,4])
    
    
    #formatting columns
    #remove trailing and leading whitespaces in the column names
    df.columns = [colstring.rstrip().lstrip() for colstring in df.columns]
    
    
    #datetime
    df['datetime'] = df['date'] + ' ' + df['time']
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M')
    
    
    
    
    
    
    #get sunrise and sunset info
    df['sunr'] = df['date']  + ' ' + df['sunr.']
    df['sunr'] = pd.to_datetime(df['sunr'], format='%d.%m.%Y %H:%M')
    
    df['sunset'] = df['date']  + ' ' + df['sunset']
    df['sunset'] = pd.to_datetime(df['sunset'], format='%d.%m.%Y %H:%M')
    

    
    
    
    #subset relevant columns
    columns_to_keep = ['datetime', 'Ta', 'RH', 'v', 'PET', 'Gact', 'sunr', 'sunset']
    df = df[columns_to_keep]
    
    #Set numeric columns to float
    numeric_columns = ['Ta', 'RH', 'v', 'PET', 'Gact']
    for col in numeric_columns:
        df[col] = df[col].astype(float)
    
    #add station name
    df['station'] = labels[station_index]
    
    #rename columns
    df = df.rename(columns={'Ta': 'Temperature',
                            'RH': 'Relative_Humidity',
                            'v': 'Windspeed',
                            'Gact': 'Global_radiation'})
    #set datetime as index
    df = df.set_index('datetime')
    
    
    #check if label is different
    
    
    
    #check if datetimeindex is equivalent
    
    
    
    #add to total df
    total_df = total_df.append(df)