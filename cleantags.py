# -*- coding: utf-8 -*-
"""\
Utilities to clean the *quantity* column.
"""

# Standard library:
import re
import typing as t
import unicodedata


def remove_accents(text: str) -> str:
    """\
    DOCME
    """
    normalized = unicodedata.normalize('NFKD', text)
    return "".join(c for c in normalized if not unicodedata.combining(c))


def replace_punctuation(text: str, by: str) -> str:
    """\
    DOCME
    """
    return "".join(by if unicodedata.category(c).startswith('P') else c for c in text)


def normalize_tag(tag: str) -> str:
    """\
    DOCME
    """
    replaced = replace_punctuation(tag, by=' ') 
    return '-'.join(remove_accents(word) for word in replaced.lower().split())


def split_lang2(tag: str, default='') -> t.Tuple[str, str]:
    """\
    DOCME
    """
    m = re.match(r'(?P<lang2>[a-z]{2})\:(?P<tag>.*)', tag)
    if m:
        return m.group('lang2'), m.group('tag')
    else:
        return default, tag
    

def _to_tags(text: str) -> str:
    """\
    DOCME
    """
    # Split and discard empty tags:
    tags = [tag.strip() for tag in text.split(',')]
    tags = [tag for tag in tags if tag != '']
    
    def clean(pair):
        lang2, tag = pair
        return lang2, normalize_tag(tag)
    
    # Use a set to remove duplicates:
    return sorted({clean(split_lang2(tag)) for tag in tags})


def to_tags(text:str, lang2_to_keep=None) -> str:
    """\
    DOCME
    """
    pairs = _to_tags(text)
    if lang2_to_keep is not None:
        pairs = [(lang2, tag) for lang2, tag in pairs if lang2 == lang2_to_keep]
    return ','.join(f'{lang2}:{tag}' if lang2 != '' else tag for lang2, tag in pairs)
