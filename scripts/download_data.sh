#!/usr/bin/env bash
# Download reference and demo FASTQ files for the variant calling pipeline.
# Run inside WSL2/Linux with wget installed.

set -euo pipefail

REF_DIR="data/reference"
RAW_DIR="data/raw"
mkdir -p "$REF_DIR" "$RAW_DIR"

echo "Download a small reference FASTA (chr22 subset) from 1000 Genomes:"
echo "  wget -O ${REF_DIR}/reference.fa.gz \\"
echo "    ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa"
echo ""
echo "Then subset to chr22 for a lightweight demo:"
echo "  samtools faidx reference.fa chr22 > ${REF_DIR}/reference.fa"
echo ""
echo "Place paired FASTQ files at:"
echo "  ${RAW_DIR}/sample_R1.fastq.gz"
echo "  ${RAW_DIR}/sample_R2.fastq.gz"
echo ""
echo "Recommended source: 1000 Genomes NA12878 chr22 exome/WGS subset"
