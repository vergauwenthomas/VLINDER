#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 13:14:04 2022

Getting the data:
    1) To download the data use the Brian-Tool: https://vlinder.ugent.be/vlinderdata/multiple_vlinders.php
        (Cisco needed for VPN connection)
    2) save the data as a csv file, and set variable 'datafile' as the path to that file
    
    3) specify an output folder

    4) execute this script


format vlinder data, apply consecutive check, makes datafiles per station (one for further google sheets 


@author: thoverga
"""
import os 
import pandas as pd
import path_handler


#%% IO


max_consec = 30 #repetetive 5min update observations
time_resolution = '30min' #resolution of the output files


#%% Path formers



paths_dict = path_handler.paths_dict

#%% create folder and data folder inside for each station

folderprefix = 'Vlinder'

station_datadir_mapper = {} #dict to get path to each datadir for each station
station_raymandir_mapper = {} #dict to get path to each raymandir for each station


for vlindernummer in path_handler.stationnumbers:
    stationname='vlinder'+ str(vlindernummer).zfill(2)
    stationdir = os.path.join(path_handler.db_location, folderprefix + str(vlindernummer).zfill(2)) #ex; create Vlinder02 
    
    stationdir_data = os.path.join(stationdir, 'data') #ex; Vlinder02/data
    #check if folder exists and create it if not.
    if not (os.path.exists(stationdir_data)):
        print('Creating datadir for ', stationname)
        os.makedirs(stationdir_data)
            
    station_datadir_mapper[stationname] = stationdir_data
    
    stationdir_rayman = os.path.join(stationdir, 'rayman_output') #ex; Vlinder02/data
    #check if folder exists and create it if not.
    if not (os.path.exists(stationdir_rayman)):
        print('Creating datadir for ', stationname)
        os.makedirs(stationdir_rayman)
            
    station_raymandir_mapper[stationname] = stationdir_rayman
    
    
#%% formatting functions
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

def get_rayman_compatible_format(subdf_rayman):
    
    #select only the good observations
    subdf_rayman = subdf_rayman[subdf_rayman['status'] == 'ok']
    
    #format to rayman standard daytime format
    subdf_rayman['_datetime'] = pd.to_datetime(subdf_rayman.index.to_series(), format='%d-%m-%Y %H:%M:%S')
    
    subdf_rayman['date'] = subdf_rayman['_datetime'].dt.strftime('%-d.%-m.%Y')
    subdf_rayman['time'] = subdf_rayman['_datetime'].dt.strftime('%-H:%M')
    
    #windspeed to m/s
    subdf_rayman['Windsnelheid'] = subdf_rayman['Windsnelheid'].astype(float)
    subdf_rayman['Windsnelheid'] = subdf_rayman['Windsnelheid'] / 3.6
    
    
    format_float_columns = ['Temperatuur', 'Vochtigheid', 'Windsnelheid']
    for form_column in format_float_columns:
        subdf_rayman[form_column] = subdf_rayman[form_column].astype(float)
        subdf_rayman[form_column] = subdf_rayman[form_column].map('{:,.1f}'.format)
        subdf_rayman[form_column] = subdf_rayman[form_column].astype(str)
        
        
    export_columns = ['date', 'time', 'Temperatuur', 'Vochtigheid', 'Windsnelheid']
    return subdf_rayman[export_columns]


def rayman_output_to_google_format(path_to_rayman_output, stationname):
    #Read data and skip the first lines
    df = pd.read_csv(path_to_rayman_output, delimiter='\t', skiprows=[0,1,2,4])
    
    
    #formatting columns
    #remove trailing and leading whitespaces in the column names
    df.columns = [colstring.rstrip().lstrip() for colstring in df.columns]
    
    
    #datetime
    df['datetime'] = df['date'] + ' ' + df['time']
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M')
    

    
    #subset relevant columns
    columns_to_keep = ['datetime', 'Ta', 'RH', 'v', 'PET', 'Gact']
    df = df[columns_to_keep]
    
    #Set numeric columns to float
    numeric_columns = ['Ta', 'RH', 'v', 'PET', 'Gact']
    for col in numeric_columns:
        df[col] = df[col].astype(float)
    
    
    
    
    #add station name
    df['station'] = stationname
    
    #rename columns
    df = df.rename(columns={'Ta': 'Temperatuur (°C)',
                            'RH': 'Relatieve Vochtigheid (%)',
                            'v': 'Windsnelheid (m/s)',
                            'Gact': 'Straling (W/m²)'})
    #set datetime as index
    df = df.set_index('datetime')
    df.index = df.index.to_series().dt.strftime('%d-%m-%Y %H:%M:%S')
    return df



#%% 
for experiment in paths_dict:
    print("Generate data for experiment: ", experiment)

    #open datafile
    df = pd.read_csv(paths_dict[experiment]['datafile'], sep=';') 
    
    #format data
    df['datetime'] = df['Datum'] + ' ' + df['Tijd (UTC)']
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
    df.set_index(df['datetime'], inplace=True)
    df['Temperatuur'] = df['Temperatuur'].astype(float)

    df_default = df.copy(deep=True)
    
    for scenario in paths_dict[experiment]['scenario']:
        print('In scenario: ',scenario )
        
        #extract info from dict for readability
        var = paths_dict[experiment]['scenario'][scenario]['var']
        to_add = paths_dict[experiment]['scenario'][scenario]['scalar_to_add']
        google_sheets_posf = paths_dict[experiment]['scenario'][scenario]['google_sheets_postfix']
        input_to_rayman_posf = paths_dict[experiment]['scenario'][scenario]['rayman_input_postfix']
        output_of_rayman_posf = paths_dict[experiment]['scenario'][scenario]['rayman_output_postfix']
        output_of_rayman_in_google_form_posf = paths_dict[experiment]['scenario'][scenario]['google_sheets_rayman_output_postfix']
        
        
        df = df_default.copy()
        df[var] = df[var] + to_add

    
        stationlist = df['Vlinder'].unique()
        totaldf = pd.DataFrame()
        for station in stationlist:
            
            print(station)
            subdf = df[df['Vlinder']==station]
            #quality control
            subdf = check_station_consec(subdf, max_consec)
            
            
            #refactor columns for writing to file
            starttime = subdf.index.min()
            endtime = subdf.index.max()
        
            selected_datetimes = pd.date_range(start=starttime,
                                           end=endtime,
                                           freq=time_resolution)
            
            
            # subdf = subdf.loc[selected_datetimes.to_series()] using this is dangerous, if a value is Nan for the given timestep or missing it raises an error
            subdf = subdf.loc[subdf.index.intersection(selected_datetimes)]
            
            
            subdf.index = subdf.index.to_series().dt.strftime('%d-%m-%Y %H:%M:%S')
            
            
            
            #drop non-relevant columns
            subdf.drop(columns=['datetime', 'Datum', 'Tijd (UTC)', 'Luchtdruk_Zeeniveau'], inplace=True)
            
            
            
            
            #write subdf
            subdf_google_sheets = subdf.copy()
            
            subdf_google_sheets = subdf_google_sheets.rename(columns={'Vochtigheid': 'Relatieve Vochtigheid'})
            subdf_google_sheets.index.name='Datetime'
            export_columns = ['Temperatuur', 'Relatieve Vochtigheid', 'Luchtdruk', 'Neerslagintensiteit',
                              'Neerslagsom', 'Windrichting', 'Windsnelheid', 'Rukwind', 'Vlinder',
                              'status']
            
            
            
            google_filename = os.path.join(station_datadir_mapper[station], station.capitalize() + google_sheets_posf )
            subdf_google_sheets[export_columns].to_csv( path_or_buf = google_filename,
                                                       header=True,
                                                       index=True,
                                                       sep='\t', 
                                                       decimal=',',
                                                       encoding='utf-8')
            
            
            
            
            #make format compatible with rayman
            rayman_subdf = get_rayman_compatible_format(subdf)
            
        
        
            #write rayman compatible subdf
            rayman_filename = os.path.join(station_datadir_mapper[station], station.capitalize() + input_to_rayman_posf )
            rayman_subdf.to_csv( path_or_buf = rayman_filename,
                                header=True,
                                index=False,
                                sep='\t', 
                                decimal='.',
                                encoding='utf-8') 
            

        
        
            #Check if rayman output is present, and if so make a google sheets compatible version in the rayman dir
            rayman_output_file = os.path.join(station_raymandir_mapper[station], station.capitalize() + output_of_rayman_posf) #To read!!
            
            if (os.path.exists(rayman_output_file)): #Rayman output is available
                print(station, ' Rayman output is available, i will make a google compatible version...')
                
                #Read data and format it
                rayman_in_google_df = rayman_output_to_google_format(rayman_output_file, station)
                
                #write the data to a google formated file
                rayman_in_google_form_file = os.path.join(station_raymandir_mapper[station], station.capitalize() + output_of_rayman_in_google_form_posf) #To write!!
                
                rayman_in_google_df.to_csv(path_or_buf = rayman_in_google_form_file,
                                           header=True,
                                           index=True,
                                           sep='\t', 
                                           decimal=',',
                                           encoding='utf-8')