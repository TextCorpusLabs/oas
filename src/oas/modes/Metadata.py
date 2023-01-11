from ..dtypes import Metadata as settings
from .. import utils

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
        if self._settings.dest.exists():
            self._settings.dest.unlink()

    def run(self) -> None:
        source_files = (path for path in utils.list_folder_tar_balls(self._settings.source))
        doc_collections = (utils.list_documents(file) for file in source_files)
        docs = (x for y in doc_collections for x in y)
        docs = utils.progress_overlay(docs, 'Reading document #')
        xxx = list(docs)
        
