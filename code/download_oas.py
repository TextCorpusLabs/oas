import pathlib
import sys
import wget
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def download_oas(dest_folder: pathlib.Path) -> None:
    """
    Downloads all the files associated with PMC's OAS data dump

    Parameters
    ----------
    dest_folder : str
        The destination location to use when saving the files
    """

    root_url = 'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/'
    file_name = wget.download(root_url)
    file_name = pathlib.Path(file_name)

    with open(file_name, 'r', encoding = 'utf-8', newline = '') as file_content:
        lines = file_content.readlines()
        files = [line.split(' ')[-1].strip() for line in lines]
        files = [file for file in files if file.endswith('.xml.tar.gz')]

    file_name.unlink()

    print(f'\ndownloading {len(files)} file(s)')

    for file in files:
        print(f'\ndownloading {file}')
        curr_url = root_url + file
        curr_file = str(dest_folder.joinpath(file))
        wget.download(curr_url, curr_file)

@typechecked
def writable_folder(folder_path: str) -> pathlib.Path:
    folder_path = pathlib.Path(folder_path).resolve()
    if not folder_path.exists():
        folder_path.mkdir(parents = True)
    elif not folder_path.is_dir():
        raise NotADirectoryError(str(folder_path))
    return folder_path

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-dest',
        help = 'Folder to contain the raw',
        type = writable_folder,
        required = True)
    args = parser.parse_args()
    print(f'folder in: {args.dest}')
    download_oas(args.dest)
