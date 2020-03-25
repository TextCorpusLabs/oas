from argparse import ArgumentParser
from collections import namedtuple
from lxml import etree
import csv
import pathlib
import progressbar as pb

# declare all the named tuples up front
JATS = namedtuple('JATS', 'id doi issn journal volume issue year category referenceCount title authors')

def extract_metadata(folder_in, file_out):
    """
    Operates over the given `folder_in` finding all the JATS files and pulling out the metadata of concern.
    """
    folder_in = pathlib.Path(folder_in)
    file_out = pathlib.Path(file_out)
    errors_out = file_out.parent.joinpath('./errors.metadata.csv')
    ensure_path(file_out)
    ensure_path(errors_out)
    errors = []
    i = 1
    widgets = [ 'Extracting metadata from file # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        with file_out.open('w', encoding = 'utf-8', newline='') as file_out:
            writer = csv.writer(file_out, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
            writer.writerow(['id', 'doi', 'issn', 'journal', 'volume', 'issue', 'year', 'category', 'referenceCount', 'title', 'authors'])
            for file_name in folder_in.iterdir():
                if file_name.is_file() and file_name.suffix.lower() == '.nxml':
                    bar.update(i)
                    i = i + 1
                    try:
                        jats = parse_jats(file_name)
                        writer.writerow([jats.id, jats.doi, jats.issn, jats.journal, jats.volume, jats.issue, jats.year, jats.category, jats.referenceCount, jats.title, jats.authors])
                    except Exception as ex:
                        errors.append([file_name.stem, str(ex)])
    write_errors(errors_out, errors)

def ensure_path(file_out):
    """
    Makes sure the path for the csv file is available
    """
    file_out.parent.mkdir(parents = True, exist_ok = True)
    if file_out.exists():
         file_out.unlink()

def parse_jats(file_name):
    """
    Gets the parts of the JATS XML we care about
    """
    with file_name.open('r', encoding = 'utf-8') as file_name:
        xml = file_name.read()
    journal = "./front/journal-meta//journal-title"
    volume = "./front/article-meta/volume"
    issue = "./front/article-meta/issue"
    id = "./front/article-meta/article-id[@pub-id-type='pmc']"
    doi = "./front/article-meta/article-id[@pub-id-type='doi']"
    issn = './front/journal-meta/issn'
    year = "./front/article-meta/pub-date/year/text()"
    category = "./front/article-meta/article-categories//subject"
    references = "./back/ref-list/ref"
    title = "./front/article-meta/title-group/article-title//text()"
    authors = "./front/article-meta/contrib-group/contrib/name"
    root = etree.fromstring(xml)
    journal = nct(root.find(journal))
    volume = nct(root.find(volume))
    issue = nct(root.find(issue))
    id = nct(root.find(id))
    doi = nct(root.find(doi))
    issn = ';'.join(map(nct, root.xpath(issn)))
    year = min(map(lambda year: int(year) , root.xpath(year)))
    category = nct(root.find(category))
    references = root.findall(references)
    title = ' '.join(''.join(root.xpath(title)).split())
    authors = ';'.join(map(extract_author_name, root.xpath(authors)))
    return JATS(id, doi, issn, journal, volume, issue, year, category, len(references), title, authors)

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

def extract_author_name(node):
    """
    gets the author name in the expected format
    """
    given = node.xpath("./given-names/text()")
    sur = node.xpath("./surname/text()")

    given = next(iter(given or []), '')
    sur = next(iter(sur or []), '')

    full = '{given} {sur}'.format(given = given, sur = sur).strip()
    
    return full if len(full) > 3 else '???'

def write_errors(errors_out, errors):
    with errors_out.open('w', encoding = 'utf-8', newline='') as errors_out:
        writer = csv.writer(errors_out, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
        writer.writerow(['PMCID', 'exception'])
        for error in errors:
            writer.writerow(error)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-in', '--folder-in', help = 'Folder containing the raw JSON files', required = True)
    parser.add_argument('-out', '--file-out', help = 'File to contain the metadata', required = True)
    args = parser.parse_args()
    print(f'folder in: {args.folder_in}')
    print(f'file out: {args.file_out}')
    extract_metadata(args.folder_in, args.file_out)
