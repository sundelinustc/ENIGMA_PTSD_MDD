### (0) Packages
import os # get & set paths
import re # pattern match in strings
import time # measuring time elapsed
import subprocess # call funcitons through the current operating system
import pandas as pd # dataframe
import numpy as np
from multiprocessing import Pool # parallel processing
import nibabel as nib # nifti file I/O
import neuroHarmonize as nh # ComBat-GAM
from neuroHarmonize import harmonizationLearn 
from neuroHarmonize.harmonizationNIFTI import createMaskNIFTI
from neuroHarmonize.harmonizationNIFTI import flattenNIFTIs
from neuroHarmonize.harmonizationNIFTI import applyModelNIFTIs

# (1) Functions
# (1.1) Function to make a folder if it does not exist
def SDL_create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

# (1.2) Extracts specified dimensions from a 4D NIfTI image and saves the resulting 3D image
# Input
# --- original_image_path (str): Path to the original 4D NIfTI image.
# --- output_image_path (str): Path to save the new 3D NIfTI image.
# --- dimensions (tuple): Indices of dimensions to extract (0-based). Defaults to (0, 1, 2).
# Output
# --- new image saved in output)image_path
def SDL_extract_and_save_dimensions(args):
    # arguments
    original_image_path, output_image_path, dimensions = args
    
    try:
        # Load the original 4D NIfTI image
        original_image = nib.load(original_image_path)
        original_data = original_image.get_fdata()
        
        # Create the destination directory if it does not exist
        destination_directory = os.path.dirname(output_image_path)
        os.makedirs(destination_directory, exist_ok=True)

        # copy & paste if raw image dimensions is equal to or smaller than dimensions of interest
        if len(original_data.shape) <= len(dimensions):
            # Create a new NIfTI image with the same data and affine
            new_image = nib.Nifti1Image(original_data, original_image.affine)

            # Save the new image
            nib.save(new_image, output_image_path)
            
        else:
            # Extract the desired dimensions
            # !!!needs to improve to handle any type of dimensions
            sliced_data = original_data[:,:,:,0]

            # Create a new NIfTI image with the sliced data
            new_image = nib.Nifti1Image(sliced_data, original_image.affine)

            # Save the new image
            nib.save(new_image, output_image_path)
        
        # print information
        print(f"New NIfTI image saved at: {output_image_path}")
    except Exception as e:
        print(f"Error: {e}")

