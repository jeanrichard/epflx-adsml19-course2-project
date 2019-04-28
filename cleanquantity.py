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


def _make_conversion_table(valid_units):
    result = {}
    for target_unit, multiples in valid_units.items():
        for translations, conversion in multiples:
            for _, words in translations.items():
                for word in words:
                    result[word] = (target_unit, conversion)
    return result


CONVERSION_TABLE = _make_conversion_table(VALID_UNITS)


def standardize_quantity(values: pd.Series) -> t.Tuple[float, t.Optional[str]]:
    """\
    DOCME
    """                                                     
    number = values['number']
    unit = values['unit']
    
    # Lookup the unit and conversion function:
    pair = CONVERSION_TABLE.get(unit, None)
    if pair is None:
        return np.nan, None
    
    # Standardize:
    target_unit, conversion = pair
    return conversion(number), target_unit
