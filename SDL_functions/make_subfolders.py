def SDL_make_subfolders(parent_folder, subfolders):
    # Packages
    import os # get & set paths
    
    # initialize a dictionary to contain the full paths of subfolders
    subfolder_paths = {}

    # for each subfolder
    for subfolder in subfolders:
        # full path of each subfolder
        subfolder_path = os.path.join(parent_folder, subfolder)
        
        # make the subfolder if it does not exist
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)

        # update the dictionary of subfolder fullpaths
        subfolder_paths[subfolder] = subfolder_path

    # Return the directionary of all subfolders' fullpaths       
    return subfolder_paths