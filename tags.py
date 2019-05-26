# -*- coding: utf-8 -*-
"""\
Utilities to clean the *quantity* column.
"""

# Standard library:
import collections
import typing as t

# 3rd party:
import pandas as pd


def _split_tag(tag: str, default_prefix='') -> t.Tuple[str, str]:
    """\
    Splits a tag into a pair ``(prefix, value)``.
    """
    try:
        idx = tag.index(':')
        return tag[:idx], tag[idx+1:]
    except ValueError:
        return default_prefix, tag


def _to_tags(text: str) -> t.Set[t.Tuple[str, str]]:
    """\
    DOCME
    """
    # Split:
    tags = [tag.strip() for tag in text.split(',')]
    # Discard empty tags:
    tags = [tag for tag in tags if tag != '']
    # Use a set to remove duplicates:
    return {_split_tag(tag) for tag in tags}


def clean_tags(text:str) -> str:
    """\
    DOCME
    """
    if pd.isna(text):
        return text
    
    pairs = _to_tags(text)
    # Sort:
    pairs = sorted(pairs)
    # Discard tags with prefixes which are not 2-letter long:
    pairs = [(prefix, value) for prefix, value in pairs if len(prefix) in (0, 2)]
    # Convert back into a string:
    return ','.join(f'{prefix}:{value}' if prefix != '' else f'{value}' for prefix, value in pairs)
