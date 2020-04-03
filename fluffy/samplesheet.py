"""Code to handle samplesheets"""

import logging
import pathlib
from typing import Iterator

LOG = logging.getLogger(__name__)


def get_separator(line: str) -> str:
    """Get the separator for file"""
    if " " in line:
        return " "
    if "," in line:
        return ","
    return None


def get_sample_col(line_content: list) -> int:
    """Get the column number that holds the sample name"""
    for column, info in enumerate(line_content):
        if info == "SampleID":
            return column
    return None


def read_samplesheet(
    samplesheet: pathlib.Path, project_dir: pathlib.Path
) -> Iterator[dict]:
    """Parse a sample sheet and return sample information

    Yields:
        samples(dict): a dictionary with a list of commands and 'se'(bool)
    """

    samples = {}
    sample_col = 0
    with open(samplesheet, "r") as infile:
        for line_nr, line in enumerate(infile):
            if line_nr == 0:
                separator = get_separator(line)
                LOG.debug("Use separator %s", separator)
                content = line.rstrip().split(separator)
                sample_col = get_sample_col(content)
                continue

            content = line.rstrip().split(separator)
            sample_name = content[sample_col]

            if sample_name in samples:
                continue

            single_end = True
            LOG.debug("Check if files are single end or not")
            for file_name in project_dir.glob(f"*{sample_name}*/*.fastq.gz"):
                if "_R2" in file_name in file_name:
                    single_end = False
                    break

            fastq = [
                "<( zcat {}/*{}*/*_R1*fastq.gz )".format(project_dir, sample_name),
                "<( zcat {}/*{}/*_R2*fastq.gz )".format(project_dir, sample_name),
            ]
            if single_end:
                LOG.info("Single end files!")
                fastq = [
                    "<( zcat {}/*{}*/*_R1*fastq.gz )".format(project_dir, sample_name)
                ]

            yield {"fastq": fastq, "single_end": single_end, "sample_id": sample_name}