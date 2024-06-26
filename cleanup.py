# WARNING: this scripts will delete all credentials, and results found in the VCF_annotator directory. BACKUP EVERYTHING YOU NEED.
from os import listdir, remove, path

print("Hold Your Horses: all credentials, and results found in the VCF_annotator directory will be deleted")
confirm = input("Are you sure you want to remove login info and results? [y/n]: ")
json_file_cred = "./scripts/settings/credentials.json"
    
if confirm=="y" or confirm=="Y":
    print("Removing files....")
    
    results_to_rm = listdir("./results/MAFTools/")    
    for res in results_to_rm:
        remove(path.join("./results/MAFTools",res))
        print(" -->",f"./results/MAFTools/{res}" , "removed.")
        


    #removes results in result directory
    results_to_rm = listdir("./results/")    
    for res in results_to_rm:
        if path.isdir(path.join("./results/",res)) == True: 
            pass
        else:
            remove(path.join("./results/",res))
            print(" -->",f"./results/{res}" , "removed.")
    
   

    #Removes JSON credentials.
    if path.exists(json_file_cred) == True:
        remove(json_file_cred)
        print("Credentials were removed.") 
    else: 
        print("Credentials were not saved, step skipped.") 
    
    print("Done! Good-bye :)")
else: 
    print("aborting...")
    print("Your files are safe.")   
