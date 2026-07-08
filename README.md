# Variant Calling Pipeline

Germline variant calling workflow: **BWA** alignment, **samtools** BAM processing, **bcftools** variant calling, and **Python VCF parsing**.

## Biological question

What genetic variants (SNPs and indels) are present in a whole-genome or exome sequencing sample?

## Tools

| Step | Tool |
|------|------|
| Alignment | BWA-MEM |
| BAM processing | samtools |
| Variant calling | bcftools (mpileup + call) |
| VCF parsing | Python (`scripts/parse_vcf.py`) |

## Installation

```bash
git clone https://github.com/kiralyrichard03/variant-calling-pipeline.git
cd variant-calling-pipeline
conda env create -f environment.yml
conda activate variant-calling
```

## Prerequisites

- **Linux or WSL2**
- Conda / Mamba
- ~10 GB free disk space for demo FASTQ + BAM + VCF

## Quick start

```bash
# Create conda environment
conda env create -f environment.yml
conda activate variant-calling

# Download reference (chr22) and GIAB NA12878 FASTQ — see "Example dataset" below

# Run pipeline from project root
snakemake -s workflow/Snakefile --configfile config/config.yaml -c 4

# Parse VCF standalone (supports .vcf and .vcf.gz)
python scripts/parse_vcf.py results/variants/variants.vcf.gz \
  -o results/variants/variant_summary.json \
  --csv results/variants/top_variants.csv
```

## Example dataset

**Sample:** NA12878 (HG001) — [GIAB Garvan HiSeq Exome](https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/NA12878/Garvan_NA12878_HG001_HiSeq_Exome/)

```bash
mkdir -p data/raw data/reference

# Paired FASTQ (trimmed L001 lane)
cd data/raw
BASE_URL="https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/NA12878/Garvan_NA12878_HG001_HiSeq_Exome"
wget -c "${BASE_URL}/NIST7035_TAAGGCGA_L001_R1_001_trimmed.fastq.gz"
wget -c "${BASE_URL}/NIST7035_TAAGGCGA_L001_R2_001_trimmed.fastq.gz"
ln -sf NIST7035_TAAGGCGA_L001_R1_001_trimmed.fastq.gz sample_R1.fastq.gz
ln -sf NIST7035_TAAGGCGA_L001_R2_001_trimmed.fastq.gz sample_R2.fastq.gz
cd ../..

# chr22 reference (GRCh38)
cd data/reference
wget -O chr22.fa.gz "https://ftp.ensembl.org/pub/release-109/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.chromosome.22.fa.gz"
gunzip -c chr22.fa.gz > reference.fa
samtools faidx reference.fa
cd ../..
```

**Tip:** Run the pipeline from a Linux home directory (e.g. `~/variant-calling-pipeline`), not from `/mnt/c/OneDrive`, to avoid Snakemake permission issues on WSL2.

## Example run (NA12878, chr22)

Validated on WSL2 Ubuntu with GIAB Garvan exome FASTQ and Ensembl chr22 reference:

| Metric | Result |
|--------|--------|
| Total variants | 260,805 |
| Chromosome | 22 |
| SNPs | 256,998 |
| Indels | 3,807 |

```json
{
  "total_variants": 260805,
  "by_chromosome": {
    "22": 260805
  },
  "snp_count": 256998,
  "indel_count": 3807,
  "top_variants_by_qual": [
    {
      "chrom": "22",
      "pos": 16307782,
      "ref": "C",
      "alt": "G",
      "qual": 228.431
    },
    {
      "chrom": "22",
      "pos": 16268238,
      "ref": "T",
      "alt": "C",
      "qual": 228.426
    },
    {
      "chrom": "22",
      "pos": 16369388,
      "ref": "A",
      "alt": "C",
      "qual": 228.426
    }
  ]
}
```

Full summary written to `results/variants/variant_summary.json` after a successful Snakemake run.

## Workflow

```
FASTQ + reference -> BWA-MEM -> sorted BAM -> bcftools -> VCF -> Python summary
```

## Input / output

| Input | Output |
|-------|--------|
| Paired FASTQ + reference FASTA | Sorted, indexed BAM |
| BAM + reference | `variants.vcf.gz` |
| VCF | JSON summary (counts by chromosome, SNP/indel split, top variants by QUAL) |

## Run tests

```bash
python -m pytest tests/ -v
```

## Project structure

```
config/config.yaml     Sample and reference paths
workflow/Snakefile     Snakemake workflow
scripts/parse_vcf.py   VCF parser and summarizer
tests/                 Unit tests with demo VCF
```

## License

MIT
