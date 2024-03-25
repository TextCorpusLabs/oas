# OAS To Text Corpus

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2023.01.11-success.svg)

The [National Institutes of Health](https://nih.gov) has provided an excellent [data source](https://www.ncbi.nlm.nih.gov/pmc/tools/textmining/) for text mining.
Not only does it cover Medical journals, but other ones from mathematics to chemistry.
The purpose of this repo is to convert the PMC Open Access Subset from the given format into the text corpus format we use.
I.E.

* The full corpus consisting of one or more TXT files in a single folder
* One or more articles in a single TXT file
* Each article will have a header in the form "--- {id} ---"
* Each article will have its abstract and body extracted
* One sentence per line
* Paragraphs are separated by a blank line

# Operation

## Install

You can install the package using the following steps:

`pip` install using an _admin_ prompt.

```{ps1}
pip uninstall oas
python -OO -m pip install -v git+https://github.com/TextCorpusLabs/oas.git
```

or if you have the code local

```{ps1}
pip uninstall oas
python -OO -m pip install -v c:/repos/TextCorpusLabs/oas
```

## Run

You are responsible for getting the source files.
They can be found on this [FTP site](ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/).
You will need to further navigate into the three sub-folders: oa_comm, oa_noncomm, and oa_other.
I recommend using [FileZilla](https://filezilla-project.org/).
I installed my copy using [Chocolatey](https://community.chocolatey.org/packages/filezilla).

You are responsible for un-compressing and validating the source files.
I recommend using [7zip](https://www.7-zip.org/).
I installed my copy using [Chocolatey](https://community.chocolatey.org/packages/7zip).

The reason you are responsible is because the server the NIH keeps the files on is fickle.
Sometimes it will serve corrupted files.
Those files need re-downloaded and re-verified, then the file inside (the files are .tar.gz) needs verified too.
OAS is also **HUGE**.
As of 2024/03/25 it is almost 500 GB in .tar form.
You must make sure you have enough space before you start.

All the below commands assume the corpus is a folder of .tar files.

1. Extracts the metadata from the corpus.

```{ps1}
oas metadata -source c:/data/oas -dest c:/data/oas.meta.csv
```

The following are required parameters:

* `source` is the folder containing the .tar'ed JATS files.
* `dest` is the CSV file used to store the metadata.

The following are optional parameters:

* `log` is the folder of raw JATS files that did not process.
  It defaults to empty (not saved).

2. Convert the data to our standard format.

```{ps1}
oas convert -source c:/data/oas -dest c:/data/oas.std
```

The following are required parameters:

* `source` is the folder containing the .tar'ed JATS files.
* `dest` is the folder for the converted TXT files.

The following are optional parameters:

* `lines` is the number of lines per TXT file.
  The default is 250000.
* `dest_pattern` is the format of the TXT file name.
  It defaults to `{source}.{id:04}.txt`.
  `source` is the source file name's stem.
  `id` is an increasing value that increments after `lines` are stored in a file. 
* `log` is the folder of raw JATS files that did not process.
  It defaults to empty (not saved).

## Debug/Test

The code in this repo is setup as a module.
[Debugging](https://code.visualstudio.com/docs/python/debugging#_module) and [testing](https://code.visualstudio.com/docs/python/testing) are based on the assumption that the module is already installed.
In order to debug (F5) or run the tests (Ctrl + ; Ctrl + A), make sure to install the module as editable (see below).

```{ps1}
pip uninstall oas
python -m pip install -e c:/repos/TextCorpusLabs/oas
```
