import csv
import pathlib
import typing as t
from ..dtypes import Article, Extractor, ProcessError
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
        articles = utils.extract_articles(docs, fields, self._log_bad_extract)
        articles = Metadata._stream_csv(self._settings.dest, field_names, articles)
        for _ in articles: pass

    def _log_bad_extract(self, error: ProcessError) -> None:
        if self._settings.log is None:
            print(f"Error: {','.join(error.issues)}")
        else:
            utils.write_log(self._settings.log, error)
    
    @staticmethod
    def _field_selection() -> t.Dict[str, Extractor]:
        fields = {}
        fields['id'] = utils.extract_id
        fields['journal'] = utils.extract_journal
        fields['volume'] = utils.extract_volume
        fields['issue'] = utils.extract_issue
        fields['year'] = utils.extract_year
        fields['category'] = utils.extract_category
        fields['doi'] = utils.extract_doi
        fields['issn'] = utils.extract_issn
        fields['authors'] = utils.extract_authors
        fields['title'] = utils.extract_title
        fields['references'] = utils.extract_references
        return fields

    @staticmethod
    def _stream_csv(dest: pathlib.Path, fields: t.List[str], articles: t.Iterator[Article]) -> t.Iterator[Article]:
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
