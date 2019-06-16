# -*- coding: utf-8 -*-
"""\
Utilities to clean the *quantity* column.
"""

# Standard library:
import re
import typing as t

# 3rd party:
import numpy as np
import pandas as pd

PATTERN_QUANTITY = re.compile(r'''
^
\s*
(?P<number>\d+(?:[.,]\d*)?)  # number
\s*
(?P<unit>[a-zA-Z]+)  # unit
''', re.VERBOSE)

# NOTE: Used Google for entries in Russian.
VALID_UNITS = {
    'g': [
        ({
            'en': ['gram', 'grams', 'g'],
            'fr': ['gramme', 'grammes', 'g'],
            'ru': ['грамм', 'грамма', 'г']
        }, lambda qty: qty),
        ({
            'en': ['kilogram', 'kilograms', 'kg'],
            'fr': ['killogramme', 'kilogrammes', 'kg'],
            'ru': ['килограмм', 'килограмма', 'кг']
        }, lambda qty: 1000.0 * qty)
    ],
    'l': [
        ({
            'en': ['milliliter', 'milliliters' 'ml'],
            'fr': ['millilitre', 'millilitres', 'ml'],
            'ru': ['миллилитр', 'миллилитра', 'мл']
        }, lambda vol: vol / 1000.0),
        ({
            'en': ['centiliter', 'centiliters', 'cl'],
            'fr': ['centilitre', 'centilitres', 'cl'],
            'ru': ['сантилитр', 'сантилитра', 'сл']
        }, lambda vol: vol / 100.0),
        ({
            'en': ['deciliter', 'deciliters', 'dl'],
            'fr': ['decilitre', 'decilitres', 'dl'],
            'ru': ['децилитр', 'децилитра', 'дл']
        }, lambda vol: vol / 10.0),
        ({
            'en': ['liter', 'liters', 'l'],
            'fr': ['litre', 'litres', 'l'],
            'ru': ['литр', 'литра', 'л']
        }, lambda vol: vol)
    ]
}


def _make_conversion_table(valid_units: t.Dict[str, t.Any]) -> t.Dict[str, t.Tuple[str, t.Callable[[float], float]]]:
    """\
    Builds the conversion table that maps the word for a given unit to a
    ``(target-unit, conversion-function)`` pair.
    
    Args:
        valid_units: A dictionary with the same structure as ``VALID_UNITS``.
    
    Returns:
        As described above.
    """
    result = {}
    for target_unit, multiples in valid_units.items():
        for translations, conversion in multiples:
            for _, words in translations.items():
                for word in words:
                    result[word] = (target_unit, conversion)
    return result


CONVERSION_TABLE = _make_conversion_table(VALID_UNITS)


def _standardize(values: pd.Series) -> t.Tuple[float, t.Optional[str]]:
    """\
    Converts all weights to gram and all volumes to liter.
    
    Args:
        values: A series with ``number`` and ``unit`` in the index.
    
    Returns:
        A ``(converted-number, unit)`` pair.
    """                                                     
    number = values['number']
    unit = values['unit']
    
    pair = CONVERSION_TABLE.get(unit, None)
    if pair is None:
        return np.nan, None
    
    target_unit, conversion = pair
    return conversion(number), target_unit


def clean(quantity: pd.Series) -> pd.DataFrame:
    """\
    Cleans a series of raw quantity strings.
    
    Args:
        quantity: The series to clean.
    
    Returns:
        A data-frame with columns ``number`` and ``unit``.
    """
    # Create a DataFrame with columns 'number' and 'unit':
    df_qty = quantity.str.extract(PATTERN_QUANTITY)

    # Convert numbers to 'float':
    df_qty['number'] = (
        df_qty['number']
        .str.replace(',', '.', regex=False)
        .map(lambda value: float(value))
    )

    # Convert units to lower case:
    df_qty['unit'] = (
        df_qty['unit']
        .str.lower()
    )

    # Standardize:
    df_qty = (
        df_qty[['number', 'unit']]
        .apply(_standardize, axis=1, result_type='expand')
        .rename(columns={0: 'number', 1: 'unit'})
    )
    
    return df_qty
