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
import rasterstats
from pathlib import Path


#%%import path file
main_repo_folder = (Path(__file__).resolve().parent.parent)
sys.path.append(str(main_repo_folder))
import path_handler
print('Path handling module loaded')

#%%settings

location_file = os.path.join(path_handler.folders['meta_data_folder'], 'coordinates_file.csv')
print('Meta data will be calculated for file ', location_file)

output_file = os.path.join(path_handler.folders['meta_data_folder'], 'coordinates_file_with_meta_data.csv')


#---------------------------------------------Landuse---------------------------------------------------------
buffer_list = [50,100,150,250]

#----------------------------------------------SVF------------------------------------------------------------

local_radius= 20 #the max distance of the surroundings to what the SVF is calculated (in DEM units = meter)
loc_buffer=2 #estimate of the precision of the station and the buffer radius that is excluded from the svf calculation. 
num_directions=8 #the number of directions to be considerd in the calculation of the SVF (i.e. 4 is only looking in the wind directions)

#%% Check data format

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
def find_height(stationdf, station_identifier, lat_identifier, lon_identifier, DEM_folder):
    #1.0
    """ This function calculates the height of all the stations in the stationsdf and add a column 
        'height' to it. The DEM_locations is a list of the paths to the DEM tiff files. """
        
    print("Reading the DEM map and get hight of stations ...")
    station_geo = gpd.GeoDataFrame(stationdf, geometry=gpd.points_from_xy(stationdf[lon_identifier], stationdf[lat_identifier]))
    station_geo = station_geo.set_crs(epsg=4326) #set coordinates to normal gps coordinates
    
    #EU-DEM v1.1 is in EPSG:3035
    station_geo = station_geo.to_crs("EPSG:3035")
    station_geo['raster_key'] = np.nan
    
    #make list of all DEM files in the DEM-folder
    DEM_map_files = [os.path.join(DEM_folder,f) for f in os.listdir(DEM_folder) if os.path.isfile(os.path.join(DEM_folder, f))]
    DEMs = pd.Series([rasterio.open(x) for x in DEM_map_files]).to_dict()
    
    def Which_map_to_use(station_geo, DEMs):
        for index in DEMs:
            raster = DEMs[index]
            bounds = raster.bounds
            for idx, row in station_geo.iterrows():
                if ((row['geometry'].x < bounds.right) & (row['geometry'].x > bounds.left) &
                    (row['geometry'].y > bounds.bottom) & (row['geometry'].y < bounds.top)):
                    station_geo.loc[station_geo[station_identifier] == row[station_identifier], 'raster_key'] = raster
        return station_geo
    
    station_geo = Which_map_to_use(station_geo, DEMs)
    
    if not station_geo[station_geo['raster_key'] == np.nan].empty:
        print('Problem, these stations are not included in the DEM domain:')
        print(station_geo[station_geo['raster_key'] == np.nan])
        
    used_rasters = station_geo['raster_key'].value_counts().index.to_list() #get a list of all used rasters
    station_geo['height'] = np.nan
    
    for raster in used_rasters:
        height_array = raster.read(1)
        sub_station_geo = station_geo[station_geo['raster_key'] == raster]
        for index, station_row in sub_station_geo.iterrows():
            spatial_point = station_row['geometry']
            row, col = raster.index(spatial_point.x, spatial_point.y)
            height = height_array[row, col]
            if height < -100.: #The height for sea- stations is a very large negative number --> adjust for this
                print('Correction for station ' + station_row[station_identifier] + ', height of ' + str(height) + ' m ---> 0.0 m')
                height = 0.
            station_geo.loc[station_geo[station_identifier] == station_row[station_identifier], 'height'] = height
        raster.close()
        del height_array
        
    return station_geo[[station_identifier, lat_identifier, lon_identifier, 'height']]





df = find_height(df, station_identifier, lat_identifier, lon_identifier,
                 os.path.join(path_handler.lu_lc_folder, 'DEM/'))


#%%


