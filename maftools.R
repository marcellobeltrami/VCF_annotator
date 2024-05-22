if (!require("BiocManager", quietly = TRUE))
     install.packages("BiocManager")
if (!require("maftools", quietly = TRUE))
     install.packages("maftools")
library(maftools)

# Here pathways to the generated file metadata are required.
clin_data <- <file path to generated metadata file>
maf_file <- file path to generated maf file>
vc_nonSyn_vector <- c("", "intron_variant", "frameshift_elongation", "lnc_RNA", "NMD_transcript_variant", "5_prime_UTR_variant", "frameshift_truncation", "processed_transcript", "3_prime_UTR_variant", "inframe_deletion", "2kb_upstream_variant", "inframe_insertion", "miRNA", "2kb_downstream_variant")

# This reads the file in MAF-tools.
laml <- read.maf(maf = maf_file,vc_nonSyn = vc_nonSyn_vector, clinicalData = clin_data)
plotmafSummary(maf = laml, rmOutlier = TRUE,  dashboard = TRUE, titvRaw = FALSE)
