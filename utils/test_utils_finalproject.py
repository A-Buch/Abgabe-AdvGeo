# import unittest
# class MyTestCase(unittest.TestCase):
#	  def test_something(self):
#		  self.assertEqual(True, False)
# if __name__ == '__main__':
#	  unittest.main()


### in CMD: python -m pytest jupyterworkflow package -- tests all in package

import os
import pandas as pd
import numpy as np
from utils_finalproject import *



def test_mergedCSVpattern():
	"""
	--- Test cells if they are of type float, int, date or object, 
		and how function deals with unregular expressions [strings,_-? \]---
	"""
	# Given
	## create test DF with predefined data types
	days = pd.date_range("20200101", periods=10)
	days = pd.Series(days, name="D")

	expressions = pd.Series(["wired expressions", "222,3", "23/ 2", "22-03", " or |nothing", "wired expressions", "222,3", "23/ 2", "22-03"," or| nothing"], name="E")

	control_df = pd.DataFrame(np.random.randint(0, 100, size=(10, 3)), columns=["A", "B", "C"])
	control_df = pd.concat([control_df, days, expressions], axis=1)
	# define columns with pandas data types (python has no datetime64 and object type)
	control_df = control_df.astype({"A": "int64", "B": "float64", "C": "int64", "D": "datetime64", "E":"object"})
	control_df.to_csv("test_df.csv", sep=";", index=False)

	control_df2 = pd.DataFrame(np.random.randint(0, 100, size=(10, 3)), columns=["A", "B", "C"])
	control_df2 = pd.concat([control_df2, days, expressions], axis=1)
	control_df2 = control_df2.astype({"A": "int64", "B": "float64", "C": "int64", "D": "datetime64", "E":"object"})
	control_df2.to_csv("test_df2.csv", sep=";", index=False)

	control_df = control_df.astype({"A": "int64", "B": "float64", "C": "int64", "D": "object", "E":"object"})							
	exp_nonchar = 8

	# when
	test_list = mergedCSVpattern(pattern_list=["test_df"])	# returns list of one item
	print("Function mergedCSVpattern() converts pandas datatype 'datetime64' to 'object' type.")
	print("Function mergedCSVpattern() ignores '-/' and whitespaces, but interpretes ',' and '|' as seperators.")

	# then
	test_df = pd.DataFrame(test_list[0])
	test_df_str = test_df.astype(str)  ## convert all df.elements to string
	dftype = test_df_str.E.str.contains(r"[,/|-]").sum()
	#test_df_str.E.applymap(lambda x: str.contains(x, r"[,/|-]")).sum()

	assert all(test_df.dtypes == control_df.dtypes)
	assert dftype == exp_nonchar




def test_merge_df2csv():
	"""
	Test if timestamp is in ascending order
	"""
	#Given
	#create lists of dataframes
	left_df = pd.DataFrame(pd.read_csv("test_df.csv", sep=";"))
	left_list = [left_df, left_df, left_df]
	right_df = pd.DataFrame(pd.read_csv("test_df2.csv", sep=";"))

	col2merge_left = "D"
	col2merge_right = "D"
	outdir = r""
	outname = "D"

	# when
	out_merge_df2csv = merge_df2csv(left_list, right_df, col2merge_left=col2merge_left, col2merge_right=col2merge_right, outdir=outdir, outname=outname)

	for df in out_merge_df2csv:
		df = df.set_index("D")
		exp_df = df.sort_index()

		# then
		assert all(df.index == exp_df.index)
	### See: https://www.youtube.com/watch?v=qMkhTo7sdHo&list=PLYCpMb24GpOC704uO9svUrihl-HY1tTJJ&index=7

#assert all(data.columns == [])
#assert isinstance(dtat.aindex, odDatetimeIndex)



def test_brackets():
## https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-python/
	# Given
	control_str =str(""" Two deleted closing brackets:
	X_train = preX_train.drop(["P1","P2","P1_category"], axis=1)
	X_test = preX_test.drop(["P1","P2", "P1_category"], axis=1
	print("Training input (rows, features): ", X_train.shape
	print("Testing target: ", y_test.shape)
	""")
	# when
	test_str = brackets(control_str)
	# then
	assert "Unbalanced" == test_str