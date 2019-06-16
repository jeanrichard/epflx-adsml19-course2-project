# -*- coding: utf-8 -*-
"""\
Utilities to process the *ingredients_text* column.
"""

# Standard library:
import collections
import enum
import itertools
import re
import typing as t
import unicodedata

# 3rd party:
import pandas as pd


#
# Tokenization
#


class TokenType(enum.Enum):
    SPACE = enum.auto()
    DELIM = enum.auto()
    LPAR = enum.auto()
    RPAR = enum.auto()
    FIELD = enum.auto()
    END = enum.auto()
    INVALID = enum.auto()


# Common sets of characters:
DELIMS = re.escape(r'.,;•?')
LPARS = re.escape(r'([')
RPARS = re.escape(r')]')

# Patterns:
P_SPACE = re.compile(r'(?P<token>\s+)')  # a sequence of white spaces
P_DELIM = re.compile(fr'(?P<token>[{DELIMS}])')  # a delimiter
P_LPAR = re.compile(fr'(?P<token>[{LPARS}])')  # a l. parenthesis
P_RPAR = re.compile(fr'(?P<token>[{RPARS}])')  # a r. parenthesis
P_FIELD = re.compile(fr'''
    (?P<token>(?:
    [^{DELIMS}{LPARS}{RPARS}]   # not: a delimiter, a l. parenthesis, a r. parenthesis
    | (?<=\d)[\.\,](?=\d)       # delimiters '.,' are allowed if surrounded by digits
    )+)
    ''', re.VERBOSE)

# Tagged patterns:
PATTERNS = [
    (TokenType.SPACE, P_SPACE),
    (TokenType.DELIM, P_DELIM),
    (TokenType.LPAR, P_LPAR),
    (TokenType.RPAR, P_RPAR),
    (TokenType.FIELD, P_FIELD)
]

Token = collections.namedtuple('Token', ['type', 'text', 'pos'], verbose=False)


def panic(rest: str) -> t.Tuple[str, str]:
    """\
    Discards characters until one of the patterns matches.
    """
    buffer = []
    panic = True
    while rest != "" and panic:
        # Try each pattern in order:
        for token_type, pattern in PATTERNS:
            m = pattern.match(rest)
            if m:
                panic = False
                break
        else:
            buffer.append(rest[0])
            rest = rest[1:]
    return ''.join(buffer), rest


def tokenize_simple(text: str, peek_size: int = 1) -> t.Iterable[Token]:
    """\
    Splits ``text`` into a sequence of tokens. Tokens of type ``SPACE`` are immediately discarded.
    Additional tokens of type ``END`` are generated upon reaching the end of the input.
    """
    rest = text
    token_pos = 0
    while rest != "":
        # Try each pattern in order:
        for token_type, pattern in PATTERNS:
            m = pattern.match(rest)
            if m:
                token_text, rest = m.group('token'), rest[m.end():]
                # Implicitely discard tokens of type 'SPACE':
                if token_type != TokenType.SPACE:
                    yield Token(token_type, token_text, token_pos)
                break
        # No match:
        else:
            token_text, rest = panic(rest)
            yield Token(TokenType.INVALID, token_text, token_pos)
        token_pos += len(token_text)
    
    # End:
    for _ in range(peek_size):
        yield Token(TokenType.END, '$', token_pos)
        token_pos += 1


def tokenize_field(token: Token, delims: t.Sequence[str], p_delim: t.Pattern) -> t.Iterable[Token]:
    """\
    Further splits tokens of type ``FIELD`` on language-specific delimiters.
    """
    subtoken_texts = p_delim.split(token.text)
    subtoken_pos = token.pos
    for subtoken_text in subtoken_texts:
        if subtoken_text in delims:
            yield Token(TokenType.DELIM, subtoken_text, subtoken_pos)
        # Discard strings that are empty or contain only white spaces:
        else:
            original_text = subtoken_text
            stripped_text = original_text.lstrip()
            lcount = len(original_text) - len(stripped_text)
            original_text = stripped_text
            stripped_text = original_text.rstrip()
            if stripped_text:
                yield Token(TokenType.FIELD, stripped_text, subtoken_pos + lcount)
        subtoken_pos += len(subtoken_text)


def tokenize(text: str, delims: t.Sequence[str] = None, peek_size: int = 1) -> t.Iterable[Token]:
    """\
    Splits ``text`` into a sequence of tokens. Tokens of type ``SPACE`` are immediately discarded.
    An additional token of type ``END`` is generated upon reaching the end-of-input.
    """    
    if delims is None:
        yield from tokenize_simple(text, peek_size)
    else:
        # Compile the pattern once:
        p_delim_str = '|'.join(re.escape(delim) for delim in delims)
        p_delim = re.compile(fr'\b({p_delim_str})\b', re.IGNORECASE)
        for token in tokenize_simple(text, peek_size):
            if token.type == TokenType.FIELD:
                yield from tokenize_field(token, delims, p_delim)
            else:
                yield token

    
