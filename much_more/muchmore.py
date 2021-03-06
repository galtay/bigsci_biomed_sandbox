# coding=utf-8
# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
MuchMore Springer Bilingual Corpus

homepage

* https://muchmore.dfki.de/resources1.htm


description of annotation format

* https://muchmore.dfki.de/pubs/D4.1.pdf


Four files are distributed

* springer_english_train_plain.tar.gz (english plain text of abstracts)
* springer_german_train_plain.tar.gz (german plain text of abstracts)
* springer_english_train_V4.2.tar.gz (annotated xml in english)
* springer_german_train_V4.2.tar.gz (annotated xml in german)

Each tar file has one member file per abstract.
There are keys to join the english and german files
but there is not a 1-1 mapping between them (i.e. some
english files have no german counterpart and some german
files have no english counterpart). However, there is a 1-1
mapping between plain text and annotations for a given language
(i.e. an abstract in springer_english_train_plain.tar.gz will
also be found in springer_english_train_V4.2.tar.gz)

Some counts,

* 15,631 total abstracts
* 7,823 english abstracts
* 7,808 german abstracts
* 6,374 matched (en/de) abstracts
* 1,449 english abstracts with no german
* 1,434 german abstracts with no english

Some notes

* Arthroskopie.00130237.eng.abstr.chunkmorph.annotated.xml seems to be empty

"""

from dataclasses import dataclass
import gzip
import os
import re
import tarfile
from typing import Dict, List
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import chardet
import datasets
import pandas as pd


"""
Step 2: Create keyword descriptors for your dataset
The following variables are used to populate the dataset entry. Common ones include:
- `_DATASETNAME` = "your_dataset_name"
- `_CITATION`: Latex-style citation of the dataset
- `_DESCRIPTION`: Explanation of the dataset
- `_HOMEPAGE`: Where to find the dataset's hosted location
- `_LICENSE`: License to use the dataset
- `_URLs`: How to download the dataset(s), by name; make this in the form of a dictionary where <dataset_name> is the key and <url_of_dataset> is the balue
- `_VERSION`: Version of the dataset
"""

_DATASETNAME = "muchmore"

# TODO: home page has a list of publications but its not clear which to choose
_CITATION = """"""

_DESCRIPTION = """\
The corpus used in the MuchMore project is a parallel corpus of English-German scientific
medical abstracts obtained from the Springer Link web site. The corpus consists
approximately of 1 million tokens for each language. Abstracts are from 41 medical
journals, each of which constitutes a relatively homogeneous medical sub-domain (e.g.
Neurology, Radiology, etc.). The corpus of downloaded HTML documents is normalized in
various ways, in order to produce a clean, plain text version, consisting of a title, abstract
and keywords. Additionally, the corpus was aligned on the sentence level.