def find_SVF(stationdf, station_identifier, lat_identifier, lon_identifier, DEM_folder, local_radius=20, loc_buffer=2, num_directions=8):    
    """ This function makes an estimate on the SVF for the given locations. This estimate is done by using the DEM. 
        IMPORTANT: the resolution of the DEM model should be in meter!! """
    

    print("Reading the DEM map and get SVF of stations ...")
    station_geo = gpd.GeoDataFrame(stationdf, geometry=gpd.points_from_xy(stationdf[lon_identifier], stationdf[lat_identifier]))
    station_geo = station_geo.set_crs(epsg=4326) #set coordinates to normal gps coordinates
    
    #EU-DEM v1.1 is in EPSG:3035
    station_geo = station_geo.to_crs("EPSG:3035")
    station_geo['raster_key'] = np.nan
    
    #make list of all DEM files in the DEM-folder
    DEM_map_files = [os.path.join(DEM_folder,f) for f in os.listdir(DEM_folder) if os.path.isfile(os.path.join(DEM_folder, f))]
    DEMs = pd.Series([rasterio.open(x) for x in DEM_map_files]).to_dict()
    
    def Which_map_to_use(station_geo, DEMs):
        for index in DEMs:
            raster = DEMs[index]
            bounds = raster.bounds
            for idx, row in station_geo.iterrows():
                if ((row['geometry'].x < bounds.right) & (row['geometry'].x > bounds.left) &
                    (row['geometry'].y > bounds.bottom) & (row['geometry'].y < bounds.top)):
                    station_geo.loc[station_geo[station_identifier] == row[station_identifier], 'raster_key'] = raster
        return station_geo
    
    station_geo = Which_map_to_use(station_geo, DEMs)
    
    
    if not station_geo[station_geo['raster_key'] == np.nan].empty:
        print('Problem, these stations are not included in the DEM domain:')
        print(station_geo[station_geo['raster_key'] == np.nan])
        
    
    

    def get_SVF_from_local_DEM(local_array, local_radius, loc_buffer=2, num_directions=8):
        alpha = 360.0/(num_directions)
        
        # find lowes point in buffer of radius 2 (map units = meter)
        ref_height = local_array[local_radius - loc_buffer: local_radius + loc_buffer,
                                 local_radius - loc_buffer: local_radius + loc_buffer].min()
        
        svf_df = pd.DataFrame()
        svf_df['direction'] = list(range(num_directions))
        svf_df['alpha'] = [x*alpha for x in svf_df['direction']]
        
        def max_phi_for_direction(row, local_array):
            dir_alpha = row['alpha']
            phi_list = []
            for i in range(local_radius): #scan along a line
                col_idx = round(i * math.sin(dir_alpha * (math.pi / 180.))) + local_radius
                row_idx = local_radius - round(i * math.cos(dir_alpha * (math.pi / 180.)))
                
                dist = math.sqrt((abs(col_idx - local_radius))**2 + (abs(row_idx - local_radius))**2)
                if (dist <= loc_buffer):
                    continue
            
                relative_height = local_array[row_idx, col_idx] - ref_height
                
                if relative_height < 0 : #not to close to ref to avoid effect of the trotoir.
                    relative_height = 0.
                
                phi = math.atan(relative_height/dist) * (180. / math.pi)
                phi_list.append(phi)     
            return max(phi_list)
        
        svf_df['phi_max'] = svf_df.apply(max_phi_for_direction, axis=1, local_array=local_array)
        
        svf = 1 - ((svf_df['phi_max'].sum())/(90 * 360))
        return svf
    
    
    

    
    used_rasters = station_geo['raster_key'].value_counts().index.to_list() #get a list of all used rasters
    stationdf['svf'] = np.nan
    
    
    for raster in used_rasters: #iterate over maps
        height_array = raster.read(1)
        sub_station_geo = station_geo[station_geo['raster_key'] == raster]
        for _, df_row in sub_station_geo.iterrows(): #iterate over location on the map
            spatial_point = df_row['geometry']
            row, col = raster.index(spatial_point.x, spatial_point.y)
    
            local_array = height_array[row - local_radius : row + local_radius, 
                                       col - local_radius : col + local_radius]
            
            svf = get_SVF_from_local_DEM(local_array,
                                         local_radius, 
                                         loc_buffer = loc_buffer,
                                         num_directions = num_directions,)
            
            stationdf.loc[stationdf[station_identifier] == df_row[station_identifier], 'svf'] = svf
        
        raster.close()
        del height_array
        
    return stationdf

