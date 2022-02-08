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

#%% ------------------------------ Paths -------------------------------------
#cordex folder
datafolder = '/mnt/HDS_CORDEXBE_RMIB/CORDEXbe/ncdf_archive'

#output folder
kili_USER = os.getenv('USER')
outputfolder = os.path.join('/scratch', kili_USER, 'cordex_timeseries_output')
#create outputfolder if the folder does not exist
if not os.path.exists(outputfolder):
    os.makedirs(outputfolder)
    
if os.listdir(outputfolder):
    print("Outputdirectory (",outputfolder, ") is not empty!!")
    cont = input('The output directory can be overwritten! Continue? (y) :')
    if cont != 'y': exit(1)

print('Outputfolder: ', outputfolder, flush=True)


#coordinate inputfile (CSV)
coordinate_datafile = '/home/thoverga/fileserver/home/cs-mask/VLINDER/github/VLINDER/Data/data.csv'

station_id_column_name = 'VLINDER' #The name of the column with a unique station identifier (i.g. the name of the station)
lat_column_name = 'lat' #latitude column name
lon_column_name = 'lon' #longtitude clumn name

#%%---------------------------Read coordinates file --------------------------

#read data
coorddata = pd.read_csv(coordinate_datafile)

#check if id, lat and lon columns exist
if not (pd.Series([station_id_column_name, lat_column_name, lon_column_name]).isin(coorddata.columns).all()):
    print("statio_id - lat - lon column identiefiers not found in coordinate datafile: ",
          station_id_column_name, ' - ', lat_column_name, ' - ', lon_column_name)
    exit(1)


#create location list to iterate over 
stationlist = []
for _, row in coorddata.iterrows():
    stationlist.append({
                        'station': row[station_id_column_name],
                        'lat': row[lat_column_name],
                        'lon': row[lon_column_name]
                        })


#%% ---------------------Settigs for which timeseries should be made ----------

