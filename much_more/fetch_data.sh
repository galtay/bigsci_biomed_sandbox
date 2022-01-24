#!/bin/bash

MUCH_MORE_BASE="https://muchmore.dfki.de/pubs"
DEST="$HOME/data/big_science_biomedical/much_more"
mkdir -p $DEST

files=(
    "springer_german_train_plain.tar.gz"
    "springer_german_train_V4.2.tar.gz"
    "springer_english_train_plain.tar.gz"
    "springer_english_train_V4.2.tar.gz"
)

for i in "${files[@]}"
do
    wget $MUCH_MORE_BASE/$i -O $DEST/$i
done

