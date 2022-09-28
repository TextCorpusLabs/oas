import jsonlines as jl
import pathlib
import progressbar as pb
import typing as t
from lxml import etree

Article = t.Dict[str, t.Union[int, str, t.List[str]]]

def main(source: pathlib.Path, dest: pathlib.Path, dest_pattern: str, count: int) -> None:
    """
    Converts the PMC OAS folders to a JSONL file containing all the articles minus any markup.
    Articles that contain no body are removed.

    Parameters
    ----------
    source : pathlib.Path
        The root folder of the folders containing JATS files
    dest : pathlib.Path
        The folder to store the converted JSON files
    dest_pattern: str
        The format of the JSON file name
    count : int
        The number of JATS files in a single JSON file
    """
    article_paths = _collect_articles(source)
    articles = (_parse_article_safe(path) for path in article_paths)
    articles = _save_articles(dest, dest_pattern, count, articles)
    articles = _progress_bar(articles, int(count/100))
    for _ in articles: pass

def _collect_articles(folder_in: pathlib.Path) -> t.Iterator[str]:
    """
    Gets the full path of the article
    """
    for sub_folder in folder_in.iterdir():
        if sub_folder.is_dir():
            for file_name in sub_folder.iterdir():
                if file_name.is_file() and file_name.stem.upper().startswith('PMC') and file_name.suffix.upper() == '.XML':
                    yield str(file_name)

def _parse_article_safe(article: str) -> Article:
    try:
        return _parse_article(article)
    except:
        print(article)
        return {}

def _parse_article(article: str) -> Article:
    """
    Gets the parts of the JATS XML we care about
    """
    with open(article, 'r', encoding = 'utf-8') as fp:
        xml = fp.read()
    root = _parse_xml(xml)

    id = "./front/article-meta/article-id[@pub-id-type='pmc']"
    journal = "./front/journal-meta//journal-title"
    volume = "./front/article-meta/volume"
    issue = "./front/article-meta/issue"
    year = "./front/article-meta/pub-date/year/text()"
    category = "./front/article-meta/article-categories//subject"
    doi = "./front/article-meta/article-id[@pub-id-type='doi']"
    issn = './front/journal-meta/issn'
    authors = "./front/article-meta/contrib-group/contrib/name"
    title = "./front/article-meta/title-group/article-title//text()"
    abstract = ["./front/article-meta/abstract//p", "./front/article-meta/trans-abstract//p"]
    body = ["./body//sec/p", "./body/p"]
    references = "./back/ref-list/ref"    

    json = {}
    json['id'] = _nct(root.find(id))
    json['journal'] = _nct(root.find(journal))
    json['volume'] = _nct(root.find(volume))
    json['issue'] = _nct(root.find(issue))
    json['year'] = min(map(lambda year: int(year) , root.xpath(year)))
    json['category'] = _nct(root.find(category))
    json['doi'] = _nct(root.find(doi))
    json['issn'] = _ncs(';'.join(map(_nct, root.xpath(issn))))
    json['authors'] = _ncs(';'.join(map(_extract_author_name, root.xpath(authors))))
    json['title'] = _ncs(' '.join(''.join(root.xpath(title)).split()))
    json['abstract'] = _ncls(_extract_paragraphs(root, abstract))
    json['body'] = _ncls(_extract_paragraphs(root, body))
    json['referenceCounts'] = len(root.findall(references))

    json = { key: value for key, value in json.items() if value is not None }

    return json

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

def _save_articles(folder_out: pathlib.Path, pattern: str, count: int, articles: t.Iterator[Article]) -> None:
    """
    Writes the relevant data to disk
    """
    fp = None
    writer: jl.Writer = None
    fp_i = 0
    fp_articles = 0
    for article in articles:
        if fp is None:
            fp_name = folder_out.joinpath(pattern.format(id = fp_i))
            fp = open(fp_name, 'w', encoding = 'utf-8')
            writer = jl.Writer(fp, compact = True, sort_keys = True)
            fp_articles = 0
        if 'body' in article and len(article['body']) > 0:
            writer.write(article)
            fp_articles = fp_articles + 1
            yield article
        if fp_articles >= count:
            writer.close()
            fp.close()
            writer = None
            fp = None
            fp_i = fp_i + 1
    if fp is not None:
        writer.close()
        fp.close()

def _progress_bar(articles: t.Iterable[Article], update_freq: int) -> t.Iterator[Article]:
    bar_i = 0
    widgets = ['Processing Articles # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        for article in articles:
            bar_i = bar_i + 1
            if bar_i % update_freq == 0:
                bar.update(bar_i)
            yield article
        bar.update(bar_i)
