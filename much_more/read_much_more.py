from dataclasses import dataclass
import gzip
import os
import re
import tarfile
from typing import Iterable, Tuple
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import chardet
import pandas as pd


NATIVE_ENCODING = "ISO-8859-1"
OUTPUT_ENCODING = "utf-8"

BASE_DATA_PATH = os.path.join(
    os.environ.get("HOME"),
    "data",
    "big_science_biomedical",
)

DATASET = "much_more"


plain_paths = {
    "en": os.path.join(BASE_DATA_PATH, DATASET, "springer_english_train_plain.tar.gz"),
    "de": os.path.join(BASE_DATA_PATH, DATASET, "springer_german_train_plain.tar.gz"),
}


def read_plain():

    rows = []
    for key, path in plain_paths.items():
        with tarfile.open(name=path, mode="r:gz") as tf:
            for member in tf.getmembers():
                prefix = re.sub(".(eng|ger).abstr", "", member.name)
                language = key
                with tf.extractfile(member) as fp:
                    content_bytes = fp.read()
                    try:
                        content_str = content_bytes.decode(NATIVE_ENCODING)
                        content_str.encode(OUTPUT_ENCODING).decode()
                    except UnicodeDecodeError:
                        print(chardet.detect(content_bytes))
                        raise ValueError()

                row = (prefix, member.name, content_str, language)
                rows.append(row)

    columns = ["prefix", "sample_id", "abstract", "language"]
    df_plain = pd.DataFrame(rows, columns=columns)
    return df_plain


df_plain = read_plain()
print('total abstracts (both languages): ', df_plain.shape[0])
print('language counts: \n', df_plain['language'].value_counts(), sep='')

en_sample = set(df_plain[df_plain['language']=='en']['prefix'])
de_sample = set(df_plain[df_plain['language']=='de']['prefix'])

print('total matched abstract pairs: ', len(en_sample & de_sample))
print('en abstracts with no de: ', len(en_sample - de_sample))
print('de abstracts with no en: ', len(de_sample - en_sample))
print()




anno_paths = {
    "en": os.path.join(BASE_DATA_PATH, DATASET, "springer_english_train_V4.2.tar.gz"),
    "de": os.path.join(BASE_DATA_PATH, DATASET, "springer_german_train_V4.2.tar.gz"),
}

rows = []
for key, path in anno_paths.items():
    with tarfile.open(name=path, mode="r:gz") as tf:
        for member in tf.getmembers():

            prefix = re.sub(".(eng|ger).abstr.chunkmorph.annotated.xml", "", member.name)
            language = key

            if "Arthroskopie.00130003" in prefix:
                print(member)

            with tf.extractfile(member) as fp:
                content_bytes = fp.read()
                try:
                    content_str = content_bytes.decode(NATIVE_ENCODING)
                    content_str.encode(OUTPUT_ENCODING).decode()
                except UnicodeDecodeError:
                    print(chardet.detect(content_bytes))
                    raise ValueError()

                row = (prefix, member.name, content_str, language)
                rows.append(row)

columns = ["prefix", "sample_id", "anno_xml", "language"]
df_anno = pd.DataFrame(rows, columns=columns)

print('total docs (both languages): ', df_anno.shape[0])
print('language counts: \n', df_anno['language'].value_counts(), sep='')

en_sample = set(df_anno[df_anno['language']=='en']['prefix'])
de_sample = set(df_anno[df_anno['language']=='de']['prefix'])

print('total matched doc pairs: ', len(en_sample & de_sample))
print('en docs with no de: ', len(en_sample - de_sample))
print('de docs with no en: ', len(de_sample - en_sample))
print()



@dataclass
class Msh:
    xcode: str


@dataclass
class Concept:
    xid: str
    xcui: str
    xpreferred: str
    xtui: str
    xmshs: Tuple[Msh,...]


@dataclass
class UmlsTerm:
    xid: str
    xfrom: str
    xto: str
    xconcepts: Tuple[Concept,...]


@dataclass
class Chunk:
    xid: str
    xfrom: str
    xto: str
    xtype: str


@dataclass
class Token:
    xid: str
    xpos: str
    xlemma: str
    xtext: str


@dataclass
class Sentence:
    xid: str
    xcorresp: str
    xumlsterms: Tuple[UmlsTerm,...]
    xchunks: Tuple[Chunk,...]
    xtext: Tuple[Token,...]


@dataclass
class Document:
    xid: str
    xtype: str
    xlang: str
    xcorresp: str
    xsentences: Tuple[Sentence,...]


sample_id = "Arthroskopie.00130003.eng.abstr.chunkmorph.annotated.xml"
xml_str = df_anno[df_anno['sample_id']==sample_id].iloc[0]['anno_xml']
xroot = ET.fromstring(xml_str)
#doc = Document()

def get_chunks_from_xsent(xsent: Element) -> Tuple[Chunk,...]:
    xchunks = xsent.find("./chunks")
    chunks = [
        Chunk(
            xid=xchunk.get("id"),
            xfrom=xchunk.get("from"),
            xto=xchunk.get("to"),
            xtype=xchunk.get("type"),
        ) for xchunk in xchunks.findall("./chunk")
    ]
    return tuple(chunks)


def get_text_from_xsent(xsent: Element) -> Tuple[Token,...]:
    xtext = xsent.find("./text")
    tokens = [
        Token(
            xid=xtoken.get("id"),
            xpos=xtoken.get("pos"),
            xlemma=xtoken.get("lemma"),
            xtext=xtoken.text,
        ) for xtoken in xtext.findall("./token")
    ]
    return tuple(tokens)


def get_umlsterms_from_xsent(xsent: Element) -> Tuple[UmlsTerm,...]:
    xumlsterms = xsent.find("./umlsterms")

    umlsterms = []
    for xumlsterm in xumlsterms.findall("./umlsterm"):

        concepts = []
        for xconcept in xumlsterm.findall("./concept"):

            mshs = []
            for xmsh in xconcept.findall("./msh"):
                msh = Msh(xcode=xmsh.get("code"))
                mshs.append(msh)

            concept = Concept(
                xid=xconcept.get("id"),
                xcui=xconcept.get("cui"),
                xpreferred=xconcept.get("preferred"),
                xtui=xconcept.get("tui"),
                xmshs=tuple(mshs),
            )
            concepts.append(concept)

        umlsterm = UmlsTerm(
            xid=xumlsterm.get("id"),
            xfrom=xumlsterm.get("from"),
            xto=xumlsterm.get("to"),
            xconcepts=tuple(concepts),
        )
        umlsterms.append(umlsterm)

    return tuple(umlsterms)



for xsent in xroot.findall("./"):
    chunks = get_chunks_from_xsent(xsent)
    text = get_text_from_xsent(xsent)
    umlsterms = get_umlsterms_from_xsent(xsent)

    sent = Sentence(
        xid=xsent.get("id"),
        xcorresp=xsent.get("corresp"),
        xumlsterms=umlsterms,
        xchunks=chunks,
        xtext=text,
    )
    break
