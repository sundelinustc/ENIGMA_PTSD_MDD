def SDL_merge(filenames, outputname):

    # This function call fslmerge function to convert multiple 3D 
    # nifti images into a 4D image.
    
    # Input
    # --- filenames, a list of fullpath & filenames for 3D images to be concatenated
    # --- outputname, fullpath & filename of the 4D image
    # Output
    # --- 4D nifti image saved
    
    ### packages
    import os
    import subprocess
    
    
    ### Define the command to run
    # e.g., fslmerge -t outputname in1 in2 ....... inN
    command = ['fslmerge', '-t', outputname]
    for file in filenames:
        command.append(file)
    
    ### Run the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print(command)
    
    
    
    