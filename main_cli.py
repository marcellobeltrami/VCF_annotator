import scripts.cravat as oc
import scripts.filter as fl 
from os import listdir, remove, path, remove
from pyfiglet import figlet_format
from json import dump, load
from argparse import ArgumentParser
from sys import exit

#<Starts  execution>
if __name__ == "__main__":
 

    print(figlet_format("VCF annotator", font="standard"))
    print("--------------------------------------------------------------------")
    #CLI interface
    main_parser = ArgumentParser(description='CLI interface for VCF annotator')
    analysisis_parser= main_parser.add_subparsers(title="analysis")
    analysis= analysisis_parser.add_parser(title="analysis", help="carries out VCF annotations and filtering")
    # CLI analysisi interface
    analysis.add_argument('-i', '--input_file', required=True, help='Path to input file')
    analysis.add_argument('-o', '--output_file', required=True, help='Output file name. Insert an identifier for your file, this is NOT the output file path')
    analysis.add_argument('-g', '--sample_groups', required=True, help='A TAB delimited file containing sample names found in VCF file. First column should be the normal, second one treatment')
    analysis.add_argument('-temp','--temp_keep', type=str, default="n",help='Determines whether to keep intermediate files[y/n].')
    analysis.add_argument('-nm','--normal_mutation_threshold', type=int, default=1,help='Mutations with genotypes above this values and lower than treatment GT will be removed ')
    analysis.add_argument('-tm','--treatment_mutation_threshold', type=int, default=2,help='Mutations with genotypes above this values and lower than normal GT will be kept ')
    
    
    # Parse arguments
    args_analysis = analysis.parse_args()
    samples_tab=str(args_analysis.sample_groups)
    input_file=str(args_analysis.input_file)
    temp_keep = args_analysis.temp_keep
    output_file =str(args_analysis.output_file)
    nml_thresh= int(args_analysis.normal_mutation_threshold)
    trt_thresh = int(args_analysis.treatment_mutation_threshold)
    

    # CLI analysisi interface for purging files
    purge_subparsers=main_parser.add_subparsers(title="purge")
    purge = purge_subparsers.add_parser("purge", type=str, help="Purge files")
    args_purge = purge.parse_args()
    purge_arg=args_purge.purge
    
    json_file_cred = "./scripts/settings/credentials.json"
    if purge_arg: 
        confirm = input("Are you sure you want to remove login info and results? [y/n]: ")

        if confirm=="y" or confirm=="Y":
            print("Removing files....")
            results_to_rm = listdir("./results/")    
            for res in results_to_rm:
                remove(res)
                print(res, "removed.")

            if path.exists(json_file_cred) == True:
                remove(json_file_cred)
            else: 
                print("Credentials were not found,  hence were not removed.") 
            
            print("Done! Good-bye :)")
            exit()

    #Functionality that allows to save credentials. 
    usr_glob=""
    psw_glob=""
    
    
    #Loads credetentials if they have been previously preserved.
    if  path.exists(json_file_cred) == True:
        cred = load(json_file_cred)
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
                                         res_threshold=trt_thresh,
                                         sens_threshold=nml_thresh,
                                         vcf_output=f"./temps/{output_file}.VCF_filtered_mut.vcf" )

    ## 3)Add cravat annotation
    print("------------------------------------------------")
    print("Annotating vcf...")
    oc.cravat_report(vcf_filtered_file_path=MUT_vcf_filtered, 
                     annotated_file_name_path="./results/annotated_VCF.vcf", 
                     username_oc=usr, password_oc=psw)

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

