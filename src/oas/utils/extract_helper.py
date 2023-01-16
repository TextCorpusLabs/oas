import typing as t
from lxml import etree # type: ignore

def extract_id(root: etree.Element) -> t.Optional[str]:
    xpath = "./front/article-meta/article-id[@pub-id-type='pmc']"
    value = _nct(root.find(xpath))
    return value

def extract_journal(root: etree.Element) -> t.Optional[str]:
    xpath = "./front/journal-meta//journal-title"
    value = _nct(root.find(xpath))
    return value

def extract_volume(root: etree.Element) -> t.Optional[str]:
    xpath = "./front/article-meta/volume"
    value = _nct(root.find(xpath))
    return value

def extract_issue(root: etree.Element) -> t.Optional[str]:
    xpath = "./front/article-meta/issue"
    value = _nct(root.find(xpath))
    return value

def extract_category(root: etree.Element) -> t.Optional[str]:
    xpath = "./front/article-meta/article-categories//subject"
    value = _ncs(';'.join([x for x in map(_nct, root.xpath(xpath)) if x is not None]))
    return value

def extract_doi(root: etree.Element) -> t.Optional[str]:
    xpath = "./front/article-meta/article-id[@pub-id-type='doi']"
    value = _ncs(';'.join(map(_nct, root.xpath(xpath))))
    return value

def extract_year(root: etree.Element) -> t.Optional[int]:
    xpath = "./front/article-meta/pub-date/year/text()"
    value = min(map(lambda year: int(year) , root.xpath(xpath)))
    return value

def extract_issn(root: etree.Element) -> t.Optional[str]:
    xpath = './front/journal-meta/issn'
    value = _ncs(';'.join([x for x in map(_nct, root.xpath(xpath)) if x is not None]))
    return value

def extract_authors(root: etree.Element) -> t.Optional[str]:
    xpath = "./front/article-meta/contrib-group/contrib/name"
    value = _ncs(';'.join(map(_extract_author_name, root.xpath(xpath))))
    return value

def extract_title(root: etree.Element) -> t.Optional[str]:
    xpath = "./front/article-meta/title-group/article-title//text()"
    value = _ncs(' '.join(''.join(root.xpath(xpath)).split()))
    return value

def extract_abstract(root: etree.Element) -> t.Optional[t.List[str]]:
    xpaths = ["./front/article-meta/abstract//p", "./front/article-meta/trans-abstract//p"]
    value = _ncls(_extract_paragraphs(root, xpaths))
    return value

def extract_body(root: etree.Element) -> t.Optional[t.List[str]]:
    xpaths = ["./body//sec/p", "./body/p"]
    value = _ncls(_extract_paragraphs(root, xpaths))
    return value

def extract_references(root: etree.Element) -> t.Optional[int]:
    xpath = "./back/ref-list/ref"
    value = len(root.findall(xpath))
    return value

def _nct(obj: etree.Element) -> t.Optional[str]:
    """
    Simple null-conditional macro
    """
    if obj is None:
        return None
    elif obj.text is None:
        return None
    else:
        return obj.text.strip()

def _ncs(txt: t.Optional[str]) -> t.Optional[str]:
    """
    Simple null-conditional macro
    """
    if txt is None:
        return None
    else:
        txt = txt.strip()
        if len(txt) == 0:
            return None
        else:
            return txt

def _ncls(list_: t.Optional[t.List[str]]) -> t.Optional[t.List[str]]:
    """
    Simple null-conditional macro
    """
    if list_ is None:
        return None
    else:
        if len(list_) == 0:
            return None
        else:
            return list_

def _extract_author_name(node: etree.Element) -> str:
    """
    gets the author name in the expected format
    """
    given = node.xpath("./given-names/text()")
    sur = node.xpath("./surname/text()")
    given = next(iter(given or []), '')
    sur = next(iter(sur or []), '')
    full = '{given} {sur}'.format(given = given, sur = sur).strip()    
    return full if len(full) > 3 else '???'

def _extract_paragraphs(root: etree.Element, xpaths: t.List[str]) -> t.List[str]:
    """
    Extracts paragraphs for the given xpath

    Parameters
    ----------
    root: etree.Element
        The document root
    xpaths: list[str]
        The list of possible locations
    """
    for xpath in xpaths:
        result = [x for x in map(lambda node: ''.join(node.xpath(".//text()")), root.xpath(xpath))]
        if len(result) > 0:
            return result
    return []
