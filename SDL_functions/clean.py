def SDL_clean(SDL):
    
    # This function cleans the (I) demographic & clinical info as well as 
    # (II) data (images & confounds) by matching (I) & (II) per subject (or observation)
    # Input
    # --- SDL, the dictionary that contains inportant parameters such as paths
    # Output
    # --- df, 
    # --- also save df into a .csv file

    ### packages
    import os
    #import openpyxl
    import fnmatch
    import pandas as pd

    ### inner function of adding new df columns of SITE & SubjID
    def my_split_path(df, pname):
        _, df['subject'] = (zip(*df[pname]
             .apply(lambda x: os.path.split(x)[0])
             .apply(lambda x: os.path.split(x)))   )
        _, df['Site'] = (zip(*df['subject']
             .apply(lambda x: os.path.split(x)[0])
             .apply(lambda x: os.path.split(x)))   )
        return df


    ### load demographic & clinical info
    df0 = pd.read_excel(SDL['file']['dem_cli'][0], sheet_name=SDL['file']['dem_cli'][1])

    ### list all file names with specified pattern
    root = SDL['file']['data'] # parent path of all data files
    pattern = '*' + SDL['data']['fALFF_falff']

    fns = [] # list of full file path & name
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                fns.append(os.path.join(path, name))

    df = pd.DataFrame({'filename': fns}) # dataframe to contain the full name of all files with the specified pattern

    df = my_split_path(df, 'filename')
    
    return df



    print(SDL)