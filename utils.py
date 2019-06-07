# -*- coding: utf-8 -*-
"""\
Miscellaneous utilities.
"""

# Standard library:
import json
import typing as t

# 3rd party:
import pandas as pd


def dump_dtypes(base_name: str, data_types: t.Dict[str, str]) -> None:
    with open(f'{base_name}.dtypes.json', 'w') as f:
        json.dump(data_types, f)


def load_dtypes(base_name: str) -> t.Dict[str, str]:
    with open(f'{base_name}.dtypes.json', 'r') as f:
        return json.load(f)

    
def amend_dtypes(data_types: t.Dict[str, str]) -> t.Tuple[t.Dict[str, str], t.List[str]]:
    """\
    Identifies columns of type ``datetime64*``, replaces ``datetime64*`` by ``object``, and
    lists the names of these columns.
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
