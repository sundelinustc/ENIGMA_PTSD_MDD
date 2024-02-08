# (0) Packages
import os # get & set paths
import re # pattern match in strings
import time # measuring time elapsed
# import subprocess # call funcitons through the current operating system
import pandas as pd # dataframe
import numpy as np
# from patsy import dmatrix # make design matrix
from multiprocessing import Pool # parallel processing
import nibabel as nib # nifti file I/O
import nimare # image-based meta-analysis
from nimare import meta
from nimare.transforms import ImageTransformer # t-to-z transformation
from nimare.workflows.ibma import IBMAWorkflow # image-based meta analysis workflow
from nimare.reports.base import run_reports # NiMARE report

# (1) Functions
# (1.1) Function to make Z statistics map using uncorrected p values
# Input
# --- p_img, full path to the image of uncorrected p values
# Output
# --- make a new image of Z statistics in the same directory
def SDL_ptoz(p_img):
    # (i) get the directory path
    dir_path = os.path.dirname(p_img)
    
    # (ii) get the filename with extension
    filename = os.path.basename(p_img)
    
    # (iii) full path of the Z image
    pass
    
    # (iv) FSL command to calculate 1-p given that the FSL p images are in fact 1-p_accurate
    # fslmaths p_img -mul -1 -add 1 p_act_img
    pass

    # (v) p-to-Z
    # fslmaths STAT_vox_p_tstat1.nii.gz -ptoz STAT_vox_zstat1.nii.gz
    pass
    
# (1.2) Function to run meta analysis using stouffers method
# Input
# --- main_folders, folders that contain the Z statistics images
# --- stat_file, filename of the statistics image (e.g., Z or T)
# --- effect_of_interest, name of effect of interest, e.g. 'GROUP'
# --- directory, the path to the final outputs
# --- my_method, meta-analysis method, default: 'Stouffers'
# Output 
# --- meta analysis results, both positive & negative images
def SDL_meta_fit(main_folders, stat_file, effect_of_interest, directory, my_method = 'Stouffers'):
    # (i) initialize an empty dictionary for data
    data = {}
    
    # (ii) contrast images & sample sizes
    # initialize a list of lists of sample sizes
    sample_sizes = []
    # loop over each site to get the contrast images & sample size
    for site_name, folder_path in main_folders:
        # Construct the path to the target images for this site
        img_path = os.path.join(folder_path, stat_file)
        # Check if the target images exist & is NOT just 0s nor NaN for this site
        if os.path.isfile(img_path):
            # load the image
            img_data = nib.load(img_path).get_fdata()
            # load desig.csv to check if the effect of interest is there
            df_design = pd.read_csv(os.path.join(folder_path, 'design.csv'))
            # if the image is NOT full of 0s or NaN & the corresponding effect_of_interest is in the design.csv
            if (not np.all(img_data == 0)) &\
                (not np.all(np.isnan(img_data))) &\
                    (effect_of_interest in df_design.columns) &\
                        ('GROUP' in df_design.columns):
                # add an entry to the data dictionary for this site
                # for the contrast id, e.g., '1' for 'STAT_tstst1.nii.gz'
                id_contrast = 'contrast' + re.search(r'STAT_tstat(.*?)\.nii\.gz', img_path).group(1)
                data[site_name] = {"contrasts": {id_contrast: {"images": {"t": img_path,}}}}
                # get sample sizes ([N_grp1, N_grp2]) of a given site
                # !!!NOW, DEGREE OF FREEDOM ONLY FOR GROUP
                list_n = df_design['GROUP'].value_counts().tolist()
                # add into the list of sample_sizes
                sample_sizes.extend([list_n])

   
    # create a NiMARE dataset
    dset = nimare.dataset.Dataset(data)
        
    # upate metadata   
    dset.metadata['sample_sizes'] = sample_sizes
  
    # t-to-z if t but NOT z images exist
    if (not 'z' in dset.images.columns) &\
        ('t' in dset.images.columns):
        z_transformer = ImageTransformer(target="z")
        dset = z_transformer.transform(dset)
    
    # image-based meta analysis workflow
    my_result = IBMAWorkflow().fit(dset)
    # img = my_result.get_map("z_corr-FDR_method-indep")
    
    # # clusters table: significant results survived cluster-level FDR correction
    # my_result.tables["z_corr-FDR_method-indep_tab-clust"]
    # # contribution table
    # my_result.tables["z_corr-FDR_method-indep_diag-Jackknife_tab-counts_tail-positive"]
    
    # reports
    run_reports(my_result, directory)
    
    # # perform the meta-analysis
    # if my_method == 'Stouffers':
    #     my_meta = meta.ibma.Stouffers(use_sample_size=False, resample=True)
    # my_result = my_meta.fit(dset)
    
    # save the image
    my_img = my_result.get_map("z", return_type="image")
    fname = 'Meta_' + my_method + '_' + os.path.basename(stat_file)
    nib.save(my_img, os.path.join(directory, fname))

    
