import pathlib

class Convert:

    def __init__(self, source: pathlib.Path, dest: pathlib.Path, count: int, dest_pattern: str, log: pathlib.Path):
        """
        Settings for convert process

        Parameters
        ----------
        source : pathlib.Path
            The folder containing the .tar'ed JATS files
        dest : pathlib.Path
            The folder for the converted TXT files
        count: int
            The number of articles per TXT file
        dest_pattern: str
            The format of the TXT file name.
        log: pathlib.Path
            The folder of raw JATS files that did not process
        """
        self._source = source
        self._dest = dest
        self._count = count
        self._dest_pattern = dest_pattern
        self._log = log

    @property
    def source(self) -> pathlib.Path:
        return self._source
    @property
    def dest(self) -> pathlib.Path:
        return self._dest
    @property
    def count(self) -> int:
        return self._count
    @property
    def dest_pattern(self) -> str:
        return self._dest_pattern
    @property
    def log(self) -> pathlib.Path:
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
        def _nonzero_int(val: int):
            if val <= 0:
                raise ValueError(f'{val} must be > 0')
        _folder(self._source)
        _folder(self._dest)
        _nonzero_int(self._count)
        if self._log is not None:
            _folder(self._log)
