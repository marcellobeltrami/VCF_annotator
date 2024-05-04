from vcf import Reader, Writer


def quality_filtering(vcf_file): 

    return 
    


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
def chr_filtering(vcf_location_path='all_samples_INDELS.vcf', output_location_path='all_samples_INDELS_filtered.vcf'):
    vcf_file = Reader(open(vcf_location_path, 'r'))
    vcf_writer = Writer(open(output_location_path, 'w'), vcf_file)

    chr_list = chrom_gen()


    for record in vcf_file: 
       
        if record.CHROM in chr_list:
        # Write the variant to the filtered VCF file
            print(record)
            vcf_writer.write_record(record)
        
    
    vcf_writer.close()

    print("Filtering done!")
    return 0 


def mutation_filter(vcf_qual_filtered, res, sens, vcf_output='./differential_SNPs.vcf',sens_threshold=1, res_threshold=2):
    resistant_set = set(res)
    sensitive_set = set(sens)

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
    
        # 0/1-1/0 heterozygous mutation, 1/1 homozygous mutation  
        #Splits info and puts them in dictionary "record_dictionary" based on sample name
        for sample_res in resistant_set: 
            genotype_res = str(record.genotype(sample_res).data.GT)
            
            if genotype_res == "0/1" or genotype_res == "1/0": 
                res_GP.append(genotype_res)
            elif genotype_res == "1/1": 
                res_GP.append(genotype_res)
            else: 
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

# Example usage
vcf_file = "/home/marcello/Thesis_dev/VCF_analyzer/scripts/test.vcf"
sample_group_res = ["BT594", "MBT357", "MBT373"]
sample_group_sens = ["BT972", "BT241", "BT935", "MBT168"]

mutation_filter(vcf_file, sample_group_res, sample_group_sens)
#print("Mutations found in two or more samples in group1 but not in group2:")

