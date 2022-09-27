# OAS To Text Corpus

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2022.09.27-success.svg)

The [National Institutes of Health](https://nih.gov) has provided an excellent [data source](https://www.ncbi.nlm.nih.gov/pmc/tools/textmining/) for text mining.
Not only does it cover Medical journals, but other ones from mathematics to chemistry.
The purpose of this repo is to convert the PMC Open Access Subset from the given format into the text corpus format we use.
I.E.

* The full corpus consisting of one or more JSONL(ines) files in a single folder
* One or more articles in a single JSONL(ines) file
* One article per JSON object
* Each JSON object on a single line
* Text free of xml.

# Operation

## Install

You can install the package using the following steps:

1. `pip` install using an _admin_ prompt.
   ```{ps1}
   pip uninstall oas
   pip install -v git+https://github.com/TextCorpusLabs/oas.git
   python -c "import nltk;nltk.download('punkt')"
   ```

## Run

You can run the package in the following ways:

1. Download all files associated with PMC's OAS data dump.
   **NOTE**: the files are both tar'ed and gz'iped.
   You will need to extract them if you want to use the other tools.
   ```{ps1}   
   oas download -dest d:/oas/dl

   $7z = 'C:/Program Files/7-Zip/7z.exe'
   . $7z x -od:/oas/dl d:/oas/dl/*.gz -y
   . $7z x -od:/oas/dl d:/oas/dl/*.tar -y
   ``` 
2. Convert PMC's OAS folders to a JSONL file containing all the articles minus any markup.
   Each JSONL file may contain more than one article.
   ```{ps1}
   oas convert -source d:/oas/raw -dest d:/oas/conv
   ```
   The following are optional parameters
   * `dest_pattern` is the format of the JSON file name.
     It defaults to `corpus.{id:02}.jsonl`
   * `count` is the number of JATS files in a single JSON file.
     This is useful to prevent any one single file from exploding in size.
     The default is `500000`
3. Tokenize JSON files using a modified Punkt/TreeBank processor.
   This will create one tokenized file per one base file
   ```{ps1}
   oas tokenize -source d:/oas/conv -dest d:/oas/tok
   ```
   The following is an optional parameter
   * `dest_pattern` is the format of the JSON file name.
     It defaults to `{name}.tokenized.jsonl`

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
