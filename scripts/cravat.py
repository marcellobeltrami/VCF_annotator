from requests import Session
import time
import csv
import pandas as pd
from base64 import b64encode
from json import dumps, load

# Function that logs usr in.
def login(username, password):
    
    # Encode the credentials in base64
    credentials = b64encode(f"{username}:{password}".encode()).decode('utf-8')

    # Create a session
    session = Session()

    # Make a GET request to the login endpoint with the Authorization header
    response = session.get('https://run.opencravat.org/server/login', headers={'Authorization': f'Basic {credentials}'})
 
    # Check the response
    if response.status_code ==  200 and response.content==b'"success"':
        print("Login successful!")
        return session
        # You can proceed with other requests using the session object
    else:
        print("Login failed. Status code:", response.status_code)
        print("Response:", response.text)
        
   
#Reads settings from JSON file and returns them for OpenCravat.
def oc_settings(json_file_path):
    # Read the JSON file
    with open(json_file_path, "r") as json_file:
        data = load(json_file)

    # Extract options from the JSON data
    options = data.get("options", {})
    
    # Convert the options dictionary to a JSON string
    options_json_str = dumps(options)
    
    # Manually construct the desired format
    formatted = {'options': options_json_str}
    
    return formatted


def cravat_report(vcf_filtered_file_path, annotated_file_vcf,annotated_file_csv, username_oc, password_oc):
    
    #Initializes a session using usr login and password
    session = login(username_oc, password_oc)
    
    #Loads settings files for Open Cravat
    settings = oc_settings(json_file_path="scripts/settings/oc_settings.json")

    #Modify options depending on what you need.
    request = session.post('https://run.opencravat.org/submit/submit', 
                      files={'file_0':open(vcf_filtered_file_path)}, 
                      data=settings) 
    
    job_id= request.json()['id']
    
    print( job_id, "submitted!")
   
    #Continuosly checks whether job has finished. 
    job_status = session.get('https://run.opencravat.org/submit/jobs/' + job_id + '/status')
    time_elapsed = 0
   
    while job_status.json()['status'] != "Finished": 
        print(job_status.json()['status'])
        time.sleep(10)
        time_elapsed += 10
        print(time_elapsed/60, "Minutes elapsed since job submission")
        
        job_status = session.get('https://run.opencravat.org/submit/jobs/' + job_id + '/status')


    #Checks whether annotation has finished and outputs Annotated VCF.        
    if job_status.json()['status'] == "Finished":         
        report = session.post('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/vcf')

        while report.json() != "done":
             time.sleep(30)
             report = session.post('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/vcf')

        if report.json() == "done":

            request_report = session.get('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/vcf')
            
            with open(annotated_file_vcf, 'w') as file:
                file.write(request_report.text) 

    #Outputs annotations as CSV file                  
    if job_status.json()['status'] == "Finished":         
        report = session.post('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/csv')

        while report.json() != "done":
             time.sleep(30)
             report = session.post('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/csv')

        if report.json() == "done":

            request_report = session.get('https://run.opencravat.org/submit/jobs/' + job_id + '/reports/csv')
            
            with open(annotated_file_csv, 'w') as file:
                file.write(request_report.text) 
    return 0

import csv

def calculate_end_position(ref, alt, pos):
    """Calculate the end position based on the variant type."""
    
    # Insertion
    if ref == "-" and alt != "-":    
        return [(pos + len(alt)), "INS"]
    
    elif ref != "-" and alt == "-":
        return [(pos + len(ref) - 1), "DEL"]

    
    else:
        # Complex indels or other cases
        return [(pos + len(ref) - 1), "SNP"]


