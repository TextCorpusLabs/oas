import typing as t
from ..dtypes import Article, Extractor, ProcessError
from ..dtypes import Convert as settings
from .. import utils
from io import TextIOWrapper

class Convert:

    _eos = "!?."
    _abbrev = ['al.', 'fig.', 'i.e.', 'e.g.']

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
        fields = Convert._field_selection()
        for path in utils.list_folder_tar_balls(self._settings.source):
            file_pattern = str(self._settings.dest.joinpath(self._settings.dest_pattern.replace("{source}", path.stem)))
            docs = utils.list_documents(path)
            docs = utils.progress_overlay(docs, f'{path.stem}: Reading documents #')
            articles = utils.extract_articles(docs, fields, self._log_bad_extract)
            Convert._flatten_and_save(file_pattern, self._settings.lines, articles)

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
        fields['title'] = utils.extract_title
        fields['abstract'] = utils.extract_abstract
        fields['body'] = utils.extract_body
        return fields

    @staticmethod
    def _flatten_and_save(file_pattern: str, count: int, articles: t.Iterator[Article]) -> None:
        fp: TextIOWrapper = None
        fp_i: int = 0
        fp_lines: int = 0
        for article in articles:
            if fp is None:
                file_name = file_pattern.format(id = fp_i)
                fp = open(file_name, 'w', encoding = 'utf-8')
                fp_i += 1
                fp_lines = 0
            lines = [line for line in Convert._flatten_article(article)]
            fp.writelines((f'{x}\n' for x in lines))
            fp_lines += len(lines) + 1
            if fp_lines >= count:
                fp.close()
                fp = None
            else:
                fp.writelines(['\n'])
        if fp is not None:
            fp.close()

    @staticmethod
    def _flatten_article(article: Article) -> t.Iterator[str]:
        yield f"--- {article['id']} ---"
        yield f"--- {article['journal']} ---"
        yield f"--- {article['title']} ---"
        yield ""
        if article['abstract'] is not None:
            for paragraph in article['abstract']:
                for sentence in Convert._split_sentences(paragraph):
                    yield sentence
                yield ""
        if article['body'] is not None:
            for paragraph in article['body']:
                for sentence in Convert._split_sentences(paragraph):
                    yield sentence
                yield ""

    @staticmethod
    def _split_sentences(text: str) -> t.Iterator[str]:
        words = text.split()
        st: int = 0
        for i in range(0, len(words)-1):
            if words[i][-1] in Convert._eos:
                if words[i] in Convert._abbrev:
                    continue
                if words[i+1][0].isupper() or words[i+1][0].isdigit():
                    yield ' '.join(words[st:(i+1)])
                    st = i + 1
        if st < len(words):
            yield ' '.join(words[st:len(text)])
