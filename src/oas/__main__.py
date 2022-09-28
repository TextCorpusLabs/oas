import pathlib
import sys
from argparse import ArgumentParser
from oas.mode import convert, download, tokenize

def main() -> None:
    parser = ArgumentParser(prog = 'oas', description = "Tools to work with PMC's OAS data")
    subparsers = parser.add_subparsers(help = 'sub-commands')
    download_parser(subparsers.add_parser('download', help = "Download all files associated with PMC's OAS data dump"))
    convert_parser(subparsers.add_parser('convert', help = "Convert PMC's OAS folders to a JSONL file containing all the articles minus any markup"))
    tokenize_parser(subparsers.add_parser('tokenize', help = "Tokenize JSON files using a modified Punkt/TreeBank processor"))
    args = parser.parse_args()

    if args.function == download:
        print('TODO: PMC changed their format.')
        #args.function(args.dest)
    elif args.function == convert:
        args.function(args.source, args.dest, args.dest_pattern, args.count)
    elif args.function == tokenize:
        print('TODO: package conversion in progress.')
        #args.function(args.source, args.dest, args.dest_pattern)
    else:
        print('--- Unknown Command ---')

def download_parser(parser: ArgumentParser) -> None:
    parser.add_argument('-dest', type = ensure_folder, required = True, help = 'The destination location to use when saving the files')
    parser.set_defaults(function = download)

def convert_parser(parser: ArgumentParser) -> None:
    parser.add_argument('-source', type = ensure_folder, required = True, help = 'The root folder of the folders containing JATS files')
    parser.add_argument('-dest', type = ensure_folder, required = True, help = 'The folder to store the converted JSON files')
    parser.add_argument('-dest_pattern',  type = str, default = 'oas.{id:02}.jsonl', help = 'The format of the JSON file name')
    parser.add_argument('-count', type = int, default = 100000, help = 'The number of JATS files in a single JSON file')
    parser.set_defaults(function = convert)

def tokenize_parser(parser: ArgumentParser) -> None:
    parser.add_argument('-source', type = ensure_folder, required = True, help = 'The folder to the base JSON files')
    parser.add_argument('-dest', type = ensure_folder, required = True, help = 'The folder for the JSON files the include the tokenized results')
    parser.add_argument('-dest_pattern',  type = str, default = '{name}.tokenized.jsonl', help = 'The format of the JSON file name')
    parser.set_defaults(function = tokenize)

def ensure_folder(folder_path: str) -> pathlib.Path:
    folder= pathlib.Path(folder_path).resolve()
    if not folder.exists():
        folder.mkdir(parents = True)
    elif not folder.is_dir():
        raise NotADirectoryError(str(folder))
    return folder

if __name__ == "__main__":
    sys.exit(main())
