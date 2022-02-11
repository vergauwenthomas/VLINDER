#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 09:22:25 2022

This script checks if a datafile, that will be saved as a csv can be loaded in google sheets
@author: thoverga
"""


import pandas as pd


risk_factor = 0.9 #will be multiplied to all the data limits


max_cells = 5000000
max_columns = 18278
max_rows = 5000000

file_size_limit = 100 #MB