#Converts INDEL csv to indel MAF 
def convert_INDEL_csv_to_maf(input_file, output_file):
    with open(input_file, 'r') as f:
        # Skip lines starting with '#' to ignore comments
        lines = filter(lambda x: not x.startswith('#'), f.readlines())
        reader = csv.DictReader(lines)
        header = [
            "Hugo_Symbol", "Chromosome", "Start_Position", "End_Position", "Reference_Allele",
            "Tumor_Seq_Allele1", "Tumor_Seq_Allele2", "Variant_Classification", "HGVSp_Short",
            "Transcript_ID", "Variant_Type", "Exon_Number", "HGVS.c", "HGVS.p", "ALL_Mappings",
            "gPos.end", "Tumor_Sample_Barcode", "Tags", "ClinVar_Sig", "ClinVar_Disease_Refs",
            "ClinVar_Disease_Names", "ClinVar_Rev_Stat", "ClinVar_ID", "ClinVar_Sig_Conf", "dbSNP_RS"
        ]
        rows = []
        annotations_list = []
        for row in reader:
            start_position = int(row["pos"])
            ref = row["ref_base"]
            alt = row["alt_base"]
            INDEL_notation = calculate_end_position(ref, alt, start_position)
            samples = row["samples"].split(';')
            tags = row["tags"].split(';')
            clinvar_sig = row["clinvar.sig"].split(';')
            clinvar_disease_refs = row["clinvar.disease_refs"].split(';')
            clinvar_disease_names = row["clinvar.disease_names"].split(';')
            clinvar_rev_stat = row["clinvar.rev_stat"].split(';')
            clinvar_id = row["clinvar.id"].split(';')
            clinvar_sig_conf = row["clinvar.sig_conf"].split(';')
            dbsnp_rs = row["dbsnp.rsid"].split(';')
            annotations_list.append(row["so"])
            
            for i, sample in enumerate(samples):
                maf_row = {
                    "Hugo_Symbol": row["hugo"],
                    "Chromosome": row["chrom"],
                    "Start_Position": start_position,
                    "End_Position": INDEL_notation[0],
                    "Reference_Allele": ref,
                    "Tumor_Seq_Allele1": alt,
                    "Tumor_Seq_Allele2": "",  # Leave empty as it's not specified in the input
                    "Variant_Classification": row["so"],
                    "HGVSp_Short": row["cchange"],
                    "Transcript_ID": row["transcript"],
                    "Variant_Type": INDEL_notation[1],  # Not specified in the input
                    "Exon_Number": row["exonno"],
                    "HGVS.c": row["achange"],
                    "HGVS.p": "",  # Not specified in the input
                    "ALL_Mappings": row["all_mappings"],
                    "gPos.end": row["gposend"],
                    "Tumor_Sample_Barcode": sample,
                    "Tags": tags[i] if i < len(tags) else "",
                    "ClinVar_Sig": clinvar_sig[i] if i < len(clinvar_sig) else "",
                    "ClinVar_Disease_Refs": clinvar_disease_refs[i] if i < len(clinvar_disease_refs) else "",
                    "ClinVar_Disease_Names": clinvar_disease_names[i] if i < len(clinvar_disease_names) else "",
                    "ClinVar_Rev_Stat": clinvar_rev_stat[i] if i < len(clinvar_rev_stat) else "",
                    "ClinVar_ID": clinvar_id[i] if i < len(clinvar_id) else "",
                    "ClinVar_Sig_Conf": clinvar_sig_conf[i] if i < len(clinvar_sig_conf) else "",
                    "dbSNP_RS": dbsnp_rs[i] if i < len(dbsnp_rs) else ""
                }
                rows.append(maf_row)


    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)

    return set(annotations_list)

# Generate metadata for maftools. 
def maf_tools_metadata(VCF_annotator_metadata_csv, output_name= "MAF_tools_metadata.csv"):
    datadf = pd.read_csv(VCF_annotator_metadata_csv, sep="\t")
    melted_df = datadf.melt(var_name= "Clinical_Info", value_name="Tumor_Sample_Barcode")
    melted_df = melted_df.dropna()
    # Rename and reorder the columns
    clinical_df = melted_df[['Tumor_Sample_Barcode', 'Clinical_Info']]
    clinical_df = clinical_df.reset_index(drop=True)
    clinical_df.to_csv(output_name, index=False)
    

    


#Function generating a starting R script for maftools annotation. 
def initial_maftools(variant_annotation_list, out_path= "./maftools.R"):
    variant_annotation_str = ', '.join([f'"{item}"' for item in variant_annotation_list])

    with open(out_path, "w" ) as file_r: 
        print('if (!require("BiocManager", quietly = TRUE))',file=file_r)
        print('     install.packages("BiocManager")',file=file_r)
        print('if (!require("maftools", quietly = TRUE))',file=file_r)
        print('     install.packages("maftools")',file=file_r)
        print('library(maftools)',file=file_r)
        print("",file=file_r)
        print("# Here pathways to the generated file metadata are required.",file=file_r)
        print('clin_data <- <file path to generated metadata file>',file=file_r)
        print('maf_file <- file path to generated maf file>',file=file_r)
        print(f'vc_nonSyn_vector <- c({variant_annotation_str})',file=file_r)
        print("",file=file_r)
        print("# This reads the file in MAF-tools.",file=file_r)
        print('laml <- read.maf(maf = maf_file,vc_nonSyn = vc_nonSyn_vector, clinicalData = clin_data)',file=file_r)
        print('plotmafSummary(maf = laml, rmOutlier = TRUE,  dashboard = TRUE, titvRaw = FALSE)',file=file_r)



# Usage example:
input_file = "/home/marcello/Thesis_dev/VCF_annotator/results/annotated_SENS_test_run_INDEL.csv"
output_file = "./annotated_SENS_test.maf"
unique_annotation = convert_INDEL_csv_to_maf(input_file, output_file)

initial_maftools(unique_annotation)
maf_tools_metadata("/home/marcello/Thesis_dev/VCF_annotator/test_data/samples_metadata.txt")



