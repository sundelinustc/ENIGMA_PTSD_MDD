# (0) Packages
from SDL_functions.initialization import SDL_initialization
from SDL_functions.clean import SDL_clean
from SDL_functions.modelling_persite import SDL_pre_meta
from SDL_functions.harmonization import SDL_harmonization
from SDL_functions.meta_analysis import SDL_meta_nimare
# from SDL_functions.mega_analysis import SDL_BLM

def main():
    # (1) Initilization
    # extract important paths & parameters, and create folders
    D = SDL_initialization('path_para.yaml')


    # (2) Clean data (to match demographic & clinical info with data files)
    # just need to RUN ONCE to make the "Subjects.csv" to contain both demographic/clinical info & file paths
    SDL_clean(D)

    # (3) Meta analysis
    SDL_pre_meta(D) # pre-Meta (Run models per site)
    SDL_meta_nimare(D) # Meta analysis using Nimare

    # (4) Mega analysis (linear model)
    # SDL_harmonization(D) # data harmonization across sites
    # SDL_mega_BLM(D)

    # (5) Mega analysis (linear mixed effects model)
    #SDL_mega_BLMM(D)



if __name__ == "__main__":
    main()
    
    print(f"\n\n\n All Finished !!! Check Your Results !!!")
    pass
