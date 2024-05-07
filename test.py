from vcf import Reader, Writer

#DELETE FILE AFTER TESTING.

vcf_file = Reader(open("./scripts/test.vcf", 'r'))
sample_group_res = ["BT594", "MBT357", "MBT373"]
sample_group_sens = ["BT972", "BT241", "BT935", "MBT168"]


with open("scripts/settings/file.txt", "w") as file: 
    print("hello there", file=file)