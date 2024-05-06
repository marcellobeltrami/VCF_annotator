from vcf import Reader, Writer

#DELETE FILE AFTER TESTING

vcf_file = Reader(open("./scripts/test.vcf", 'r'))
sample_group_res = ["BT594", "MBT357", "MBT373"]
sample_group_sens = ["BT972", "BT241", "BT935", "MBT168"]


for record in vcf_file: 
    for sample in sample_group_res: 
        print(str(record.FILTER == []))
        try:
            FREQ= str(record.genotype(sample).data.FREQ)
            FREQ_fl = float(FREQ.replace("%", ""))
            

            if FREQ_fl > 50: 
                print(record)
        except ValueError:
            pass  