#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract timeseries from the CORDEXbe files, for a list of coordinates. 

Created on Wed Dec 22 14:36:25 2021

@author: thoverga
"""
import os
from os import listdir
from os.path import isfile, join

import pandas as pd
import matplotlib.pyplot as plt

import xarray as xr

#%%

datafolder = '/home/thoverga/fileserver/home/ncdf_archive_cordexbe'
outputfolder = '/home/thoverga/fileserver/home/scratch/VLINDER_data/eurocordex-data'

vlinderdatafile = '/home/thoverga/fileserver/home/Documents/VLINDER_github/VLINDER/Data/data.csv'


#%%

vlinderdata = pd.read_csv(vlinderdatafile)
stationlist = []
for _, row in vlinderdata.iterrows():
    stationlist.append({
                        'station': row['VLINDER'],
                        'lat': row['lat'],
                        'lon': row['lon']
                        })


#%%

settings = {
    'variables':{
                'tas':{
                        'name': 'temperature',
                        'res': '3hr',
                        },
                'hurs':{
                        'name': 'relative_humidity',
                        'res': '3hr',
                        },
                'pr':{
                        'name': 'precipitation',
                        'res': '3hr',
                        },
                'vas':{
                        'name': 'N-wind',
                        'res': '6hr',
                        },
                'uas':{
                        'name': 'E-wind',
                        'res': '6hr',
                        },
                        
            },
    'senario': ['rcp26', 'rcp45', 'rcp85'],
    'runs': ['200601', '204001', '207001']
    }


#%%

def read_eurocordex_at_coordinate_to_df(file, variable, sen, settings, lat, lon):
    
    #open dataset
    ds = xr.open_dataset(file, engine="h5netcdf")
    #load subet
    ds = ds.load()
    #select field
    field = ds[variable]
    
    #map lat lon to closest x-y pair

    londf = pd.DataFrame(field['lon'].values)
    latdf = pd.DataFrame(field['lat'].values)
    
    min_londf_mat = (londf-lon).abs().values
    min_latdf_mat = (latdf-lat).abs().values

    min_diff_df = pd.DataFrame(min_londf_mat + min_latdf_mat)

    x_index_equi = min_diff_df.min(axis='index').idxmin()
    y_index_equi = min_diff_df[x_index_equi].idxmin()

    x_equi = float(field['x'][x_index_equi].values)
    y_equi = float(field['y'][y_index_equi].values)
    
    #subset by the equivalent x and y coordinates
    local_data = field.sel(x=x_equi, y=y_equi)
    
    #xarray to pandas dataframe
    df = pd.DataFrame()
    df[variable] = local_data.values
    
    #formatting data
    df[variable] = pd.to_numeric(df[variable])
    df['datetime'] = local_data['time'].values
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    #formatting data units
    if variable == 'tas':
        df[variable] = df[variable]-273.15
    
    df = df.rename(columns={variable: settings['variables'][variable]['name']+'_'+sen})
    
    
    return df

#%% iterate over variables, senarios and runs

for vlinderstation in stationlist:
    
    stationname = vlinderstation['station']
    location_lat = vlinderstation['lat']
    location_lon = vlinderstation['lon']
    print("collecting data of ", stationname, flush=True)
    

    exportdf = pd.DataFrame()
    for variable in settings['variables']:
        print("Field:  ", variable, flush=True)
        vardf = pd.DataFrame()
        for sen in settings['senario']:
            print('Climate senario:  ', sen, flush=True)
            senariodf = pd.DataFrame()
            for run in settings['runs']:
    			#build filepath
                
                experiment_folder = os.path.join(datafolder, sen.upper() + '_be', run)
                experiment_folder = os.path.join(experiment_folder, 'CORDEX', 'output', 'be-04', 'RMIB-UGent', 'CNRM-CERFACS-CNRM-CM5', sen, 'r1i1p1', 'RMIB-UGent-ALARO-0', 'v1', settings['variables'][variable]['res'], variable)
    
                files = [os.path.join(experiment_folder, f) for f in listdir(experiment_folder) if isfile(join(experiment_folder, f))]
                for file in files:
                    subdf = read_eurocordex_at_coordinate_to_df(file=file,
                                                                variable=variable,
                                                                settings=settings,
                                                                sen=sen,
                                                                lat = location_lat,
                                                                lon = location_lon)
                    senariodf = senariodf.append(subdf)
            vardf = vardf.merge(senariodf, how='outer', left_index=True, right_index=True)
            vardf = vardf.sort_index()
        exportdf = exportdf.merge(vardf, how='outer', left_index=True, right_index=True)
    
    exportdf = exportdf.sort_index()

    # print("max datetime: ", exportdf.index.max() )
    # print("columns :", exportdf.columns)
    # print('head: ')
    # print(exportdf.head())

    # write data
    exportdf['station'] = stationname
    exportdf['lat'] = location_lat
    exportdf['lon'] = location_lon

    exportfile = os.path.join(outputfolder, stationname+'_cordexbe_data.csv')


    exportdf.to_csv(exportfile,
                    index=True,
                    sep=',',
                    float_format= "%.2f",
                    date_format=None)




