# OAS To Text Corpus

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)

The [National Institutes of Health](https://nih.gov) has provided an excelent [data source](https://www.ncbi.nlm.nih.gov/pmc/tools/textmining/) for text mining.
Not only does it cover Medical journals, but other ones from mathmatics to chemestry.
The purpose of this repo is to convert the PMC Open Access Subset from the given format into the normal text corpus format.
I.E. one document per file, one sentence per line, pargraphs have a blank line between them.

# Prerequisites

_After_ completing our standard [prerequisite](https://github.com/TextCorpusLabs/getting-started#prerequisites) and [Python](https://github.com/TextCorpusLabs/getting-started#python) instructions, please follow the below steps:

1. Install NLTK package
   ```{shell}
   python -c "import nltk;nltk.download('punkt')"
   ```

# Steps

The below document describes how to recreate the text corpus.
It assumes that a particular path structure will be used, but the commands can be modified to target a different directory structure without changing the code.
For the target folder, make sure you have a _lot_ of space.
[This page](ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/) lists the current dumps.
They files seem to be on some form of continious rolling update.
**Note:** The shell syntax is PowerShell.
If you use a different shell, your syntax will be different. 

1. Clone this repo then open a shell to the `~/code` directory.
2. [Retrieve](./code/download_oas.py) the dataset.
```{ps1}
python download_oas.py -dest d:/oas/gz
``` 
3. Extract the data in-place.
   This needs done twice due to the `*.tar.gz` compression.
```{ps1}
. "C:/Program Files/7-Zip/7z.exe" x -od:/oas/tar "d:/oas/gz/*.gz"
. "C:/Program Files/7-Zip/7z.exe" x -aos -od:/oas/raw "d:/oas/tar/*.tar"
del "d:/oas/gz/*.gz"
del "d:/oas/tar/*.tar"
```
4. [Extract](./code/extract_metadata.py) the metadata.
   This will create a single `metadata.csv` containing some useful information.
   In general this would be used as part of segementation or as part of a MANOVA.
   Some of the files provide by NIH do not parse.
   These _incomplete_ files are filtered out of the final folders and noted in `{{file-out}}error.csv`
```{ps1}
python extract_metadata.py -in d:/oas/raw -out d:/oas/metadata.csv
```
5. [Convert](./code/convert_to_corpus.py) the raw JATS files into the nomal folder corpus format.
   This will create a text corpus folder at the location I.E. `./corpus` containing 2 sub folders, one for the abstract and one for the body.
   Some of the files provide by NIH do not parse.
   These _incomplete_ files are filtered out of the final folders and noted in `{{folder-out}}.error.csv`
```{ps1}
python convert_to_corpus.py -in d:/oas/raw -out d:/oas/corpus
```