df = find_SVF(stationdf = df,
                   station_identifier = station_identifier,
                   lat_identifier = lat_identifier,
                   lon_identifier = lon_identifier,
                   DEM_folder = os.path.join(path_handler.lu_lc_folder, 'DEM/'),
                   local_radius=local_radius,
                   loc_buffer=loc_buffer,
                   num_directions=num_directions)




#%% Landcover

def calculate_landuse(stationdf, bufferlist, BBK_folder, ESM_folder, 
                      station_identifier, lat_identifier, lon_identifier,
                      aggregate_simplyfied = True):
    
    """ This functions calculate the landuse as fractions for the stations based on a buffer radius. 
        As a first attempt, the landuse will be derived from the BBK2015 map. If the station (or the buffer),
        is outside the domain of the BBK2015 map, the ESM map is used. 
        
         Keyword arguments: \n
            stationdf -- pd.DataFrame
                        a pandas dataframe with at least the following columns: station (the name of the station),
                        lat (latitute of station), lon (lontitude of the station) 
            bufferlist -- list
                        a LIST with the buffer radii in meter \n
            BBK_folder -- string
                        a string that is the PATH TO THE FOLDER that contains the BBK maps \n
            landuse_folder -- string
                        a string that is the PATH TO THE FOLDER that contains the ESM maps \n
            ESM_maps -- list
                        a list of strings where each element is the name of a ESM map (ex. ['N30E38', 'N32E36, ...'])
                        These names schould be maps inside the landuse_folder. \n
            aggregate_simplyfied -- Bool(default False)
                        if True, the aggregated landuseclasses 'green' and 'impervious' will be calculated. \n
        
        Return
            stationdf with added columns for the landuseclasses as fractions, a column indication for: the used map, the buffer radius. """
        

    print('Calculating the landuse....')
    
    if bool(set(['geometry', 'crop_buffer', 'map_to_use', 'buffer']) & set(list(stationdf.columns))):
        _var = input("One of following columns in dataframe will be overwritten: 'geometry', 'crop_buffer', 'map_to_use', 'buffer'. Do you wanna continiue? (y/n)")
        if _var == 'n':
            exit()

        
    print('Calculating function')
    
    
    station_geo = gpd.GeoDataFrame(stationdf, geometry=gpd.points_from_xy(stationdf[lon_identifier], stationdf[lat_identifier]))
    station_geo = station_geo.set_crs(epsg=4326)
    
    
    
    def which_map_to_use_BBK(station_geo, BBK_folder, bufferlist):
        """ This functions looks which BBK map to use for a given station with a crop_buffer.  """
        
        BBK_maps = []
        for file in os.listdir(BBK_folder):
            if file.endswith(".tif"):
                BBK_maps.append(file)
        
        
        crop_buffer = max(bufferlist) + 10
        #convert latlon to projection of the BBK maps + create buffers
        station_geo = station_geo.to_crs("EPSG:31370")
        station_geo['crop_buffer'] = station_geo['geometry'].buffer(crop_buffer, resolution=16)
        
        station_geo['map_to_use'] = [[] for _ in range(len(station_geo))] #initialise empty lists for this column
        maps_boundries = {}
        
        #get boundaries of the ESM maps
        for Map in BBK_maps:
            raster = rasterio.open(os.path.join(BBK_folder, Map))
            maps_boundries[Map] = {'left': raster.bounds.left,
                                    'right': raster.bounds.right,
                                    'bottom': raster.bounds.bottom,
                                    'top': raster.bounds.top}
            raster.close()
        
        #check if the buffer is (partly) inside a map boundaries
        def is_geometry_in_boundary(row, rasterinfodict):
            geometry = row['crop_buffer']
            minx = geometry.bounds[0] #boundary of the buffer around the station
            miny = geometry.bounds[1] #boundary of the buffer around the station
            maxx = geometry.bounds[2] #boundary of the buffer around the station
            maxy = geometry.bounds[3] #boundary of the buffer around the station
            
            if (((rasterinfodict['left'] <= minx <= rasterinfodict['right']) | (rasterinfodict['left'] <= maxx <= rasterinfodict['right']))
                &
                ((rasterinfodict['bottom'] <= miny <= rasterinfodict['top']) | (rasterinfodict['bottom'] <= maxy <= rasterinfodict['top']))):
                return True
            else:
                return False
                
        #loop over all maps and stations to link maps and stations
        station_geo.reset_index(inplace = True)
        for index, row in station_geo.iterrows():
            for key in maps_boundries:
                if is_geometry_in_boundary(row, maps_boundries[key]):
                    station_geo.loc[index,'map_to_use'].append(key)
        
        #label the stations where the BBK map should be used
        station_geo['use_bbk'] = False
        for idx, row in station_geo.iterrows():
            if row['map_to_use']:
                station_geo.loc[idx, 'use_bbk'] = True
        
        return station_geo.drop(['crop_buffer'], axis=1)
    
    station_geo = which_map_to_use_BBK(station_geo, BBK_folder, bufferlist)
    
    
    
    def Calculate_landuse_by_BBK(station_geo, bufferlist, aggregate_simplyfied):
       
        landusedict_BBK = {
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
                            14: 'trees_water',
                        }
    
        returndf = pd.DataFrame()
        for radius in bufferlist:
            station_geo_one_buf = station_geo #create station geo for one buffer
            station_geo_one_buf['buffer'] = station_geo_one_buf['geometry'].buffer(radius, resolution=30) #create buffer geometry
            station_geo_one_buf['radius'] = radius
            
            #create landusecolumns in the station_geo_one_buf
            for key in landusedict_BBK:
                station_geo_one_buf[landusedict_BBK[key]] = 0.0
                
            #create landusecolumns in the station_geo_one_buf
            if aggregate_simplyfied:
                station_geo_one_buf['green'] = 0.0
                station_geo_one_buf['impervious'] = 0.0
                
            for idx, row in station_geo_one_buf.iterrows():
                all_landuse_types = [landusedict_BBK[x] for x in landusedict_BBK]
                vals = [0.0 for x in all_landuse_types]
                landuse = pd.DataFrame(data = vals, index=all_landuse_types)
                landuse.index.name = 'type'
                for bbkmap in row['map_to_use']:
                    raster = os.path.join(BBK_folder, bbkmap) #directory of map
                    zs = rasterstats.zonal_stats(
                                 vectors = row['buffer'],
                                 raster = raster,
                                 band_num=1, 
                                 all_touched= True, #if true, inclueds the cells at the boundaries of the polygon
                                 categorical = True,
                                 category_map = landusedict_BBK,
                                 raster_out= True,
                                 # prefix=str(layer)+'_'
                                 )
                    landuse_one_map = pd.Series(zs[0]).drop(['mini_raster_affine', 'mini_raster_array', 'mini_raster_nodata'])
                    # landuse_one_map.index = [x for x in landuse_one_map.index] #rename landuse with the formatter
                    #handling of observations that has multiple maps in their buffer span.
                    landuse_one_map = landuse_one_map.to_frame()
                    landuse_one_map.index.name = 'type'
                    landuse = landuse.merge(landuse_one_map, how='outer', on='type').fillna(0) 
                
                landuse = landuse.sum(axis=1) #sum the landuse type by type 
                landusesum = sum(landuse) #get the total tile number of the buffer.
                
                #check if landuse has enough tiles, if not the station is skipped and labeled for the ESM module.
                if landusesum < (np.pi * float(radius)**2):
                    print('Not sufficient data for station: ', row[station_identifier], ' . Station is labeled for ESM maps.')
                    station_geo_one_buf.loc[idx,'use_bbk'] = False #label station to go to the ESM module
                    continue
                
                #normalize landuse
                for landusetype in landuse.index:
                    station_geo_one_buf.loc[idx, landusetype] = float(landuse[landusetype])/landusesum
                #aggregate landuse
                if aggregate_simplyfied:
                    green_columns = ['tree', 'rest_non_impervious', 'gras_shrub', 'crop_land', 'gras_shrub_agriculture', 'gras_shrub_road', 
                                     'gras_shrub_water', 'trees_water', 'trees_road']
                    imp_columns = ['road', 'rest_impervious', 'rail_road', 'building']
                    
                    station_geo_one_buf.loc[idx, 'green'] = sum([station_geo_one_buf.loc[idx, x] for x in green_columns])
                    station_geo_one_buf.loc[idx, 'impervious'] = sum([station_geo_one_buf.loc[idx, x] for x in imp_columns])
                #add info to the station geo
                station_geo_one_buf.loc[idx, 'used_map'] = 'BBK2015'
                
            returndf = returndf.append(station_geo_one_buf)
                
        return returndf
    
    #First try to get the landuse using BBK 
    print("calculating landuse by BBK map.")   
    station_geo_BBK = Calculate_landuse_by_BBK(station_geo[station_geo['use_bbk'] == True],
                                               bufferlist,
                                               aggregate_simplyfied = aggregate_simplyfied,
                                               )
    
    no_BBK_stations = list(set(station_geo_BBK[station_geo_BBK['use_bbk'] == False][station_identifier].to_list()))
    
    #Collect the stations that are handled by the BBK
    station_geo_BBK = station_geo_BBK[~station_geo_BBK[station_identifier].isin(no_BBK_stations)]
    
    #Collect the stations that are not handled by the BBK
    station_geo_ESM = station_geo[station_geo['use_bbk'] == False]
    station_geo_ESM = station_geo_ESM.append(station_geo[station_geo[station_identifier].isin(no_BBK_stations)])
    
    
    def ESM_landuse(station_geo, bufferlist, ESM_folder, ESM_maps, aggregate_simplyfied = False):
        """ Get landcover fractions for locations and a buffer radius based on the ESM maps.
    
        Keyword arguments: \n
            stationdf -- pd.DataFrame
                        a pandas dataframe with at least the following columns: station (the name of the station),
                        lat (latitute of station), lon (lontitude of the station) 
            bufferlist -- list
                        a LIST with the buffer radii in meter (default 0.0) \n
            landuse_folder -- string
                        a string that is the PATH TO THE FOLDER that contains the ESM maps \n
            ESM_maps -- list
                        a list of strings where each element is the name of a ESM map (ex. ['N30E38', 'N32E36, ...'])
                        These names schould be maps inside the landuse_folder. \n
            aggregate_simplyfied -- Bool(default False)
                        if True, the aggregated landuseclasses 'green' and 'impervious' will be calculated. \n
        
        Return
            stationdf with added columns for the landuseclasses as fractions
        """
        
        
        def which_map_to_use_ESM(station_geo, ESM_folder, ESM_maps, crop_buffer = 500):
            """ This functions looks which ESM map to use for a given station with a crop_buffer. The
                crop_buffer should be bigger than used buffers. """
            
            
            #convert latlon to projection of the ESM maps + create buffers
            station_geo = station_geo.to_crs("EPSG:3035")
            station_geo['crop_buffer'] = station_geo['geometry'].buffer(crop_buffer, resolution=16)
            
            station_geo['map_to_use'] = [[] for _ in range(len(station_geo))] #initialise empty lists for this column
            maps_boundries = {}
            
            #get boundaries of the ESM maps
            for Map in ESM_maps:
                esm_0 = os.path.join(ESM_folder, Map)
                esm_0 = os.path.join(esm_0, 'class_0')
                esm_0 = os.path.join(esm_0, '200km_10m_' + Map +'_' + 'class0.TIF')
                raster = rasterio.open(esm_0)
                maps_boundries[Map] = {'left': raster.bounds.left,
                                        'right': raster.bounds.right,
                                        'bottom': raster.bounds.bottom,
                                        'top': raster.bounds.top}
                raster.close()
            
            #check if the buffer is (partly) inside a map boundaries
            def is_geometry_in_boundary(row, rasterinfodict):
                geometry = row['crop_buffer']
                minx = geometry.bounds[0] #boundary of the buffer around the station
                miny = geometry.bounds[1] #boundary of the buffer around the station
                maxx = geometry.bounds[2] #boundary of the buffer around the station
                maxy = geometry.bounds[3] #boundary of the buffer around the station
                
                if (((rasterinfodict['left'] <= minx <= rasterinfodict['right']) | (rasterinfodict['left'] <= maxx <= rasterinfodict['right']))
                    &
                    ((rasterinfodict['bottom'] <= miny <= rasterinfodict['top']) | (rasterinfodict['bottom'] <= maxy <= rasterinfodict['top']))):
                    return True
                else:
                    return False
                    
            #loop over all maps and stations to link maps and stations
            for index, row in station_geo.iterrows():
                for key in maps_boundries:
                    if is_geometry_in_boundary(row, maps_boundries[key]):
                        station_geo.loc[index,'map_to_use'].append(key)
            return station_geo.drop(['crop_buffer'], axis=1)
        
        station_geo = which_map_to_use_ESM(station_geo, ESM_folder, ESM_maps,
                                           crop_buffer=max(bufferlist) + 20)
        
        
        
        #check if station is not contained in ESM and BBK, and remove if so
        for idx, row in station_geo.iterrows():
            if not bool(row['map_to_use']):
                print('STATION ', row[station_identifier], ' IS NOT CONTAINED IN BBK NOR ESM')
                print('removing this station ...')
        
        station_geo['to_drop'] = ['yes' if not bool(x) else 'no' for x in station_geo['map_to_use']]
        station_geo = station_geo[station_geo['to_drop'] == 'no']
        station_geo.drop(columns=['to_drop'], inplace=True)
        
        classes = {'0':"no_data", #layer number --- representations
                    '1':"water",
                    '2':"railways",
                    '10':"nbu_area-open_space",
                    '15':"nbu_area-streets",
                    '20':"nbu_area-green_ndvi",
                    '25':"nbu_area-street_green_ndvi",
                    '30':"bu_area-open_space",
                    '35':"bu-area-streets",
                    '40':"bu_area-green_ndvi",
                    '41':"bu_area-green_ua",
                    '45':"bu_area-street_green_ndvi",
                    '50':"bu_buildings"}
        
        
        #get paths to the maps and their layers
        mapdict = {}
        for mapname in ESM_maps:
            tif_file_dict= {}
            for key in classes:
                esm_loc = os.path.join(ESM_folder, mapname)
                esm_loc = os.path.join(esm_loc, 'class_' + key)
                esm_loc = os.path.join(esm_loc, '200km_10m_' + mapname +'_' + 'class' + key + '.TIF')
                tif_file_dict[key] =  esm_loc
            mapdict[mapname] = tif_file_dict
        
        
        def get_landuse(geo_df, buffer_radius, layerlist, layerdict, mapdict, aggregate_simplyfied=False):
            #Create buffer, iterate over the layers and for each station the landuse is calculated. 
            geo_df['buffer'] = geo_df['geometry'].buffer(buffer_radius, resolution=30)
            for layer in layerlist:
                columnname = layerdict[str(layer)] #landuse class for this layer
                geo_df[columnname] = 0 #initiate landuse column
                for index, row in geo_df.iterrows():
                    landuse_count = 0. #variable for count overloading in case of raster boundary overlap.
                    for mapdir in row['map_to_use']:
                        layer_path = mapdict[mapdir][str(layer)] #directory of map
                        zs = rasterstats.zonal_stats(row['buffer'], layer_path, band_num=1, 
                                         all_touched= True, #if true, inclueds the cells at the boundaries of the polygon
                                         categorical = False,
                                         raster_out= True,
                                         prefix=str(layer)+'_')
                        
                        if zs[0][str(layer) + '_mean'] is None:
                            continue
                        
                        landuse_count += zs[0][str(layer) + '_mini_raster_array'].data.sum() #add to variable to handle buffers that extends two rasters.
                    geo_df.loc[index, columnname] = landuse_count #write to landuse column
                    
            #normalize landuse as fractions
            landusetypelist = list(layerdict.values())
            for index, row in geo_df.iterrows():
                landusesum = row[landusetypelist].sum()
                for landusetype in landusetypelist:
                    geo_df.loc[index, landusetype] = (row[landusetype] / landusesum)
                    
                    
                    
            #aggregate landuse to simplyfied classes
            if aggregate_simplyfied:
                impervious_list = ['railways', 'nbu_area-streets', 'bu-area-streets', 'bu_buildings']
                green_list = ['nbu_area-open_space', 'nbu_area-green_ndvi', 'nbu_area-street_green_ndvi', 'bu_area-green_ndvi', 'bu_area-green_ua', 'bu_area-street_green_ndvi']
                
                geo_df['impervious'] = geo_df[impervious_list].sum(axis=1) + (0.5 * geo_df['bu_area-open_space'])
                geo_df['green'] = geo_df[green_list].sum(axis=1) + (0.5 * geo_df['bu_area-open_space'])
            #return geo_df.drop(['buffer', 'map_to_use'], axis=1), landusetypelist
            return geo_df
         
    
    
        returndf = pd.DataFrame()
        for buffer_radius in bufferlist:           
            buffer_station_geo = get_landuse(station_geo, buffer_radius = buffer_radius,
                               layerlist = [0,1,2,10,15,20,25,30,35,40,41,45,50],
                               layerdict=classes,
                               mapdict = mapdict,
                               aggregate_simplyfied = aggregate_simplyfied, #aggregate to water, imimpervious and impervious
                               ) 
            buffer_station_geo['radius'] = buffer_radius
            buffer_station_geo['used_map'] = 'ESM'
            returndf = returndf.append(buffer_station_geo)
        
        
    
        return returndf
    print("calculating landuse by ESM map.")
    
    ESM_maps = os.listdir(ESM_folder) #list all map tiles available
    
    station_geo_ESM = ESM_landuse(
                       station_geo_ESM,
                       bufferlist = bufferlist,
                       ESM_folder = ESM_folder,
                       ESM_maps = ESM_maps,
                       aggregate_simplyfied = aggregate_simplyfied)
    
    
    #combining the ESM and BBK data
    station_geo_total = station_geo_BBK.append(station_geo_ESM)
    station_geo_total.sort_values(by=[station_identifier, 'radius'], inplace=True)
    station_geo_total.reset_index(drop = True, inplace=True)
    station_geo_total = station_geo_total.drop(columns=['use_bbk', 'geometry'])
    return station_geo_total


