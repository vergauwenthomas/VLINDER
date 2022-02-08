#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 13:14:04 2022

Getting the data:
    1) To download the data use the Brian-Tool: https://vlinder.ugent.be/vlinderdata/multiple_vlinders.php

    2) save the data as a csv file, and set variable 'datafile' as the path to that file
    
    3) specify an output folder

    4) execute this script


format vlinder data, apply consecutive check, makes datafiles per station (one for further google sheets 


@author: thoverga
"""
import os 
import pandas as pd
import matplotlib.pyplot as plt

#%% Read data

datafile="/home/thoverga/Downloads/Vlinders van 2020-08-01 tot 2020-08-31.csv"

outputfolder = "/home/thoverga/Documents/VLINDER_github/VLINDER/hittestress_workshop/output_data/"


df = pd.read_csv(datafile, sep=';')



#%% format columns
df['datetime'] = df['Datum'] + ' ' + df['Tijd (UTC)']

df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
df.set_index(df['datetime'], inplace=True)



    
#%% Look for networkerror

max_consec = 30 #repetetive 5min update observations
time_resolution = '30min'



def check_station_consec(df, max_consec):
    df = df.sort_index()
    grouped = df.groupby((df['Temperatuur'].shift() != df['Temperatuur']).cumsum()) 
    #the above line groups the observations which have the same value and consecutive datetimes.
    #if a group has
    
    group_sizes = grouped.size()
    outlier_groups = group_sizes[group_sizes > max_consec]
    if outlier_groups.size == 0: #no large consecutive observations
        df['status'] = 'ok'
        return df
    else:
        
        
        # station = config.network.get_station(obs.name) 
        outlier_datetimes = []
        for group_idx in outlier_groups.index:
            outlier_datetimes_this_group = grouped.get_group(group_idx).index.to_list()
            outlier_datetimes.extend(outlier_datetimes_this_group)
        
        df['status'] = ['error' if datetime in outlier_datetimes else 'ok' for datetime in df.index]
        
        return df

def get_rayman_compatible_format(subdf):
    
    #format to rayman standard daytime format
    subdf['_datetime'] = pd.to_datetime(subdf.index.to_series(), format='%d-%m-%Y %H:%M:%S')
    
    subdf['date'] = subdf['_datetime'].dt.strftime('%-d.%-m.%Y')
    subdf['time'] = subdf['_datetime'].dt.strftime('%-H:%M')
    
    #windspeed to m/s
    subdf['Windsnelheid'] = subdf['Windsnelheid'].astype(float)
    subdf['Windsnelheid'] = subdf['Windsnelheid'] / 3.6
    
    
    format_float_columns = ['Temperatuur', 'Vochtigheid', 'Windsnelheid']
    for form_column in format_float_columns:
        subdf[form_column] = subdf[form_column].astype(float)
        subdf[form_column] = subdf[form_column].map('{:,.1f}'.format)
        subdf[form_column] = subdf[form_column].astype(str)
        
        
    export_columns = ['date', 'time', 'Temperatuur', 'Vochtigheid', 'Windsnelheid']
    return subdf[export_columns]


stationlist = df['Vlinder'].unique()
totaldf = pd.DataFrame()
for station in stationlist:
    subdf = df[df['Vlinder']==station]
    #quality control
    subdf = check_station_consec(subdf, max_consec)
    
    
    #refactor columns for writing to file
    starttime = subdf.index.min()
    endtime = subdf.index.max()

    selected_datetimes = pd.date_range(start=starttime,
                                   end=endtime,
                                   freq=time_resolution)
    
    subdf = subdf.loc[selected_datetimes.to_series()]
    
    subdf.index = subdf.index.to_series().dt.strftime('%d-%m-%Y %H:%M:%S')
    
    
    
    
    #drop non-relevant columns
    subdf.drop(columns=['datetime', 'Datum', 'Tijd (UTC)', 'Luchtdruk_Zeeniveau'], inplace=True)
    
    
    
    #write subdf
    filename = outputfolder+station+'_aug_2020.csv'
    subdf.to_csv( path_or_buf = filename,
                  header=True,
                  index=True,
                  sep='\t', 
                  decimal=',',
                  encoding='utf-8')
    
    
    
    
    #make format compatible with rayman
    rayman_subdf = get_rayman_compatible_format(subdf)
    #write rayman compatible subdf
    rayman_filename = os.path.join(outputfolder, 'rayman_format', station+'_aug_2020_rayman_input.txt')
    rayman_subdf.to_csv( path_or_buf = rayman_filename,
                        header=True,
                        index=False,
                        sep='\t', 
                        decimal='.',
                        encoding='utf-8') 
    
    #update totaldf
    totaldf = totaldf.append(subdf)
    
    
    # test = subdf[['Temperatuur', 'status']]
    # test = test.pivot(columns='status', values='Temperatuur')
    # test.plot(figsize=(12,6))
    # plt.title(station)
    # plt.show()

filename_all = outputfolder + "all_vlinders_aug_2020.csv"
totaldf.to_csv( path_or_buf = filename_all,
                  header=True,
                  index=True,
                  sep='\t', 
                  decimal=',',
                  encoding='utf-8')
#%%
