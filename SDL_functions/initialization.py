# (0) Packages
import os # get & set paths
import time # measuring time elapsed
import yaml # read/write .yaml files
import pandas as pd # dataframe

# (1) Sub-functions
# (1.1) Make subfolders under the parent_folder   
# Input
# --- parent_folder, path to the parent folder
# --- subfolders, a list of the names of subfolders
# Output
# --- make subfolders if they do not exist
def SDL_make_subfolders(parent_folder, subfolders):
    # (i) initialize a dictionary to contain the full paths of subfolders
    subfolder_paths = {}

    # (ii) for each subfolder
    for subfolder in subfolders:
        # full path of each subfolder
        subfolder_path = os.path.join(parent_folder, subfolder)
        
        # make the subfolder if it does not exist
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)

        # update the dictionary of subfolder fullpaths
        subfolder_paths[subfolder] = subfolder_path

    # (iii) Return the directionary of all subfolders' fullpaths       
    return subfolder_paths

# (1.2) Print the contents of a dictionary in an organized way
# Input
# --- D, dictionary in which some keys correspond to numbers or characters, 
# some keys correspond to list of strings, and some to dictionaries
# --- indent, indentation level for nested dictionaries
# Output
# --- print the contents of D in an organized way
def SDL_print_dict(D, indent=0):
    for key, value in D.items():
        print('  ' * indent + f"Key: {key}")
        if isinstance(value, dict):
            SDL_print_dict(value, indent + 1)
        elif isinstance(value, list):
            print('  ' * indent + "Values:")
            for i, v in enumerate(value):
                print('  ' * (indent + 1) + f"{i+1}. {v}")
        else:
            print('  ' * indent + f"Value: {value}")
        print('  ' * indent + "---")

# (2) Main function
# Make directories of Processes and Results, as well as create the dictionary of D for futher analysis
# Input
# --- yaml_file, filename of the yaml file of important paths & parameters
# Output
# --- make directories: Processes, Results, and jobs
# --- return a dictionary named D to convey important info of paths & parameters
def SDL_initialization(yaml_file):  
    # (i) load yaml file of key paths & parameters
    with open('path_para.yaml', 'r') as file:
        D = yaml.safe_load(file)
        
    # (ii) make folders
    # The upper directory of the current directory is set to the folder of this project
    # 
    D['path'] = {'Project': os.path.dirname(os.getcwd()),
                 'Scripts': os.getcwd(),
                 'Data':    D['data_path']}
    # list of subfolders
    # -- Processes, data & files in the mid-way
    # -- Results, final results for drafts of manuscripts
    # -- jobs, debug information when running the scripts in a cluster
    subfolders = ['Processes','Results','jobs'] 
    # make subfolders (if they do not exist)
    subfolder_paths = SDL_make_subfolders(D['path']['Project'], subfolders)
    # update the dictionary named D
    D['path'].update(subfolder_paths) # add paths to subfolder into SDL['path']
  
    # (iii) important parameters: filenames (part) of interest
    pass # the yaml file already contains these information
    
    
    # (iv) print D
    t0 = time.time()
    print(f"\n-----------\nShowing contents of the dictionary D:")
    SDL_print_dict(D)
    print(f"Time Elapsed: {time.time()-t0}\n-----------\n")
    
    # (v) return
    return D