def remove_accents(text: str) -> str:
    """\
    Removes accents. 
    """
    # See e.g. https://unicodebook.readthedocs.io/unicode.html:
    normalized = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in normalized if not unicodedata.combining(c))


def replace_punctuation(text: str, repl=' ') -> str:
    """\
    Replaces punctuation marks by a single space.
    """
    # See e.g. https://unicodebook.readthedocs.io/unicode.html:
    return ''.join(c if not unicodedata.category(c).startswith('P') else repl for c in text)


#
# Normalization
#

P_NORM_WHITESPACE = re.compile(r'\s+')
P_NORM_NUMBER = re.compile(r'\b\d+(?:[\.\,]\d*)?\b')


def normalize_text(text: str) -> str:
    """\
    Performs the following steps:
    - Convert to lower-case
    - Remove numbers
    - Replace punctuation marks by a single space
    - Remove accents
    - Replace multiple white spaces by a single space
    - Strip leading and trailing white spaces
    """
    text = text.lower()
    # We do this before removing punctuation as it may help to find word boundaries:
    text = P_NORM_NUMBER.sub(' ', text)
    text = replace_punctuation(text)
    text = remove_accents(text)
    text = P_NORM_WHITESPACE.sub(' ', text)
    text = text.strip()
    return text

    
def normalize(tokens: t.Iterable[Token]) -> t.Iterable[Token]:
    for token in tokens:
        if token.type == TokenType.FIELD:
            text = normalize_text(token.text)
            if text:  # not empty
                yield Token(token.type, text, token.pos)
        else:
            yield token

            
def highlight(text: str, start: int, end: int, start_marker: str, end_marker: str) -> str:
    return f'{text[:start]}{start_marker}{text[start:end]}{end_marker}{text[end:]}'


def highglight_token(text: str, token: Token, start_marker: str, end_marker: str) -> str:
    return highlight(text, token.pos, token.pos + len(token.text), start_marker, end_marker)


#
# Utilities
#


# This is an old itertools recipe:
def window(seq: t.Iterable[t.Any], n=2) -> t.Iterable[t.Sequence[t.Any]]:
    """\
    Returns a sliding window (of width ``n``) over data from the iterable.
    For a sequence ``s``, the result will be ``(s0, s1, ..., s[n-1]), (s1, s2, ..., s[n]), ...``.
    """
    it = iter(seq)
    result = tuple(itertools.islice(it, n))
    if len(result) == n:
        yield result    
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def tokens_to_ingredients(tokens: t.Iterable[Token]) -> t.Iterable[t.Tuple[str, int]]:
    """\
    Allows to convert a sequence of tokens into a list of pairs (ingredient, is-composite).
    """
    # Peek 3 tokens ahead:
    for t1, t2, t3 in window(tokens, 3):
        if t1.type == TokenType.END:
            break
        # Implicitely discard tokens of a type other than 'FIELD':
        if t1.type == TokenType.FIELD:
            # Figure out if the ingredient is composite (see assumptions):
            is_composite = (t2.type == TokenType.LPAR and
                            t3.type == TokenType.FIELD)
            yield (t1.text, int(is_composite))


def text_to_ingredients(text: str, delims: t.Sequence[str]) -> t.Iterable[t.Tuple[str, int]]:
    """\
    Converts a single list of ingredients into a (single) lists of pairs 
    ``(normalized-ingredient, is-composite)``.
    """
    yield from tokens_to_ingredients(normalize(tokenize(text, delims, 3)))
    

def texts_to_ingredients(texts: t.Iterable[str], delims: t.Sequence[str]) -> t.Iterable[t.Tuple[str, int]]:
    """\
    Convert multiple lists of ingredients into a (single) list of pairs 
    ``(normalized-ingredient, is-composite)``.
    """
    for text in texts:
        yield from text_to_ingredients(text, delims)


def texts_to_ingredients_df(texts: pd.Series, delims: t.Sequence[str]) -> pd.DataFrame:
    """\
    Convert multiple lists of ingredients into a data-frame.
    """
    return pd.DataFrame.from_records(
        texts_to_ingredients(texts, delims), columns=['ingredient', 'is_composite'])


def reconcile_composite(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """\
    Takes care of ingredients that appear multiple times, sometimes marked as "simple" and sometime 
    marked as "composite".
    """
    # Compute count and mean:
    df_reconciled = (
        df
        .groupby(by='ingredient')
        .agg(['count', 'mean'])
        .rename(columns={'count': 'count', 'mean': 'composite_mean'})
    )
    # Get rid of the multi-index:
    df_reconciled.columns = df_reconciled.columns.get_level_values(1)
    # Reconcile:
    df_reconciled['is_composite'] = (df_reconciled['composite_mean'] > threshold)
    df_reconciled = df_reconciled.drop(columns=['composite_mean'])
    return df_reconciled
