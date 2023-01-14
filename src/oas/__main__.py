import pathlib
import sys
from argparse import ArgumentParser, Namespace
from .dtypes import Convert as settings_conv, Metadata as settings_meta
from .modes import Convert as app_conv, Metadata as app_meta

def main() -> None:
    parser = ArgumentParser(prog = 'oas', description = "Tools to work with PMC's OAS data")
    subparsers = parser.add_subparsers(help = 'sub-commands')    
    metadata_parser(subparsers.add_parser('metadata', help = "Extracts the metadata from the corpus"))
    convert_parser(subparsers.add_parser('convert', help = "Convert the data to our standard format"))
    args = parser.parse_args()
    print_args(args)
    args.run(args)

def metadata_parser(parser: ArgumentParser) -> None:
    def run(args: Namespace) -> None:
        set = settings_meta(args.source, args.dest, args.log)
        app = app_meta(set)
        app.init()
        app.run()
    parser.add_argument('-source', type = pathlib.Path, required = True, help = "The folder containing the .tar'ed JATS files.")
    parser.add_argument('-dest', type = pathlib.Path, required = True, help = "The CSV file used to store the metadata")
    parser.add_argument('-log', type = pathlib.Path, required = True, help = 'The folder of raw JATS files that did not process')
    parser.set_defaults(run = run)
    parser.set_defaults(cmd = 'metadata')

def convert_parser(parser: ArgumentParser) -> None:
    def run(args: Namespace) -> None:
        set = settings_conv(args.source, args.dest, args.count, args.dest_pattern, args.log)
        app = app_conv(set)
        app.init()
        app.run()
    parser.add_argument('-source', type = pathlib.Path, required = True, help = 'The folder to the base JSON files')
    parser.add_argument('-dest', type = pathlib.Path, required = True, help = 'The folder for the converted TXT files')
    parser.add_argument('-count', type = int, default = 25000, help = 'The number of articles per TXT file')
    parser.add_argument('-dest_pattern',  type = str, default = 'oas.{id:04}.txt', help = 'The format of the TXT file name')
    parser.add_argument('-log', type = pathlib.Path, required = True, help = 'The folder of raw JATS files that did not process')
    parser.set_defaults(run = run)
    parser.set_defaults(cmd = 'convert')

def print_args(args: Namespace) -> None:
    print(f'--- {args.cmd} ---')
    for key in args.__dict__.keys():
        if key not in ['cmd', 'run']:
            print(f'{key}: {args.__dict__[key]}')
    print('---------')

if __name__ == "__main__":
    sys.exit(main())
