import typing as t
from ..dtypes import Article, Extractor
from lxml import etree # type: ignore

def extract_articles(documents: t.Iterator[str], fields: t.Dict[str, Extractor]) -> t.Iterator[Article]:
    """
    Extracts an article's named fields from the string representation
    """
    for document in documents:
        article = _extract_article(document, fields)
        if article is not None:
            yield article

def _extract_article(document: str, fields: t.Dict[str, Extractor]) -> t.Optional[Article]:
    root = _parse_xml_safe(document)
    if root is not None:
        art: Article = {}
        for name, extractor in fields.items():
            value = _extractor_safe(name, extractor, root)
            if value is not None:
                art[name] = value
        if len(art) > 0:
            return art

def _parse_xml_safe(document: str) -> t.Optional[etree.Element]:
    try:
        return _parse_xml(document)
    except:
        print(f'--- ERROR ---\nCould not parse document\n{document}')

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

def _extractor_safe(name: str, extractor: Extractor, root: etree.Element) -> t.Optional[t.Union[int, str, t.List[str]]]:
    try:
        return extractor(root)
    except:
        print(f'--- ERROR ---\nCould not extract {name}')