Automatic (!) annotation includes: Part-of-Speech; Morphology (inflection and
decomposition); Chunks; Semantic Classes (UMLS: Unified Medical Language System,
MeSH: Medical Subject Headings, EuroWordNet); Semantic Relations from UMLS.
"""

_HOMEPAGE = "https://muchmore.dfki.de/resources1.htm"

# TODO: website says public domain, but didn't see a specific license 
_LICENSE = ""

# TODO: there are 4 files in this corpus. played around with different configs
# but for now the default is to download the english annotated tar file.
# should we make different configs for lots of use cases?  
_URLs = {
    "en_plain": "https://muchmore.dfki.de/pubs/springer_english_train_plain.tar.gz",
    "de_plain": "https://muchmore.dfki.de/pubs/springer_german_train_plain.tar.gz",
    "en_anno": "https://muchmore.dfki.de/pubs/springer_english_train_V4.2.tar.gz",
    "de_anno": "https://muchmore.dfki.de/pubs/springer_german_train_V4.2.tar.gz",
    "muchmore": "https://muchmore.dfki.de/pubs/springer_english_train_V4.2.tar.gz",
}

# took version from annotated file names
_VERSION = "4.2.0"



NATIVE_ENCODING = "ISO-8859-1"

class MuchMoreDataset(datasets.GeneratorBasedBuilder):
    """MuchMore Springer Bilingual Corpus"""

    VERSION = datasets.Version(_VERSION)

    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name=_DATASETNAME,
            version=VERSION,
            description=_DESCRIPTION,
        ),
    ]

    DEFAULT_CONFIG_NAME = _DATASETNAME

    # heavily nested. this represents the structure in the raw xml
    # we can definitely do more to organize this, but what shape 
    # should that take? 
    def _info(self):

        if self.config.name == _DATASETNAME:
            features = datasets.Features({
                "sample_id": datasets.Value("string"),
                "corresp": datasets.Value("string"),
                "language": datasets.Value("string"),
                "sentences": datasets.Sequence({
                    "id": datasets.Value("string"),
                    "corresp": datasets.Value("string"),
                    "umlsterms": datasets.Sequence({
                        "id": datasets.Value("string"),
                        "from": datasets.Value("string"),
                        "to": datasets.Value("string"),
                        "concepts": datasets.Sequence({
                            "id": datasets.Value("string"),
                            "cui": datasets.Value("string"),
                            "preferred": datasets.Value("string"),
                            "tui": datasets.Value("string"),
                            "mshs": datasets.Sequence({
                                "code": datasets.Value("string"),
                            }),
                        }),
                    }),
                    "ewnterms": datasets.Sequence({
                        "id": datasets.Value("string"),
                        "to": datasets.Value("string"),
                        "from": datasets.Value("string"),
                        "senses": datasets.Sequence({
                            "offset": datasets.Value("string"),
                        }),
                    }),
                    "semrels": datasets.Sequence({
                        "id": datasets.Value("string"),
                        "term1": datasets.Value("string"),
                        "term2": datasets.Value("string"),
                        "reltype": datasets.Value("string"),
                    }),
                    "chunks": datasets.Sequence({
                        "id": datasets.Value("string"),
                        "to": datasets.Value("string"),
                        "from": datasets.Value("string"),
                        "type": datasets.Value("string"),
                    }),
                    "tokens": datasets.Sequence({
                        "id": datasets.Value("string"),
                        "pos": datasets.Value("string"),
                        "lemma": datasets.Value("string"),
                        "text": datasets.Value("string"),
                    }),
                })
            })


        return datasets.DatasetInfo(
            # This is the description that will appear on the datasets page.
            description=_DESCRIPTION,
            features=features,
            # If there's a common (input, target) tuple from the features,
            # specify them here. They'll be used if as_supervised=True in
            # builder.as_dataset.
            supervised_keys=None,
            # Homepage of the dataset for documentation
            homepage=_HOMEPAGE,
            # License for the dataset if available
            license=_LICENSE,
            # Citation for the dataset
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # TODO: This method is tasked with downloading/extracting the data and defining the splits depending on the configuration
        # If several configurations are possible (listed in BUILDER_CONFIGS), the configuration selected by the user is in self.config.name

        # dl_manager is a datasets.download.DownloadManager that can be used to download and extract URLs
        # It can accept any type or nested list/dict and will give back the same structure with the url replaced with path to local files.
        # By default the archives will be extracted and a path to a cached folder where they are extracted is returned instead of the archive
        my_urls = _URLs[self.config.name]
        data_dir = dl_manager.download(my_urls)
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                # These kwargs will be passed to _generate_examples
                # `iter_archive` will yield (file_path, file_pointer)
                # tuples for each abstract / member of the tar.gz
                # file when iterated over. 
                gen_kwargs={
                    "file_paths": dl_manager.iter_archive(data_dir),
                    "split": "train",
                },
            ),
        ]


    @staticmethod
    def _get_umlsterms_from_xsent(xsent: Element) -> List:
        xumlsterms = xsent.find("./umlsterms")

        umlsterms = []
        for xumlsterm in xumlsterms.findall("./umlsterm"):

            concepts = []
            for xconcept in xumlsterm.findall("./concept"):

                mshs = [{
                    "code": xmsh.get("code")
                } for xmsh in xconcept.findall("./msh")]

                concept = {
                    "id": xconcept.get("id"),
                    "cui": xconcept.get("cui"),
                    "preferred": xconcept.get("preferred"),
                    "tui": xconcept.get("tui"),
                    "mshs": mshs,
                }
                concepts.append(concept)

            umlsterm = {
                "id": xumlsterm.get("id"),
                "from": xumlsterm.get("from"),
                "to": xumlsterm.get("to"),
                "concepts": concepts,
            }
            umlsterms.append(umlsterm)

        return umlsterms


    @staticmethod
    def _get_ewnterms_from_xsent(xsent: Element) -> List:
        xewnterms = xsent.find("./ewnterms")

        ewnterms = []
        for xewnterm in xewnterms.findall("./ewnterm"):

            senses = [{
                "offset": xsense.get("offset")
            } for xsense in xewnterm.findall("./sense")]

            ewnterm = {
                "id": xewnterm.get("id"),
                "from": xewnterm.get("from"),
                "to": xewnterm.get("to"),
                "senses": senses,
            }
            ewnterms.append(ewnterm)

        return ewnterms


    @staticmethod
    def _get_semrels_from_xsent(xsent: Element) -> List[Dict[str,str]]:
        xsemrels = xsent.find("./semrels")
        return [{
            "id": xsemrel.get("id"),
            "term1": xsemrel.get("term1"),
            "term2": xsemrel.get("term2"),
            "reltype": xsemrel.get("reltype"),
        } for xsemrel in xsemrels.findall("./semrel")]


    @staticmethod
    def _get_chunks_from_xsent(xsent: Element) -> List[Dict[str,str]]:
        xchunks = xsent.find("./chunks")
        return [{
            "id": xchunk.get("id"),
            "to": xchunk.get("to"),
            "from": xchunk.get("from"),
            "type": xchunk.get("type"),
        } for xchunk in xchunks.findall("./chunk")]


    @staticmethod
    def _get_tokens_from_xsent(xsent: Element) -> List[Dict[str,str]]:
        xtext = xsent.find("./text")
        return [{
            "id": xtoken.get("id"),
            "pos": xtoken.get("pos"),
            "lemma": xtoken.get("lemma"),
            "text": xtoken.text,
        } for xtoken in xtext.findall("./token")]


    def _generate_examples(self, file_paths, split):
        _id = 0
        for file_path, f in file_paths:

            content_bytes = f.read()
            content_str = content_bytes.decode(NATIVE_ENCODING)
            if content_str == "":
                print(content_str)
                print("skipping")
                print()
                continue

            xroot = ET.fromstring(content_str)

            sentences = []
            for xsent in xroot.findall("./"):
                sentence = {
                    "id": xsent.get("id"),
                    "corresp": xsent.get("corresp"),
                    "umlsterms": self._get_umlsterms_from_xsent(xsent),
                    "ewnterms": self._get_ewnterms_from_xsent(xsent),
                    "semrels": self._get_semrels_from_xsent(xsent),
                    "chunks": self._get_chunks_from_xsent(xsent),
                    "tokens": self._get_tokens_from_xsent(xsent),
                }
                sentences.append(sentence)

            yield _id, {
                "sample_id": xroot.get("id"),
                "corresp": xroot.get("corresp"),
                "language": xroot.get("lang"),
                "sentences": sentences,
            },
            _id += 1
