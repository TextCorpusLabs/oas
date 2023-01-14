import csv
import pathlib
import tarfile as tf
import typing as t
import uuid
from ..dtypes import Article

def list_folder_tar_balls(folder_in: pathlib.Path) -> t.Iterator[pathlib.Path]:
    """
    Lists the tar balls in the folder

    Parameters
    ----------
    folder_in : pathlib.Path
        The folder path containing the tar balls
    """
    def _is_tar_ball(file_path: pathlib.Path) -> bool:
        result = \
            file_path.is_file() and \
            file_path.suffix.lower() == '.tar' and \
            not file_path.stem.startswith('_')
        return result
    for file_name in folder_in.iterdir():
        if file_name.is_file():
            if _is_tar_ball(file_name):
                yield file_name

def list_documents(tarball: pathlib.Path) -> t.Iterator[str]:
    """
    Lists all the documents in the tar ball

    Parameters
    ----------
    tarball : pathlib.Path
        The the tar ball
    """
    def _is_pmc_file(info: tf.TarInfo) -> bool:
        if info.isfile():
            name = info.name.upper()
            return name.startswith('PMC') and name.endswith('.XML')
        return False
    with tf.open(tarball, 'r') as tar_ball:
        tar_info = tar_ball.next()
        while tar_info is not None:
            if _is_pmc_file(tar_info):
                tar_file = tar_ball.extractfile(tar_info)
                if tar_file is not None:
                    stream = tar_file.read()
                    document = stream.decode('utf-8')
                    yield document
            tar_info = tar_ball.next()

def stream_csv(dest: pathlib.Path, fields: t.List[str], articles: t.Iterator[Article]) -> t.Iterator[Article]:
    """
    Saves the documents to CSV
    
    Parameters
    ----------
    dest : pathlib.Path
        The CSV file containing all the documents
    fields : List[str]
        The name(s) of the elements to fields
    articles : Iterator[Article]
        The `Article`s to save
    """
    with open(dest, 'w', encoding = 'utf-8', newline = '') as fp:
        writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)    
        writer.writerow(fields)
        for article in articles:
            row = [None] * len(fields)
            for i in range(0, len(fields)):
                if fields[i] in article:
                    row[i] = article[fields[i]]
            writer.writerow(row)
            yield article

def write_log(log: pathlib.Path, message: str) -> None:
    """
    Writes out a message as a single file

    Parameters
    ----------
    log : pathlib.Path
        The folder of raw messages
    message : str
        The message itself
    """
    path = log.joinpath(f'PMC.{uuid.uuid4()}.xml')
    with open(path, 'w', encoding = 'utf-8', newline = '') as fp:
        fp.write(message)
