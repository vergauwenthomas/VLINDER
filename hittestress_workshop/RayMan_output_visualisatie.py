#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 16:44:30 2022

@author: thoverga
"""


import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import datetime
import os
import path_handler



#%% Create the stucture of dictionaries


def make_dirs_and_check_rayman_data_availability(vlinderlist, experiment, scenario):
    data_available = {stat: False for stat in vlinderlist}
    for station in vlinderlist:
        #1 station folder exist
        stationdir = os.path.join(path_handler.db_location, station)
        if not (os.path.exists(stationdir)):
            print('No dir found for ', station, ' at this location:', stationdir)
            os.makedirs(stationdir)
            print(stationdir, ' created')
        
        
        #2 check if rayman_output folder exist for this station
        rayman_output_dir = os.path.join(stationdir, 'rayman_output')
        if not(os.path.exists(rayman_output_dir)):
            print('No rayman_output dir found for ', station)
            os.makedirs(rayman_output_dir)
            print(rayman_output_dir, ' created')
            
        #3 check if figures folder exist
        barplots_dir = os.path.join(stationdir, 'figures')
        if not(os.path.exists(barplots_dir)):
            print('No figures dir found for ', station)
            os.makedirs(barplots_dir)
            print(barplots_dir, ' created')
        
        
        #4 check if the available data exists
        rayman_specific_output_file = os.path.join(rayman_output_dir, station + path_handler.paths_dict[experiment]['scenario'][scenario]['rayman_output_postfix'])
        if (os.path.exists(rayman_specific_output_file)):
            print('Rayman data found for ', station)
            data_available[station] = rayman_specific_output_file
     
    
    return {x: data_available[x] for x in data_available if data_available[x]!=False}       


#%% functions


#------------------------------------------Data read and format functions ------------------------------------------------

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

#---------------------------------------------------Barplot functions ----------------------------------------

def calculate_heatstress_category_frequencies(stationdf, hittestress_labels):

    # stationdf = total_df[total_df['station'] == station] #subset data for the given stationname
    
    #create counting table
    counts = stationdf[['dag/nacht','stress_categories']].groupby('dag/nacht')['stress_categories'].value_counts(normalize=True)
    counts.name = 'category_freq'
    counts = counts.reset_index()
    
    #format data structure 
    counts = counts.pivot(index='dag/nacht', columns='stress_categories', values='category_freq')
    counts = counts.fillna(0)


    #add labels that are missing
    for hitte_label in hittestress_labels:
        if not (hitte_label in counts.columns):
            counts[hitte_label] = 0
    
    counts = counts[hittestress_labels] #rearange columns from extreme cold to extreme hot
    
    #to percentage
    counts = counts * 100.
    
    return counts



def make_categorical_staggered_barplot(counts, ax, stationname, shrink_ratio_perc=15):
    
    #----------------------------------make bar plot -----------------------
    counts.plot.bar(stacked=True, colormap="jet", ax=ax)
    
    
    # --------------------------set legend -------------------------
    # Shrink current axis's height by x% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * (shrink_ratio_perc/100.),
                     box.width, box.height * (1-(shrink_ratio_perc/100))])
    
    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
              fancybox=True, shadow=True, ncol=5)
    
    
    # ------------------- Add procentage anotations ----------------------------
    for container in ax.containers:
    
        ax.bar_label(container, label_type='center',
                     fmt='%0.1f%%')
    
    
    #----------------Format axis ---------------------------------------------
    
    ax.yaxis.set_major_formatter(mtick.PercentFormatter()) #percentage sign for y axes
    ax.set_xticklabels(labels=list(counts.index), rotation=0, fontsize=15) #set dag/ nacht horizontal and with fontsize
    
    ax.set_xlabel('') #remove the x label 
    ax.set_ylabel('Percentage (%)')
    return ax





def make_barplot_of_station(station, rayman_path_to_file, path_to_save_fig, scenario_att, periode_att):
    
    #Read data
    df = read_rayman_output(rayman_path_to_file, station)
    
    
    #add categorical labels
    
    hittestress_labels = ['Extreme koudestress', 'Sterke koudestress', 'Matige koudestress',
                          'Lichte koudestress', 'Geen stress', 'Lichte hittestress', 
                          'Matige hittestress', 'Sterke hittestress', 'Extreme hittestress']

    df['stress_categories'] = pd.cut(x=df['PET'],
                                     bins=[-100, 4.1, 8.0, 13.0, 18.0, 23.0, 29.0, 35.0, 41.0, 100],
                                     right=True,
                                     labels=hittestress_labels)
    #Label dag/nacht regime
    def dag_nacht_labeler(row):
        if (row['datetime'] <= row['sunset']) and (row['datetime'] >= row['sunr']):
            return 'dag'
        else:
            return 'nacht'
    df = df.reset_index()
    df['dag/nacht'] = df.apply(dag_nacht_labeler, axis=1)
    
    
    
    counts = calculate_heatstress_category_frequencies(stationdf=df,
                                                       hittestress_labels=hittestress_labels)
    
    fig, ax = plt.subplots(figsize=(10,10))
    
    ax=make_categorical_staggered_barplot(counts=counts,
                                          ax=ax,
                                          stationname = station)
    
    ax.set_title('Hittestress ' + station + ' ' + scenario_att + ', ' + periode_att, fontsize=20)
    
    plt.savefig(path_to_save_fig)
    # plt.show()
    
# ------------------------------------------Time series functions -------------------------------------------------------


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
    
    
    

    
#%% Test with barplots
# paths_dict = path_handler.paths_dict

# for experiment in paths_dict:
#     print("Generate barplots for experiment: ", experiment)

#     for scenario in paths_dict[experiment]['scenario']:
#         print('In scenario: ',scenario )


#         #create dict with vlindername and corresponding rayman output folder
#         vlinderlist = ['Vlinder' + str(x).zfill(2) for x in path_handler.stationnumbers]
        
#         #make dictionaries and find which station have data available
#         available_stations = make_dirs_and_check_rayman_data_availability(vlinderlist,
#                                                                          experiment,
#                                                                          scenario)
        
        
#         for station in available_stations:
#             print(station)
#             rayman_file = available_stations[station]

#             fig_file = os.path.join(path_handler.db_location, station, 'figures', station + paths_dict[experiment]['scenario'][scenario]['barplot_postfix'])
#             print(fig_file)
            
#             period_att = paths_dict[experiment]['period_title_att']

#             if (paths_dict[experiment]['scenario'][scenario]['scalar_to_add'] == 0):
#                 scenario_att = '' #empty
#             else:
#                 #(scenario: temperatuur +2.5°C)
#                 scenario_att = '(scenario: ' + paths_dict[experiment]['scenario'][scenario]['var'].lower() + \
#                                 ' +' + str(paths_dict[experiment]['scenario'][scenario]['scalar_to_add']) + '°C)'
                
#             #Barplot
#             make_barplot_of_station(station, rayman_file, fig_file, scenario_att, period_att)    
            
            
#             #Timeseries plot
            
#             fig_file_timeseries_single_station = os.path.join(path_handler.db_location, station, 'figures', station + paths_dict[experiment]['scenario'][scenario]['timeseriesplot_postfix'])
#             make_timeseries_analysis_plot(station, available_stations, fig_file_timeseries_single_station, scenario_att )
            
#             #Group timeseries plot
            
#             for group in paths_dict[experiment]['scenario'][scenario]['comparison_stationnumbers']: #iterate over groups
#                 all_members_available=True
                
#                 stationsgroup = ['Vlinder' + str(nr).zfill(2) for nr in group] #groupnumbers to stationnames
#                 print('Generate timeseries plot for group: ', stationsgroup)
                
#                 #check if data is available for each groupmember
#                 for station in stationsgroup:
#                     if not station in available_stations:
#                         print('No data found for ', station, '. This group is skipped!!! ', stationsgroup)
#                         all_members_available=False

#                 if not all_members_available:
#                     continue #go to next group because at least one group member has missing data
                
            
                
#                 group_fig_path = os.path.join(path_handler.comp_plots_dir, 'Vlinders_' + '_'.join(map(str, group)) + paths_dict[experiment]['scenario'][scenario]['timeseriesplot_postfix'])
                
#                 make_timeseries_analysis_plot(stationsgroup, available_stations, group_fig_path, scenario_att )
            
