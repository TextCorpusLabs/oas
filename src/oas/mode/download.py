# type: ignore
import pathlib
import wget

def main(dest_folder: pathlib.Path) -> None:
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
