import pathlib
import typing as t

class Metadata:

    def __init__(self, source: pathlib.Path, dest: pathlib.Path, log: t.Optional[pathlib.Path]):
        """
        Settings for metadata process

        Parameters
        ----------
        source : pathlib.Path
            The folder containing the .tar'ed JATS files
        dest : pathlib.Path
            The CSV file used to store the metadata
        log: pathlib.Path
            The folder of raw JATS files that did not process
        """
        self._source = source
        self._dest = dest
        self._log = log

    @property
    def source(self) -> pathlib.Path:
        return self._source
    @property
    def dest(self) -> pathlib.Path:
        return self._dest
    @property
    def log(self) -> t.Optional[pathlib.Path]:
        return self._log

    def validate(self) -> None:
        """
        Ensures the settings have face validity
        """
        def _folder(path: pathlib.Path) -> None:
            if not path.exists():
                raise ValueError(f'{str(path)} is does not exist')
            if not path.is_dir():
                raise ValueError(f'{str(path)} is not a folder')
        _folder(self._source)
        _folder(self._dest.parent)
        if self._log is not None:
            _folder(self._log)

