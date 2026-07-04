import gzip
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from parse_vcf import parse_vcf, write_csv


def test_parse_vcf_counts():
    summary = parse_vcf(ROOT / "tests" / "data" / "demo.vcf")
    assert summary["total_variants"] == 5
    assert summary["snp_count"] == 4
    assert summary["indel_count"] == 1
    assert summary["by_chromosome"]["chr22"] == 4


def test_top_variants_sorted_by_qual():
    summary = parse_vcf(ROOT / "tests" / "data" / "demo.vcf", top_n=2)
    top = summary["top_variants_by_qual"]
    assert len(top) == 2
    assert top[0]["qual"] >= top[1]["qual"]


def test_write_csv(tmp_path):
    summary = parse_vcf(ROOT / "tests" / "data" / "demo.vcf")
    csv_path = tmp_path / "top.csv"
    write_csv(summary, csv_path)
    content = csv_path.read_text(encoding="utf-8")
    assert "chrom" in content and "qual" in content


def test_parse_gzipped_vcf(tmp_path):
    demo = (ROOT / "tests" / "data" / "demo.vcf").read_bytes()
    gz_path = tmp_path / "demo.vcf.gz"
    gz_path.write_bytes(gzip.compress(demo))
    summary = parse_vcf(gz_path)
    assert summary["total_variants"] == 5
