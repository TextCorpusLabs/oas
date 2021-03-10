import jsonlines as jl
import mp_boilerplate as mpb
import pathlib
import typing as t
from argparse import ArgumentParser
from lxml import etree
from typeguard import typechecked

@typechecked
def oas_to_jsonl(folder_in: pathlib.Path, jsonl_out: pathlib.Path, sub_process_count: int) -> None:
    """
    Converts the PMC OAS folders to a JSONL file containing all the articles minus any markup.
    Articles that contain no body are removed.

    Parameters
    ----------
    folder_in : pathlib.Path
        The root of the JATS folders
    jsonl_out : pathlib.Path
        JSONL containing all the wikimedia articles
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.EPTS(
        extract = _collect_articles, extract_args = (folder_in),
        transform = _parse_article_safe,
        save = _save_articles_to_jsonl, save_args = (jsonl_out),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _collect_articles(folder_in: pathlib.Path) -> t.Iterator[str]:
    """
    Gets the full path of the article
    """

    for sub_folder in folder_in.iterdir():
        if sub_folder.is_dir():
            for file_name in sub_folder.iterdir():
                if file_name.is_file() and file_name.stem.upper().startswith('PMC') and file_name.suffix.upper() == '.NXML':
                    yield str(file_name)

def _parse_article_safe(article: str) -> t.Dict[str, t.Union[int, str, t.List[str]]]:
    try:
        return _parse_article(article)
    except:
        print(article)
        return {}

@typechecked
def _parse_article(article: str) -> t.Dict[str, t.Union[int, str, t.List[str]]]:
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

    return _clean_dict(json)

@typechecked
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

@typechecked
def _save_articles_to_jsonl(results: t.Iterator[t.Dict[str, t.Union[int, str, t.List[str]]]], jsonl_out: pathlib.Path) -> None:
    """
    Writes the relevant data to disk
    """
    with open(jsonl_out, 'w', encoding = 'utf-8') as fp:
        with jl.Writer(fp, compact = True, sort_keys = True) as writer:
            for item in results:
                if 'body' in item and len(item['body']) > 0:
                    writer.write(item)

@typechecked
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

@typechecked
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

@typechecked
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

@typechecked
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

@typechecked
def _extract_paragraphs(root: etree.Element, xpaths: t.List[str]) -> t.List[str]:
    """
    Extracts paragraphs for the given xpath

    Parameters
    ----------
    root: etree.Element
        The document root
    xpaths: list[str]
        The list of posible locations
    """
    for xpath in xpaths:
        result = [x for x in map(lambda node: ''.join(node.xpath(".//text()")), root.xpath(xpath))]
        if len(result) > 0:
            return result
    return []

@typechecked
def _clean_dict(dict_: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    """
    Removes dictionary entries where item/value is any/None
    """
    result = {}
    for key,value in dict_.items():
        if value is not None:
            result[key] = value
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--folder-in',
        help = 'Folder containing the raw JATS files',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--jsonl-out',
        help = 'JSONL file containing all the articles',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()
    print(f'folder in: {args.folder_in}')
    print(f'jsonl out: {args.jsonl_out}')
    print(f'sub process count: {args.sub_process_count}')
    oas_to_jsonl(args.folder_in, args.jsonl_out, args.sub_process_count)
