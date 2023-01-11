from ..dtypes import Metadata as settings

class Metadata:

    def __init__(self, settings: settings):
        """
        Extracts the metadata from the corpus.

        Parameters
        ----------
        settings : dtypes.settings.metadata
            The settings for the process
        """
        self._settings = settings

    def init(self) -> None:
        self._settings.validate()

    def run(self) -> None:
        print('TODO: package conversion in progress.')
