#!/usr/bin/env python3
"""Parse VCF files and summarize variant statistics."""

import argparse
import csv
import gzip
import json
import sys
from collections import Counter
from pathlib import Path


def open_vcf(path: Path):
    """Open a plain or gzip-compressed VCF file for text reading."""
    if path.suffix == ".gz" or path.name.endswith(".vcf.gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open(encoding="utf-8")


def parse_vcf(path: Path, top_n: int = 10) -> dict:
    """Parse a VCF file and return summary statistics."""
    chrom_counts: Counter = Counter()
    snp_count = 0
    indel_count = 0
    variants = []

    with open_vcf(path) as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                continue

            chrom, pos, _id, ref, alt, qual, _filter, _info = fields[:8]
            chrom_counts[chrom] += 1

            alt_allele = alt.split(",")[0]
            if len(ref) == 1 and len(alt_allele) == 1:
                snp_count += 1
            else:
                indel_count += 1

            try:
                qual_value = float(qual) if qual != "." else 0.0
            except ValueError:
                qual_value = 0.0

            variants.append(
                {
                    "chrom": chrom,
                    "pos": int(pos),
                    "ref": ref,
                    "alt": alt,
                    "qual": qual_value,
                }
            )

    top_variants = sorted(variants, key=lambda v: v["qual"], reverse=True)[:top_n]

    return {
        "total_variants": sum(chrom_counts.values()),
        "by_chromosome": dict(chrom_counts),
        "snp_count": snp_count,
        "indel_count": indel_count,
        "top_variants_by_qual": top_variants,
    }


def write_csv(summary: dict, output_path: Path) -> None:
    """Write top variants to CSV."""
    rows = summary["top_variants_by_qual"]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["chrom", "pos", "ref", "alt", "qual"]
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse and summarize VCF files")
    parser.add_argument("vcf", type=Path, help="Input VCF or VCF.gz file")
    parser.add_argument(
        "-o", "--output", type=Path, help="JSON summary output path"
    )
    parser.add_argument(
        "--csv", type=Path, help="Optional CSV output for top variants"
    )
    parser.add_argument("--top", type=int, default=10, help="Top N variants by QUAL")
    args = parser.parse_args(argv)

    summary = parse_vcf(args.vcf, top_n=args.top)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote summary to {args.output}")

    if args.csv:
        write_csv(summary, args.csv)
        print(f"Wrote top variants to {args.csv}")

    print(f"Total variants: {summary['total_variants']}")
    print(f"SNPs: {summary['snp_count']}, indels: {summary['indel_count']}")
    for chrom, count in sorted(summary["by_chromosome"].items()):
        print(f"  {chrom}: {count}")

    return 0


# Snakemake script entry point
if __name__ == "__main__":
    if len(sys.argv) == 1:
        vcf_path = Path(snakemake.input.vcf)  # type: ignore[name-defined]
        out_path = Path(snakemake.output.summary)  # type: ignore[name-defined]
        summary = parse_vcf(vcf_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    else:
        raise SystemExit(main())
