#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  5 15:29:30 2021

@author: thoverga

This script will generate landuse information for given coordinates based on the ESM dataset.
These raster data can be found at: https://land.copernicus.eu/pan-european/GHSL/european-settlement-map

Note:
    * The required packages can be installed by opening the corresponding conda enviroment (.yml file)
      Use the following commands: 
          $ conda env create -f landuseenviroment.yml         (create the enviroment)
          $ conda env list                                    (list the conda envirmonts)
          choose the corresponding enviroment and activat it with
          $ conda activate 'enviroment'                       (change 'enviroment' by the corresponding name)
    
    * The datafile with locations is a csv file with (at least) these three columns:
        * 'station' : name of the station or location
        * 'lat'     : latitude of the station
        * 'lon'     : lontitude of the station
        
    * Keep in mind that the ESM dataset is not yet validated and faults are propable for some regions (ex. Mechelen)

"""

#%% imports and path handling

import os
import pandas as pd
import geopandas as gpd
import rasterio
import rasterstats


data_import_file = "/home/thoverga/Desktop/vlinderdata.csv"

data_output_file = "/home/thoverga/Desktop/test.csv"

ESM_folder = '/home/thoverga/Documents/github/maps/Landuse/'
ESM_maps = ["N30E38", "N32E36", "N32E38", "N30E40", "N32E40"]

bufferlist = [150, 250]
aggregate_simplyfied = True
only_simplyfied_landuse = False

#%% interactive settings

print('These are the settings for the script: ')
print('............IO................')
print("data input file (should end with .csv): ", data_import_file)
print("data output file (should end with .csv): ", data_output_file)
print("ESM folder containing the ESM maps (should end with /): ", ESM_folder)
print("ESM maps in the ESM folder: ", ESM_maps)
print("..........parameters......... ")
print("bufferlist (in meter): ", bufferlist)
print("calculate the aggregated classes (water, green, pervious): ",aggregate_simplyfied)
print ("return ONLY the aggregated classes? ", only_simplyfied_landuse)


_settings_var = input("Are these settings ok?  (y/n)")
if _settings_var != 'y':

    def path_handling(path, pathdiscription):
        print('The ' + pathdiscription + ' is: ' + path)
        _var = input('Ok? (y/n)')
        if _var == 'y':
            print('Ok!')
            return path
        else:
            new_path = input('type the new path :')
            print(pathdiscription + 'path has changed into: ', str(new_path))
            return str(new_path)
    data_import_file = path_handling(data_import_file, 'data inport file (csv)')
    data_output_file = path_handling(data_output_file, 'output file (add .csv at the end)')
    ESM_folder = path_handling(ESM_folder, 'path to the FOLDER (/ at the end) containing the ESM raster folders')
    
    def add_maps(ESM_maps):
        print('These are the maps that will be used (should be folders in the previous given folder location)')
        print(ESM_maps)
        _var = input('ok, new list, add ?  (ok/new/add)')
        if _var == 'new':
            new_esm_map = input('new list (ex. ["N30E42","N32E46"]) :')
            print("The ESM maps that will be used are: ", new_esm_map)
            return new_esm_map
        if _var == 'add':
            _ok = False
            while not _ok:        
                new_esm_map = input('type the map to add: ')
                ESM_maps.append(str(new_esm_map)) 
                print('the maps that will be used are: ', ESM_maps)
                _interact = input('Ok or add another?   (ok/add):')
                if _interact == 'ok':
                    _ok=True
        ESM_maps = list(set(ESM_maps))
        print("Oke, that is all. These maps will be used: ", ESM_maps)
        return ESM_maps
                
    ESM_maps = add_maps(ESM_maps)

print ("oke, lets go...")



#%% Reading data
stationdf = pd.read_csv(data_import_file)

if bool(set(['geometry', 'crop_buffer', 'map_to_use', 'buffer']) & set(list(stationdf.columns))):
    _var = input("One of following columns in dataframe will be overwritten: 'geometry', 'crop_buffer', 'map_to_use', 'buffer'. Do you wanna continiue? (y/n)")
    if _var == 'n':
        exit()
if not 'station' in stationdf:
    print('The columnname for the stations is not called: station! Rename this column.')
    exit()
if not stationdf['station'].is_unique:
    print('Column station has non-unique names.')
    exit()


#%%


def ESM_landuse(stationdf, bufferlist, ESM_folder, ESM_maps, aggregate_simplyfied = False, only_simplyfied_landuse = False):
    """ Get landcover fractions for locations and a buffer radius based on the ESM maps.

    Keyword arguments: \n
        stationdf -- pd.DataFrame
                    a pandas dataframe with at least the following columns: station (the name of the station),
                    lat (latitute of station), lon (lontitude of the station) 
        bufferlist -- list
                    a LIST with the buffer radii in meter (default 0.0) \n
        ESM_folder -- string
                    a string that is the PATH TO THE FOLDER that contains the ESM maps \n
        ESM_maps -- list
                    a list of strings where each element is the name of a ESM map (ex. ['N30E38', 'N32E36, ...'])
                    These names schould be maps inside the ESM_folder. \n
        aggregate_simplyfied -- Bool(default False)
                    if True, the aggregated landuseclasses 'green' and 'pervious' will be calculated. \n
        only_simplyfied_landuse -- Bool(default False)
                    if True, only the aggregated classes will be returned. \n
    Return
        stationdf with added columns for the landuseclasses as fractions
    """

    if bool(set(['geometry', 'crop_buffer', 'map_to_use', 'buffer']) & set(list(stationdf.columns))):
        _var = input("One of following columns in dataframe will be overwritten: 'geometry', 'crop_buffer', 'map_to_use', 'buffer'. Do you wanna continiue? (y/n)")
        if _var == 'n':
            exit()
    if not 'station' in stationdf:
        print('The columnname for the stations is not called: station! Rename this column.')
        exit()
    if not stationdf['station'].is_unique:
        print('Column station has non-unique names.')
        exit()
            
        
    station_geo = gpd.GeoDataFrame(stationdf, geometry=gpd.points_from_xy(stationdf.lon, stationdf.lat))
    station_geo = station_geo.set_crs(epsg=4326)
    crop_buffer = max(bufferlist) + 50

    
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
    
    station_geo = which_map_to_use_ESM(station_geo, ESM_folder, ESM_maps)
    
    
    
    
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
    
    
    def get_landuse(geo_df, buffer_radius, layerlist, layerdict, mapdict, aggregate_simplyfied=False, only_simplyfied_landuse=False):
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
            pervious_list = ['railways', 'nbu_area-streets', 'bu-area-streets', 'bu_buildings']
            green_list = ['nbu_area-open_space', 'nbu_area-green_ndvi', 'nbu_area-street_green_ndvi', 'bu_area-green_ndvi', 'bu_area-green_ua', 'bu_area-street_green_ndvi']
            
            geo_df['pervious'] = geo_df[pervious_list].sum(axis=1) + (0.5 * geo_df['bu_area-open_space'])
            geo_df['green'] = geo_df[green_list].sum(axis=1) + (0.5 * geo_df['bu_area-open_space'])
            if only_simplyfied_landuse:
                
                landusetypelist.remove('water')
                geo_df = geo_df.drop(landusetypelist, axis=1) #drop specific landuseclasses
                landusetypelist = ['water', 'green', 'pervious']
            else:
                landusetypelist.extend(['green', 'pervious'])
        return geo_df.drop(['buffer', 'map_to_use'], axis=1), landusetypelist
     


    returndf = pd.DataFrame()
    for buffer_radius in bufferlist:           
        buffer_station_geo, landusecolumns = get_landuse(station_geo, buffer_radius = buffer_radius,
                           layerlist = [0,1,2,10,15,20,25,30,35,40,41,45,50],
                           layerdict=classes,
                           mapdict = mapdict,
                           aggregate_simplyfied = aggregate_simplyfied, #aggregate to water, impervious and pervious
                           only_simplyfied_landuse=only_simplyfied_landuse) 
        buffer_station_geo['buffer'] = buffer_radius
        returndf = returndf.append(buffer_station_geo)
    
    
    pivot_columns = landusecolumns
    pivot_columns.append('buffer')
    
    meta_data_df = returndf[returndf.columns.difference(pivot_columns)] #select all colums that are not part of the landuse function
    
    pivot_columns.append('station')
    returndf = returndf[pivot_columns].pivot_table(index='station', columns='buffer').swaplevel(axis=1).sort_index(1)
    returndf = pd.merge(meta_data_df,returndf, how='inner', on='station')
    
    returndf.drop_duplicates(inplace=True)
    returndf.set_index('station', inplace=True)
    
    
    return returndf
geo_data = ESM_landuse(stationdf,
                   bufferlist = bufferlist,
                   ESM_folder = ESM_folder,
                   ESM_maps = ESM_maps,
                   aggregate_simplyfied = aggregate_simplyfied,
                   only_simplyfied_landuse = only_simplyfied_landuse)

#%%writing

print("Done, you can find the output here: ", data_output_file)
geo_data.to_csv(data_output_file)