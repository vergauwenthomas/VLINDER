#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This scripts handles the relative paths in the VLINDER repo. Always import this to the scripts, and update if a script or file is added.
Created on Tue Sep 14 15:57:56 2021

@author: thoverga
"""

from pathlib import Path
import os
current_folder = (Path(__file__).resolve().parent)


#%%Folders
folders = {
    "dashboard_visuals": 
        {'map_plot': os.path.join(os.path.join(current_folder, 'Dashboard_visuals'), 'map_plot')
         },
    'data': os.path.join(current_folder, 'Data'),
    'landcover_scripts': os.path.join(current_folder, 'Landcover_script'),
    'Mbili_code': os.path.join(current_folder, 'Mbili_code'),
    }

#%% often used paths

meta_data_stations =  os.path.join(folders['data'], 'data.csv')


