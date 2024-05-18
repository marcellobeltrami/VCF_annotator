import scripts.cravat as oc
import scripts.filter as fl 
from os import listdir, remove, path, remove
from pyfiglet import figlet_format
from json import dump, load
from argparse import ArgumentParser

#<Starts  execution>
if __name__ == "__main__":
 

    print(figlet_format("VCF annotator", font="standard"))
    print("--------------------------------------------------------------------")
    #CLI interface
    main_parser = ArgumentParser(description='CLI interface for VCF annotator')
    
    # CLI analysisi interface
    main_parser.add_argument('-i', '--input_file', required=True, help='Path to input file')
    main_parser.add_argument('-o', '--output_file', required=True, help='Output file name. Insert an identifier for your file, this is NOT the output file path')
    main_parser.add_argument('-g', '--sample_groups', required=True, help='A TAB delimited file containing sample names found in VCF file. First column should be the normal, second one treatment')
    main_parser.add_argument('-temp','--temp_keep', type=str, default="n",help='Determines whether to keep intermediate files[y/n].')
    main_parser.add_argument('-Num','--normal_mutations', nargs=2, type=int, default=[2,0],help='Mutations found in samples = or above  the first item and = or below the seconds item will be kept')
    main_parser.add_argument('-Tum','--treatment_mutations', nargs=2, type=int, default=[0,2],help='Mutations found in samples = or below the first item and = or above the seconds item will be kept')
    
    
    # Parse arguments
    args_analysis = main_parser.parse_args()
    samples_tab=str(args_analysis.sample_groups)
    input_file=str(args_analysis.input_file)
    temp_keep = args_analysis.temp_keep
    output_file =str(args_analysis.output_file)
    nml_thresh = list(map(int, args_analysis.normal_mutations))
    trt_thresh = list(map(int, args_analysis.treatment_mutations))
    

    #Functionality that allows to save credentials. 
    usr_glob=""
    psw_glob=""
    
    json_file_cred = "./scripts/settings/credentials.json"
    #Loads credetentials if they have been previously preserved.
    if  path.exists(json_file_cred) == True:
        with  open(json_file_cred, "r") as credentials:
            cred = load(credentials)
            usr_glob = cred["username"]
            psw_glob = cred["password"]

    #Checks if credentials have been previously saved. 
    else:
        usr=input("OpenCravat user name: ")
        psw=input("OpenCravat password: ")
        keep=input("Keep credentials?[y/n]:")
        usr_glob=usr
        psw_glob=psw
    
        #Allows to save credentials in a json file
        if keep =="y" or keep =="Y":
            with open(json_file_cred,"w") as cred_bank: 
                cred_dict = {"username":usr, "password":psw}
                dump(cred_dict, cred_bank, indent=4)
    


    ## 1)Filter VCF chromosomes
    print("------------------------------------------------")
    print("Filtering chromosomes...")
    CHRM_vcf_filtered = fl.chr_filtering(vcf_location_path=input_file, output_location_path= f"./temps/{output_file}.VCF_filtered_chr.vcf")
    
    print("------------------------------------------------")
    print("Filtering mutations...")
    ## 2)Filter VCF diff mutations mutations based on samples genotypes.
    
    MUT_vcf_filtered= fl.mutation_filter(vcf_qual_filtered=CHRM_vcf_filtered,
                                         samples_csv=samples_tab,
                                         FREQ_thresh=30,
                                         Rtrt_threshold=trt_thresh[1],
                                         Rnorm_threshold=trt_thresh[0],
                                         Strt_threshold=nml_thresh[1],
                                         Snorm_threshold=nml_thresh[0],
                                         Rvcf_output=f"./temps/{output_file}.VCF_RES_filtered_mut.vcf",
                                          Svcf_output=f"./temps/{output_file}.VCF_SENS_filtered_mut.vcf")

    ## 3)Add cravat annotation
    print("------------------------------------------------")
    print("Annotating vcf...")

    for key, value in MUT_vcf_filtered.items():
        oc.cravat_report(vcf_filtered_file_path=value, 
                        annotated_file_name_path=f"./results/annotated_{key}_{output_file}_VCF.vcf", 
                        username_oc=usr_glob, password_oc=psw_glob)
    
    

    #Files are read in each function.      
    temp_dir="./temps"
    #Removes temporary files if user inputs n (no)
    if temp_keep == "n":
        print("Cleaning up files in /temps...")
        temp_fls = listdir(temp_dir)
        for i in temp_fls:
            remove(path.join(temp_dir, i))
        print("done!")
    
    print("------------------------------------------------")
    print("Analysis finished.")
    print("------------------------------------------------")             

