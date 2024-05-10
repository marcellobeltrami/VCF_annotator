from vcf import Reader, Writer
import pandas as pd
from math import isnan
#Function that generates relevant chromosomes. Preset is for humans. 
def chrom_gen(chromosome=25):
    chrom_list=[]
    for i in range(1,chromosome):
        
        if i == (chromosome-2): 
            chrom_list.append("chr"+ "X")
        elif i == (chromosome-1): 
            chrom_list.append("chr"+ "Y")
        else:
            chrom_list.append("chr"+ str(i))

    return chrom_list


#Function that filters out all scaffolds variant found in the VCF file. Function requires input and output
def chr_filtering(vcf_location_path, output_location_path):
    vcf_file = Reader(open(vcf_location_path, 'r'))
    vcf_writer = Writer(open(output_location_path, 'w'), vcf_file)

    chr_list = chrom_gen()

    chrom_checked = "chr1"
    print(chrom_checked, "being checked...")
    # Filters out partial chromosome (suggested practice on GATK). 
    for record in vcf_file: 
       # Write the variant to the filtered VCF file
        if record.CHROM in chr_list:
            vcf_writer.write_record(record)
        
        # Tracker of chromosome being filtered. 
        if record.CHROM != chrom_checked:
            chrom_checked = record.CHROM 
    
    vcf_writer.close()

    print("Filtering done!")
    return output_location_path 


def mutation_filter(vcf_qual_filtered, samples_csv, vcf_output,sens_threshold, res_threshold, FREQ_thresh=10, ADP_thres=10, GQ_thresh=30):
    
    #Reads in samples data and removes nans from the respective list.
    df = pd.read_csv(samples_csv, sep='\t')
    sensitive_pd = df.iloc[:, 0].tolist()
    sensitive_set = list(filter(lambda x: not isinstance(x, float), sensitive_pd))
    resistant_pd = df.iloc[:, 1].tolist()
    resistant_set = list(filter(lambda x: not isinstance(x, float), resistant_pd))
   
    vcf_reader = Reader(filename=vcf_qual_filtered)
    differential_mutations = Writer(open(vcf_output, 'w'), vcf_reader)
    
    chrom_checked = "chr1"
    print(chrom_checked, "being checked...")
    # For each record in file, accesses the sample INFO
    for record in vcf_reader:
        if chrom_checked != record.CHROM:
                print(chrom_checked, "done!")
                print(record.CHROM,"being checked...")
                chrom_checked = record.CHROM

        res_GP = []
        sens_GP = []
    
        
        #Checks for errors in filter and threshold of ADP (Average per-sample depth based on Phred score). 
        if record.FILTER == [] and record.INFO.get('ADP') >= ADP_thres:
        
            for sample_res in resistant_set: 
                genotype_res = str(record.genotype(sample_res).data.GT)
                genotype_qual = str(record.genotype(sample_res).data.GQ)
                
                try:
                    # 0/1-1/0 heterozygous mutation, 1/1 homozygous mutation  
                    #Splits info and puts them in dictionary "record_dictionary" based on sample name
                    
                    #Checks for genotype quality.
                    if int(genotype_qual) >= GQ_thresh:

                        FREQ= str(record.genotype(sample_res).data.FREQ)
                        FREQ_fl = float(FREQ.replace("%", "")) 
                        #Checks for FREQUENCY threshold.
                        if FREQ_fl >= FREQ_thresh: 
                            if genotype_res == "0/1" or genotype_res == "1/0": 
                                res_GP.append(genotype_res)
                            elif genotype_res == "1/1": 
                                res_GP.append(genotype_res)
                            else: 
                                pass
                #Exception is raised when mutations called is absent in all samples. Such record is then ignored.
                except ValueError:
                    pass  

            #Checks sensitive genotypes for each sample and appends them to a list if they are heterozygous or homozygous mutations.  
            for sample_sens in sensitive_set: 
                genotype_sens = str(record.genotype(sample_sens).data.GT)

                if genotype_sens == "0/1" or genotype_sens == "1/0": 
                    sens_GP.append(genotype_sens)
                elif genotype_sens == "1/1": 
                    sens_GP.append(genotype_sens)
                else: 
                    pass
        
            #Determines differential mutations by using length of respective lists and saves record to a file.

            if len(res_GP) >= res_threshold and len(sens_GP) <= sens_threshold:
                
                differential_mutations.write_record(record)

    #Lists are emptied for each record to save memory.
    sens_GP = []
    res_GP = []

    print(chrom_checked,"done!")

    return vcf_output
