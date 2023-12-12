### (0) Loading packages
import os # get & set paths
import pandas as pd # dataframe
from SDL_functions.make_subfolders import SDL_make_subfolders
from SDL_functions.clean import SDL_clean
from SDL_functions.modelling_preparation import SDL_merge

### (1) Parameters
SDL = {} # initilize the dictionary of global parameters

## (1.1) paths
SDL['path'] = {'Project':'/Volumes/dusom_morey/Data/Lab/Delin/Projects/ENIGMA_PTSD-MDD'} # make the key of 'path' & Project path
#SDL['path'] = {'Project':os.path.dirname(os.getcwd())} # BIAC cluster does NOT accept the relative path
# make subfolders (if they do not exist)
subfolders = ['Scripts','Processes','Results'] # list of subfolder names
subfolder_paths = SDL_make_subfolders(SDL['path']['Project'], subfolders)
SDL['path'].update(subfolder_paths) # add paths to subfolder into SDL['path']
# Data are from new_halfpipe outputs
SDL['path']['Data'] = '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs'

## (1.2) files
# - 'dem_cli', demographic & clinical info, 1st value=file path, 2nd value=sheetname (if exists)
# - 'data', path to the folder of all data
# - 'cleaned_data_info', path to the file of cleaned data info (subjects' demo&cli info as well as corresponding data path)
SDL['file'] = {'dem_cli':[os.path.join(SDL['path']['Data'],\
                                      'ENIGMA-PGC_master_v1.1.xlsx'),'forPGC'],
               'data':SDL['path']['Data']                 }
## (1.3) data types (key=data type, value=corresponding pattern in the filename)
SDL['data'] = {'corrMatrix_atlas-schaefer2011Combined':'task-rest_feature-corrMatrix_atlas-schaefer2011Combined_timeseries.tsv',
               'confounds':'confounds_timeseries.tsv',
               'fALFF_alff':  'task-rest_feature-fALFF_alff.nii.gz',
               'fALFF_falff': 'task-rest_feature-fALFF_falff.nii.gz',
               'fALFF_mask':  'task-rest_feature-fALFF_mask.nii.gz',
               'fALFF1_alff': 'task-rest_feature-fALFF1_alff.nii.gz',
               'fALFF1_falff':'task-rest_feature-fALFF1_falff.nii.gz',
               'ALFF1_mask':  'task-rest_feature-fALFF1_mask.nii.gz'
               }


### (2) Clean data (to match demographic & clinical info with data files)
#df = SDL_clean(SDL)

### (3) Run models per site
filenames = ['/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1043/sub-1043_task-rest_feature-fALFF_falff.nii.gz',
                 '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1180/sub-1180_task-rest_feature-fALFF_falff.nii.gz',
                 '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1233/sub-1233_task-rest_feature-fALFF_falff.nii.gz',
                 '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1105/sub-1105_task-rest_feature-fALFF_falff.nii.gz',
                 '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1113/sub-1113_task-rest_feature-fALFF_falff.nii.gz',
                 '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1195/sub-1195_task-rest_feature-fALFF_falff.nii.gz',
                 '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1142/sub-1142_task-rest_feature-fALFF_falff.nii.gz',
                 '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1246/sub-1246_task-rest_feature-fALFF_falff.nii.gz',
                 '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1127/sub-1127_task-rest_feature-fALFF_falff.nii.gz',
                 '/Volumes/dusom_morey/Data/Lab/new_halfpipe/Outputs/falff_reho/UWash/sub-1152/sub-1152_task-rest_feature-fALFF_falff.nii.gz'
                 ]
    
outputname = os.path.join(SDL['path']['Processes'], 'output4D.nii.gz')

SDL_merge(filenames, outputname)


print(SDL)