df = calculate_landuse(stationdf = df,
                           bufferlist = buffer_list,
                           BBK_folder = os.path.join(path_handler.lu_lc_folder,'Landuse', 'BBK2015'),
                           ESM_folder = os.path.join(path_handler.lu_lc_folder,'Landuse', 'ESM'),
                           station_identifier = station_identifier,
                           lat_identifier=lat_identifier,
                           lon_identifier=lon_identifier,
                           aggregate_simplyfied = True)



#%% get LCZ

def get_lcz(stationdf, lcz_file):
    print('Finding the LCZ for all the stations')
    
    #create geo pandas opbject with the correct projection
    station_geo = gpd.GeoDataFrame(stationdf, geometry=gpd.points_from_xy(stationdf[lon_identifier], stationdf[lat_identifier]))
    station_geo = station_geo.set_crs(epsg=4326)
    station_geo = station_geo.to_crs("EPSG:3035")
    
    lcz_map = {
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
        }

    
    station_geo['LCZ'] = 'unknown'
    for idx, row in station_geo.iterrows():
        point = row['geometry']
        lcz = rasterstats.zonal_stats(point,lcz_file, categorical=True, category_map=lcz_map)[0]
        if bool(lcz):
            station_geo.at[idx, 'LCZ'] = list(lcz.keys())[0]
        continue

    
    if station_geo[station_geo['LCZ'] == 'unknown'].shape[0]>0:
        print("Warning, the LCZ for the following locations could not be determind:")
        print(station_geo[station_geo['LCZ'] == 'unknown'])
        _var = input("Set all LCZ to water (LCZ-G) (y/n)")
        if _var == 'n':
            print ('exit script, LCZ not determind for above stations')
            exit()
        else:
            print("LCZ set as water.")
            station_geo['LCZ'] = station_geo['LCZ'].replace({'unknown': lcz_map[17]})
            
        
    return station_geo.drop(columns=['geometry'])




df = get_lcz(stationdf = df,
               lcz_file = os.path.join(path_handler.lu_lc_folder, 'Landuse', 'EU_LCZ_map.tif'))



#%% save df
print('saving data to: ', output_file)
df.to_csv(output_file, index=False)

