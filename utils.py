# -*- coding: utf-8 -*-
"""\
Miscellaneous utilities.
"""

# Standard library:
import json

# 3rd party:
import pandas as pd


def dump_dataframe(df: pd.DataFrame, rootname: str) -> None:
    data_types = df.dtypes.astype(str).to_dict()
    with open(f'{rootname}.dtypes.json', 'w') as f:
        json.dump(data_types, f)
    df.to_csv(f'{rootname}.csv', index=False)


def load_dataframe(rootname: str) -> pd.DataFrame:
    data_types = None
    parse_dates=[]
    data_types2 = {}
    with open(f'{rootname}.dtypes.json', 'r') as f:
        data_types = json.load(f)
    for col_name, data_type in data_types.items():
        if data_type.startswith('datetime64'):
            parse_dates.append(col_name)
            data_types2[col_name] = 'object'
        else:
            data_types2[col_name] = data_type    
    df = pd.read_csv(
        f'{rootname}.csv',
        header=0,
        parse_dates=parse_dates,
        dtype=data_types2)
    return df
