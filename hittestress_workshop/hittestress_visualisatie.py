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


#%%
input_folder = '/home/thoverga/Documents/VLINDER_github/VLINDER/hittestress_workshop/Rayman_output'

filename = 'Vlinder_57.txt'

Textfiles = [os.path.join(input_folder, filename)]


labels = ['VLINDER 57'] #the name of the vlinder stations, in the same order as the data files!!



#%% Reading and formatting data


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


#%% Testing

newdf = total_df.copy()

newdf['PET'] = newdf['PET'] - 4.3
newdf['station'] = 'test'

total_df = total_df.append(newdf)




#%% create sunset/sunrise series
sunrises = total_df['sunr'].unique()
sunsets = total_df['sunset'].unique()

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
                                



#%% make multiline plot


# -------------------------------------make figure --------------------------------------------------
fig, axs = plt.subplots(nrows=5,ncols=1,figsize=(36,36))


def make_timeseries_plot(ax, variable, totaldf, sunsets, sunrises, ylabel):
    # --------------------------Add variable lines graphs -----------------------------------------------------------
    
    #make pivot table where the columns represent the variable for different stations
    pivot = total_df.pivot(columns='station', values=variable)
    
    pivot.plot(ax=ax)

    # ---------------------------make day/night vertical extends in the graph --------------------------------
    for index in zip(sunrises, sunsets):
        ax.axvspan(index[0], index[1], facecolor='gray', alpha=0.5)
        
        
        
        
    # --------------------------Style attributes ------------------------------------------------------------------
    
    ax.set_ylabel(ylabel)
        
    ax.legend(loc='upper right')
        
        
    return ax

axs[0] = make_timeseries_plot(ax = axs[0], variable='PET', totaldf=total_df,
                              sunsets=sunsets, sunrises=sunrises, 
                              ylabel = 'PET-score (°C)')

axs[1] = make_timeseries_plot(ax = axs[1], variable='Temperature', totaldf=total_df,
                              sunsets=sunsets, sunrises=sunrises,
                              ylabel = 'Temperatuur (°C)')

axs[2] = make_timeseries_plot(ax = axs[2], variable='Windspeed', totaldf=total_df,
                              sunsets=sunsets, sunrises=sunrises,
                              ylabel = 'Windsnelheid (m/s)')

axs[3] = make_timeseries_plot(ax = axs[3], variable='Relative_Humidity', totaldf=total_df,
                              sunsets=sunsets, sunrises=sunrises,
                              ylabel='Relatieve vochtigheid (%)')

axs[4] = make_timeseries_plot(ax = axs[4], variable='Global_radiation', totaldf=total_df,
                              sunsets=sunsets, sunrises=sunrises,
                              ylabel='Straling ($W/m^2$)')

axs[0].set_title('Hittestress analyse', fontsize=80)


# plt.savefig('Grafieken.pdf')
plt.show()




















#%% create normalized category frequncies


def calculate_heatstress_category_frequencies(total_df, station, hittestress_labels):

    stationdf = total_df[total_df['station'] == station] #subset data for the given stationname
    
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
    ax.set_title('Hittestress: ' + stationname, fontsize=20)
    
    return ax




#%% categorize PET
hittestress_labels = ['Extreme koudestress', 'Sterke koudestress', 'Matige koudestress',
                      'Lichte koudestress', 'Geen stress', 'Lichte hittestress', 
                      'Matige hittestress', 'Sterke hittestress', 'Extreme hittestress']

total_df['stress_categories'] = pd.cut(x=total_df['PET'],
                                       bins=[-100, 4.1, 8.0, 13.0, 18.0, 23.0, 29.0, 35.0, 41.0, 100],
                                       right=True,
                                       labels=hittestress_labels)



#Label dag/nacht regime
def dag_nacht_labeler(row):
    if (row['datetime'] <= row['sunset']) and (row['datetime'] >= row['sunr']):
        return 'dag'
    else:
        return 'nacht'
    
    
    
    
total_df = total_df.reset_index()
total_df['dag/nacht'] = total_df.apply(dag_nacht_labeler, axis=1)


stationlist = total_df['station'].unique()
for station in stationlist:

    counts = calculate_heatstress_category_frequencies(total_df=total_df,
                                                       station = station,
                                                       hittestress_labels=hittestress_labels)
    
    fig, ax = plt.subplots(figsize=(10,10))
    
    ax=make_categorical_staggered_barplot(counts=counts,
                                          ax=ax,
                                          stationname = station)
    
    # plt.savefig('Grafieken2.pdf')
    plt.show()
