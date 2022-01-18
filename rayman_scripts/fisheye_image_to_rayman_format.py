#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 11:07:17 2022

@author: thoverga
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import copy

#%% settings

#debug
image_path = "/home/thoverga/Documents/VLINDER_github/VLINDER/rayman_scripts/VLINDER_foto/24_Eeklo_HetLeen.jpg"

output_path = "/home/thoverga/Documents/VLINDER_github/VLINDER/rayman_scripts/testje2.bmp"

#%%

def plotimg(img):
    plt.imshow(img)
    plt.show()
    
def format_image(image_path, output_path):
    # Read the image, convert it into grayscale, and make in binary image for threshold value of 1.
    img = cv2.imread(image_path,0)
    
    # keep a copy of original image
    original = cv2.imread(image_path)
    
    # use binary threshold, all pixel that are beyond 3 are made white
    _, thresh_original = cv2.threshold(img, 70, 255, cv2.THRESH_BINARY)
    # plotimg(thresh_original)
    
    # Now find contours in it.
    thresh = copy.copy(thresh_original)
    im2,contours,hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    #get contours with highest height
    lst_contours = []
    for cnt in contours:
        ctr = cv2.boundingRect(cnt)
        lst_contours.append(ctr)
        
    #select the biggest boundingbox    
    x,y,w,h = sorted(lst_contours, key=lambda coef: coef[3])[-1]

    
    
    # draw contours
    ctr = copy.copy(original)
    cv2.rectangle(ctr, (x,y),(x+w,y+h),(0,255,0),2)
    

    
    #crop image to boundingbox
    cropped_img = original[y:y+h, x:x+w]

    
    #resize image to square 1000 X 1000
    def resizeAndPad(img, size, padColor=0):
        h, w = img.shape[:2]
        sh, sw = size
    
        # interpolation method
        if h > sh or w > sw: # shrinking image
            interp = cv2.INTER_AREA
        else: # stretching image
            interp = cv2.INTER_CUBIC
    
        # aspect ratio of image
        aspect = w/h  # if on Python 2, you might need to cast as a float: float(w)/h
    
        # compute scaling and pad sizing
        if aspect > 1: # horizontal image
            new_w = sw
            new_h = np.round(new_w/aspect).astype(int)
            pad_vert = (sh-new_h)/2
            pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
            pad_left, pad_right = 0, 0
        elif aspect < 1: # vertical image
            new_h = sh
            new_w = np.round(new_h*aspect).astype(int)
            pad_horz = (sw-new_w)/2
            pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
            pad_top, pad_bot = 0, 0
        else: # square image
            new_h, new_w = sh, sw
            pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0
    
        # set pad color
        if len(img.shape) is 3 and not isinstance(padColor, (list, tuple, np.ndarray)): # color image but only one color provided
            padColor = [padColor]*3
    
        # scale and pad
        scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interp)
        scaled_img = cv2.copyMakeBorder(scaled_img, pad_top, pad_bot, pad_left, pad_right, borderType=cv2.BORDER_CONSTANT, value=padColor)
    
        return scaled_img
    
    
    scaled_cropped_img = resizeAndPad(cropped_img, (1000,1000), 127)
    plotimg(scaled_cropped_img)
    
    #write to BMP file
    cv2.imwrite(output_path, scaled_cropped_img)
    return
    
    
format_image(image_path, output_path)