settings = {
    'variables':{
                'tas':{
                        'name': 'temperature',
                        'res': '3hr',
                        },
                # 'hurs':{
                        # 'name': 'relative_humidity',
                        # 'res': '3hr',
                        # },
                # 'pr':{
                        # 'name': 'precipitation',
                        # 'res': '3hr',
                        # },
                # 'vas':{
                        # 'name': 'N-wind',
                        # 'res': '6hr',
                        # },
                # 'uas':{
                        # 'name': 'E-wind',
                        # 'res': '6hr',
                        # },
                        
            },
    'senario': ['rcp26', 'rcp45', 'rcp85'],
    #'senario': ['rcp26', 'rcp45'],
    'runs': ['200601', '204001', '207001'],
    #'runs': ['200601']
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
    #TODO the equivalent x-y pair extraction should be made cleaner

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


def read_and_format_data(df):
    
    
    #df = pd.read_csv(inputfile)
    
    columns_to_keep = ['datetime', 'temperature_rcp26', 'temperature_rcp45', 'temperature_rcp85', 'station']
    
    df = df[columns_to_keep]
    
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d %H:%M:%S')
    
    df = df[df['datetime'].dt.minute == 0] #remove nan rows
    
    df = df.set_index('datetime') 
    
    station = df['station'].iloc[0]
    df = df.drop(columns=['station'])
    
    df = df.rename(columns={'temperature_rcp26': 'RCP2.6',
                            'temperature_rcp45': 'RCP4.5',
                            'temperature_rcp85': 'RCP8.5'})
    return df

def make_and_save_plots(df, outputfolder, station):

    months_to_keep = [7,8,9]
    df['month'] = df.index.to_series().dt.month
    
    
    subdf = df[df['month'].isin(months_to_keep)]
    
    subdf['year'] = subdf.index.to_series().dt.year
    
    
    
    #optie 1 : maximum temp per jaar
    subfolder='/yearly/'
    
    subdf_to_plot = subdf.drop(columns=['month'])
    agg = subdf_to_plot.groupby('year').agg('max')
    
    ax = agg.plot(kind='line', figsize=(20,10))
    ax.set_title(station + ': De maximum temperatuur tijdens de zomer.')
    plt.grid()
    plt.ylabel('Temperatuur (°C)')
    plt.xlabel('Jaar')
    
    figname=str(outputfolder)+str(subfolder)+str(station)+'_tijdreeks.png'
    plt.savefig(figname)
    
    
    ax = agg.plot(kind='box', figsize=(10,10))
    ax.set_title(station + ': De maximum temperatuur tijdens de zomer.')
    plt.grid()
    plt.ylabel('Temperatuur (°C)')
    plt.xlabel('Scenario')
    
    figname=str(outputfolder)+str(subfolder)+str(station)+'_boxplot.png'
    plt.savefig(figname)
    
    ax = agg.plot(kind='kde', figsize=(10,10))
    ax.set_title(station + ': De maximum temperatuur tijdens de zomer.')
    plt.grid()
    plt.xlabel('Temperatuur (°C)')
    plt.ylabel('Dichtheid')
    
    figname=str(outputfolder)+str(subfolder)+str(station)+'_kde.png'
    plt.savefig(figname)
    
    
    #optie 2: gemiddelde van de maandelijkse maxima in de zomer
    
    subfolder='/monthly/'
    agg=subdf.groupby(['year', 'month']).agg('max')
    agg = agg.groupby('year').agg('mean')
    
    
    ax = agg.plot(kind='line', figsize=(20,10))
    ax.set_title(station + ': Het gemiddelde van de maandelijkse maximum temperatuur tijdens de zomer.')
    plt.grid()
    plt.ylabel('Temperatuur (°C)')
    plt.xlabel('Jaar')
    
    figname=str(outputfolder)+str(subfolder)+str(station)+'_tijdreeks.png'
    plt.savefig(figname)
    
    ax = agg.plot(kind='box', figsize=(10,10))
    ax.set_title(station + ': De maximum temperatuur tijdens de zomer.')
    plt.grid()
    plt.ylabel('Temperatuur (°C)')
    plt.xlabel('Scenario')
    
    figname=str(outputfolder)+str(subfolder)+str(station)+'_boxplot.png'
    plt.savefig(figname)
    
    ax = agg.plot(kind='kde', figsize=(10,10))
    ax.set_title(station + ': De maximum temperatuur tijdens de zomer.')
    plt.grid()
    plt.xlabel('Temperatuur (°C)')
    plt.ylabel('Dichtheid')
    
    figname=str(outputfolder)+str(subfolder)+str(station)+'_kde.png'
    plt.savefig(figname)
    
    #optie 3: gemiddelde van de weekelijkse maxima in de zomer
    subfolder='/weekly/'
    
    subdf_to_plot = subdf
    subdf_to_plot = subdf_to_plot.drop(columns=['month'])
    subdf_to_plot['week'] = subdf_to_plot.index.to_series().dt.weekofyear
    agg=subdf_to_plot.groupby(['year', 'week']).agg('max')
    agg = agg.groupby('year').agg('mean')
    
    ax = agg.plot(kind='line', figsize=(20,10))
    ax.set_title(station + ': Het gemiddelde van de weekelijkse maximum temperatuur tijdens de zomermaanden.')
    plt.grid()
    plt.ylabel('Temperatuur (°C)')
    plt.xlabel('Jaar')
    
    figname=str(outputfolder)+str(subfolder)+str(station)+'_tijdreeks.png'
    plt.savefig(figname)
    
    ax = agg.plot(kind='box', figsize=(10,10))
    ax.set_title(station + ': De maximum temperatuur tijdens de zomer.')
    plt.grid()
    plt.ylabel('Temperatuur (°C)')
    plt.xlabel('Scenario')
    
    figname=str(outputfolder)+str(subfolder)+str(station)+'_boxplot.png'
    plt.savefig(figname)
    
    ax = agg.plot(kind='kde', figsize=(10,10))
    ax.set_title(station + ': De maximum temperatuur tijdens de zomer.')
    plt.grid()
    plt.xlabel('Temperatuur (°C)')
    plt.ylabel('Dichtheid')
    
    figname=str(outputfolder)+str(subfolder)+str(station)+'_kde.png'
    plt.savefig(figname)

#%% iterate over variables, senarios and runs

for station in stationlist:
    
    stationname = station['station']
    location_lat = station['lat']
    location_lon = station['lon']
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
                experiment_folder = os.path.join(experiment_folder, 'CORDEX', 'output', 'be-04', 'RMIB-UGent',
                                                 'CNRM-CERFACS-CNRM-CM5', sen, 'r1i1p1', 'RMIB-UGent-ALARO-0',
                                                 'v1', settings['variables'][variable]['res'], variable)
    
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

    # write metadata (handy if multiple timeseries for different locations are compaired)
    exportdf['station'] = stationname
    exportdf['lat'] = location_lat
    exportdf['lon'] = location_lon
    
    #make figures and export them
    
    figdf = read_and_format_data(exportdf)
    make_and_save_plots(figdf, outputfolder, stationname)
    

    
    #Export data
    exportfile = os.path.join(outputfolder, stationname+'_cordexbe_timeseries_data.csv')
    exportdf = exportdf[~exportdf.index.duplicated(keep='first')] #keep first to exclude model-spinup-out-of-balance problems

    #write file
    exportdf.to_csv(exportfile,
                    index=True,
                    sep=',',
                    float_format= "%.2f",
                    date_format=None)




