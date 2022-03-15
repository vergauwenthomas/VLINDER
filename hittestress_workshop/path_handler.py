#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 08:59:16 2022

@author: thoverga
"""

import os

#%% HARDCODED 
db_location = "/home/thoverga/Desktop/workshop_data/db"
input_data_dir = '/home/thoverga/Desktop/workshop_data/db/Bulk_data' #where the downloaded datafiles are
rayman_data_dir =  '/home/thoverga/Desktop/workshop_data/db/Rayman_output' #where the rayman outputfiles are
fisheye_fotos_dir = '/home/thoverga/Desktop/workshop_data/db/fisheye_fotos' #where the fisheyefotos are 

#%% Relatives
#Comparison folder
#check if the 'comparison_plots' folder exist
comp_plots_dir = os.path.join(db_location, 'comparison_plots')
if not (os.path.exists(comp_plots_dir)):
    print('No comparison_plots folder found, this will be created: ', comp_plots_dir)
    os.makedirs(comp_plots_dir)

#google db dir: this contains google compatible data files in a structure so that it can easely be uploaded as a google drive db
google_db = os.path.join(db_location, 'google_db')
if not (os.path.exists(google_db)):
    print('No google_db folder found, this will be created: ', google_db)
    os.makedirs(google_db)
    
    
#brian_db folder contains the figures, that are compatible with the brian online tool for the workshop 
brian_db = os.path.join(db_location, 'brian_db')
if not (os.path.exists(brian_db)):
    print('No brian_db folder found, this will be created: ', google_db)
    os.makedirs(brian_db)

#subfolders
datafoldername = 'data' #folder that contains the observational data inside the station folder
raymanfoldername = 'rayman_output' #folder that contains the raymandata inside the station folder


#fisheye fotos
fisheye_foto_format = 'jpg'

#%% 

stationnumbers = list(range(1, 59+1)) #the stations to include as a list of numbers




paths_dict = {
    "august": {
                'datafile': os.path.join(input_data_dir, 'all_stations_aug_2020.csv'),
                'period_title_att': 'augustus 2020', #will be added in the title of the figures
                'scenario': {'scenario0': {
                                        #Data formatting
                                        'var': 'Temperatuur',
                                        'scalar_to_add': 0.0,
                                        # 'google_sheets_postfix': '_data_aug_google.csv', #ex; Vlinder02_data_aug_google.csv
                                        'google_sheets_postfix': '_data_aug_google.csv', #ex; Vlinder02_data_aug_google.csv
                                        'google_sheets_rayman_output_postfix': '_rayman_output_aug_google.csv', #ex; Vlinder02_data_aug_google.csv
                                        'rayman_input_postfix': '_data_aug_rayman.csv', #ex; Vlinder02_data_aug_rayman.csv
                                        
                                        #google_db
                                        'google_db_folder_base_name': 'augustus_2020', #basename of folder for the google db for this experiment
                                        
                                        #figure generator
                                        'rayman_output_postfix': '_aug_rayman_output.txt', #for making plots
                                        'barplot_postfix': '_aug2020_bar.png', #the postfix of the barplot
                                        'timeseriesplot_postfix': '_aug2020_time.png', #the postfix of the timeseries gigure
                                        'comparison_stationnumbers': [[2,27,59], #ghent group for timeseries plot
                                                                      [36, 42, 57], #test group
                                                                      ],
                                        'comparison_postfix': '_aug2020_time.png',
                                        #fig title attributes
                                        'fig_scenario_att': '',
                                        'fig_time_att': 'augustus 2020'
                                    },
                            'scenario1': {
                                        'var': 'Temperatuur',
                                        'scalar_to_add': 1.5,
                                        'google_sheets_postfix': '_data_aug_scenario_1-5_google.csv', #ex; Vlinder02_data_aug_scenario_1-5_google.csv
                                        'google_sheets_rayman_output_postfix': '_rayman_output_aug_scenario_1-5_google.csv', #ex; Vlinder02_data_aug_google.csv
                                        'rayman_input_postfix': '_data_aug_scenario_1-5_rayman.csv', #ex; Vlinder02_data_aug_scenario_1-5_rayman.csv
                                        
                                        #google_db
                                        'google_db_folder_base_name': 'augustus_2020_1-5', #basename of folder for the google db for this experiment
                                   
                                        'rayman_output_postfix': '_aug_scenario_1-5_rayman_output.txt', #for making plots
                                        'barplot_postfix': '_aug2020_scenario15_bar.png', #the postfix of the barplot
                                        'timeseriesplot_postfix': '_aug2020_scenario15_time.png', #the postfix of the timeseries gigure
                                        'comparison_stationnumbers': [[2,27,59], #ghent group for timeseries plot
                                                                      [36, 42, 57],  #test group
                                                                      ],
                                        'comparison_postfix': '_aug2020_scenario15_time.png',
                                        #fig title attributes
                                        'fig_scenario_att': '(scenario: temperatuur +1.5°C)',
                                        'fig_time_att': 'augustus 2020'
                                    },
                            'scenario2': {
                                        'var': 'Temperatuur',
                                        'scalar_to_add': 2.5,
                                        'google_sheets_postfix': '_data_aug_scenario_2-5_google.csv', #ex; Vlinder02_data_aug_scenario_2-5_google.csv
                                        'google_sheets_rayman_output_postfix': '_rayman_output_aug_scenario_2-5_google.csv', #ex; Vlinder02_data_aug_google.csv
                                        'rayman_input_postfix': '_data_aug_scenario_2-5_rayman.csv', #ex; Vlinder02_data_aug_scenario_2-5_rayman.csv
                                        
                                        #google_db
                                        'google_db_folder_base_name': 'augustus_2020_2-5', #basename of folder for the google db for this experiment
                                   
                                        'rayman_output_postfix': '_aug_scenario_2-5_rayman_output.txt', #for making plots 
                                        'barplot_postfix': '_aug2020_scenario25_bar.png', #the postfix of the barplot
                                        'timeseriesplot_postfix': '_aug2020_scenario25_time.png', #the postfix of the timeseries gigure
                                        'comparison_stationnumbers': [[2,27,59], #ghent group for timeseries plot
                                                                      [36, 42, 57], #test group
                                                                      ],
                                        'comparison_postfix': '_aug2020_scenario25_time.png',
                                        #fig title attributes
                                        'fig_scenario_att': '(scenario: temperatuur +2.5°C)',
                                        'fig_time_att': 'augustus 2020'
                                   }
                            }
                },
    # '2021': {
    #         'datafile': os.path.join(input_data_dir, 'all_stations_2021.csv'),
    #         'period_title_att': '2021 - 2022', #will be added in the title of the figures
    #         'scenario': {
    #                 'scenario0': {
    #                             'var': 'Temperatuur',
    #                             'scalar_to_add': 0.0,
    #                             'google_sheets_postfix': '_data_2021_google.csv', #ex; Vlinder02_data_2021_google.csv
    #                             'google_sheets_rayman_output_postfix': '_rayman_output_2021_google.csv', #ex; Vlinder02_data_aug_google.csv
    #                             'rayman_input_postfix': '_data_2021_rayman.csv', #ex; Vlinder02_data_2021_rayman.csv
                                
    #                             'rayman_output_postfix': '_2021_rayman_output.txt', #for making plots
    #                             'barplot_postfix': '_2021_PET_bar.pdf', #the postfix of the barplot
    #                             'timeseriesplot_postfix': '_2021_PET_timeseries.pdf', #the postfix of the timeseries gigure
    #                             'comparison_stationnumbers': [[2,27,59]] #ghent group for timeseries plot
                                                             
    #                             }
    #                     }
    #         }
    }




if not (os.path.exists(input_data_dir)):
    print('No Bulk_data folder found, this will be created: ', comp_plots_dir)
    os.makedirs(comp_plots_dir)
    print('Now, add the follwing databundles to this folder: ', [paths_dict[exp]['datafile'] for exp in paths_dict])