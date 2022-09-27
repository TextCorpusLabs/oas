# OAS To Text Corpus

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2022.09.27-success.svg)

The [National Institutes of Health](https://nih.gov) has provided an excelent [data source](https://www.ncbi.nlm.nih.gov/pmc/tools/textmining/) for text mining.
Not only does it cover Medical journals, but other ones from mathmatics to chemestry.
The purpose of this repo is to convert the PMC Open Access Subset from the given format into the normal text corpus format.
I.E. one document per file, one sentence per line, pargraphs have a blank line between them.



# Operation

## Install

You can install the package using the following steps:

1. `pip` install using an _admin_ prompt.
   ```{ps1}
   pip uninstall oas
   pip install -v git+https://github.com/TextCorpusLabs/oas.git
   ```


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
They files seem to be on some form of continuous rolling update.
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
   $7z = 'C:/Program Files/7-Zip/7z.exe'
   . $7z x -od:/oas/tar "d:/oas/gz/*.gz"
   . $7z x -od:/oas/raw "d:/oas/tar/*.tar"
   rm -r -path "d:/oas/gz/*.gz"
   rm -r -path "d:/oas/tar/*.tar"
   ```
4. [Convert](./code/oas_to_jsonl.py) the raw JATS files into a single JSONL file.
   There is an optional parameter `-spc` that defaults to 1.
   This allows for tuning on multi core machines.
   On my i7-6700k w/64GB RAM, the best value seems to be `-spc 4`
   ```{ps1}
   python oas_to_jsonl.py -in d:/oas/raw -out d:/oas/corpus.jsonl
   ```
5. [Tokenize](./code/tokenize_oas_jsonl.py) the article text.
   This will create a file containing all the tokenized documents.
   There is an optional parameter `-spc` that defaults to 1.
   This allows for tuning on multi core machines.
   On my i7-6700k w/64GB RAM, the best value seems to be `-spc 8`
   ```{ps1}
   python tokenize_oas_jsonl.py -in d:/oas/corpus.jsonl -out d:/oas/corpus.tokenized.jsonl
   ```
6. [Extract](./code/extract_metadata.py) the metadata.
   This will create a single `metadata.csv` containing some useful information.
   In general this would be used as part of segmentation or as part of a MANOVA.
   Some of the files provide by NIH do not parse.
   These _incomplete_ files are filtered out of the final folders and noted in `{{file-out}}error.csv`
   ```{ps1}
   python extract_metadata.py -in d:/oas/raw -out d:/oas/metadata.csv
   ```

# Development

## Prerequisites

Install the required modules for each of the repositories.

1. Clone this repository then open an _Admin_ shell to the `~/` directory.
2. Install the required modules.
   ```{shell}
   pip uninstall oas
   pip install -e c:/repos/TextCorpusLabs/oas
   ```
3. Setup the `~/.vscode/launch.json` file (VS Code only)
   1. Click the "Run and Debug Charm"
   2. Click the "create a launch.json file" link
   3. Select "Python"
   4. Select "module" and enter _oas_
   5. Select one of the following modes and add the below `args` to the launch.json file.
      The `args` node should be a sibling of the `module` node.
      They may need to be changed for your pathing.
      1. Download
         ```{json}
         "args" : [
           "download",
           "-dest", "d:/oas/gz"]
         ```
      2. Conversion
         ```{json}
         "args" : [
           "convert",
           "-source", "d:/oas/raw",
           "-dest", "d:/oas/conv",
           "-dest_pattern", "corpus.{id:02}.jsonl",
           "-count", "500000"]
         ```
      3. Tokenize
         ```{json}
         "args" : [
           "tokenize",
           "-source", "d:/oas/raw",
           "-dest", "d:/oas/tok",
           "-dest_pattern", "{name}.tokenized.jsonl"]
         ```
