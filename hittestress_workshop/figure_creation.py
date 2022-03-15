#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 15:04:43 2022

Input arguments -experiment -vlindernames_array -basefolder
return: (print statments) NULL (if error or missing data), unique name of file in the figure folder.


example
./figure_creation.py --aug --stationarray=[Vlinder02, Vlinder59] --basedir=/home/thoverga/Desktop/workshop_data/db

** ASSUMPTIONS:
    
    * In the basedir directory is a subdirectory with the name set by 'db_name' (see IO hardcoded).
        (basedir = ../../vlinder/WWW/hitteworkshop) I assume
    * the stationarray list contains the name of the vlinderstations, WITH capital V!
    * It is possible to give a stationarray with only one station
    
    
@author: thoverga
"""

import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import random
import string
from datetime import datetime


#%% IO hardcoded 

#!!! BRIAN, DEZE LIJNEN ZUL JE MISSCHIEN NOG MOETEN AANPASSEN.

figdir_name = 'FIGURES' #dir where to place the generated figures

db_name = 'db' #where the data is stored (this directory should be a subdirectory of the basedir!)
db_name = 'brian_db'
""" Directory structure:
    
    ../.. 'basedir'../'db_name'/ 
    should contain folders like:
        ../.. 'basedir'../'db_name'/Vlinder02/ #this directory contains the figures specific to this station (and a subfolder: data/)
        ../.. 'basedir'../'db_name'/Vlinder02/data/ #this directory contains the output txt files from Rayman
        
