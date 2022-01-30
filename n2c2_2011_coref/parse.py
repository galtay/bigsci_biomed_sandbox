"""
n2c2 2011 Coref

homepage

* https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/



task_1c:


"""
from collections import defaultdict
from dataclasses import dataclass
import gzip
import os
import re
import tarfile
from typing import Iterable, Tuple
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import zipfile

import chardet
import pandas as pd


BASE_DATA_PATH = os.path.join(
    os.environ.get("HOME"),
    "data",
    "big_science_biomedical",
)

DATASET = "n2c2_2011_coref"


PATHS = {
    "task_1c": os.path.join(BASE_DATA_PATH, DATASET, "Task_1C.zip"),
}


path = PATHS["task_1c"]

samples = defaultdict(dict)
with zipfile.ZipFile(path) as zf:
    for info in zf.infolist():

        base, filename = os.path.split(info.filename)
        exts = tuple(filename.split('.')[1:])
        sample_id = filename.split('.')[0]

        if exts in [("txt",), ("txt", "con")]:
            metapath = tuple(base.split("/"))
            samples[sample_id]["metapath"] = metapath
            content = zf.read(info).decode("utf-8")

            if exts == ("txt",):
                samples[sample_id]["txt"] = content

            elif exts == ("txt", "con"):
                samples[sample_id]["con"] = content



sample_id = "clinical-522"
text = samples[sample_id]["txt"]
text_lines = text.splitlines()
concepts_lines = samples[sample_id]["con"].splitlines()

dq = '''"'''
sq = """'"""


for cl in concepts_lines:

    cpart, tpart = cl.split("||")
    cpart = cpart.replace("c=", "")
    cpart = cpart.replace(dq, '')
    cpart_pieces = cpart.split()
    cpart_tokens = tuple(cpart_pieces[:-2])
    cpart_start = cpart_pieces[-2]
    cpart_end = cpart_pieces[-1]

    cpart_start_line, cpart_start_token = [int(el) for el in cpart_start.split(":")]
    cpart_end_line, cpart_end_token = [int(el) for el in cpart_end.split(":")]
    assert(cpart_start_line == cpart_end_line)
    cpart_line = cpart_start_line - 1
    cpart_end_token += 1

    tpart = tpart.replace("t=", "")
    concept_type = tpart.replace(dq, '')

    tokens_from_line = tuple([
        el.lower() for el in
        text_lines[cpart_line].split()[cpart_start_token: cpart_end_token]
    ])

    assert(tokens_from_line == cpart_tokens)
