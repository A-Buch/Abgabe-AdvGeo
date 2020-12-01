#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Module with tests to check if functions from "utils_waterfrequency" work correctly
"""

__author__ = "Anna Buch, Student, Heidelberg University"
__email__ = "a.buch@stud.uni-heidelberg.de"

import os
import numpy as np
import rasterio as rio
from utils_waterfrequency import *


def test_satellite_search_AWS():
	"""
	---Check if the user hints are printed correctly if collection type or time period are in a wrong format---
	"""
	# Given incorrect satellite name and switched timespan
	collection = "sentinel-2-l2c" # right: sentinel-2-l1c
	time_period = "2020-12-30/2020-09-30"
	exp_userhint_time = "Switch start and end time of your timespan"
	exp_userhint_collection = "This satellite name does not exist in AWS Open Data Repository\neg. try 'landsat-8-l1' or 'sentinel-s1-l1c'."

	######## Code snippets to test: #######
	## Check if collection exists in AWS
	collection_query = {"collection": {"eq": collection}}
	collection_expression = Search(query=collection_query)
	if collection_expression.found() == 0:
		userhint_collection ="This satellite name does not exist in AWS Open Data Repository\neg. try 'landsat-8-l1' or 'sentinel-s1-l1c'."
	else:
		query = {"eo:cloud_cover": {"lt": cloud_cover},
			"collection": {"eq": collection}}

	## check if timespan is an appropriate format
	start_time, end_time = time_period.split("/") 
	try:
		start_time = datetime.strptime(start_time, "%Y-%m-%d").date()
		end_time = datetime.strptime(end_time, "%Y-%m-%d").date()
		if start_time < end_time:
			time_period = str(start_time) + "/" + str(end_time)
		else:
			userhint_time = "Switch start and end time of your timespan"
	except TypeError:
		print("Adapt the time period to an appropriate format of type: 'YYYY-MM-DD/YYYY-MM-DD' ")


	# then
	assert userhint_time == exp_userhint_time
	assert userhint_collection == exp_userhint_collection



def test_geogr_2_image():
	"""
	---- Tests the function geogr_2_image() with one coordinate pair inside the image ----
	"""
	# Given
	west = 204285.0
	north = 4268115.0
	pixel_size_y = 30
	pixel_size_x = 30
	affine = rio.transform.from_origin(west, north, pixel_size_x, pixel_size_y)
	exp_x = 10
	exp_y = 20
	pixel_x = west + exp_x * pixel_size_x
	pixel_y = north - exp_y * pixel_size_y

	# when
	img_x, img_y = geogr_2_image(affine, pixel_x, pixel_y)

	assert img_x == exp_x
	assert img_y == exp_y



def test_get_window_utm_bbox():
	"""
	---Tests get_window_for_scene() with a bounding box given in UTM (same as scene crs)---
	"""
	# Given
	west = 204285.0
	north = 4268115.0
	pixel_size_y = 30
	pixel_size_x = 30
	scene_affine = rio.transform.from_origin(west, north, pixel_size_x, pixel_size_y)
	scene_crs = 'EPSG:32628'
	rows = 40
	cols = 10
	bbox = [west, north - rows * pixel_size_y, west + cols * pixel_size_x, north]
	bbox_crs = 'EPSG:32628'

	# when
	win = get_window_for_scene(bbox, bbox_crs, scene_affine, scene_crs)
	expected_win = rio.windows.Window(0, 0, cols, rows)
	print(win)
	print(expected_win)

	assert win == expected_win



def test_get_window_geogr_bbox():
	"""
	--- Tests get_window_for_scene() with a bounding box given in geogr. coordinates ----
	"""
	# Given
	west = 206685.0
	north = 1715415.0
	pixel_size_y = 30
	pixel_size_x = 30
	scene_affine = rio.transform.from_origin(west, north, pixel_size_x, pixel_size_y)
	scene_crs = 'EPSG:32628'

	bbox = [-16.811, 13.627, -16.356, 14.14]
	bbox_crs = 'EPSG:4326'

	# expected
	rows = 1903
	cols = 1627
	col_off = 3261
	row_off = 5048

	# When
	win = get_window_for_scene(bbox, bbox_crs, scene_affine, scene_crs)
	expected_win = rio.windows.Window(col_off, row_off, cols, rows)

	assert win == expected_win



def test_read_metafile():
	"""
	--- Test if metadata file is not empty and in ascii format ---
	"""
	# Given
	# Get user defined parameters from config_file and apply them to load satellite images from Amazon AWS Open Data Registry.
	collection = "landsat-8-l1" #"sentinel-2-l1c" #
	time_period = "2019-06-01/2020-05-01"
	bbox = [-16.811,13.627,-16.356,14.14] # [minx, miny, maxx, maxy]
	time_period = '2019-06-01/2020-06-01'
	cloud_cover=3
	items = satellite_search_AWS(bbox, time_period, cloud_cover, collection)
	item =items[0]
	scene_dir = r".\scenes"
	if not os.path.exists(scene_dir):
		os.mkdir(scene_dir)

	# when
	mtl_file = item.download("MTL", path=scene_dir)
	filetype = mtl_file.rsplit(".",1)[1] # split at last occurence
	item = read_metafile(item, scene_dir)

	# then
	assert filetype == "txt"
	assert len(item)> 0



def test_parse_mtl():
	"""
	Check if floats and negative numbers are detected and convert correctly
	"""
	# Given
	metadata = ['REFLECTANCE_MULT_BAND_2 = 2.0000E-05\n',
		'REFLECTANCE_MULT_BAND_3 = 2.0000E-05\n',
		'REFLECTANCE_MULT_BAND_9 = 2.0000E-05\n',
		'REFLECTANCE_ADD_BAND_1 = -0.100000\n',
		'REFLECTANCE_ADD_BAND_2 = -0.100000\n',
		'END_GROUP = MIN_MAX_REFLECTANCE\n',
		'GROUP = MIN_MAX_PIXEL_VALUE\n',
		'QUANTIZE_CAL_MAX_BAND_1 = 65535\n',
		'QUANTIZE_CAL_MIN_BAND_1 = 1\n']
	# when 
	parameters = parse_mtl(metadata)
	
	# float test
	assert parameters["REFLECTANCE_MULT_BAND_3"] == 2.0000E-05
	# negative numbers test
	assert parameters["REFLECTANCE_ADD_BAND_1"] == -0.1



def test_to_toa():
	"""
	--- Test if raw band just contain no data values---
	"""
	# Given
	band3_add = np.float64(-0.1)
	band3_mult = np.float64(0.43656365691)
	nan_array = np.empty((1000,2000))
	nan_array[:] = np.NaN
	bandNAN = to_toa(nan_array, band3_add, band3_mult)

	exp_bandNAN = np.empty((1000,2000))
	exp_bandNAN[:] = np.float64(4)
	#exp_bandNAN = np.NaN * nan_array + np.NaN #np.NaN #

	if np.array_equal(bandNAN, exp_bandNAN, equal_nan=True) != True:
		print("Satellite scene only contain no data values")



def test_get_valid_pixels():
	"""
	--- Test if 3 dimensional array contains bands with no data values---
	"""
	# Given
	exp_array = np.empty((1903, 1627))
	exp_array[:] = np.int32(3)
	bands_arr = np.empty((3,1903, 1627))

	valid_pixels = np.invert(np.isnan(bands_arr)).sum(axis=0)
	# valid_pixels: 3-dimensional array (timeseries) was changed to 2-dimensional (single image)
	# valid_pixels : NANs converted to integer 3

	assert valid_pixels.sum() == exp_array.sum(), "Satellite scene only contains no data values.\nBe careful the number of scenes with NaNs affects the calculation"