# (1.3) Function to do ComBat-GAM harmonization for a single site
# Input
# --- args, including df0, D, data_type, image name pattern, mask name pattern
# Output
# --- make a new image of Z statistics in the same directory
def SDL_ComBat_GAM_single(args):
    # (i) arguments
    df0, D, data_type, img_pattern, mask_pattern = args
    
    # (ii) make folder to contain harmonized data
    # folder name per data type
    folder_path = os.path.join(D['path']['Processes'],'Harmonized_ComBat-GAM',data_type)
    # make the folder if it does not exist
    SDL_create_directory(folder_path)
    
    # (iii) Data preparation
    # make a dataframe to contain info for the given data type
    df = pd.DataFrame()
    df = df0.loc[:,['SITE','GROUP','AGE','SEX']]
    # old paths of images
    df['PATH'] = df0['FULL_PATH_' + data_type]
    # new paths of images (pre_harmonized)
    df['PATH_NEW_Pre_Harmonized'] = df['PATH'].replace(to_replace=D['path']['Data'], 
                                        value=os.path.join(D['path']['Processes'],'Harmonized_ComBat-GAM',data_type,'Pre_Harmonized'), regex=True)
    # new paths of images (harmonized)
    df['PATH_NEW'] = df['PATH'].replace(to_replace=D['path']['Data'], 
                                        value=os.path.join(D['path']['Processes'],'Harmonized_ComBat-GAM',data_type,'Harmonized'), regex=True)
    
    # (iv) images pre-harmonization (parallel processing)
    # arguments
    my_args = [(row["PATH"], row["PATH_NEW_Pre_Harmonized"], (0,1,2)) for _, row in df.iterrows()]
    # extract pre-defined domensions (usually the first 3 dimensions: x, y z) of nifti images & save them into new paths
    with Pool() as pool:
        results = pool.map(SDL_extract_and_save_dimensions, my_args)
    

    ### example
    # variables of interest, 1st must be SITE, and the last 2 must be PATH & PATH_NEW
    vars  = df.columns
    # clean sites
    sites = df.SITE.unique().tolist() # all sites
    sites_remove = ['Groningen','MinnVA'] # sites to be removed given 4D but not 3D images in the 2 sites
    sites = [x for x in sites if x not in sites_remove]
    print(f"\nSITE:\n{sites}\n")
    
    # remove rows with missing values in variables of interest
    df = df.loc[df.SITE.isin(sites), vars].dropna(subset=vars)

    # check the dimensions of image (should be 3D)
    for img_path in df.PATH:
        try:
            image = nib.load(img_path)
            if image.shape != (97,115,97):
                print(f"image.shape={image.shape} for {img_path}")
        except Exception as e:
            print(f"Error: {e}")
    
    
    ### (3) ComBat-GAM
    ## (3.1) Compute mask
    t0 = time.time()
    print('ComBat-GAM, computing mask:')
    
    df.to_csv('brain_images_paths.csv',index=False)
    nifti_list = pd.read_csv('brain_images_paths.csv')
    nifti_avg, nifti_mask, affine, hdr0 = createMaskNIFTI(nifti_list, threshold=0)
    t1 = time.time()
    print(f"Time elapsed: {t1-t0}")
    
    ## (3.2) Flattern images
    t0 = time.time()
    print('ComBat-GAM, flatterning images:')
    nifti_array = flattenNIFTIs(nifti_list, 'thresholded_mask.nii.gz')
    t1 = time.time()
    print(f"Time elapsed: {t1-t0}")
    
    ## (3.3) Run harmonization
    t0 = time.time()
    print('ComBat-GAM, running harmonization:')
    # remove MY_MODEL if it exists
    if os.path.exists('MY_MODEL'):
        os.remove('MY_MODEL')
    covars = df[vars[:-2]] # exclude PATH and PATH_NEW
    my_model, nifti_array_adj = nh.harmonizationLearn(nifti_array, covars)
    nh.saveHarmonizationModel(my_model, 'MY_MODEL')
    t1 = time.time()
    print(f"Time elapsed: {t1-t0}")
    
    ## (3.4) Apply model
    t0 = time.time()
    print('ComBat-GAM, apply model:')
    my_model = nh.loadHarmonizationModel('MY_MODEL')
    
    # make the directory of PATH_NEW if they do not exist
    for path in nifti_list.PATH_NEW:
        dir_new = os.path.dirname(path)
        if not os.path.exists(dir_new):
            os.makedirs(dir_new)
            
    # apply models
    applyModelNIFTIs(covars, my_model, nifti_list, 'thresholded_mask.nii.gz')
    t1 = time.time()
    print(f"Time elapsed: {t1-t0}")


# (2) Function to parallely run data harmonization across data types
# Input
# --- D, the dictionary of important paths and parameters
# Output
# --- create harmonized images and model data across data types
def SDL_harmonization(D):
    # (i) load Subjects.csv
    df0 = pd.read_csv(os.path.join(D['path']['Processes'],'Subjects.csv')) 

    # (ii) modelling across sites, data type, statistical models & contrasts in parallel
    # (iia) arguments: df, D, data_type, filename pattern, mask name pattern
    my_args = [(df0, D, k_dtype, v_dtype[0], v_dtype[2])\
        for k_dtype, v_dtype in D['data'].items() if k_dtype != 'demographic_clinical']

    # test purpose only
    SDL_ComBat_GAM_single(my_args[0])

    # (iib) parallel processing
    t0 = time.time()
    print(f"\n-----------\nNifti Harmonization...")
    
    # use all of the CPUs to run parallel processing
    with Pool() as pool:
        results = pool.map(SDL_ComBat_GAM_single, my_args)
        print(results)
        
    print(f"Nifti Harmonization, Time Elapsed: {time.time()-t0}\n-----------\n")
    
    return results






