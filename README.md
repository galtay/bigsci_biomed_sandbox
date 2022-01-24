# bigsci_biomed_sandbox

# MuchMore

## Links

* https://muchmore.dfki.de/resources1.htm 
* https://muchmore.dfki.de/pubs/D4.1.pdf 

## Notes

Had to use chardet to (hopefully) discover the correct encoding. 
https://pypi.org/project/chardet/

Looks like it is ISO-8859-1

Four files are distributed

* springer_english_train_plain.tar.gz (just text in english)
* springer_german_train_plain.tar.gz (just text in german)
* springer_english_train_V4.2.tar.gz (annotated tokens in english)
* springer_german_train_V4.2.tar.gz (annotated tokens in german)

## Plain Text

* springer_english_train_plain.tar.gz (just text in english)
* springer_german_train_plain.tar.gz (just text in german)

This is a parallel corpus in english and german. 

Here we have 15,631 abstracts. 
* 7823 in english
* 7808 in german

Sample ids are of the form `Arthroskopie.00130003.eng.abstr`. 
For abstracts that have entries in both languages you will find sample IDs like, 
* Arthroskopie.00130003.eng.abstr
* Arthroskopie.00130003.ger.abstr

More Counts
* total matched abstract pairs:  6374
* en abstracts with no de:  1449
* de abstracts with no en:  1434

## Annotated Data

* springer_english_train_V4.2.tar.gz (annotated tokens in english)
* springer_german_train_V4.2.tar.gz (annotated tokens in german)

tar file members have names like, 
* Arthroskopie.00130003.eng.abstr.chunkmorph.annotated.xml

Looks like all the `xrceterms` fields are empty.


Missing 

* Arthroskopie.00130237.eng.abstr.chunkmorph.annotated.xml
