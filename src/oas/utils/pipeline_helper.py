import typing as t
from ..dtypes import Article, Extractor
from lxml import etree # type: ignore

def extract_articles(documents: t.Iterator[str], fields: t.Dict[str, Extractor], log: t.Callable[[str], None]) -> t.Iterator[Article]:
    """
    Extracts an article's named fields from the string representation
    """
    for document in documents:
        article = _extract_article_safe(document, fields, log)
        if article is not None:
            yield article

def _extract_article_safe(document: str, fields: t.Dict[str, Extractor], log: t.Callable[[str], None]) -> t.Optional[Article]:
    try:
        return _extract_article(document, fields)
    except:
        log(document)

def _extract_article(document: str, fields: t.Dict[str, Extractor]) -> t.Optional[Article]:
    root = _parse_xml(document)
    art: Article = {}
    for name, extractor in fields.items():
        art[name] = extractor(root)
    return art

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
