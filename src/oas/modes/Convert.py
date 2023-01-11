from ..dtypes import Convert as settings

class Convert:

    def __init__(self, settings: settings):
        """
        Convert the data to our standard format.

        Parameters
        ----------
        settings : dtypes.settings.convert
            The settings for the process
        """
        self._settings = settings

    def init(self) -> None:
        self._settings.validate()

    def run(self) -> None:
        print('TODO: package conversion in progress.')
