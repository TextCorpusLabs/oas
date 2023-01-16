import typing as t
from ..dtypes import Article, Extractor, ProcessError
from lxml import etree # type: ignore

def extract_articles(documents: t.Iterator[str], fields: t.Dict[str, Extractor], log: t.Callable[[ValueError], None]) -> t.Iterator[Article]:
    """
    Extracts an article's named fields from the string representation
    """
    for document in documents:
        try:
            yield _extract_article(document, fields)
        except ProcessError as error:
            log(error)


def _extract_article(document: str, fields: t.Dict[str, Extractor]) -> Article:
    try:
        root =  _parse_xml(document)
    except Exception as exception:
        raise ProcessError(document, ['Bad XML']) from exception
    article: Article = {}
    missing: t.List[str] = []
    for name, extractor in fields.items():
        try:
            article[name] = extractor(root)
        except:
            missing.append(name)
    if len(missing) > 0:
        raise ProcessError(document, [f'Missing {name}' for name in missing])
    return article

def _parse_xml(xml: str) -> etree.Element:
    """
    Most of the time the JATS XML will be missing the encoding declaration (<?xml version="1.0" encoding="UTF-8"?>).
    This is desirable as `etree.fromstring()` does not like it.
    When it is included, case it to bytes first then continue processing per https://stackoverflow.com/questions/57833080
    """
    try:
        return etree.fromstring(xml)
    except ValueError:
        return etree.fromstring(bytes(xml, encoding = 'utf-8'))
