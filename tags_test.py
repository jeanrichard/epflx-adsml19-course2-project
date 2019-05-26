# -*- coding: utf-8 -*-

# Standard library:
import textwrap

# Project:
import cleantags


def test_text_no_lang() -> None:
    # Arrange:
    given_readable = '''\
        Aliments et boissons à base de végétaux, 
        Boissons, 
        Aliments d'origine végétale, 
        Boissons chaudes, 
        Infusions, 
        Thés, 
        Thés noirs, 
        Boissons non sucrées, 
        Thés noirs aromatisés, 
        Thés aromatisés'''
    given_text = textwrap.dedent(given_readable).replace('\n', '')
    
    expected_readable = '''\
        aliments-d-origine-vegetale,
        aliments-et-boissons-a-base-de-vegetaux,
        boissons,
        boissons-chaudes,
        boissons-non-sucrees,
        infusions,
        thes,
        thes-aromatises,
        thes-noirs,
        thes-noirs-aromatises'''
    expected_tags = textwrap.dedent(expected_readable).replace('\n', '')
    
    # Act:
    given_tags = cleantags.to_tags(given_text)
    
    # Assert:
    assert given_tags == expected_tags

    
def test_text_fr_duplicates() -> None:
    # Arrange:
    given_readable = '''\
        fr:Pâtes à tartiner aux noisettes et au cacao, 
        fr:Pâtes à tartiner aux noisettes et au cacao,
        en:Something else'''
    given_text = textwrap.dedent(given_readable).replace('\n', '')
    
    expected_readable = '''\
        fr:pates-a-tartiner-aux-noisettes-et-au-cacao'''
    expected_tags = textwrap.dedent(expected_readable).replace('\n', '')
    
    # Act:
    given_tags = cleantags.to_tags(given_text, 'fr')  # keep only 'fr'
    
    # Assert:
    assert given_tags == expected_tags
