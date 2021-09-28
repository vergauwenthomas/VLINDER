#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 15:42:09 2021

Collection of GIS functions


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
import matplotlib.pyplot as plt
import matplotlib.colors
from collections import Counter
from shapely.geometry import Polygon, Point, box
from rasterio.merge import merge
from rasterio.mask import mask



import geo_maps_config

#%% Get information functions

def geo_map_info(src):
    """ This functions prints out some basic info of a geo object """
    
    print('MAP INFO')
    print('map mode: ', src.mode)
    print('map closed?: ',src.closed)
    print('number of bands: ', src.count)
    print('dtypes per band: ', {i: dtype for i, dtype in zip(src.indexes, src.dtypes)})
    print('number of gridpoints (width): ', src.width)
    print('number of gridpoints (height): ', src.height)
    print('')
    print('MAP GEO INFO')
    print('map bounds in projection space: ', src.bounds)
    print('spatial resolution in physical units along x-axis: ', src.transform[0])
    print('spatial resolution in physical units along y-axis: ', -src.transform[4])
    print('CRS of the projection: ', src.crs)
    print('Spatial units: ', src.crs.linear_units_factor)
    
    
    y = input('Plot the raster band 1? (y/n): ')
    if y == 'y':
        plt.imshow(src.read(1), cmap='pink')
        plt.show()


def geo_in_domain_of(raster, small_geo):
    """ This functions returns True if small_geo is FULLY contained in the raster bounderies, else it returns False. """
    
    if not ((raster.bounds[0] < small_geo.bounds[0]) & (raster.bounds[2] > small_geo.bounds[0])): #left bound
        print('left bound of polygon not in domain of raster')
        return False
    
    if not ((raster.bounds[1] < small_geo.bounds[1]) & (raster.bounds[3] > small_geo.bounds[1])): #bottom
        print('bottom bound of polygon not in domain of raster')
        return False
    if not ((raster.bounds[2] > small_geo.bounds[2]) & (raster.bounds[0] < small_geo.bounds[2])): #right
        print('bottom bound of polygon not in domain of raster')
        return False
    if not ((raster.bounds[3] > small_geo.bounds[3]) & (raster.bounds[1] < small_geo.bounds[3])): #top
        return False
    return True
    
#%% plot functions

def plot_polygon(geo_map):
    """ Basic function to plot a polygon. """
    
    if isinstance(geo_map,Polygon):
         p = gpd.GeoSeries(geo_map)
         p.plot()
         plt.show()
    else:
        print('format is not a polygon')


def plot_raster(raster, raster_info, band = 1):
    """ This function plots a Georaster using the colormap defined in the config file. """
    
    if not isinstance(raster, rasterio.io.DatasetReader):
         print('format of the raster is not a DatasetReader!')
         return None
    colormapdict = geo_maps_config.get_color_map_dict(raster_info)
    
    #create colormapper
    cmap = matplotlib.colors.ListedColormap(colormapdict.values())
    boundaries = list(colormapdict.keys())
    norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)
    
    #plot object
    plt.imshow(raster.read(band), cmap=cmap, norm = norm, interpolation = None)
    
    # getting current axes
    a = plt.gca()
      
    # set visibility of x-axis as False
    xax = a.axes.get_xaxis()
    xax = xax.set_visible(False)
      
    # set visibility of y-axis as False
    yax = a.axes.get_yaxis()
    yax = yax.set_visible(False)
    
    
    plt.show()
    
    
    

#%% Create polygon functions
        
def get_country_geometry(countryname = 'Belgium', crs = 'EPSG:4326'):
    """ This function returns a (multi) polygon that represents the bounaries of a given country. 
        The coordinate reference system of the polygon can be set with the crs argument.
        Make shure the countryname is writen in English. """
    
    file = '/home/thoverga/Documents/github/maps/country_borders/WB_countries_Admin0_10m/WB_countries_Admin0_10m.shp'
    shapefile = gpd.read_file(file)
    shapefile = shapefile.to_crs(crs)
    return shapefile.loc[shapefile['NAME_EN'] == countryname, 'geometry'].iloc[0], shapefile.crs

