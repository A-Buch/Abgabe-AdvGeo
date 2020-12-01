#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import rasterio as rio
import pyproj
from satsearch import Search
from datetime import datetime



def satellite_search_AWS(bbox, time_period, cloud_cover, collection):
	"""
	---- Userdefined search for satellite scenes on Amazon AWS Open Data Registery -------
	bbox : list of coordinates in epsg:4326, format [min_x, min_y, max_x, max_y]
	time_period: string wit start and end date in format "YYYY-MM-DD/YYYY-MM-DD"
	cloud_cover: singel integer indicating the maximum cloud cover in percent (%)
	collection: string of the satellite version eg. "landsat-8-l1" or "sentinel-s1-l1c"
	return satstac.itemcollection.ItemCollection
	"""
	## Check if collection exists in AWS
	collection_query = {"collection": {"eq": collection}}
	collection_expression = Search(query=collection_query)
	if collection_expression.found() == 0:
		print("This satellite name does not exist in AWS Open Data Repository\neg. try 'landsat-8-l1' or 'sentinel-s1-l1c'.")
	
	else:
		query = {"eo:cloud_cover": {"lt": cloud_cover},
			"collection": {"eq": collection}}
	
	## check if timespan is an appropriate format
	try:
		start_time, end_time = time_period.split("/")
		try:
			start_time = datetime.strptime(start_time, "%Y-%m-%d").date()
			end_time = datetime.strptime(end_time, "%Y-%m-%d").date()

			# check if the start date of the time period is before the end date
			if start_time < end_time:
				# join start and end date to one string for using in Search() as the datetime
				time_period = str(start_time) + "/" + str(end_time)
			else:
				print("Switch start and end time of your timespan")

		except TypeError:
			print("Adapt the time period to an appropriate format of type: 'YYYY-MM-DD/YYYY-MM-DD'")
	except:
		print("Adapt the time period to an appropriate format of type: 'YYYY-MM-DD/YYYY-MM-DD'")

	# execute search on AWS Open Data Registry
	search_result = Search(bbox=bbox, query=query, datetime=time_period)
	# show user the number of scenes
	print("{} satellite scenes were found".format(search_result.found())) 
	items = search_result.items()

	return items



def geogr_2_image(affine,x, y):
	"""
	--- Converts image coordimates to geographic coordinates ----
	affine: affine tranformation of scene (affine.Affine)
	x: x coordinate
	y: y coordinate
	return tuple of geographixc coordinates
	"""
	return ~affine * (x, y)

def image_2_geogr(affine,x, y):
	"""
	--- Converts geographic coordimates to image coordinates -----
	affine: affine tranformation of scene (affine.Affine)
	x: x coordinate
	y: y coordinate
	return tuple of image coordinates
	"""
	return affine * (x, y)


def get_window_for_scene(bbox, bbox_crs, band_affine, band_crs):
	"""
	---- Calculates the window for reading a raster file based on a bounding box -----
	bbox: list of coordinates [xmin, ymin, xmax, ymax]
	bbox_crs: crs of bounding box given as string, eg. "epsg:4326"
	band_affine: affine tranformation of scene
	band_crs: crs of band given as string, eg. "epsg:4326"
	return rasterio.windows.Window
	"""
	# change the crs (coordinate reference system) of the bounding box to the crs of the satellite scenes
	ul_x, ul_y = pyproj.transform(pyproj.Proj(init=bbox_crs), pyproj.Proj(init=band_crs), bbox[0], bbox[3])
	lr_x, lr_y = pyproj.transform(pyproj.Proj(init=bbox_crs), pyproj.Proj(init=band_crs), bbox[2], bbox[1])

	ul_row, ul_col = rio.transform.rowcol(band_affine, ul_x, ul_y, op=round)
	lr_row, lr_col = rio.transform.rowcol(band_affine, lr_x, lr_y, op=round)
	#ul_x, ul_y = pyproj.transform(pyproj.Proj(init=bbox_crs), pyproj.Proj(init=band_crs), bbox[0], bbox[3])
	#lr_x, lr_y = pyproj.transform(pyproj.Proj(init=bbox_crs), pyproj.Proj(init=band_crs), bbox[1], bbox[2])
	#ul_col, ul_row = geogr_2_image(band_affine, ul_x, ul_y)
	#lr_col, lr_row = geogr_2_image(band_affine, lr_x, lr_y)

	## round coordinates
	# ul_row = round(ul_row)
	# ul_col = round(ul_col)
	# lr_row = round(lr_row)
	# lr_col = round(lr_col)
	# rows = round(lr_row - ul_row)
	# cols = round(lr_col - ul_col)

	rows = lr_row - ul_row
	cols = lr_col - ul_col
	
	return rio.windows.Window(ul_col, ul_row, cols, rows)


def read_metafile(item, mtl_dir):
	"""
	--- Get metadata file (txt) which is associated to a single satellite scene ---
	item : satstac.itemcollection.ItemCollection indicating a single satellite scene
	scene_dir : path indicating the location of the metadata file
	return list of tuples with metadata from a satellite scene
	"""
	mtl_file = item.download("MTL", path=mtl_dir)
	with open(mtl_file) as src:
		mtl = src.readlines()
		
		return mtl


def parse_mtl(metadata):
	"""
	Parse metadata 
	metadata : metadata as a list of tuples
	returns: dictionary where the keys are the parameters from metadata, values are floats or srings
	"""
	params = {}
	rest = {}

	for i in metadata[:-1]:
		k, v = i.strip().split(" = ")

		# Try to convert values to float.
		try:
			v = float(v)
			params[k] = v
		except ValueError:
			v = str(v)
			rest[k] = v
	print("Could convert", len(params), "items from a satellite metafile to float and added them to output,\nall other items were added as strings", len(rest), "items.")

	return params

def get_valid_pixels(bands_array):
	"""
	--- Calculates which pixels are empty or have a value ---
	bands_arr : numpy array of satelite band(s), 2- or 3-dimensional
	return one dimensional array indicating which pixels are NAN or not
	"""
	valid_pixels = np.invert(np.isnan(bands_array)).sum(axis=0)
	return valid_pixels

def to_toa(raw_band, add, mult):
	'''
	--- Converts the raw band to reflectance ----
	raw_band : satellite band
	add : additive band
	mult: multiplicative band
	return top-of-atmosphere reflectance band
	'''
	toa = mult * raw_band + add
	return toa
	

def calc_ndwi(green, swir):
	'''
	green : satellite band for green
	swir : second satellite band for short wave inrared
	returns the Normalized Difference Water Index (NDWI) 
	'''
	ndwi = (green - swir) / (green + swir)
	return ndwi

