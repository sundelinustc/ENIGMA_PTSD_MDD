### (0) Loading packages
import os # get & set paths
import pandas as pd # dataframe
from SDL_functions.make_subfolders import SDL_make_subfolders
from SDL_functions.clean import SDL_clean

### (1) Parameters
SDL = {} # initilize the dictionary of global parameters

## (1.1) paths
SDL['path'] = {'Project':os.path.dirname(os.getcwd())} # make the key of 'path' & Project path
# make subfolders (if they do not exist)
subfolders = ['Scripts','Data','Processes','Results'] # liost of subfolder names
subfolder_paths = SDL_make_subfolders(SDL['path']['Project'], subfolders)
SDL['path'].update(subfolder_paths) # add paths to subfolder into SDL['path']

## (1.2) files
# - 'dem_cli', demographic & clinical info, 1st value=file path, 2nd value=sheetname (if exists)
# - 'data', path to the folder of all data
# - 'cleaned_data_info', path to the file of cleaned data info (subjects' demo&cli info as well as corresponding data path)
SDL['file'] = {'dem_cli':[os.path.join('..','..','SFC_DFC','Data',\
                                      'ENIGMA-PGC_master_v1.1_TR&fID_v1.xlsx'),'forPGC'],
               'data':os.path.join('..','..','SFC_DFC','Data',\
                                   'BIAC_Server','Volumes','dusom_morey','Data',\
                                    'Lab','new_halfpipe','Outputs'),
               'cleaned_data_info':os.path.join(SDL['path']['Processes'], 'cleaned_data_info.csv')                   }
## (1.3) data types (key=data type, value=pattern in the filename)
SDL['data'] = {'atlas_conn':'task-rest_feature-corrMatrix_atlas-schaefer2011Combined_timeseries.tsv',
               'confounds':'confounds_timeseries.tsv'}


### (2) Clean data (to match demographic & clinical info with data files)
df = SDL_clean(SDL)


print(SDL)