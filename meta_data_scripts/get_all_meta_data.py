#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script calculates the meta data (height, landcover and LCZ) of a location in a file of coordinates.


The input should contain a column with the station identifiers (i.e the statio name), a latitude and longitude column. The names of 
these columns can be specified when running the script. 

By default the file 'coordinates_file.csv' in the folder of this script is used as input, and the output will appear in this folder also. 
The radii for the landcover buffers can changed in the settings cell. 


SPECIFIC TO USER: make shure the lu_lc_folder is on your device AND the path to this folder is in the path_handler. 

Specifications:
    1) Height is calculated using a DEM map
    2) Landcover is calculated using the BBK map. If the coverage is not sufficient the ESM map is used. In the output one can find simplyfied aggregated landcover types. 
    3) The LCZ is obtained using the LCZ map of Europe.
    4) An estimate of the SVF is made using a DEM map.



Created on Wed Sep 15 10:56:27 2021

@author: thoverga
"""


import sys 
import os
import pandas as pd
import math
import numpy as np
import geopandas as gpd
import rasterio
from shapely.geometry import box
import rasterstats
from pathlib import Path


#%import path file
file_folder = (Path(__file__).resolve().parent)
sys.path.append(str(file_folder))
import gis_functions as gis


main_repo_folder = (Path(__file__).resolve().parent.parent)
sys.path.append(str(main_repo_folder))
import path_handler
print('Path handling module loaded')

#%settings

location_file = os.path.join(path_handler.folders['meta_data_folder'], 'coordinates_file.csv')
print('Meta data will be calculated for file ', location_file)

output_file = os.path.join(path_handler.folders['meta_data_folder'], 'coordinates_file_with_meta_data.csv')


#---------------------------------------------Landuse---------------------------------------------------------
buffer_list = [50,100,150,250]

#----------------------------------------------SVF------------------------------------------------------------

local_radius_meter= 200 #the max distance of the surroundings to what the SVF is calculated (in meter)
loc_buffer_meter=20 #estimate of the precision IN METER of the station and the buffer radius that is excluded from the svf calculation. 
num_directions=8 #the number of directions to be considerd in the calculation of the SVF (i.e. 4 is only looking in the wind directions)

#% Check data format

df = pd.read_csv(location_file, sep=',')
columnlist = list(df.columns)
if not 'station' in df.columns:
    print('The column: station, not found in the input file. These columnnames are found instead: ', columnlist)
    station_identifier = input('Type the name of the unique station identifier: ')
else:
    station_identifier = 'station'


if not df[station_identifier].is_unique:
    print('the column ', station_identifier, ' is not unique!! Stop script.')
    sys.exit()

if not 'lat' in df.columns:
    print('the column: lat, not found in the input file. These columnnames are found instead: ', columnlist)
    lat_identifier = input('Type the name of the latitude identifier: ')
else:
    lat_identifier = 'lat'
    
if not 'lon' in df.columns:
    print('the column: lon, not found in the input file. These columnnames are found instead: ', columnlist)
    lon_identifier = input('Type the name of the lon identifier: ')
else:
    lon_identifier = 'lon'
    







#%% Find height
def find_height(stationdf, lat_identifier, lon_identifier, DEM_folder):
    #create geo df
    station_geo = gis.df_to_geodf(stationdf, "EPSG:3035", lat_identifier, lon_identifier)


    #make list of all DEM files in the DEM-folder
    DEM_map_files = [os.path.join(DEM_folder,f) for f in os.listdir(DEM_folder) if os.path.isfile(os.path.join(DEM_folder, f))]
    
    #calculate height
    station_geo['height'] = station_geo['geometry'].apply(gis.ULTIMATE_read_from_rasterfile, raster_file_list = DEM_map_files)
   
    #remove geometry column
    return station_geo.drop(columns=['geometry'])





df = find_height(df, lat_identifier, lon_identifier,
                 os.path.join(path_handler.lu_lc_folder, 'DEM/'))

#%% SVF


def find_SVF(stationdf, station_identifier, lat_identifier, lon_identifier, DEM_folder, local_radius=200, loc_buffer=2, num_directions=8):    
    """ This function makes an estimate on the SVF for the given locations. This estimate is done by using the DEM. 
        IMPORTANT: the resolution of the DEM model should be in meter!! """
    

    print("Reading the DEM map and get SVF of stations ...")
    #create geo df
    station_geo = gis.df_to_geodf(stationdf, "EPSG:3035", lat_identifier, lon_identifier)
    
    
    #point to square geometry
    def point_to_square(point, dist_to_bounds_meter):
        return box((point.x - dist_to_bounds_meter),
                   (point.y - dist_to_bounds_meter),
                   (point.x + dist_to_bounds_meter),
                   (point.y + dist_to_bounds_meter))
    
    station_geo['polygon'] = station_geo['geometry'].apply(point_to_square, dist_to_bounds_meter = local_radius)
    
    

    
    def get_SVF_from_local_DEM(local_array, local_radius, raster_info, loc_buffer=2, num_directions=8):
        alpha = 360.0/(num_directions)
        array_resolution = raster_info["resolution"]
        
        ref_index = int(local_array.shape[0]/2)
        
        buffer_index = math.ceil(loc_buffer/array_resolution)
        
        
        # find lowes point in buffer of radius 2 (map units = meter)
        ref_height = local_array[ref_index - buffer_index: ref_index + buffer_index,
                                 ref_index - buffer_index: ref_index + buffer_index].min()
        
        
        svf_df = pd.DataFrame()
        svf_df['direction'] = list(range(num_directions))
        svf_df['alpha'] = [x*alpha for x in svf_df['direction']]
        
        def max_phi_for_direction(row, local_array, ref_index, buffer_index, resolution):
            dir_alpha = row['alpha']
            phi_list = []
            for i in range(math.floor(local_array.shape[0]/2)): #scan along a line
                col_idx = round(i * math.sin(dir_alpha * (math.pi / 180.))) + ref_index
                row_idx = ref_index - round(i * math.cos(dir_alpha * (math.pi / 180.)))
                
                #not to close to ref to avoid effect of the trotoir.
                if ((ref_index - buffer_index <= col_idx) & (col_idx <= ref_index + buffer_index)) & \
                    ((ref_index - buffer_index <= row_idx) & (row_idx <= ref_index + buffer_index)):
                    continue
                
                
                center_index = float(local_array.shape[0]/2.0) #can be different than ref_index if array shape is uneven
                dist_gridspace = math.sqrt((abs(col_idx - center_index))**2 + (abs(row_idx - center_index))**2)
                dist = float(dist_gridspace) * float(resolution)
                
                relative_height = local_array[row_idx, col_idx] - ref_height
                
                if relative_height < 0 : 
                    relative_height = 0.
                
                
                phi = math.atan(relative_height/dist) * (180. / math.pi)
                phi_list.append(phi)     
            return max(phi_list)
        
        svf_df['phi_max'] = svf_df.apply(max_phi_for_direction, axis=1,
                                         local_array=local_array,
                                         ref_index = ref_index,
                                         buffer_index = buffer_index,
                                         resolution = array_resolution)
        
        svf = 1 - ((svf_df['phi_max'].sum())/(90 * 360))
        return svf
    
    
    
    
    #make list of all DEM files in the DEM-folder
    DEM_map_files = [os.path.join(DEM_folder,f) for f in os.listdir(DEM_folder) if os.path.isfile(os.path.join(DEM_folder, f))]
    
    station_geo['svf'] = np.nan
    
    for _idx, row in station_geo.iterrows():
        geometry = row['polygon']
        local_array, raster_info = gis.ULTIMATE_read_from_rasterfile(geometry, DEM_map_files, return_map_info=True)
        svf = get_SVF_from_local_DEM(local_array,
                                     local_radius,
                                     raster_info,
                                     loc_buffer=loc_buffer,
                                     num_directions=num_directions)
        
        station_geo.loc[station_geo[station_identifier] == row[station_identifier], 'svf'] = svf
    
    return station_geo.drop(columns=['geometry', 'polygon'])


df = find_SVF(stationdf = df,
                   station_identifier = station_identifier,
                   lat_identifier = lat_identifier,
                   lon_identifier = lon_identifier,
                   DEM_folder = os.path.join(path_handler.lu_lc_folder, 'DEM/'),
                   local_radius=local_radius_meter,
                   loc_buffer=loc_buffer_meter,
                   num_directions=num_directions)



#%%

#raster info

BBK_folder = os.path.join(path_handler.lu_lc_folder,'Landuse', 'BBK2015')
ESM_folder = os.path.join(path_handler.lu_lc_folder,'Landuse', 'ESM')

raster_dict= {
    'BBK':{
        'raster_files': [os.path.join(BBK_folder, x) for x in os.listdir(BBK_folder) if x.endswith(".tif")],
        'mapper': {
            1: 'building',
            2: 'road',
            3: 'rest_impervious',
            4: 'rail_road',
            5: 'water',
            6: 'rest_non_impervious',
            7: 'crop_land',
            8: 'gras_shrub',
            9: 'tree',
            10: 'gras_shrub_agriculture',
            11: 'gras_shrub_road',
            12: 'trees_road',
            13: 'gras_shrub_water',
            14: 'trees_water'
            },
        'agg':{
            'green': ['tree', 'rest_non_impervious', 'gras_shrub', 'crop_land', 'gras_shrub_agriculture', 'gras_shrub_road', 
                                         'gras_shrub_water', 'trees_water', 'trees_road'],
            'impervious' : ['road', 'rest_impervious', 'rail_road', 'building']
            },
        'crs': "EPSG:31370"
        },
    'S2GLC':{
        'raster_files': os.path.join(path_handler.lu_lc_folder,'Landuse', 'S2GLC_EUROPE_2017', 'S2GLC_Europe_2017_v1.2.tif'),
        'mapper':  {
            0:'clouds',
            62: 'Artificial_surfaces_and_constructions',
            73: 'Cultivated areas',
            75: 'Vineyards',
            82: 'Broadleaf tree cover',
            83: 'Coniferious tree cover',
            102: 'Herbaceous vegetation',
            103: 'Moors and heathland',
            104: 'Sclerophyllous vegetation',
            105: 'Marshes',
            106: 'Peatbogs',
            121: 'Natural material surfaces',
            123: 'Permanent snow covered surfaces',
            162: 'Water',
            255: 'No data'
            },
        'agg':{
            'green': ['Cultivated areas', 'Vineyards', 'Broadleaf tree cover', 'Coniferious tree cover',
                      'Herbaceous vegetation', 'Moors and heathland', 'Sclerophyllous vegetation',
                      'Marshes', 'Peatbogs', 'Natural material surfaces', 'Permanent snow covered surfaces'],
            'impervious' : ['Artificial_surfaces_and_constructions'],
            },
        'crs': 'EPSG:3035'
        }
    }





def calculate_landuse(stationdf, bufferlist, raster_dict, lat_identifier, lon_identifier):
     
    """ This functions calculate the landuse as fractions for the stations based on a buffer radius. 
        As a first attempt, the landuse will be derived from the first key in the rasterdict (BBK). If the station (or the buffer),
        is outside the domain of the these maps, the next map is used. 
        
         Keyword arguments: \n
            stationdf -- pd.DataFrame
                        a pandas dataframe with at least the following columns: station (the name of the station),
                        lat (latitute of station), lon (lontitude of the station) 
            bufferlist -- list
                        a LIST with the buffer radii in meter \n
        
        Return
            stationdf with added columns for the landuseclasses as fractions, a column indication for: the used map, the buffer radius. """
        
    
    
    total_geodf = pd.DataFrame() #initiate return df
    for _idx, row in stationdf.iterrows():
        raster_iterator = iter(raster_dict) #create a iterable of the rastersets
        raster = next(raster_iterator) #try with the first raster in the raster dict
        for buffer_radius in bufferlist:
            append_row = row.copy()
            append_row['buffer_radius'] = buffer_radius
            
            #create circular buffer in the coordinates of the raster file
            buffer_geometry = gis.coordinate_to_circular_buffer_geometry(lat_center=append_row[lat_identifier],
                                                                         lon_center=append_row[lon_identifier],
                                                                         radius_m=buffer_radius,
                                                                         crs = raster_dict[raster]['crs'])
            #get cell value frequency table of the geometry on the raster
            freq_table = gis.ULTIMATE_read_from_rasterfile(geometry = buffer_geometry,
                                                           raster_file_list = raster_dict[raster]['raster_files'],
                                                           return_map_info = False,
                                                           return_counts=True,
                                                           none_if_no_overlap=True)
            if freq_table is None: #geometry not in raster files, try the next raster folder
                raster = next(raster_iterator)
                #create circular buffer in the coordinates of the raster file
                buffer_geometry = gis.coordinate_to_circular_buffer_geometry(lat_center=append_row[lat_identifier],
                                                                         lon_center=append_row[lon_identifier],
                                                                         radius_m=buffer_radius,
                                                                         crs = raster_dict[raster]['crs'])
               #get cell value frequency table of the geometry on the raster
                freq_table = gis.ULTIMATE_read_from_rasterfile(geometry = buffer_geometry,
                                                           raster_file_list = raster_dict[raster]['raster_files'],
                                                           return_map_info = False,
                                                           return_counts=True,
                                                           none_if_no_overlap=True)
                if freq_table is None: #if the geometry is not found in the two maps
                    print('geometry not found in any map!!')
                    sys.exit()
            #add map info
            append_row['used_map'] = raster
            
            
            #normalize
            total_counts = freq_table['counts'].sum()
            freq_table['fractions'] = [x/total_counts for x in freq_table['counts']]
            
            #map apparant classes
            freq_table['lc'] = freq_table['category'].map(raster_dict[raster]['mapper'])
            
            #add unused classes for consistency
            freq_table = freq_table.merge(pd.Series(raster_dict[raster]['mapper'].values(), name='lc'),how='outer', on='lc')
            freq_table['fractions'] = freq_table['fractions'].fillna(0.0)
            freq_table = pd.Series(data=list(freq_table['fractions']), index=freq_table['lc'], name='fraction')
            
            #add lu info to the row info
            append_row = append_row.append(freq_table)
            #aggregate classes
            for agg_class in raster_dict[raster]['agg']:
                append_row[agg_class] = append_row[raster_dict[raster]['agg'][agg_class]].sum()
            #add row to the df
            total_geodf = total_geodf.append(append_row, ignore_index=True)
    return total_geodf

df = calculate_landuse(stationdf = df,
                       bufferlist = buffer_list,
                       raster_dict = raster_dict,
                       lat_identifier=lat_identifier,
                       lon_identifier=lon_identifier)





#%%


lcz_dict = {
    'file': os.path.join(path_handler.lu_lc_folder, 'Landuse', 'EU_LCZ_map.tif'),
    'mapper': {
        1: 'LCZ-1, compact highrise',
        2: 'LCZ-2, compact midrise',
        3: 'LCZ-3, compact lowrise',
        4: 'LCZ-4, open highrise',
        5: 'LCZ-5, open midrise',
        6: 'LCZ-6, open lowrise',
        7: 'LCZ-7, lightweight lowrise',
        8: 'LCZ-8, large lowrise',
        9: 'LCZ-9, sparsely built',
        10: 'LCZ-10, heavy industry',
        11: 'LCZ-A, dense trees',
        12: 'LCZ-B, scattered trees',
        13: 'LCZ-C, bush, scrub',
        14: 'LCZ-D, low plants',
        15: 'LCZ-E, bare rock or paved',
        16: 'LCZ-F, bare soil or sand',
        17: 'LCZ-G, water' 
        },
    'crs': "EPSG:3035"
    }

def get_lcz(stationdf, lcz_dict, station_identifier, lat_identifier, lon_identifier):
    stationdf['lcz'] = np.nan
    stations_list = stationdf[station_identifier].unique()
    for station in stations_list:
        station_info = stationdf[stationdf[station_identifier] == station].iloc[0]
        
        point_geometry = gis.coordinate_to_point_geometry(lat = station_info[lat_identifier],
                                                          lon = station_info[lon_identifier],
                                                          crs = lcz_dict['crs']
                                                          )
        lcz_number = gis.ULTIMATE_read_from_rasterfile(geometry = point_geometry,
                                                       raster_file_list=lcz_dict['file'],
                                                       return_map_info=False,
                                                       return_counts=False,
                                                       none_if_no_overlap=True)
        if lcz_number is None:
            print('LCZ for station: ', station , ' could not be found on the LCZ map !!!')
            print('LCZ for station: ', station, ' is manually set as water' )
            lcz = 'LCZ-G, water'
        else: 
            lcz = lcz_dict['mapper'][lcz_number]
        
        stationdf.loc[stationdf[station_identifier] == station, 'lcz'] = lcz
    return stationdf



df = get_lcz(stationdf = df,
             lcz_dict = lcz_dict,
             station_identifier = station_identifier,
             lat_identifier = lat_identifier,
             lon_identifier = lon_identifier)






#%% save df

#arrange columns so that the added columns comes after the original columns
meta_columns = list(set(list(df.columns)) - set(columnlist))
columnlist.extend(meta_columns)
df = df[columnlist]

print('saving data to: ', output_file)
df.to_csv(output_file, index=False)

