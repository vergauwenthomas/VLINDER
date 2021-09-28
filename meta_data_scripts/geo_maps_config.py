#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 09:20:11 2021

@author: thoverga
"""







#%% S2GLC_EUROPE_2017 Landcover map
s2glc_settings = {
    'file': '/home/thoverga/Documents/github/maps/Landuse/S2GLC_EUROPE_2017/S2GLC_Europe_2017_v1.2.tif',
    'data_band': 1,
    'classes': {
        0: {'color': (255,255,255,255), 'name': 'clouds'},
        62: {'color': (210,0,0,255), 'name': 'Artificial surfaces and constructions'},
        73: {'color': (253,211,39,255), 'name': 'Cultivated areas'},
        75: {'color': (176,91,16,255), 'name': 'Vineyards'},
        82: {'color': (35,152,0,255), 'name': 'Broadleaf tree cover'},
        83: {'color': (8,98,0,255), 'name': 'Coniferious tree cover'},
        102: {'color': (249,150,39,255), 'name': 'Herbaceous vegetation'},
        103: {'color': (141,139,0,255), 'name': 'Moors and heathland'},
        104: {'color': (95,53,6,255), 'name': 'Sclerophyllous vegetation'},
        105: {'color': (149,107,196,255), 'name': 'Marshes'},
        106: {'color': (77,37,106,255), 'name': 'Peatbogs'},
        121: {'color': (154,154,154,255), 'name': 'Natural material surfaces'},
        123: {'color': (106,255,255,255), 'name': 'Permanent snow covered surfaces'},
        162: {'color': (20,69,249,255), 'name': 'Water bodies'},
        255: {'color': (255,255,255,255), 'name': 'No data'}
        }
    }

lcz_settings = {
    'file': '/home/thoverga/Documents/github/maps/Landuse/EU_LCZ_map.tif',
    'data_band': 1,
    'classes': {
        1: {'color': (20,18,18,255), 'name': 'LCZ-1, compact highrise'},
        2: {'color': (255,17,0,255), 'name': 'LCZ-2, compact midrise'},
        3: {'color': (232,163,2,255), 'name': 'LCZ-3, compact lowrise'},
        4: {'color': (104,0,250,255), 'name': 'LCZ-4, open highrise'},
        5: {'color': (163,98,252,255), 'name': 'LCZ-5, open midrise'},
        6: {'color': (206,171,255,255), 'name': 'LCZ-6, open lowrise'},
        7: {'color': (6,149,196,255), 'name': 'LCZ-7, lightweight lowrise'},
        8: {'color': (86,211,252,255), 'name': 'LCZ-8, large lowrise'},
        9: {'color': (252,247,86,255), 'name': 'LCZ-9, sparsely built'},
        10: {'color': (133,132,129,255), 'name': 'LCZ-10, heavy industry'},
        11: {'color': (0,94,27,255), 'name': 'LCZ-A, dense trees'},
        12: {'color': (2,171,50,255), 'name': 'LCZ-B, scattered trees'},
        13: {'color': (59,237,74,255), 'name': 'LCZ-C, bush, scrub'},
        14: {'color': (195,235,87,255), 'name': 'LCZ-D, low plants'},
        15: {'color': (133,94,3,255), 'name': 'LCZ-E, bare rock or paved'},
        16: {'color': (244,164,25,255), 'name': 'LCZ-F, bare soil or sand'},
        17: {'color': (25,208,224,255), 'name': 'LCZ-G, water'},
        0: {'color': (25,208,244,255), 'name': 'LCZ-G, water'} #omdat de zee 0 is
        }
    }



#%% predefined regions

gent_region = {
        'xmin': 3.6498,
        'xmax': 3.828586,
        'ymin': 51.0053,
        'ymax': 51.111377
        }

belgium_region = {
        'xmin': 2.521798,
        'xmax': 6.433314,
        'ymin': 49.475441,
        'ymax': 51.516600
    }



#%%functions



def rgb_to_hex(rgb_tuple):
    """Return color as #rrggbb for the given color values."""
    return '#%02x%02x%02x' % (rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])



def normalize_colors(settings):
    dic = settings['classes']
    for category in dic:
        # dic[category]['color'] =  tuple([(float(x)/255.0) for x in dic[category]['color']])
        dic[category]['color'] = rgb_to_hex(dic[category]['color'])
    settings['classes'] = dic
    return settings

s2glc_settings = normalize_colors(s2glc_settings)
lcz_settings = normalize_colors(lcz_settings)

def get_color_map_dict(map_info):
    return {value: map_info['classes'][value]['color'] for value in map_info['classes']}
def get_color_map_dict_by_classname(map_info):
    return {map_info['classes'][value]['name']: map_info['classes'][value]['color'] for value in map_info['classes']}
def get_name_map_dict(map_info):
    return {value: map_info['classes'][value]['name'] for value in map_info['classes']}
