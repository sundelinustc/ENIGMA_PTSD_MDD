
# (0) Packages
import os # get & set paths
import time # measuring time elapsed
import pandas as pd # dataframe
import numpy as np
from multiprocessing import Pool # parallel processing

# (1) Functions
# (1.1) Function to list the files with a given string pattern in a folder
# Input
# args, a tuple with 3 elements
#          --- folder, path to the folder in which to search for files of interest
#          --- pattern, string pattern that all of the files of interst have in their file names, e.g., "task-rest_falff.nii.gz"
#          --- data_type, data type, e.g., "fALFF", "ReHo"
# Output
# --- df, return a dataframe (one file per row) with 3 columns: 
#          --- full_path, full path to the file of interst
#          --- fID, concatenation of site name and subject ID, seperated by "_" 
#          --- data_type, data type, e.g., "fALFF", "ReHo"
def SDL_list_files(args):
    folder, pattern, data_type = args
    data = {'full_path': [], 'fID': [], 'data_type': []}
    
    for root, dirs, files in os.walk(folder):
        for file in files:
            if pattern in file:
                full_path = os.path.join(root, file)
                data['full_path'].append(full_path)
                
                upper_folder = os.path.basename(os.path.dirname(full_path))
                file_start = file.split("_")[0]
                
                # fID: sitename + "_" + subjectID, based on data filename
                if upper_folder != file_start:
                    # for CENC data, e.g., CENC1/sub-1234_task-rest_falff.nii.gz
                    fID = upper_folder + "_" + file_start
                else:
                    # for new_halfpipe data, e.g., Duke/sub-1234/sub-1234_task-rest_falff.nii.gz
                    second_upper_folder = os.path.basename(os.path.dirname(os.path.dirname(full_path)))
                    fID = second_upper_folder + "_" + file_start
                
                data['fID'].append(fID)
                data['data_type'].append(data_type)
    
    df = pd.DataFrame(data)
    return df

# # (1.2) Function of parallel processing to run list_files() function across folders and data types
# # Input
# # args, list of tuples with 3 elements
# #          --- folder, path to the folder in which to search for files of interest
# #          --- pattern, string pattern that all of the files of interst have in their file names, e.g., "task-rest_falff.nii.gz"
# #          --- data_type, data type, e.g., "fALFF", "ReHo"
# # Output
# # --- return a dataframe which is by pooling and concatenating the dataframes (one file per row) with 3 columns: 
# #          --- full_path, full path to the file of interst
# #          --- fID, concatenation of site name and subject ID, seperated by "_" 
# #          --- data_type, data type, e.g., "fALFF", "ReHo"
# def SDL_process_patterns_in_parallel(args):
#     with Pool() as pool:
#         dfs = pool.map(SDL_list_files, args)  
#     return pd.concat(dfs)


# (1.3) Function of descriptive statistics of Subjects.csv
# Input
# --- df, dataframe that was saved in the "Subjects.csv"
# Output
# --- print the descriptive statistics per diaonosis group per SITE
# --- save the above information into "Subjects_descriptive_statistics.csv"
def SDL_descriptive_statistics(df,D): 
    # (1.3.2) define group variables
    group_vars = ['SITE','GROUP']
    
    # (1.3.3) Calculate count, mean and standard deviation of continuous variables
    continuous_vars = ['Age', 'PTSD_percent', 'depression_percent']
    df_continuous = df.groupby(group_vars)[continuous_vars].agg(['count','mean', 'std'])
    print(df_continuous)

    # (1.3.4) Calculate count and proportion of categorical variables
    df_categorical = df.groupby(group_vars).agg(
        # Count the number of males and females per group
        num_male = ('Sex', lambda x: x.eq(0).sum()),
        num_female = ('Sex', lambda x: x.eq(1).sum()),
        # Calculate the proportion of females per group
        prop_female = ('Sex', lambda x: x.eq(1).mean()*100),
    )
    print(df_categorical)
    
    # (1.3.5) Merge the two dataframes
    df_summary = pd.concat([df_continuous, df_categorical], axis=1)

    # (1.3.6) Save the results in a new dataframe
    outfile = os.path.join(D['path']['Processes'],'Subjects_descriptive_statistics.csv')
    df_summary.to_csv(outfile, index=True) 
    print(f"Subjects Statistics saved in: \n{outfile}")





# (2) Function (Main) to match (I) demographic & clinical info & (II) data (images & confounds)
# Input
# --- D, the dictionary that contains important paths and parameters
# Output
# --- df, return a dataframe of demographic/clinical info and the full path of corresponding images
# --- also save df into a .csv file ("Subjects.csv")
def SDL_clean(D):

    # (i) demographic & clinical info
    # (ia) load demographic & clinical info
    df0 = pd.read_excel(os.path.join(D['path']['Data'][0], 
                        D['data']['demographic_clinical'][0]), 
                        sheet_name = D['data']['demographic_clinical'][1])
    
    # (ib) change the column names
    df0.rename(columns={D['model']['predictors'][old_name][0]: old_name\
        for old_name in D['model']['predictors']}, inplace=True)
    
    # (ic) keep the columns of interest
    var_of_interest = list(D['model']['predictors'].keys())
    df0 = df0[var_of_interest]
    
    # (id) replace old values with new values across columns
    for col_name, value_list in D['model']['predictors'].items():
        df0[col_name] = df0[col_name].replace(value_list[2])
    
    # (ie) keep the rows with particular values in given columns
    for col_name, value_list in D['model']['predictors'].items():
        if value_list[3]:  # if the list is not empty
            df0 = df0[df0[col_name].isin(value_list[3])]
    
    # (if) drop rows that are NaN across columns
    df0 = df0.dropna(how='all')
    
    # (ig) set 'fID' as index
    df0.set_index('fID', inplace=True)
    
    # (ii) search for the files in parallel
    # (iia) arguments: (folder, pattern, data_type) tuples for parallel processing
    my_args = [(folder, v[0], k)\
        for folder in D['path']['Data']\
        for k, v in D['data'].items()\
        if k != 'demographic_clinical']

    # (iib) parallel processing
    t0 = time.time()
    print(f"\n-----------\nSearching for all files of interest (time consuming, ~10min !!)...")
    # df = SDL_process_patterns_in_parallel(my_args)
    if __name__ == '__main__':
        # use all of the CPUs to run parallel processing
        with Pool() as pool:
            dfs = pool.map(SDL_list_files, my_args)  
        df = pd.concat(dfs)
    print(f"Time Elapsed: {time.time()-t0}\n-----------\n")
    
    # (iii) convert to a wide dataframe
    df_wide = df.pivot(index='fID', columns='data_type', values='full_path')
    # Add prefix to the column names
    df_wide.columns = ['FULL_PATH_' + col for col in df_wide.columns]
    
    # (iv) merge demographic/clinical info (df0) with data paths (df)
    df_merged = df0.merge(df_wide, left_index=True, right_index=True)
 
    # (v) drop the rows that are NaN across columns starts with "FULL_PATH_"
    cols = [col for col in df_merged.columns if col.startswith('FULL_PATH_')]
    df_merged = df_merged.dropna(subset=cols, how='all')
 
    # (vi) save into Subjects.csv
    df_merged.to_csv(os.path.join(D['path']['Processes'],'Subjects.csv'), index=True)
    
    
    # (vii) (Optional) descriptive statistics of Subjects.c
    #SDL_descriptive_statistics(df_merged)
    
    # retuen
    return df_merged
