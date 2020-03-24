from argparse import ArgumentParser
import pathlib
import sys
import wget

def download_oas(dest_folder):
    """
    Downloads all the files associated with PMC's OAS data dump
    Parameters
    ----------
    dest_folder : str
        The destination location to use when saving the files
    """

    dest_folder = pathlib.Path(dest_folder)
    dest_folder.mkdir(parents = True, exist_ok = True)

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

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-dest', '--dest-folder', help = 'Folder to contain the raw', required = True)
    args = parser.parse_args()
    print(f'folder in: {args.dest_folder}')
    download_oas(args.dest_folder)
