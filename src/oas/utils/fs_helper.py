import pathlib
import tarfile as tf
import typing as t


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
    with tf.open(tarball, 'r') as tar_ball:
        tar_info = tar_ball.next()
        while tar_info is not None:
            if tar_info.isfile():
                tar_file = tar_ball.extractfile(tar_info)
                if tar_file is not None:
                    stream = tar_file.read()
                    document = stream.decode('utf-8')
                    yield document
            tar_info = tar_ball.next()
