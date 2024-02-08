# (0) Loading packages
import os # get & set paths
import time # measuring time elapsed
import subprocess # call funcitons through the current operating system
import pandas as pd # dataframe
import numpy as np
from patsy import dmatrix # make design matrix
from multiprocessing import Pool # parallel processing

# (1) Functions
# (1.1) Function to run statistical model per site per per statistical model & per contrast for Pre-Meta analysis
# Input
# --- args, tuple of arguments including df, site, data_type, model_title, model_formula, effect_of_interest
# Output
# --- create a series of statistical images (4D, T, Z, p, & p_corrected)
def SDL_model_pre_meta_single(args):
    # (i) arguments
    df, D, site, data_type, model_title, model_formula, effects_of_interest = args
    t0 = time.time()
    print(f"\n-----------\n--Pre-Meta Modelling (time consuming, ~20 min for a single modelling)...")
    print(f"site: {site}, data_type: {data_type}")
    print(f"model_title: {model_title}")
    print(f"formula: {model_formula}")
    print(f"effects_of_interest: {effects_of_interest}")

    # (ii) make the directory
    directory = os.path.join(D['path']['Processes'], 'Pre_Meta', site, 'FSL', data_type, model_title)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # (iii) dataframe for this single modelling
    # only the site of interest
    df1 = df.loc[df['SITE']==site,:]
    # get a list of all column names that do not start with "FULL_PATH_"
    column_names = [col for col in df1.columns if not col.startswith('FULL_PATH_')]
    # add paths to the interested data type to the list
    column_names.append("FULL_PATH_" + data_type)
    # only the data type of interest
    df1 = df1[column_names]
    # drop any rows with NaN
    df1 = df1.dropna()
    # save the dataframe
    fname = os.path.join(directory, 'data.csv')
    df1.to_csv(fname, index=False)
    print(f"--Data file: \n{fname}")

    # (iv) design matrix
    # patsy design matrix to pandas dataframe
    design = dmatrix(model_formula, df1, return_type='dataframe')
    # design = dmatrix(model_formula, df1)
    # design_array = np.asarray(design)
    # remove columns that have a constant value, except for 'Intercept'
    # e.g. Capetown_capetown, Capetown_tygerberg, Cisler, Emory, Ghent, Groningen, McCLean, Tours
    for column in design.columns:
        if column != 'Intercept' and design[column].nunique() == 1:
            design = design.drop(column, axis=1)
    # save into .csv file
    fname = os.path.join(directory, 'design.csv')
    design.to_csv(fname, index=False) # keep header to understand the data structure
    # save into .txt file
    fname = os.path.join(directory, 'design.txt')
    design.to_csv(fname, sep='\t', index=False, header=False)
    # np.savetxt(fname, design_array, fmt='%.3f', delimiter='\t')
    # convert to dsign.mat according to FSL
    fname1 = os.path.join(directory, 'design.mat')
    command = ['Text2Vest'] # FSL command, e.g. Text2Vest design.txt design.mat
    command.append(fname)
    command.append(fname1)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"--Design matrix: \n{fname1}")

    # (v) contrasts
    # column names of the design matrix
    col_names = design.columns.to_list()
    # col_names = design.design_info.term_names
    # for loop of each effect of interest
    contrasts = []
    for effect_of_interest in effects_of_interest:
        # contrast1: for positive effect
        contrast1 = [1 if x == effect_of_interest else 0\
            for x in col_names]
        # update contrasts
        contrasts.append(contrast1)
        # # contrast2: for negative effect (no need for image-based meta-analysis)
        # contrast2 = [-1 * x for x in contrast1]
        # # update contrasts
        # contrasts.append(contrast2)

    # save into .txt file
    fname = os.path.join(directory, 'contrasts.txt')
    np.savetxt(fname, contrasts, fmt='%d')
    # convert to contrasts.mat according to FSL
    fname1 = os.path.join(directory, 'design.con')
    command = ['Text2Vest'] # FSL command, e.g. Text2Vest design.txt design.mat
    command.append(fname)
    command.append(fname1)
    # run the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"--Contrasts: \n{fname1}")

    # (vi) 4D image
    # fslmerge function to convert multiple 3D nifti images into a 4D image
    # e.g., fslmerge -t outputname in1 in2 ....... inN
    # full path to the output directory
    outputname = os.path.join(directory, '4D.nii.gz')
    # text of the fsl command
    command = ['fslmerge', '-t', outputname]
    # column starts with "FULL_PATH_"
    col = df1.filter(like='FULL_PATH_').columns.to_list()[0]
    # filenames of all 3D images to be merged
    filenames = df1[col].to_list()
    # add full filnames one by one to the fsl command
    for file in filenames:
        command.append(file)
    # run the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"--4D.nii.gz: \n{outputname}")

    # (vii) run models
    # randomise -i <4D_input_data> -o <output_rootname> -d <design.mat> -t <design.con>  -m <mask_image> -n 500 -T -D
    # e.g. randomise -i 4D.nii.gz -o STAT -d design.mat -t design.con -T -D -x -n 500 --uncorrp
    # command = ['randomise','-i',os.path.join(directory, '4D.nii.gz'),
    #            '-o',os.path.join(directory,'STAT'),
    #            '-d',os.path.join(directory, 'design.mat'),
    #            '-t',os.path.join(directory, 'design.con'),
    #            '-n','10',
    #            '-T','-D','-x','--uncorrp']
    # only t statistics is needed
    command = ['randomise','-i',os.path.join(directory, '4D.nii.gz'),
            '-o',os.path.join(directory,'STAT'),
            '-d',os.path.join(directory, 'design.mat'),
            '-t',os.path.join(directory, 'design.con'),
            '-R','-D']
    # run the command
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print('\n!!!Error: command failed!!!\n')
    
    # (viii) (Optional) rename the statistical outputs with effect of inerest
    pass

    print(f"--Statistical outputs:\n{directory}")
    print(f"Time Elapsed: {time.time()-t0}\n-----------\n")

# (2) Function to parallely run modelling per site
# Input
# --- D, the dictionary that contains important paths and parameters
# Output
# --- create a series of statistical images (4D, T, Z, p, & p_corrected) per site per data type, per statistical model & contrast
def SDL_pre_meta(D):
    # (i) load Subjects.csv
    df = pd.read_csv(os.path.join(D['path']['Processes'],'Subjects.csv')) # 6189 x 71

    # (ii) modelling across sites, data type, statistical models & contrasts in parallel
    # (iia) arguments: df, site, data_type, img_pattern, model_title, model_formula, effect_of_interest
    my_args = [(df, D, site, k_dtype, k_mdl, v_mdl[0], v_mdl[1])\
        for site in df['SITE'].unique()\
        for k_dtype, v_dtype in D['data'].items() if k_dtype != 'demographic_clinical'\
        for k_mdl, v_mdl in D['model']['models_pre_meta'].items()]

    # # test purpose only
    # SDL_model_pre_meta_single(my_args[0])

    # (iib) parallel processing
    t0 = time.time()
    print(f"\n-----------\nParallel Modelling (time consuming!!)...")
    
    # use all of the CPUs to run parallel processing
    with Pool() as pool:
        results = pool.map(SDL_model_pre_meta_single, my_args)
        
    print(f"Parallel Modelling Time Elapsed: {time.time()-t0}\n-----------\n")
    
    return results