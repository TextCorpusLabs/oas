from argparse import ArgumentParser
from collections import namedtuple
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from shutil import rmtree
import csv
from lxml import etree
import pathlib
import progressbar as pb

punkt_param = PunktParameters()
punkt_param.abbrev_types = set(['al', 'fig', 'i.e', 'e.g'])
sent_tokenize = PunktSentenceTokenizer(punkt_param)

JATS = namedtuple('JATS', 'id abstract body')

def convert_folder_to_corpus(folder_in, folder_out):
    folder_in = pathlib.Path(folder_in)
    folder_out = pathlib.Path(folder_out)
    errors_out = folder_out.joinpath(f'./{folder_out.stem}.errors.csv')
    create_folder_structure(folder_out)
    errors = []
    i = 1
    widgets = [ 'Converting File # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        for file_name in folder_in.iterdir():
            if file_name.is_file() and file_name.suffix.lower() == '.nxml':
                bar.update(i)
                i = i + 1
                try:
                    article = parse_jats_article(file_name)
                    if article == None:
                        errors.append([file_name.stem, 'not full text'])
                    else:
                        write_article(folder_out, article)
                except Exception as ex:
                    errors.append([file_name.stem, str(ex)])
    write_errors(errors_out, errors)

def create_folder_structure(folder_out):
    if folder_out.exists():
        if folder_out.is_dir():
            rmtree(folder_out)
        else:
            folder_out.unlink()
    folder_out.mkdir(parents = True)
    folder_out.joinpath('./abstract').mkdir()
    folder_out.joinpath('./body').mkdir()

def parse_jats_article(file_name):
    """
    Gets the parts of the JATS XML we care about
    """
    with file_name.open('r', encoding = 'utf-8') as file_name:
        xml = file_name.read()
    root = etree.fromstring(xml)
    id = "./front/article-meta/article-id[@pub-id-type='pmc']"
    abstract = ["./front/article-meta/abstract//p", "./front/article-meta/trans-abstract//p"]
    body = ["./body//sec/p", "./body/p"]
    id = nct(root.find(id))
    abstract = extract_paragraphs(root, abstract)    
    abstract = convert_to_sentences(abstract)
    body = extract_paragraphs(root, body)
    body = convert_to_sentences(body)
    return JATS(id, abstract, body) if len(abstract) > 0 and len(body) > 0 else None

def nct(obj):
    """
    Simple null-conditional macro
    """
    if obj is None:
        return None
    elif obj.text is None:
        return None
    else:
        return obj.text.strip()

def extract_paragraphs(root, xpaths):
    for xpath in xpaths:
        result = [x for x in map(lambda node: ''.join(node.xpath(".//text()")), root.xpath(xpath))]
        if len(result) > 0:
            return result
    return []

def convert_to_sentences(paragraphs):
    result = [sent_tokenize.tokenize(paragraph) for paragraph in paragraphs]
    return result

def write_article(folder_out, article):
    write_article_part(folder_out.joinpath(f'./abstract/PMC{article.id}.txt'), article.abstract)
    write_article_part(folder_out.joinpath(f'./body/PMC{article.id}.txt'), article.body)

def write_article_part(file_out, paragraphs):
    first = True
    with file_out.open('w', encoding = 'utf-8') as file_out:
        for paragraph in paragraphs:
            if first:
                first = False
            else:
                file_out.write('\n')
            for sentence in paragraph:
                file_out.write(sentence)
                file_out.write('\n')

def write_errors(errors_out, errors):
    if errors_out.exists():
        errors_out.unlink()
    with errors_out.open('w', encoding = 'utf-8', newline='') as errors_out:
        writer = csv.writer(errors_out, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
        writer.writerow(['PMCID', 'exception'])
        for error in errors:
            writer.writerow(error)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-in', '--folder-in', help = 'Folder containing the raw JATS files', required = True)
    parser.add_argument('-out', '--folder-out', help = 'Folder containing the newly created text corpus', required = True)
    args = parser.parse_args()
    print(f'folder in: {args.folder_in}')
    print(f'folder out: {args.folder_out}')
    convert_folder_to_corpus(args.folder_in, args.folder_out)
    