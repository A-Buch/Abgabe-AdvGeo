# import unittest
# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)
# if __name__ == '__main__':
#     unittest.main()

import os
import pandas as pd
import numpy as np
from utils_finalproject import mergedCSVpattern, merge_df2csv, brackets

os.chdir(r"C:\Users\Anna\Documents\UNI\MA Semi 1\Adv Geoscripting\AdvGeo_Project\data")

def test_mergedCSVpattern():
    """
    Test the function if cells have an unregular expression and is float or int (also date objects):
    """
    # Given
    ## create test DF with predefined data types
    days = pd.date_range("20200101", periods=15)
    days = pd.Series(days, name="D")

    control_df = pd.DataFrame(np.random.randint(0, 100, size=(15, 3)), columns=["A", "B", "C"])
    control_df = pd.concat([control_df, days], axis=1)
    control_df = control_df.astype({"A": "int64", "B": "float64", "C": "int64", "D": "int64"})
    control_df.to_csv("test_df.csv", sep=";", index=False)

    control_df2 = pd.DataFrame(np.random.randint(0, 100, size=(15, 3)), columns=["A", "B", "C"])
    control_df2 = pd.concat([control_df2, days], axis=1)
    control_df2 = control_df2.astype({"A": "int64", "B": "float64", "C": "int64", "D": "int64"})
    control_df2.to_csv("test_df2.csv", sep=";", index=False)

    exp_type = control_df.dtypes
    exp_nonchar = 0
    pattern_list = ["test_df"]

    # when
    test_list = mergedCSVpattern(pattern_list)  # returns list of one item

    # then
    test_df = pd.DataFrame(test_list[0])
    test_df_type = test_df.dtypes
    test_df_str = test_df.astype(str)  ## convert all df.elements to string
    dftype = test_df_str.applymap(lambda x: str.count(x, ",/|-")).sum()

    assert test_df_type.all() == exp_type.all()
    assert sum(dftype) == exp_nonchar


def test_merge_df2csv():
    """
    Test if timestamp is in ascending order
    """
    # Given
    # create lists of dataframes
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
        assert df.index.all() == exp_df.index.all()


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