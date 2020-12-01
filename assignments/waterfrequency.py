#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Don't forget to apply the best-practices for scientific programming:

Write tests: Check special cases. Satellite images often show no data values. 
  What happens to them during the ToA conversion or when calculating the spectral index,
  when calculating the number valid pixels.
Follow the PEP8 Style guide and refactore (rename) variables for better readability
"""

import json
import os
import math
import numpy as np
import rasterio as rio
import pyproj
import matplotlib.pyplot as plt
from utils_waterfrequency import *
from test_utils_waterfrequency import *
import pdb


def calc_water_frequency(config_site, output_dir):
	"""
	-----  Calculates the water frequency of a whole satellite time series ------
	config_site : arguments from Configuration file (.json) indicating for which area(s) the water frequency is proceed
	output_dir :  argument from Configuration file (.json) indicating the folder where to store the output
	returns TIF file on disk
	"""


	########### ------- STEP 1: -------########
	## Create and execute query for satellite images

	# Get user defined parameters from config_file and apply them to load satellite images from Amazon AWS Open Data Registry.
	bbox = config_site["bbox"]
	time_period = config_site["time"]
	cloud_cover = config_site["cloud_cover"]
	collection = "landsat-8-l1"

	items = satellite_search_AWS(bbox, time_period, cloud_cover, collection)

	print(items._collections)
	print(items.summary())

	# Create a folder to store the data.
	scene_dir = r".\scenes"
	if not os.path.exists(scene_dir):
		os.mkdir(scene_dir)
	#os.chdir(scene_dir)

	#########------- STEP 2: --------##############
	## Get paramters for NDWI calculation, which is needed to detect areas coverd by water

	# Areas within the bounding box which are not covered by the image are assigned the value 65535, later they are replaced with no value
	FILL_VALUE = 65535
	# Store calculated water frequency from each scene in list bands
	bands = []
	# amount of all scenes, needed for user information
	total_itemNumber = len(items)
	# scene which is currently proceed while going through the time series, needed for user information
	item_counter = 0

	# window coordinates for scene
	bbox_crs = "EPSG:4326"


	########### ------- STEP 3: --------##############
	## Calculate NDWI (Normalized difference water index) by going through each satellite scene

	for item in items[:2]:
		item_counter += 1

		# Load images from URLs by using rasterio
		band_swir_url = item.assets["B7"]["href"]
		band_green_url = item.assets["B3"]["href"]

		# Read metadata from each satellite scene
		mtl = read_metafile(item, scene_dir)

		###### Parsing the metadata files ########
		reflectance_mult = 'REFLECTANCE_MULT_BAND_'
		reflectance_add = 'REFLECTANCE_ADD_BAND_'
		parameters = parse_mtl(mtl)

		# Extract required parameters for conversion to ToA reflectance
		band_green_mult = parameters[reflectance_mult + '3']
		band_green_add = parameters[reflectance_add + '3']
		band_swir_mult = parameters[reflectance_mult + '7']
		band_swir_add = parameters[reflectance_add + '7']
	
		# Read green spectral band (band 3)
		with rio.open(band_green_url) as src:
			scene_affine = src.transform
			scene_crs = src.crs
			win = get_window_for_scene(bbox, bbox_crs, scene_affine, scene_crs)
			green = src.read(1, window=win, boundless=True, fill_value=FILL_VALUE)
	
		# Read shortwave infrared spectral band (band 7)
		with rio.open(band_swir_url) as src:
			scene_affine = src.transform
			scene_crs = src.crs
			win = get_window_for_scene(bbox, bbox_crs, scene_affine, scene_crs)
			swir = src.read(1, window=win, boundless=True, fill_value=FILL_VALUE)

		# Create a binary array indicating pixels which contain valid data
		valid_pixels = np.where((green != FILL_VALUE) & (swir > 0) & (green > 0), True, False)

		# Convert the two spectral bands to ToA reflectance.
		green_toa = to_toa(green, band_green_add, band_green_mult)
		swir_toa = to_toa(swir, band_swir_add, band_swir_mult)
		#plt.imshow(green_toa)

		# calculate ndwi
		ndwi = calc_ndwi(green_toa, swir_toa)
		#plt.imshow(ndwi)

		# convert invalid pixels to nan
		ndwi = np.where(valid_pixels, ndwi, np.nan)

		bands.append(ndwi)

		print("NDWI-Scene {} was append to output list,\nit's the {}. item from {} satellite scenes".format(item, item_counter, total_itemNumber))


	#############--------- STEP 4:	----------###########
	## Calculate the water frequency and save it

	# NDWI images stacked to 3-dimnesional array
	bands_arr = np.array(bands)

	# Create binary values based on boundary (0.3), with water (1) and no-water (0).
	water_masks = np.where(bands_arr >= 0.3, 1, 0)
	print("Create binary values indicating areas covered by water or land")

	# Number of valid pixels during in whole time series
	valid_pixels = get_valid_pixels(bands_arr)

	# Number of pixel with water in whole time series
	water_frequency = water_masks.sum(axis=0) / valid_pixels
	print("Calculate the water frequency for the whole time period")

	# Display the water frequency (whole time series)
	fig, axes = plt.subplots(1,1,figsize=(10,10))
	water_freq_plot = axes.imshow(water_frequency, cmap="Blues")
	plt.colorbar(mappable=water_freq_plot)
	
	# Display number of valid pixel
	fig, axes = plt.subplots(1,1,figsize=(10,10))
	valid_pixels_plot = axes.imshow(valid_pixels, cmap="Blues")
	plt.colorbar(mappable=valid_pixels_plot)


	###############------------ STEP 5: ----------#################
	## Saving image of water frequency as tif file
	outname=config_site["name"]+"_waterfrequency.tif"
	outfilepath = output_dir + "/" + outname

	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	## source : https://geohackweek.github.io/raster/04-workingwithrasters/
	## Reuse profile from band7 (STEP 3) and adapt it to size and datatype of waterfrequency (array)
	with rio.open(band_swir_url) as src:
		profile = src.profile.copy()
	profile.update({'dtype': 'float64',
				'height': water_frequency.shape[0],
				'width': water_frequency.shape[1]}) 
				#'transform':scene_affine stays the same like in STEP 3

	with rio.open(outfilepath, "w", **profile) as dst:
		print("Write water frequency to: {}".format(outname))
		dst.write(water_frequency, 1)



if __name__ == "__main__":

	config_file = r".\config.json"
	with open(config_file) as src:
		config = json.load(src)

	for site in config["sites"].items():
		calc_water_frequency(site[1], config["output_dir"])
## site[1] = inner dictonary with bbox, name, time = keys()

