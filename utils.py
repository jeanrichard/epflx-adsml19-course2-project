# -*- coding: utf-8 -*-
"""\
Miscellaneous utilities.
"""

# Standard library:
import functools
import itertools
import json
import typing as t

# 3rd party:
import pandas as pd

ALL_COLS = ('display.max_columns', None)
ALL_ROWS = ('display.max_rows', None)
FULL_ENTRIES = ('display.max_colwidth', -1)


def display_with_options(*options: t.Sequence[t.Tuple[str, t.Any]]):
    """\
    Returns a function that Behaves like ``display`` but in a context where some options are set.
    
    Args:
        options: A sequence of ``(option, value)`` pairs.
        
    Returns:
        As described above.
    """
    list_ = list(itertools.chain(*options))
    
    @functools.wraps(display)  # nicer for interactive use
    def wrapper(*args, **kwargs):
        with pd.option_context(*list_):
            display(*args, **kwargs)
    
    return wrapper


def profile(df: pd.DataFrame) -> pd.DataFrame:
    """\
    Profiles the columns of a given data-frame.
    
    Args:
        df: The data-frame to profile.
        
    Returns:
        A data-frame with the same columns and the following rows:
        
        - ``Types``: Types and number of occurrences foudn the column.
        - ``NA``: Number of NA values in the column.
        - ``NA %``: Percentage of NA values in the column.
        - ``Non-NA``: Number of non-NA values in the column.
        - ``Non-NA %``: Percentage of non-NA values in the column.
    """
    
    def get_type_name(obj: t.Any) -> str:
        return type(obj).__name__
        
    types_ = [df[col].map(get_type_name).value_counts().to_dict() for col in df.columns]
    data = {
        'Types': types_,
        'NA': df.apply(lambda series: series.isna().sum()),
        'NA %': df.apply(lambda series: series.isna().mean() * 100.0),
        'Non-NA': df.apply(lambda series: series.notna().sum()),
        'Non-NA %': df.apply(lambda series: series.notna().mean() * 100.0)
    }
    return pd.DataFrame(data)


def dump_dtypes(base_name: str, data_types: t.Dict[str, str]) -> None:
    """\
    Dumps the data-types in a separate JSON file. The data-types can be obtained with
    ``df.dtypes.astype(str).to_dict()``.
    
    Args:
        base_name: The actual file-name will be ``{base_name}.dtypes.json``.
        data_types: The data-types of a data-frame.
    """
    with open(f'{base_name}.dtypes.json', 'w') as f:
        json.dump(data_types, f)


def load_dtypes(base_name: str) -> t.Dict[str, str]:
    """\
    Loads the data-types from a separate JSON file.
    
    Args:
        base_name: The actual file-name will be ``{base_name}.dtypes.json``.
        
    Returns:
        As described above.
    """
    with open(f'{base_name}.dtypes.json', 'r') as f:
        return json.load(f)


def amend_dtypes(data_types: t.Dict[str, str]) -> t.Tuple[t.Dict[str, str], t.List[str]]:
    """\
    Identifies those columns of type ``datetime64*``, replaces ``datetime64*`` by ``object``, and
    list those columns.
    
    Args:
        data_types: The data-types of a data-frame.
        
    Returns:
        The amended data-types and the list of those columns of type ``datetime64*``. 
    """
    amended = {}
    parse_dates = []
    for col_name, col_type in data_types.items():
        if col_type.startswith('datetime64'):
            parse_dates.append(col_name)
            amended[col_name] = 'object'
        else:
            amended[col_name] = col_type
    return amended, parse_dates


def load_and_amend_dtypes(base_name: str) -> t.Tuple[t.Dict[str, str], t.List[str]]:
    """\
    Convenience, equivalent to ``amend_dtypes(load_dtypes(base_name))``.
    """
    return amend_dtypes(load_dtypes(base_name))
