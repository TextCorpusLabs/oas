import typing as t
from ..dtypes import Extractor
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
        fields = Metadata._field_selection()
        field_names = [x for x in fields.keys()]
        source_files = (path for path in utils.list_folder_tar_balls(self._settings.source))
        doc_collections = (utils.list_documents(file) for file in source_files)
        docs = (x for y in doc_collections for x in y)
        docs = utils.progress_overlay(docs, 'Reading document #')
        articles = utils.extract_articles(docs, fields)
        articles = utils.stream_csv(self._settings.dest, field_names, articles)
        for _ in articles:
            pass
    
    @staticmethod
    def _field_selection() -> t.Dict[str, Extractor]:
        fields = {}
        fields['id'] = utils.extract_id
        return fields
