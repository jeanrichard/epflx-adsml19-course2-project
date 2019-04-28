# -*- coding: utf-8 -*-

# Project:
import ean


def test_compute_check_digit():
    # Examples from the page on Wikipedia:
    assert ean.compute_check_digit("400638133393") == "1"
    assert ean.compute_check_digit("7351353") == "7"
    

def test_is_valid():
    # Examples from the page on Wikipedia:
    assert ean.is_valid("4006381333931")
    assert ean.is_valid("73513537")
