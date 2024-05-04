#import scripts.filter as flt
import scripts.cravat as oc 
from os import listdir, remove, path
from pyfiglet import figlet_format 
if __name__ == "__main__":
    
    print(figlet_format("VCF annotator", font="standard"))
    

    terminate="y"
    
    while terminate=="y" or terminate=="Y":
        input_file=str(input("Path to vcf:"))
        temp_keep = str(input("Keep temp files?[y/n]:"))
        temp_dir ="./temps/"
        #Files are read in each function.      
        
        ## Filter VCF chromosomes

        ## Quality filtering 

        ## Filter VCF diff mutations mutations based on samples

        ## Add cravat annotation

        #Removes temporary files if user inputs n (no)
        if temp_keep == "n":
            print("Cleaning up...")
            temp_fls = listdir(temp_dir)
            for i in temp_fls:
                remove(path.join(temp_dir, i))
            print("done!")
        
        print("-------------------------------------------------------------")
        terminate=input("Analysis finished. Another vcf to analyze? [y/n]: ")
        print("-------------------------------------------------------------")             

   