def create_box_polygon(bound, crs = 'epsg:4326'):
    """ This function returns a rectangular polygon based on the max. and min. latlon coordinates in the bound dictionary. 
        The coordinate reference system of the polygon can be set with the crs argument.
        
        The bound dictionary has following keys: xmin, xmax, ymin, ymax with values in latlon coordinates. """
        
    p1 = [bound['xmin'], bound['ymax']]
    p2 = [bound['xmax'], bound['ymax']]
    p3 = [bound['xmax'], bound['ymin']]
    p4 = [bound['xmin'], bound['ymin']]
    
    polygon_geom = Polygon([p1,p2,p3,p4])
    init_crs = 'epsg:4326'
    polygon = gpd.GeoDataFrame(index=[0], crs=init_crs, geometry=[polygon_geom])
    polygon = polygon.to_crs(crs)
    return polygon.iloc[0]

        
#%%%%   GIS FUNCTIONS



def df_to_geodf(df, crs, lat_identifier, lon_identifier):
    """ This function returns a geopandas dataframe with a geometry column in the given crs coordinates. """

    geo_df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_identifier], df[lat_identifier]))
    geo_df = geo_df.set_crs(epsg = 4326) #inpunt are gps coordinates
    geo_df = geo_df.to_crs(crs)
    return geo_df


def coordinate_to_point_geometry(lat, lon, crs):
    """ This function returns a shapely point object in the given coordinate referece frame. """
    
    point_geo = gpd.GeoDataFrame(pd.DataFrame(data={'lat': [lat], 'lon': [lon]}), geometry=gpd.points_from_xy([lon], [lat]))
    point_geo = point_geo.set_crs(epsg = 4326) #inpunt are gps coordinates
    point_geo = point_geo.to_crs(crs)
    
    return point_geo.iloc[0]['geometry']

def coordinate_to_circular_buffer_geometry(lat_center, lon_center, radius_m, crs):
    """ This function returns a shapely (circular) polygon object with a given radius in meter, in the given coordinate referece frame. """

    
    circ_geo = gpd.GeoDataFrame(pd.DataFrame(data={'lat': [lat_center], 'lon': [lon_center]}), geometry=gpd.points_from_xy([lon_center], [lat_center]))
    circ_geo = circ_geo.set_crs(epsg = 4326) #inpunt are gps coordinates
    circ_geo = circ_geo.to_crs(crs)
  
    circ_geo['polygon'] = circ_geo['geometry'].buffer(float(radius_m), resolution=30)
    
    return circ_geo.iloc[0]['polygon']

def coordinates_to_rectangel_geometry(lat_1, lat_2, lon_1, lon_2, crs):
    """ This function returns a shapely (rectangular) polygon object, in the given coordinate reference frame. """


    data = pd.DataFrame(data={'lat': [float(lat_1), float(lat_2)], 'lon': [float(lon_1), float(lon_2)]})
    geodf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['lon'], data['lat']))
    geodf = geodf.set_crs(epsg = 4326) #inpunt are gps coordinates
    geodf = geodf.to_crs(crs)
    
    x_values = [geom.x for geom in geodf['geometry']]
    y_values = [geom.y for geom in geodf['geometry']]
    
    return box(min(x_values), min(y_values), max(x_values), max(y_values))




