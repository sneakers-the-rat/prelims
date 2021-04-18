import pypandoc
from pathlib import Path
import typing
import re

def jekyll_to_tex(
    path: typing.Union[Path, str], 
    output: typing.Optional[typing.Union[Path, str]]=None,
    document_class: str = "article",
    document_class_options:list= [],
    title: str = "",
    author: str = "",
    date:str = "\\today",
    load_packages: list = [],
    additional_calls: list = [()],
    toc:bool = True,
    domain: typing.Optional[str] = None,
    img_root: typing.Optional[str] = None,
    strip:typing.Optional[list]=None):

    path = Path(path)
    if output is not None:
        output = Path(output).with_suffix('.tex')

    text = pypandoc.convert_file(str(path), 'tex')

    # sort out frontmatter
    frontmatter = build_frontmatter(
        document_class, document_class_options, title, author, date,
        load_packages, additional_calls, toc)

    # ending
    ending = tex_call('end', 'document')

    text = '\n'.join((frontmatter, text, ending))


    # text-wide alterations
    # fix cite calls
    text = re.compile(r'(?s)\\\{\\%[^\\]*cite\s*([^\s]*)\s*\\%\\\}').sub(r'\\cite{\1} ', text)
    # fix cites spearated with space not comma
    text = re.compile(r'(?s)(?<=\\cite\{)\s*(\S*)\s*([^\s]*)\s').sub(r'\1,\2', text)

    if domain is not None or img_root is not None:
        text = fix_relative_links(text, domain, img_root)

    if strip is not None:
        for to_strip in strip:
            text = re.compile(to_strip).sub('', text)

    if 'tufte' in document_class:
        text = re.compile(r'(?s)\\footnote').sub(r'\\sidenote', text)

    if output is not None:
        with open(output, 'w') as out_f:
            out_f.write(text)

    return text

def build_frontmatter(document_class: str = "article",
    document_class_options:list = [],
    title: str = "",
    author: str = "",
    date:str = "\\today",
    load_packages: list = [],
    additional_calls:list=[()],
    toc:bool = True):
    
    if len(document_class_options) == 0:
        doc_class = f"\\documentclass{{{document_class}}}\n"
    else:
        doc_class_opts = ', '.join(document_class_options)
        doc_class = f"\\documentclass[{doc_class_opts}]{{{document_class}}}\n"

    # add packages
    packs = '\n'.join([tex_call('usepackage', pack) for pack in load_packages])

    # declare title and author and date
    title =tex_call('title', title)
    author = tex_call('author', author)
    date = tex_call('date', date)

    # add any other calls
    calls = '\n'.join([tex_call(call[0], call[1]) for call in additional_calls])

    begin = '\\begin{document}\n\\maketitle'

    toc_cmd = ""
    if toc:
        toc_cmd = "\\tableofcontents"

    # combine
    return '\n'.join((doc_class, packs, title, author, date, calls, begin, toc_cmd))







def tex_call(function, argument=None):
    if argument is None:
        return f"\\{function}"
    else:
        return f"\\{function}{{{argument}}}"




def fix_relative_links(text, href=None, includegraphics=None):
    # fix \href{/link}
    if href is not None:
        text = re.compile(r'(?<=\\href\{)(/[^}]*)').sub(fr'{href}\1', text)
    # and \includegraphics{/link}
    if includegraphics is not None:
        text = re.compile(r'(?<=\\includegraphics\{)(/[^}]*)').sub(fr'{includegraphics}\1', text)
    return text




if __name__ == "__main__":
    in_fn = Path('../markdown/2021-03-07-Distributed-Systems-Neuro-Infrastructure.markdown').absolute()
    out_fn = Path('../tex/infrastructure/distributed_infrastructure_autorender.tex').absolute()

    print(f'Converting {in_fn} to .tex...')
    document_class = 'article'

    if document_class == "tufte-book-jls":
        text = jekyll_to_tex(
            in_fn,
            document_class= document_class,
            document_class_options=['nohyper'],
            title = "Distributed Infrastructure For Systems Neuroscience Would Revolutionize The Discipline",
            author = "Jonny L. Saunders",
            date = "\\today",
            load_packages = [],
            additional_calls= [('addbibresource', '/Users/jonny/git/sneakers-the-rat.github.io/_preblog/assets/blog.bib')],
            toc = True,
            domain = 'https://jon-e.net',
            strip=(
                r'\\tightlist',
                r'(?s)\\footnote\{\\begin\{quote\}\n\s*\\ldots.*neuroscientists\}',
                r'(?s)\\footnote\{\\begin\{quote\}\n\s*"Among the.*\\end\{quote\}\}'))
    elif document_class=='article':
        text = jekyll_to_tex(
            in_fn,
            document_class= document_class,
            title = "Distributed Infrastructure For Systems Neuroscience Would Revolutionize The Discipline",
            author = "Jonny L. Saunders",
            date = "\\today",
            load_packages = ['jls_base'],
            additional_calls= [('addbibresource', '/Users/jonny/git/sneakers-the-rat.github.io/_preblog/assets/blog.bib')],
            toc = True,
            domain = 'https://jon-e.net',
            strip=(
                r'\\tightlist',
                r'(?s)\\footnote\{\\begin\{quote\}\n\s*\\ldots.*neuroscientists\}',
                r'(?s)\\footnote\{\\begin\{quote\}\n\s*"Among the.*\\end\{quote\}\}'))



    text = re.compile(r'(?<=\\includegraphics\{)/blog([^}]*)').sub(fr'{"/Users/jonny/git/sneakers-the-rat.github.io/_preblog"}\1', text)
    text = re.compile(r'\\begin\{quote\}').sub(r'\\begin{leftbar}', text)
    text = re.compile(r'\\end\{quote\}').sub(r'\\end{leftbar}', text)
    text = re.compile(r'(?<=\\includegraphics)(\{[^}]*})').sub(r'[width=\\linewidth]\1', text)
    
    with open(out_fn, 'w') as out_f:
        out_f.write(text)

    print(f'Wrote tex to {out_fn}')


