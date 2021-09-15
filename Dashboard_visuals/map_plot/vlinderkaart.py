#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate the spatial VLINDER maps per station as is used in the dashboard. 

Created on Tue Sep 14 15:42:26 2021

@author: thoverga
"""

#%% Imports
import pandas as pd
from bokeh.tile_providers import get_provider, Vendors
from bokeh.plotting import figure, show
from pyproj import Proj, transform
from bokeh.models.markers import Circle
from bokeh.models import ColumnDataSource
from bokeh.models.glyphs import Text
from bokeh.io import export_png, output_notebook
from bokeh.models import Legend
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead, Label
import os, sys
from pathlib import Path

#%%import path file
main_repo_folder = (Path(__file__).resolve().parent.parent.parent)
sys.path.append(str(main_repo_folder))
import path_handler
print('Path handling module loaded')

#%% Load paths to use
#imput
data_path = path_handler.meta_data_stations

#output
savedirectory = os.path.join(path_handler.folders['dashboard_visuals']['map_plot'], 'output')
#%% what station to plot


vlinder_to_plot = 'vlinder28'
with_stacked_barchart_bool = True

plot_all_stations = True


#%% Import data

data = pd.read_csv(data_path)

vlinderlijst = list(data['VLINDER'].unique())

landcovers = ['groen', 'verhard', 'water'] #volgorde van belang voor de stack 
#landcover_colors = ['green', 'red', 'blue'] #volgorde corresponderend met landcovers
landcover_colors = ["#6ebd02","#8c8c8c", "#00afff"] #groen - grijs - blauw
#landcover_colors = ["#6ebd02","#d12f06", "#00afff"] #groen - rood - blauw
buffers = ['20', '50', '100', '250', '500']






def make_stacked_hist(station, data, landcovers = landcovers, landcover_colors = landcover_colors, buffers = buffers, save_directory = savedirectory):
    subdf = data[data['VLINDER'] == station] #subsetting data
    
    #refactor data in dictionary

    histdict = {x:[] for x in landcovers}
    histdict['buffers'] = buffers

    for buf in buffers:
        for landcovertype in landcovers:
            columnname = landcovertype + buf
            histdict[landcovertype].append(subdf[columnname].iloc[0])
            
    #create figure
    p = figure(x_range=histdict['buffers'], plot_height=250,
           toolbar_location=None, tools="")

    p.vbar_stack(landcovers, x='buffers', width=0.9, color=landcover_colors, fill_alpha = 0.7, source=histdict,
                 legend_label=landcovers)

    p.xaxis.axis_label = 'Buffer straal (m)'
    p.yaxis.axis_label = 'Fractie'


    p.axis.axis_label_text_font_style = 'bold'
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    p.xaxis.major_label_text_font_style = 'bold'
    p.yaxis.major_label_text_font_style = 'bold'

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.legend.location = "bottom_center"
    p.legend.orientation = "horizontal"
    
    p.background_fill_alpha= 0.0
    p.border_fill_alpha = 0.0
    p.background_fill_color = None
    p.border_fill_color = None
    
    
    

    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.legend.location = "bottom_center"
    p.legend.orientation = "horizontal"


    p.xaxis.axis_line_width = 3 
    p.yaxis.axis_line_width = 3 
    p.xaxis.axis_label_text_font_size = '17pt'
    p.yaxis.axis_label_text_font_size = '15pt'
    p.xaxis.axis_label_text_font_style = 'bold'
    p.yaxis.axis_label_text_font_style = 'bold'

    p.yaxis.major_label_text_font_style = "bold"
    p.yaxis.major_label_text_font_size = '15pt'
    p.xaxis.major_label_text_font_style = "bold"
    p.xaxis.major_label_text_font_size = '15pt'

    p.legend.label_text_font_size = "15pt"
    p.legend.border_line_width = 3
    p.legend.border_line_color = "navy"
    p.legend.border_line_alpha = 0.5
    #p.legend.background_fill_color = "grey"
    p.legend.background_fill_alpha = 0.8

    p.background_fill_color = "#000000"
    p.border_fill_color = "#000000"
    p.background_fill_alpha= 0.0
    p.border_fill_alpha = 0.0
    
    
    
    #save figure
    figure_location = os.path.join(save_directory,"stacked_" + station + ".png")
    
    export_png(p, filename= figure_location)
    print("Stacked histograme saved here: " + figure_location)
    return figure_location
    





def makefigure(station,optie,savedirectory,data, with_stacked_barchart = False, landcovers = landcovers, landcover_colors = landcover_colors, buffers = buffers, save_directory = savedirectory):
    print(station)
    
    subdata = data[data["VLINDER"] == station]
    
    

    def projectie(subdata):
        # The coordinates have to be transformed from latlon to mercator
        inProj = Proj(init='epsg:4326') #lat lon coordinate system
        outProj = Proj(init='epsg:3857') # mercator coordinate system
        lat = list(subdata["lon"])[0]
        lon = list(subdata["lat"])[0]
        
        proj = transform(inProj, outProj, lat, lon)
        
        y_mercator = proj[0]
        x_mercator = proj[1]
        return x_mercator, y_mercator
    x,y = projectie(subdata)
    

    


    school = list(subdata['school'])[0]
    naam = list(subdata['VLINDER'])[0]
    stad = list(subdata['stad'])[0]
    titel = naam +' (' + stad + ') - ' + school
    
    print(titel)


    #output_file("tile.html")
    #kaart = get_provider(Vendors.STAMEN_TONER) #kaart1
    #kaart = get_provider(Vendors.CARTODBPOSITRON) #kaart2
    #kaart = get_provider(Vendors.CARTODBPOSITRON_RETINA) #kaart3
    kaart = get_provider(Vendors.STAMEN_TERRAIN) #kaart4
    #kaart = get_provider(Vendors.STAMEN_TERRAIN_RETINA) #kaart5
    #kaart = get_provider(Vendors.STAMEN_TONER_BACKGROUND) #kaart6

    if (optie):

        xrange = 7000.
        yrange = 3500.
        xmin = x -(xrange * 0.4)
        xmax = x + (xrange * 0.6)
        leftfraction = 0.01
        ymin = y - (yrange * leftfraction)
        ymax = y + (yrange * (1-leftfraction))
        

        figuur = figure(x_range=(ymin, ymax), y_range=(xmin, xmax), x_axis_type="mercator", y_axis_type="mercator", plot_width=600, plot_height=300)
        figuur.add_tile(kaart)
        figuur.title.text = titel
        figuur.toolbar.logo = None
        figuur.toolbar_location = None
        figuur.title.text_font_size = '16pt'
        figuur.axis.visible = False
        figuur.xgrid.grid_line_color = None
        figuur.ygrid.grid_line_color = None
        #show(figuur)

   
        source = ColumnDataSource(subdata)
    

        dots = Circle(x=y, y=x, size=12, fill_color="red", fill_alpha=0.8, line_color=None)

        lengtefactor = 1./8.
        lengtefactor_arrow = 8./5.

        glyph20 = Circle(x=y, y=x, size=20*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)
        glyph50 = Circle(x=y, y=x, size=50*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)
        glyph100 = Circle(x=y, y=x, size=100*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)
        glyph250 = Circle(x=y, y=x, size=250*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)
        glyph500 = Circle(x=y, y=x, size=500*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)


        #figuur.add_layout(Arrow(end=NormalHead(fill_color="#3288bd", size=10), x_start=y, y_start=x, x_end=y+500*lengtefactor_arrow, y_end=x))

        mytext = Label(x=y + 1300, y=x-400, text='500m', text_font_size = "10pt", text_color = "#3288bd", angle = 1.57 )
        #figuur.add_layout(mytext)


        #figuur.add_glyph(source, glyph20)
        #figuur.add_glyph(source, glyph50)
        #figuur.add_glyph(source, glyph100)
        #figuur.add_glyph(source, glyph250)
        #figuur.add_glyph(source, glyph500)

        figuur.add_glyph(source, dots)

        #print(savedirectory+station+"_plot_no_background.png")
        #figuur.image_url(url=[savedirectory + station + "_plot_no_background.png"], x=y+(xrange * 0.1)+1200, y=x+(yrange*1.15), w=1.1*xrange, h=0.95*yrange)
        #figuur.image_url(url=['/home/thomas/Documents/VLINDER/Sever code/plot.png'], x=y+(xrange * 0.1), y=x+(yrange*1.15), w=1.1*xrange, h=0.95*yrange)
    
    
    
        figuur.image_url(url=[os.path.join(path_handler.folders['dashboard_visuals']['map_plot'],'north.png')], x=y+(xrange * 1.04)+1200, y=x-(yrange*0.3), w=0.2*xrange, h=0.2*xrange)
        figuur.image_url(url=[os.path.join(path_handler.folders['dashboard_visuals']['map_plot'],'km_scale.png')], x=y+(xrange * 0.47)+1200, y=x-(yrange*0.48), w=0.55*xrange, h=0.1*xrange)
    else :

        xrange = 7000.
        yrange = 3500.
        xmin = x -(xrange * 0.4)
        xmax = x + (xrange * 0.6)
        leftfraction = 0.9
        ymin = y - (yrange * leftfraction)
        ymax = y + (yrange * (1-leftfraction))
        
        

        figuur = figure(x_range=(ymin, ymax), y_range=(xmin, xmax), x_axis_type="mercator", y_axis_type="mercator", plot_width=600, plot_height=300)
        figuur.add_tile(kaart)
        figuur.title.text = titel
        figuur.toolbar.logo = None
        figuur.toolbar_location = None
        figuur.title.text_font_size = '16pt'
        figuur.axis.visible = False
    
        #show(figuur)

   
        source = ColumnDataSource(subdata)
    

        dots = Circle(x=y, y=x, size=12, fill_color="red", fill_alpha=0.8, line_color=None)

        lengtefactor = 1./8.
        lengtefactor_arrow = 8./5.

        glyph20 = Circle(x=y, y=x, size=20*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)
        glyph50 = Circle(x=y, y=x, size=50*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)
        glyph100 = Circle(x=y, y=x, size=100*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)
        glyph250 = Circle(x=y, y=x, size=250*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)
        glyph500 = Circle(x=y, y=x, size=500*lengtefactor, line_color="#3288bd", line_width=3, fill_alpha = 0.0)


        #figuur.add_layout(Arrow(end=NormalHead(fill_color="#3288bd", size=10), x_start=y, y_start=x, x_end=y+500*lengtefactor_arrow, y_end=x))

        mytext = Label(x=y + 1300, y=x-400, text='500m', text_font_size = "10pt", text_color = "#3288bd", angle = 1.57 )
        figuur.add_layout(mytext)


        figuur.add_glyph(source, glyph20)
        figuur.add_glyph(source, glyph50)
        figuur.add_glyph(source, glyph100)
        figuur.add_glyph(source, glyph250)
        figuur.add_glyph(source, glyph500)

        figuur.add_glyph(source, dots)

    
        figuur.image_url(url=[savedirectory + station + "_plot.png"], x=y-(xrange * 1.5)+1400, y=x+(yrange*1.15), w=1.1*xrange, h=0.95*yrange)
        #figuur.image_url(url=['/home/thomas/Documents/VLINDER/Sever code/plot.png'], x=y+(xrange * 0.1), y=x+(yrange*1.15), w=1.1*xrange, h=0.95*yrange)
    
    
    
        figuur.image_url(url=[os.path.join(path_handler.folders['dashboard_visuals']['map_plot'],'north.png')], x=y+(xrange * 0.6)+1350, y=x-(yrange*0.3), w=0.2*xrange, h=0.2*xrange)
        figuur.image_url(url=[os.path.join(path_handler.folders['dashboard_visuals']['map_plot'],'km_scale.png')], x=y+(xrange * 0.1)+1000, y=x-(yrange*0.48), w=0.55*xrange, h=0.1*xrange)
    
    
    if with_stacked_barchart:
        bar_im_location = make_stacked_hist(station, data)
        
        #figuur.image_url(url=[bar_im_location],anchor = 'top_right', x = ymax, y = xmax, w = 9000, h = 3000)
        figuur.image_url(url=[bar_im_location],anchor = 'top_right', x = ymax + 6400, y = xmax, w = 8000, h = 3000)
    
    
    export_png(figuur, filename=os.path.join(save_directory, naam+".png"))
    print('figure for ', naam, ' is saved here: ', os.path.join(save_directory, naam+".png"))
    return figuur


#%%
figuur = makefigure(vlinder_to_plot, True, savedirectory,data = data, with_stacked_barchart = with_stacked_barchart_bool)




if plot_all_stations:
    for stationname in data['VLINDER']:
        makefigure(stationname, True, savedirectory,data = data, with_stacked_barchart = with_stacked_barchart_bool)