def ULTIMATE_read_from_rasterfile(geometry, raster_file_list, return_map_info = False, return_counts = False, none_if_no_overlap = False):
    """ The ultimate GIS-application function takes as arguments an geometry and a (list of) geotiff file(s).
        This function can handle multiple rasters and merges them if nesecary. 
        
        The return depends on the geometry type:
            * If geometry type is a point, the corresponding raster value is returned. 
            * if geometry type is a polygon, the return is an array of corresponding raster values inside the geometry.
        """
    
    # --------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------HELP functions ----------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------------------------------
    
    def validate_raster(raster_file_list):
        print('validate raster maps ...')
        categorical_bool = False
        #check raster meta info
        raster_file_dict = {file: {} for file in raster_file_list}
        for raster in raster_file_dict:
            with rasterio.open(raster) as src:
                res_x_y = src.res
                if (not res_x_y[0] == res_x_y[1]) & (abs(float(res_x_y[0]) - float(res_x_y[1]))/float(res_x_y[0]) > 0.05): #if x and y resolution differs more than 5%
                    print('raster map(' + raster + ') has different x and y resolution. This functionality is not included!')
                    sys.exit()
                if not src.crs.linear_units_factor[0] == 'metre':
                    print('raster map unit is not meter but ', str(src.crs.linear_units_factor[0]), ' this functionality is not included!')
                    sys.exit()
                if not src.count == 1:
                    print('There are ', str(src.count) , ' raster bands detected. This functionality is not implemented.')
                    sys.exit()
                
                if not src.dtypes[0] == 'float32':
                    print('The data type of the grid cells in the raster are no floats. The raster will be considered to be categorical!')
                    categorical_bool = True
                    
                #TODO: check if dtypes of all rasters are the same
                
                
                raster_file_dict[raster]['resolution'] = src.res[0]
                raster_file_dict[raster]['crs'] = src.crs
       
        
        res_list = [float(raster_file_dict[x]['resolution']) for x in raster_file_dict.keys()]
        if not all((abs(x - res_list[0])/res_list[0]) < 0.05  for x in res_list):
            print('The resolutions of the different maps are not equal, no buffer geometries can be made')
            print(raster_file_dict)
            sys.exit()
      
            
        if not len(set([raster_file_dict[x]['crs'] for x in raster_file_dict.keys()])) == 1:
            print('The CRSs of the different DEM maps are not equal, no buffer geometries can be made')
            sys.exit()
        
        return categorical_bool
    
    
    def geometry_in_map(geometry, raster_file):
        
        if geometry.geom_type == 'Point':
            with rasterio.open(raster_file) as src:
                bounds = src.bounds
                if ((geometry.x < bounds.right) & (geometry.x > bounds.left) & (geometry.y > bounds.bottom) & (geometry.y < bounds.top)):
                    return True
                else:
                    return False
                
        if geometry.geom_type == 'Polygon':
        #first check if a part of the geometry is contained in the raster 
            with rasterio.open(raster_file) as src:
                raster_bounds_polygon = box(src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top)
                if raster_bounds_polygon.contains(geometry): #geometry fully in raster
                    return True, 'fully_contained'
                elif raster_bounds_polygon.intersects(geometry): #part of geometry in raster
                    return True, 'partially'
                else:
                        return False, 'none'
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    

    
    # --------------------------------------------------------VALIDATE INPUT DATA -----------------------------------------------------------------------
    
    if isinstance(raster_file_list, str): #if there is one tif file
        raster_file_list = [raster_file_list]
    
    
    if geometry.geom_type == 'Point':
        print('geometry is Point type, raster value will be returned!')
        geom_type = 'Point'
    
    
    elif geometry.geom_type == 'Polygon':
        print('geometry is Polygon type, cropped array will be returned!')
        geom_type = 'Polygon'
        categorical_bool = validate_raster(raster_file_list = raster_file_list)
    
    else:
        print('geometry type of geometry not supported. Only Point and Polygon are supported.')
    
    with rasterio.open(raster_file_list[0]) as src:
        
        raster_CRS = src.crs
        raster_RES = src.res[0]
        raster_spatial_UNIT = src.crs.linear_units_factor[0]
        raster_BANDS = src.count
    raster_info = {
        'crs': raster_CRS,
        'resolution': raster_RES,
        'spatial_unit': raster_spatial_UNIT,
        'bands': raster_BANDS
        }
    
    
    #-------------------------------------------------------get POINT value ------------------------------------------------
    if geom_type == 'Point':
        #get map to use
        map_to_use = "None"
        for raster_file in raster_file_list:
            if geometry_in_map(geometry, raster_file):
                map_to_use = raster_file
                break
        
        if map_to_use == 'None':
            print('The point with coordinats:')
            print('x: ', geometry.x, '  y: ', geometry.y)
            print('is not contained in these maps: ', raster_file_list)
            print('Make shure if the CRS of the geometry is equal to the CRS of the map: ')
            print(raster_CRS.to_string())
            if none_if_no_overlap:
                return None
            else:
                sys.exit()
        
        
        #get raster value
        with rasterio.open(map_to_use) as src:
            band_values = [val for val in src.sample([(geometry.x, geometry.y)])]
            
        value = band_values[0][0]
    
    # -----------------------------------------------------get POLYGON cropped array -----------------------------------------------------
    # find the maps to use
    if geom_type == 'Polygon':
        maps_to_use = []
        for raster_file in raster_file_list:
            intersect_bool, intersect_info = geometry_in_map(geometry, raster_file)
            if intersect_bool:
                maps_to_use.append(raster_file)
                print('geometry is ', intersect_info, ' contained in ', raster_file)
                
        #return None if no raster is found that overlaps
        if not bool(maps_to_use): 
            print('The polygon with extends:')
            print(geometry.bounds)
            print('is not contained in these maps: ', raster_file_list)
            print('Make shure if the CRS of the geometry is equal to the CRS of the map: ')
            print(raster_CRS.to_string())
            if none_if_no_overlap:
                return None
            else:
                sys.exit()
        
        
        # if geometry is encompassed in one raster 
        
        if len(maps_to_use) == 1: #geometry fully contained in raster
            zs = rasterstats.zonal_stats(vectors = geometry,
                                         raster = maps_to_use[0],
                                         band_num=1, 
                                         all_touched= True, #if true, inclueds the cells at the boundaries of the polygon
                                         categorical = categorical_bool,
                                         raster_out= True,
                                         # prefix=str(layer)+'_'
                                              )
            if return_counts & categorical_bool: #return frequency table 
                category_counts = pd.Series(zs[0]).drop(['mini_raster_affine', 'mini_raster_array', 'mini_raster_nodata'])
                category_counts.name = 'counts'
                category_counts = category_counts.to_frame()
                category_counts['category'] = category_counts.index
                category_counts.reset_index(drop=True, inplace=True)
                return category_counts
            else:   
                value = zs[0]['mini_raster_array']
        
        else: # if geometry overlaps with multiple maps
            print('Cropping and temporary saving rasters...')
            cropped_raster_file_list = []
            i = 0
            
            #create rectangle around geometry to crop and clip the rasters to. 
            geometry_box = box(geometry.bounds[0], geometry.bounds[1],
                               geometry.bounds[2], geometry.bounds[3])
            
            #create a cropped version for each map that encompasses the geometry bounderies
            for raster in maps_to_use:
                with rasterio.open(raster) as src:
                    out_image, out_transform = rasterio.mask.mask(src, [geometry_box], crop=True)
                    out_meta = src.meta
                    
                out_meta.update({"driver": "GTiff",
                                 "height": out_image.shape[1],
                                 "width": out_image.shape[2],
                                 "transform": out_transform})
                
                #temporaly save the tif map in the script folder location
                cropped_file = os.path.join(path_handler.folders['meta_data_folder'], 'cropped_raster_' + str(i) + '.tif')
                cropped_raster_file_list.append(cropped_file)
                with rasterio.open(cropped_file, "w", **out_meta) as dest:
                    dest.write(out_image)
                i += 1
                
          
            #merge the cropped rasters and temporaly save in the script folder location
            merged_array, merged_affine = rasterio.merge.merge([rasterio.open(x) for x in cropped_raster_file_list])
            merged_meta = src.meta 
            merged_meta.update({"driver": "GTiff",
                                 "height": merged_array.shape[1],
                                 "width": merged_array.shape[2],
                                 "transform": merged_affine})
            
            merged_location = os.path.join(path_handler.folders['meta_data_folder'], 'merged_raster.tif')
            with rasterio.open(merged_location, "w", **merged_meta) as dest:
                    dest.write(merged_array)
            
            #get local array from the merged raster
            zs = rasterstats.zonal_stats(vectors = geometry,
                                         raster = merged_location,
                                         band_num=1, 
                                         all_touched= True, #if true, inclueds the cells at the boundaries of the polygon
                                         categorical = categorical_bool,
                                         raster_out= True,
                                         # prefix=str(layer)+'_'
                                              )
            if return_counts & categorical_bool: #return frequency table 
                category_counts = pd.Series(zs[0]).drop(['mini_raster_affine', 'mini_raster_array', 'mini_raster_nodata'])
                category_counts.name = 'counts'
                category_counts = category_counts.to_frame()
                category_counts['category'] = category_counts.index
                category_counts.reset_index(drop=True, inplace=True)
                value = category_counts
            else:
                value = zs[0]['mini_raster_array']
            
            #Delete the create raster tif files
            for crop_tif in cropped_raster_file_list: os.remove(crop_tif)
            os.remove(merged_location)
    if return_map_info:    
        return value, raster_info
    else:
        return value
