#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This scripts handles the relative paths in the VLINDER repo. Always import this to the scripts, and update if a script or file is added.
Created on Tue Sep 14 15:57:56 2021

@author: thoverga
"""

from pathlib import Path
import os
current_folder = str(Path(__file__).resolve().parent)

#%% local folders!!!!! ADJUST THESE PATHS TO YOUR MACHINE
_who_is_running = 'thomas'
# _who_is_running = 'michiel'
# _who_is_running = 'sara'
# _who_is_running = 'steven'



print("The path_handler is set to the local path structure of ", _who_is_running)

if _who_is_running == 'thomas':
    lu_lc_folder = "/home/thoverga/Documents/github/maps" 
    
if _who_is_running == 'michiel':
    lu_lc_folder = "..." 

if _who_is_running == 'sara':
    lu_lc_folder = "..." 

if _who_is_running == 'steven':
    lu_lc_folder = "..." 
    
    
    
#%%Folders
folders = {
    "dashboard_visuals": 
        {'map_plot': os.path.join(os.path.join(current_folder, 'Dashboard_visuals'), 'map_plot')
         },
    'data': os.path.join(current_folder, 'Data'),
    'landcover_scripts': os.path.join(current_folder, 'Landcover_script'),
    'Mbili_code': os.path.join(current_folder, 'Mbili_code'),
    'meta_data_folder': os.path.join(current_folder, 'meta_data_scripts'),
    }

#%% often used paths

meta_data_stations =  os.path.join(folders['data'], 'data.csv')


