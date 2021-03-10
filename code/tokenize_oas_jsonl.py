import pathlib
import jsonlines as jl
import mp_boilerplate as mpb
import typing as t
from argparse import ArgumentParser
from nltk.tokenize import word_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from typeguard import typechecked

punkt_param = PunktParameters()
punkt_param.abbrev_types = set(['al', 'fig', 'i.e', 'e.g'])
sent_tokenize = PunktSentenceTokenizer(punkt_param)

@typechecked
def tokenize_oas_jsonl(jsonl_in: pathlib.Path, jsonl_out: pathlib.Path, sub_process_count: int) -> None:
    """
    Tokenizes all the articles into the standard form: one sentence per line, paragraphs have a blank line between them.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the articles
    jsonl_out : pathlib.Path
        The JSONL containing all the articles after tokenization
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.EPTS(
        extract = _collect_articles, extract_args = (jsonl_in),
        transform = _tokenize_article,
        save = _save_articles_to_jsonl, save_args = (jsonl_out),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _collect_articles(jsonl_in: pathlib.Path) -> t.Iterator[t.Dict[str, t.Union[int, str, t.List[str]]]]:
    with open(jsonl_in, 'r', encoding = 'utf-8') as fp:
        with jl.Reader(fp) as reader:
            for item in reader:
                yield item

@typechecked
def _tokenize_article(article: t.Dict[str, t.Union[int, str, t.List[str]]]) -> t.Dict[str, t.Union[int, str, t.List[str]]]:
    json = {}
    json['id'] = article['id']

    if 'abstract' in article:
        lines = article['abstract']
        lines = [line for line in _tokenize_lines(lines)]
        json['abstract_tokenized'] = lines

    if 'body' in article:
        lines = article['body']
        lines = [line for line in _tokenize_lines(lines)]
        json['body_tokenized'] = lines

    return json

@typechecked
def _tokenize_lines(lines: t.List[str]) -> t.Iterator[str]:
    """
    Tokenizes all the lines into paragraphs/words using standard Punkt + Penn Treebank tokenizers
    Due to how OAS articles were extracted in the prior step, 1 line = 1 paragraph
    """

    for line in lines:
        line = line.strip()
        if line == '':
            yield ''
        else:
            sentences = sent_tokenize.tokenize(line)
            for sentence in sentences:
                words = word_tokenize(sentence)
                yield ' '.join(words)

@typechecked
def _save_articles_to_jsonl(results: t.Iterator[t.Dict[str, t.Union[int, str, t.List[str]]]], jsonl_out: pathlib.Path) -> None:
    """
    Writes the relevant data to disk
    """
    with open(jsonl_out, 'w', encoding = 'utf-8') as fp:
        with jl.Writer(fp, compact = True, sort_keys = True) as writer:
            for item in results:
                writer.write(item)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL containing all the articles',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--jsonl-out',
        help = 'The JSONL containing all the articles after tokenization',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()    
    print(f'jsonl in: {args.jsonl_in}')
    print(f'jsonl out: {args.jsonl_out}')
    print(f'sub process count: {args.sub_process_count}')
    tokenize_oas_jsonl(args.jsonl_in, args.jsonl_out, args.sub_process_count)
