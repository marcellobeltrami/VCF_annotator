BiocManager::install("maftools")
library(maftools)
# Here pathways to the generated file metadata are required.
clin_data <- <file path to generated metadata file>
maf_file <- file path to generated maf file>
vc_nonSyn_vector <- c({'', 'processed_transcript', '5_prime_UTR_variant', 'intron_variant', 'miRNA', '2kb_downstream_variant', 'frameshift_truncation', 'lnc_RNA', '3_prime_UTR_variant', '2kb_upstream_variant', 'inframe_insertion', 'inframe_deletion', 'frameshift_elongation', 'NMD_transcript_variant'})

# This reads the file in MAF-tools.
laml <- read.maf(maf = maf_file,vc_nonSyn = vc_nonSyn_vector, clinicalData = clin_data)
plotmafSummary(maf = laml, rmOutlier = TRUE,  dashboard = TRUE, titvRaw = FALSE)
