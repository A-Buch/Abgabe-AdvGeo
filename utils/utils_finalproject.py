#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import os
import glob
import numpy as np
import pandas as pd
from datetime import datetime, date
from wetterdienst.dwd.observations import DWDObservationData, DWDObservationParameterSet, DWDObservationPeriod, DWDObservationResolution

from sklearn.svm import SVR, SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error


def get_weatherdata(station_id, weather_parameters, resolution, periods, start_date, end_date):
	"""
	--- Return timeseries of DWD weatherstations with userdefined parameters, spatial and temporal resoultion ---- 
	station_id : list of station number(s) eg. [4928]
	weather_parameters: list of parameters in format: DWDObservationParameterSet.PARAMETERNAME,
	resolution :  resolution time in format: DWDObservationResolution.RESOLUTION
	periods : list of observation period in format: DWDObservationPeriod.PERIOD
	start_date : string indicating the start date in format "YYYY-MM-DD"
	end_date : string indicating the end date in format "YYYY-MM-DD"
	return pandas DataFrame with selected observations
	
	Further information for parameter types: https://wetterdienst.readthedocs.io/_/downloads/en/latest/pdf/	  
	If resolution has not a certain parameter: --> Atrribute error 
	"""
	observations = DWDObservationData(
		station_ids = station_id,
		parameters = weather_parameters,
		resolution = resolution,
		periods = periods,
		start_date = start_date,
		end_date = end_date,
		tidy_data = True,
		humanize_column_names = True).collect_safe()

	return observations
	
	
def mergedCSVpattern(pattern_list, selected_cols=None, sep_char="[;,|]"):
	'''
	--- Read in and merge csv files accoridng to pattern in filename ----
	pattern_list: list of identical patterns in filenames to merge files with same pattern
	selected_cols : predefine which columns should be loaded
	sep_char : string or regular expression to indicate seperator
	return : group files in current and all subdirectories based on pattern in filename and filetype to one pd.DF
	'''
	df_combi_list = []

	for item in pattern_list:
		## also look in the next subfolders
		files = glob.glob("**/*{}*.csv".format(item), recursive=True)  ## get from cur. dir and all sub.dirs
		#pdb.set_trace()
		df_combi = pd.concat([pd.DataFrame(pd.read_csv(f, sep=sep_char, engine="python", index_col=False), columns=selected_cols) for f in files], join="inner")  # join on identical col.names
		# index_col shouldnt be read in
		# try to fetch multiple separor types, def engine="python" to not confuse it with regex separators, which can be read via c-engine
		df_combi_list.append(df_combi)

	return df_combi_list


def merge_df2csv(left_dfs_list, right_df, col2merge_left, col2merge_right, outdir, outname):
	"""
	---- Merges pandas DataFrames according to identic column values and saves them as CSV ----
	left_dfs_list: list of similar dataframes, column names and datatypes should be identic between the dataframes
	right_df: single dataframe which should be merged, needs at least one identic column and datatype, rows which just occure in this dataframe (but not in the left dataframe) are ignored
	outname : use a column element (eg. sensor id) to generate unique filenames
	merge_pattern : column names with identical values and datatype in both dataframes (str)
	returns list of merged dataframes and saves each dataframe as csv file
	"""
	df_all_list = []

	for df in left_dfs_list:
		df_merged = pd.merge(df, right_df, left_on=col2merge_left, right_on=col2merge_right)
		df_all_list.append(df_merged)
		#pdb.set_trace()
		outname_sep = df_merged[outname][0]
		fpath = os.path.join(outdir, "dataset_" + str(outname_sep) + ".csv")
		df_merged.to_csv(fpath, sep=";")

	return df_all_list


def splitTrainTest_TS(df, split_date, feature_cols, target_col, standarize=False):
	"""
	--- Create Train and Test data based on a certain boundary date ----
	df : pandas Dataframe which should be splitted
	split_date : string object indicating the temporal boundary, format "YYYY-MM-DD HH:MM:SS"
	feature_cols : list of strings indicating the column names which are used as features
	target_col : string indicating the column which should be predicted
	standarize : boolean indicating if feaures should be scaled to similar units, defaullts False
	return four pandas DataFrames in the order of X_train, y_train, X_test, y_test
	"""
	X = df[feature_cols]
	Y = df[target_col]
	#preX_train, preX_test, y_train, y_test = train_test_split(X, Y, test_size=0.4, random_state=42)

	if standarize == True:
		### Standardize data due to different untis of the paramters/features (columns)
		scaler = StandardScaler() 
		X = pd.DataFrame(scaler.fit_transform(X),columns=X.columns) 

	# create training and testing date by splitting by certain date
	X_train = X.loc[:split_date] # before date
	X_test = X.loc[split_date:] # after date

	y_train = Y.loc[:split_date] 
	y_test = Y.loc[split_date:]

	print("Training input (rows, features): ", X_train.shape)
	print("Training target: ", y_train.shape)
	print("Testing input (rows, features): ", X_test.shape)
	print("Testing target: ", y_test.shape)

	return X_train, y_train, X_test, y_test



def brackets(input_section):
	## https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-python/
	'''
	--- Check if the brackets in given string are balanced -----
	input_section: part which should be tested if all brackets are set probably
	return: message if brackets are balanced
	'''
	# balanced parentheses in an expression
	open_list = ["[", "{", "("]
	close_list = ["]", "}", ")"]

	#input_section = str("""  """).format(input_section)

	stack = []
	for i in input_section:
		if i in open_list:
			stack.append(i)
		elif i in close_list:
			pos = close_list.index(i)
			if ((len(stack) > 0) and
					(open_list[pos] == stack[len(stack) - 1])):
				stack.pop()
			else:
				return "Unbalanced"
	if len(stack) == 0:
		return "Balanced"
	else:
		return "Unbalanced"

## medium http:/
# def check_balance(expression):
#	  open_list = ['(', '[', '{']
#	  close_list = [')', ']', '}']
#	  stack = []
#	  for c in expression:
#		  if c in open_list:
#			  stack.append(c)
#		  elif c in close_list:
#			  pos = close_list.index(c)
#			  if len(stack) > 0 and stack[-1] == open_list[pos]:
#				  stack.pop()
#			  else:
#				  return False
#	  return True if not stack else False
#
#
# n = int(input())
# for i in range(n):
#	  exp = input()
#	  print(check_balance(exp))