"""








#%% ---------------------------------Arguments ----------------------------------------------
parser = argparse.ArgumentParser(description='Simple script to retrieve figures, (or make them) from a folder for the VLINDER workshop on heatstress.')


parser.add_argument('--aug', action='store_true',
                    help='If this argument is given, the august experiment figures will be returned')

parser.add_argument('--scenario15', action='store_true',
                    help='If this argument is given, the august scenario +1.5°C experiment figures will be returned')

parser.add_argument('--scenario25', action='store_true',
                    help='If this argument is given, the august scenario +2.5°C experiment figures will be returned')

# Station array
parser.add_argument('--stationarray', type=str, required=True, 
                    help='Array of stationnames ex: [Vlinder02, Vlinder15, Vlinder16]')

# Base path
parser.add_argument('--basedir', type=str, required=True, 
                    help='Base directory of share???')

args = parser.parse_args()

#%% ---------------------------------------------------- Helperfunctions ----------------------------------------------------------

errorcodes_to_human = { 0: 'Succesfull',
                        1: 'Stationnumber is not in the dataset (or not an int)',
                        2: 'No valid experiment is selected',
                        3: 'Multiple experiments are selected, select only one',
                        4: 'No heatstress data available for the selected station and experiment',
                        5: 'basedir does not exist or could not be found.',
                        6: 'not all titan data is available'
                        }   
errorcodes_to_robot = { 0: 'Succesfull',
                        1: 'NULL', #'Stationnumber is not in the dataset (or not an int)',
                        2: 'NULL', #'No valid experiment is selected',
                        3: 'NULL', #'Multiple experiments are selected, select only one',
                        4: 'NULL', #'No heatstress data available for the selected station and experiment'
                        5: 'NULL', #basedir does not exist or could not be found.
                        6: 'NULL', #not all titan data is available
                        }   

def stop_and_set_errorcode(errornumber, path_to_files=None):
    # os.environ[_EXPORT_VARIABLE] = str(errornumber)
    if errornumber!=0:
        print(errorcodes_to_robot[errornumber], flush=True)
    sys.exit(1)


#%% --------------------------------Arguments checks --------------------------------------------

#1 check if at least one experiment arguments
if not any([args.aug, args.scenario15, args.scenario25]):
    stop_and_set_errorcode(2)

if ([args.aug, args.scenario15, args.scenario25].count(True) > 1):
    stop_and_set_errorcode(3)

if args.aug:
    experiment='aug'
elif args.scenario15:
    experiment='scenario15'
else:
    experiment='scenario25'


#2. Check
#check if multiple stations are given


#%% ------------------------------------Path Checks ------------------------------------------
#Check if basedir exist
BASEDIR = args.basedir
if not os.path.isdir(BASEDIR):
    stop_and_set_errorcode(5)    

    
#create figure dir if it does not exist as a submap of the BASEDIR
FIGDIR = os.path.join(BASEDIR,figdir_name)
if not os.path.isdir(FIGDIR):
    os.makedirs(FIGDIR)
      
    
    

#remove brackets, leading and trailing witespaces and make list by splitting on the ,-sign
vlinderlist = args.stationarray.replace('[', '').replace(']', '').strip().split(',')


def create_path_to_datafile(stationname, experiment):
    if experiment == 'aug': 
        file_postfix = ''
    elif experiment == 'scenario15':
        file_postfix = 'scenario_1-5_'
    else:
        file_postfix = 'scenario_2-5_'
    filepath = os.path.join(BASEDIR, db_name, stationname, 'data',
                            stationname + '_aug_' + file_postfix + 'rayman_output.txt')
    return filepath
    

vlinderfilelist = [create_path_to_datafile(x, experiment) for x in vlinderlist]
#check if Raymandata is available for the stations and for the experiment
all_data_is_available = all([os.path.exists(x) for x in vlinderfilelist])
if not all_data_is_available:
    stop_and_set_errorcode(6)
    
#a dict to map the station to its datafile
station_and_file_dict = dict(zip(vlinderlist, vlinderfilelist))




#create random name for odef get_random_string(length):
def create_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    result_str = result_str+str(datetime.now().strftime("%Y%m%d%Hh%Mm%S")) # add current time to avoid seeding problems on restarts
    return result_str +'.png'

output_file_name = create_random_string(6)


#%% create figure

def read_rayman_output(filepath, station):
   
    
    #Read data and skip the first lines
    
    df = pd.read_csv(filepath, delimiter='\t', skiprows=[0,1,2,4])
    
    
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
    df['station'] = station
    
    #rename columns
    df = df.rename(columns={'Ta': 'Temperature',
                            'RH': 'Relative_Humidity',
                            'v': 'Windspeed',
                            'Gact': 'Global_radiation'})
    #set datetime as index
    df = df.set_index('datetime')
    return df


def make_timeseries_analysis_plot(station, station_and_file_dict, fig_file, scenario_att ):
    
    
    
    if isinstance(station, str):
        single_station_mode = True
        df = read_rayman_output(station_and_file_dict[station], station)
    elif isinstance(station, list):
        #append data if a group of stations is given
        single_station_mode = False
        df = pd.DataFrame()
        for sta in station:
            subdf = read_rayman_output(station_and_file_dict[sta], sta)
            df = df.append(subdf)
    
    # ---------------------------------------Sub Functions -----------------------------------------------------
    
    def plot_one_timeseries(ax, variable, plotdf, sunsets, sunrises, ylabel):
        # Add variable lines graphs
        
        #make pivot table where the columns represent the variable for different stations
        pivot = plotdf.pivot(columns='station', values=variable)
        
        pivot.plot(ax=ax)
    
        # make day/night vertical extends in the graph
        for index in zip(sunrises, sunsets):
            ax.axvspan(index[0], index[1], facecolor='gray', alpha=0.5)
    
        # tyle attributes
        ax.set_ylabel(ylabel)
        ax.legend(loc='upper right')
        return ax
    
    def get_sunsets_and_sunrises(df):
       
        sunrises = df['sunr'].unique()
        sunsets = df['sunset'].unique()
        
        #depending on the start and end hour, there may be more sunsets or sunrises than the other
        if len(sunsets) > len(sunrises):
            #create a sunset one day before the first day
            new_sunrise = min(sunrises) - np.timedelta64(1, 'D')
            sunrises = np.append(sunrises, new_sunrise)
            sunrises = np.sort(sunrises)
        elif len(sunrises) > len(sunsets):
            #add sunset at the end of the datetime series
            new_sunset = max(sunsets) + np.timedelta64(1, 'D')
            sunsets = np.append(sunsets, new_sunset)
        return sunrises, sunsets
    
    
    
    
    # -------------------------------------make figure --------------------------------------------------
    fig, axs = plt.subplots(nrows=5,ncols=1,figsize=(30,18))
    titlesize = 40
    
    #get sunsets/sunrises
    sunrises, sunsets = get_sunsets_and_sunrises(df)
    
    
    
    axs[0] = plot_one_timeseries(ax = axs[0], variable='PET', plotdf=df,
                                  sunsets=sunsets, sunrises=sunrises, 
                                  ylabel = 'PET-score (°C)')
    
    axs[1] = plot_one_timeseries(ax = axs[1], variable='Temperature', plotdf=df,
                                  sunsets=sunsets, sunrises=sunrises,
                                  ylabel = 'Temperatuur (°C)')
    
    axs[2] = plot_one_timeseries(ax = axs[2], variable='Windspeed', plotdf=df,
                                  sunsets=sunsets, sunrises=sunrises,
                                  ylabel = 'Windsnelheid (m/s)')
    
    axs[3] = plot_one_timeseries(ax = axs[3], variable='Relative_Humidity', plotdf=df,
                                  sunsets=sunsets, sunrises=sunrises,
                                  ylabel='Relatieve vochtigheid (%)')
    
    axs[4] = plot_one_timeseries(ax = axs[4], variable='Global_radiation', plotdf=df,
                                  sunsets=sunsets, sunrises=sunrises,
                                  ylabel='Straling ($W/m^2$)')
    
    axs[0].set_title('Hittestress analyse ' + scenario_att, fontsize=titlesize)
    
    
    if single_station_mode:
        axs[0].get_legend().remove()
        axs[1].get_legend().remove()
        axs[2].get_legend().remove()
        axs[3].get_legend().remove()
        axs[4].get_legend().remove()
    
        axs[0].set_title('Hittestress analyse ' + station + ' ' + scenario_att, fontsize=titlesize)
    
    plt.savefig(fig_file)
    # plt.show()
    

#create title attributes for the experiments
title_scenario_att_dict = {'aug': '',
                           'scenario15': '(scenario: temperatuur +1.5°C)',
                           'scenario25': '(scenario: temperatuur +2.5°C)'}


#read data, make figure and save the figure
make_timeseries_analysis_plot(station = list(station_and_file_dict.keys()),
                              station_and_file_dict = station_and_file_dict,
                              fig_file = os.path.join(FIGDIR, output_file_name),
                              scenario_att = title_scenario_att_dict[experiment])

#print the name of the figure in the terminal
print(figdir_name + '/' + output_file_name)
sys.exit(0)