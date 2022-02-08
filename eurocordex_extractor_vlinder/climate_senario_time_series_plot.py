#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 08:45:32 2022

@author: thoverga
"""

import pandas as pd
import matplotlib.pyplot as plt


#BIG input files !
inputfile = "/home/thoverga/Documents/VLINDER_github/VLINDER/eurocordex_extractor_vlinder/vlinder01_cordexbe_data.csv"
outputfolder = "/home/thoverga/Documents/VLINDER_github/VLINDER/eurocordex_extractor_vlinder/figures"

#%%

def read_and_format_data(inputfile):
    
    
    df = pd.read_csv(inputfile)
    
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
df = read_and_format_data(inputfile)

station = 'VLINDER01'

#%% Subset to summer periods

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
    
    
make_and_save_plots(df, outputfolder, station)
    

    
    
    
    
    
# # plot




# #%% aggregate

# aggregation = 'max'




# #create weeknumber dict of the mean over the senarios for the max temperature that occured per week from start to 2021 to serve as reference

# def create_reference_temperature_dict(df, aggregation, endyear_ref=2021):

#     testperiod = df[df.index.to_series().dt.year <= endyear_ref] #select refperiod
    
#     # testperiod['daynumber'] = testperiod.index.to_series().dt.dayofyear #add dayofyear column
    
#     testperiod['weeknumber'] = testperiod.index.to_series().dt.weekofyear #add dayofyear column
#     # testperiod['monthnumber'] = testperiod.index.to_series().dt.weekofyear #add dayofyear column
    
    
    
#     # agg_refdf = testperiod.groupby('daynumber').agg(aggregation) #max temperature per day for each scenario over testperiod
#     agg_refdf = testperiod.groupby('weeknumber').agg(aggregation) #max temperature per week for each scenario over testperiod
#     # agg_refdf = testperiod.groupby('monthnumber').agg(aggregation)
    
#     agg_refdf['reftemp'] = agg_refdf[['RCP2.6', 'RCP4.5', 'RCP8.5']].mean(axis='columns') #mean of max's of the scenarios
    
    
#     refdict = agg_refdf['reftemp'].to_dict()
#     return refdict

# refdict_max = create_reference_temperature_dict(df, aggregation)



# #create relative temperature df

# df['weekofyear'] = df.index.to_series().dt.weekofyear
# # df['monthofyear'] = df.index.to_series().dt.month
# df['year'] = df.index.to_series().dt.year

# df['reftemp'] = df['weekofyear'].map(refdict_max)
# # df['reftemp'] = df['monthofyear'].map(refdict_max)

# df['datetime'] = df.index.to_series()


# agg_df = df.groupby(['year', 'weekofyear']).agg(aggregation)
# # agg_df = df.groupby(['year', 'monthofyear']).agg(aggregation)
# agg_df = agg_df.set_index('datetime')

# reftemp_series = agg_df['reftemp']
# agg_df = agg_df.drop(columns=['reftemp'])

# # agg_rel_df = agg_df.sub(reftemp_series,axis=0)


# #%% Per month
# test = agg_df

# test['month'] = test.index.to_series().dt.month 

# test = test[test['month'] == 8]

# test = test.drop(columns=['month'])

# ax = test.plot(kind='box', figsize=(15,10))
# ax.set_title('VLINDER01 weekly maximum temperature for august CordexBE ( boxplot)')


# #%%
# import math
# year_group_size = 20
# yearmin = min(test.index.to_series().dt.year)
# yearmax = max(test.index.to_series().dt.year)

# yearranger = range(yearmin, yearmax+1)

# group_mapper = {year: math.floor((year - yearmin)/(year_group_size)) for year in yearranger}



# test['year'] = test.index.to_series().dt.year
# test['group'] = test['year'].map(group_mapper)

# test = test.drop(columns=['year'])





# groups = test['group'].unique()

# groupname_dict = {}
# for group in groups:
#     subdf = test[test['group'] == group]
#     groupstart = str(min(subdf.index.to_series().dt.year))
#     groupend = str(max(subdf.index.to_series().dt.year))
    
#     groupname_dict[group] = "(" + groupstart + " - " + groupend + ")"
    


# test['group'] = test['group'].map(groupname_dict)
# # fig, axs = plt.subplots()
# axes = test.boxplot(by='group', figsize=(25,15))


# # axes = df.boxplot(by='g')

# fig = axes[0][0].get_figure()

# fig.suptitle('VLINDER01 weekly maximum temperature for august CordexBE (boxplot) grouped', fontsize=18)




# # fig.set_title('VLINDER01 weekly maximum temperature for august CordexBE ( boxplot)')
# #%% data resolutie aanpassen

# agg_rel_df['month'] = agg_rel_df.index.to_series().dt.month
# agg_rel_df['year'] = agg_rel_df.index.to_series().dt.year

# monthly_rel_df = agg_rel_df.groupby(['year', 'month']).agg('max')

# monthly_rel_df = monthly_rel_df.reset_index()

# monthly_rel_df['datemonth'] = monthly_rel_df['year'].astype(str) + ":" + monthly_rel_df['month'].astype(str)
# monthly_rel_df['datemonth'] = pd.to_datetime(monthly_rel_df['datemonth'], format="%Y:%m")

# monthly_rel_df = monthly_rel_df.set_index('datemonth')
# monthly_rel_df = monthly_rel_df.drop(columns=['year', 'month'])

# monthly_rel_df.plot(figsize=(25,10))


#%%

# fig, axs = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(25,15))


# axs[0] = aggregate_data(df,'max').plot(ax=axs[0])

# axs[0].set_title('Weekelijkse maximum temperatuur projecties')
# axs[1] = aggregate_data(df,'min').plot(ax=axs[1])

# axs[1].set_title('Weekelijkse minimum temperatuur projecties')


# fig.title = station + " weekelijkse maximum temperatuur projecties" 