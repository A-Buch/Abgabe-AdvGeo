def mergedCSVpattern(pattern_list, selected_cols=None, sep_char="[;,|]"):
    '''
    pattern_list: list of identical patterns in filenames to merge files with same pattern
    selected_cols : predefine which columns should be loaded
    sep_char : string or regular expression to indicate seperator
    return : group files in current and all subdirectories based on pattern in filename and filetype to one pd.DF
    '''
    import glob
    import numpy as np
    import pandas as pd
    import pdb
    df_combi_list = []

    for item in pattern_list:
        ## also look in the next subfolders
        files = glob.glob("**/*{}*.csv".format(item), recursive=True)  ## get from cur. dir and all sub.dirs
        pdb.set_trace()
        df_combi = pd.concat([pd.DataFrame(pd.read_csv(f, sep=sep_char, engine="python", index_col=False), columns=selected_cols) for f
             in files], join="inner")  # join on identical col.names
        # index_col shouldnt be read in
        # try to fetch multiple separor types, def engine="python" to not confuse it with regex separators, which can be read via c-engine
        df_combi_list.append(df_combi)

    return df_combi_list


def merge_df2csv(left_dfs_list, right_dfs, col2merge_left, col2merge_right, outdir, outname):
    """
    left_dfs_list: list of similar dataframes, column names and datatypes should be identic between the dataframes
    right_df: single dataframe which should be merged, needs at least one identic column and datatype
    outname : use a column element (eg. sensor id) to generate unique filenames
    merge_pattern : column names with identical values and datatype in both dataframes (str)
    returns list of merged dataframes and saves each as csv
    """
    import os
    import pandas as pd
    import pdb

    df_all_list = []

    for df in left_dfs_list:
        df_merged = pd.merge(df, right_dfs, left_on=col2merge_left, right_on=col2merge_right)
        df_all_list.append(df_merged)
        pdb.set_trace()
        outname_sep = df_merged[outname][0]
        fpath = os.path.join(outdir, "dataset_" + str(outname_sep) + ".csv")
        df_merged.to_csv(fpath, sep=";")

    return df_all_list


## Idea from: https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-python/


def brackets(input_section):
    ## https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-python/
    '''
    input_section: part which should be tested if all brackets are set probably
    return: message if brackets are balanced
    '''
    import numpy as np
    import pandas as pd
    import pdb

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
#     open_list = ['(', '[', '{']
#     close_list = [')', ']', '}']
#     stack = []
#     for c in expression:
#         if c in open_list:
#             stack.append(c)
#         elif c in close_list:
#             pos = close_list.index(c)
#             if len(stack) > 0 and stack[-1] == open_list[pos]:
#                 stack.pop()
#             else:
#                 return False
#     return True if not stack else False
#
#
# n = int(input())
# for i in range(n):
#     exp = input()
#     print(check_balance(exp))