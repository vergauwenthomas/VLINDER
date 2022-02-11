#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 08:59:16 2022

@author: thoverga
"""

import os


db_location = "/home/thoverga/Desktop/workshop_data/db"

#Comparison folder
#check if the 'comparison_plots' folder exist
comp_plots_dir = os.path.join(db_location, 'comparison_plots')
if not (os.path.exists(comp_plots_dir)):
    print('No comparison_plots folder found, this will be created: ', comp_plots_dir)
    os.makedirs(comp_plots_dir)



stationnumbers = list(range(1, 59+1)) #the stations to include as a list of numbers

input_data_dir = os.path.join(db_location, 'Bulk_data') #where the downloaded datafiles are


paths_dict = {
    "august": {
                'datafile': os.path.join(input_data_dir, 'all_stations_aug_2020.csv'),
                'period_title_att': 'augustus 2020', #will be added in the title of the figures
                'scenario': {'scenario0': {
                                        #Data formatting
                                        'var': 'Temperatuur',
                                        'scalar_to_add': 0.0,
                                        'google_sheets_postfix': '_data_aug_google.csv', #ex; Vlinder02_data_aug_google.csv
                                        'google_sheets_rayman_output_postfix': '_rayman_output_aug_google.csv', #ex; Vlinder02_data_aug_google.csv
                                        'rayman_input_postfix': '_data_aug_rayman.csv', #ex; Vlinder02_data_aug_rayman.csv
                                        
                                        #figure generator
                                        'rayman_output_postfix': '_aug_rayman_output.txt', #for making plots
                                        'barplot_postfix': '_aug_PET_bar.pdf', #the postfix of the barplot
                                        'timeseriesplot_postfix': '_aug_PET_timeseries.pdf', #the postfix of the timeseries gigure
                                        'comparison_stationnumbers': [[2,27,59], #ghent group for timeseries plot
                                                                      [36, 42, 57], #test group
                                                                      ] 
                                    },
                            'scenario1': {
                                        'var': 'Temperatuur',
                                        'scalar_to_add': 1.5,
                                        'google_sheets_postfix': '_data_aug_scenario_1-5_google.csv', #ex; Vlinder02_data_aug_scenario_1-5_google.csv
                                        'google_sheets_rayman_output_postfix': '_rayman_output_aug_scenario_1-5_google.csv', #ex; Vlinder02_data_aug_google.csv
                                        'rayman_input_postfix': '_data_aug_scenario_1-5_rayman.csv', #ex; Vlinder02_data_aug_scenario_1-5_rayman.csv
                                   
                                        'rayman_output_postfix': '_aug_scenario_1-5_rayman_output.txt', #for making plots
                                        'barplot_postfix': '_aug_scenario_1-5_PET_bar.pdf', #the postfix of the barplot
                                        'timeseriesplot_postfix': '_aug_scenario_1-5_PET_timeseries.pdf', #the postfix of the timeseries gigure
                                        'comparison_stationnumbers': [[2,27,59], #ghent group for timeseries plot
                                                                      [36, 42, 57],  #test group
                                                                      ]
                                    },
                            'scenario2': {
                                        'var': 'Temperatuur',
                                        'scalar_to_add': 2.5,
                                        'google_sheets_postfix': '_data_aug_scenario_2-5_google.csv', #ex; Vlinder02_data_aug_scenario_2-5_google.csv
                                        'google_sheets_rayman_output_postfix': '_rayman_output_aug_scenario_2-5_google.csv', #ex; Vlinder02_data_aug_google.csv
                                        'rayman_input_postfix': '_data_aug_scenario_2-5_rayman.csv', #ex; Vlinder02_data_aug_scenario_2-5_rayman.csv
                                   
                                        'rayman_output_postfix': '_aug_scenario_2-5_rayman_output.txt', #for making plots 
                                        'barplot_postfix': '_aug_scenario_2-5_PET_bar.pdf', #the postfix of the barplot
                                        'timeseriesplot_postfix': '_aug_scenario_2-5_PET_timeseries.pdf', #the postfix of the timeseries gigure
                                        'comparison_stationnumbers': [[2,27,59], #ghent group for timeseries plot
                                                                      [36, 42, 57], #test group
                                                                      ] 
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