# (1.3) Function to run meta analysis for a single data_type, formula, effect_of_interest
# Input
# --- args, arguments: df, D, data_type, model_title, model_formula, effect_of_interest
# Output
# --- series of meta-analysis outputs
def SDL_meta_nimare_single(args):
    # (i) arguments
    df, D, data_type, model_title, model_formula, effects_of_interest, effect_of_interest = args
    t0 = time.time()
    print(f"\n-----------\n--Meta-analysis using NiMARE...")
    print(f"data_type: {data_type}")
    print(f"model_title: {model_title}")
    print(f"formula: {model_formula}")
    print(f"effect_of_interest: {effect_of_interest}")

    # (ii) make the directory
    directory = os.path.join(D['path']['Results'], 'Meta', 'NiMARE', 'FSL', data_type, model_title, effect_of_interest)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # (iii) paths of input folders across sites
    # paths to all folders of statistical images of interest
    list_folders = [(site, os.path.join(D['path']['Processes'],'Pre_Meta', site, 'FSL', data_type, model_title))\
        for site in df.SITE.unique()]
    # keep the folders that exist
    main_folders = [(site_name, folder_path) for site_name, folder_path in list_folders if os.path.isdir(folder_path)]
    
    # (iv) specify the name pattern of the target statistic image file
    # index of the effect_of_interest in the list of effects_of_interest
    idx = effects_of_interest.index(effect_of_interest) # starts from 0

    # (v) run meta analysis for given effect of interest
    my_file = 'STAT_tstat' + str(idx+1) + '.nii.gz'
    SDL_meta_fit(main_folders, my_file, effect_of_interest, directory)

    print(f"Meta-analysis by NiMARE, Time Elapsed: {time.time()-t0}\n-----------\n")



# (2) Function to parallely run modelling per site
# Input
# --- D, the dictionary of important paths and parameters
# Output
# --- create mata-analysis statistical images (4D, T, Z, p, & p_corrected) per data type, per statistical model & contrast
def SDL_meta_nimare(D):
    # (i) load Subjects.csv
    df = pd.read_csv(os.path.join(D['path']['Processes'],'Subjects.csv')) # 6189 x 71

    # (ii) modelling across sites, data type, statistical models & contrasts in parallel
    # (iia) arguments: df, D, data_type, model_title, model_formula, effects_of_interest, effect_of_interest
    my_args = [(df, D, k_dtype, k_mdl, v_mdl[0], v_mdl[1], eff)\
        for k_dtype, v_dtype in D['data'].items() if k_dtype != 'demographic_clinical'\
        for k_mdl, v_mdl in D['model']['models_pre_meta'].items()\
        for eff in v_mdl[1]]

    # # test purpose only
    # SDL_meta_nimare_single(my_args[0])

    # (iib) parallel processing
    t0 = time.time()
    print(f"\n-----------\nMeta-analysis Parallel Processing...")
    
    # use all of the CPUs to run parallel processing
    with Pool() as pool:
        results = pool.map(SDL_meta_nimare_single, my_args)
        print(results)
        
    print(f"Meta-analysis Parallel Processing, Time Elapsed: {time.time()-t0}\n-----------\n")
    
    return results