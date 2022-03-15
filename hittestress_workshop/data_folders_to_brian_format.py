#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a Database with structure:
Example:
    - Vlinder02
        -data
            -Vlinder02_aug_rayman_output.txt
            -Vlinder02_aug_scenario_1-5_rayman_output.txt
            - ...
        -Vlinder02_aug2020_bar.png
        -Vlinder02_aug2020_time.png
        - ...

@author: thoverga
"""

import shutil
# import pandas as pd
import os 
import path_handler as ph

print('Creating a Database structure to use for the online Brian-tool')


#%%
def make_dir_if_needed(dirpath):
    #check if dirpath exist and make if it does not exist
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
        

#%%
# dbfolder = ph.brian_db
vlinderlist = ['Vlinder' + str(x).zfill(2) for x in ph.stationnumbers]


for period in ph.paths_dict:
    for scenario in ph.paths_dict[period]['scenario']:
        infodict = ph.paths_dict[period]['scenario'][scenario]
        for vlinder in vlinderlist:
            #copy titan output to make coparison plots
            titanoutput =  os.path.join(ph.db_location, vlinder, ph.raymanfoldername, vlinder+infodict['rayman_output_postfix'])
            target_dir = os.path.join(ph.brian_db, vlinder)
            if (os.path.exists(titanoutput)):
                print('titan output found for station ', vlinder)
                #create station dir in Brian db
                make_dir_if_needed(target_dir)
                
                #create data dir inside station dir for the data files
                make_dir_if_needed(os.path.join(target_dir, 'data'))
                shutil.copy(titanoutput, os.path.join(target_dir, 'data'))
            
            #barplot
            barplotfile = os.path.join(ph.db_location, vlinder, ph.raymanfoldername, vlinder+infodict['barplot_postfix'])
            if (os.path.exists(barplotfile)):
                print('barplot found for station ', vlinder)
                shutil.copy(barplotfile, target_dir)
            #timeseries plot
            timeseriesplotfile = os.path.join(ph.db_location, vlinder, ph.raymanfoldername, vlinder+infodict['timeseriesplot_postfix'])
            if (os.path.exists(timeseriesplotfile)):
                print('timeplot found for station ', vlinder)
                shutil.copy(timeseriesplotfile, target_dir)


    

