#import scripts.filter as flt
import scripts.cravat as oc
import scripts.filter as fl 
from os import listdir, remove, path
from pyfiglet import figlet_format
from json import dump, load


#<Starts  execution>
if __name__ == "__main__":
    
    print(figlet_format("VCF annotator", font="standard"))
    

    terminate="y"
    
    while terminate=="y" or terminate=="Y":
        input_file=str(input("Path to vcf:"))
        temp_keep = str(input("Keep temp files?[y/n]:"))
        file_name =str(input("Output_file_name:"))
        
        #Add functionality that allows to save credentials. 
        usr_glob=""
        psw_glob=""
        #Checks if credentials have been previously saved. 
        if path.exists("scripts/settings/credentials.json") == False:
            usr=input("Input OpenCravat user name:")
            psw=input("Input OpenCravat password:")
            keep=input("Keep credentials?[y/n]:")
            usr_glob=usr
            psw_glob=psw
        
            #Allows to save credentials in a json file
            json_file_cred = "scripts/settings/credentials.json"
            if keep =="y" or "Y":
                with open(json_file_cred,"w") as cred_bank: 
                   cred_dict = {"username":usr, "password":psw}
                   dump(cred_dict, cred_bank, indent=4)
        
        #Loads credetentials if they have been previously preserved.
        elif  path.exists(json_file_cred) == True:
            cred = load(json_file_cred)
            usr_glob = cred["username"]
            psw_glob = cred["password"]

        ## 1)Filter VCF chromosomes
        CHRM_vcf_filtered = fl.chr_filtering(vcf_location_path=input_file,output_location_path= f"/temps/{file_name}.VCF_filtered_chr.vcf")
        
        ## 2)Filter VCF diff mutations mutations based on samples.
        MUT_vcf_filtered= fl.mutation_filter(vcf_qual_filtered=CHRM_vcf_filtered,FREQ_thresh=30,vcf_output=f"/temps/{file_name}.VCF_filtered_mut.vcf" )

        ## 3)Add cravat annotation
        oc.cravat_report(vcf_filtered_file_path=MUT_vcf_filtered, annotated_file_name_path="results/annotated_VCF.py", username_oc=usr, password_oc=psw)

        #Files are read in each function.      
        temp_dir="./temps"
        #Removes temporary files if user inputs n (no)
        if temp_keep == "n":
            print("Cleaning up files in /temps...")
            temp_fls = listdir(temp_dir)
            for i in temp_fls:
                remove(path.join(temp_dir, i))
            print("done!")
        
        print("-------------------------------------------------------------")
        terminate=input("Analysis finished. Another vcf to analyze? [y/n]: ")
        print("-------------------------------------------------------------")             

   