# def SDL_harmonization(D):
    
#     # This function is to harmoniza imaging data across sites
    
#     # Input
#     # --- SDL, the dictionary of all important paths & filenames
#     # Output
#     # --- a series of images (including statistical outputs) & documents to be saved

    
#     ### (1) Data preparation
#     ## (1.1) load Subjects.csv
#     t0 = time.time()
#     df = pd.read_csv(os.path.join(D['path']['Processes'],'Subjects.csv')) 
#     df['PATH'] = df['FULLPATH_fALFF_falff']
#     df['PATH_NEW'] = df['PATH'].str.replace(D['path']['Data'], 
#                                             os.path.join(SDL['path']['Processes'],'Harmonized_ComBat-GAM'))
    
#     # clean variables
#     df['SITE'] = df['site2']
#     df = df[df['currentPTSD_dx'].isin([0, 1])]
#     df = df[df['Sex'].isin(['M', 'F'])]
#     df['Sex'] = df['Sex'].replace({'M': 0, 'F': 1})
#     t1 = time.time()
#     print(f"Data Preparation, Loading Subjects.csv: Time Elapsed {t1-t0}")
    
#     ### example
#     # variables of interest, 1st must be SITE, and the last 2 must be PATH & PATH_NEW
#     vars  = ['SITE','currentPTSD_dx','Age','Sex','PATH','PATH_NEW']
#     # clean sites
#     sites = df.SITE.unique().tolist() # all sites
#     sites_remove = ['Groningen','MinnVA'] # sites to be removed given 4D but not 3D images in the 2 sites
#     sites = [x for x in sites if x not in sites_remove]
#     print(f"\nSITE:\n{sites}\n")
    
#     # remove rows with missing values in variables of interest
#     df = df.loc[df.SITE.isin(sites), vars].dropna(subset=vars)

#     # check the dimensions of image (should be 3D)
#     for img_path in df.PATH:
#         image = nib.load(img_path)
#         if image.shape != (97,115,97):
#             print(f"image.shape={image.shape} for {img_path}")
    
    
    
#     ### (3) ComBat-GAM
#     ## (3.1) Compute mask
#     t0 = time.time()
#     print('ComBat-GAM, computing mask:')
    
#     df.to_csv('brain_images_paths.csv',index=False)
#     nifti_list = pd.read_csv('brain_images_paths.csv')
#     nifti_avg, nifti_mask, affine, hdr0 = createMaskNIFTI(nifti_list, threshold=0)
#     t1 = time.time()
#     print(f"Time elapsed: {t1-t0}")
    
#     ## (3.2) Flattern images
#     t0 = time.time()
#     print('ComBat-GAM, flatterning images:')
#     nifti_array = flattenNIFTIs(nifti_list, 'thresholded_mask.nii.gz')
#     t1 = time.time()
#     print(f"Time elapsed: {t1-t0}")
    
#     ## (3.3) Run harmonization
#     t0 = time.time()
#     print('ComBat-GAM, running harmonization:')
#     # remove MY_MODEL if it exists
#     if os.path.exists('MY_MODEL'):
#         os.remove('MY_MODEL')
#     covars = df[vars[:-2]] # exclude PATH and PATH_NEW
#     my_model, nifti_array_adj = nh.harmonizationLearn(nifti_array, covars)
#     nh.saveHarmonizationModel(my_model, 'MY_MODEL')
#     t1 = time.time()
#     print(f"Time elapsed: {t1-t0}")
    
#     ## (3.4) Apply model
#     t0 = time.time()
#     print('ComBat-GAM, apply model:')
#     my_model = nh.loadHarmonizationModel('MY_MODEL')
    
#     # make the directory of PATH_NEW if they do not exist
#     for path in nifti_list.PATH_NEW:
#         dir_new = os.path.dirname(path)
#         if not os.path.exists(dir_new):
#             os.makedirs(dir_new)
            
#     # apply models
#     applyModelNIFTIs(covars, my_model, nifti_list, 'thresholded_mask.nii.gz')
#     t1 = time.time()
#     print(f"Time elapsed: {t1-t0}")
   
#     pass