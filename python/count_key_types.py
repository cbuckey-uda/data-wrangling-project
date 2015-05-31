#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint

from collections import Counter
from util import logging_itr, lower, alpha, word_plus_colon, lower_colon, problemchars

"""
This file verifies whether any keys will be problematic by classifying them into
various types and printing out the counts of each type.
"""



def key_type(element):
    '''
    If the given element is a tag, returns which of 6 types the key attribute
    belongs to:
      - lower: The key contains only lowercase letters and underscores.
      - lower_colon: The key contains only lowercase letters, underscores, and
        colons.
      - alpha_with_upper: The key contains only lettrs and underscores, and at
        least on letter is uppercase.
      - word_plus_colon: The key contains only word characters (letters,
        numbers, and underscores), plus colons, but does not fit into any of the
        above types.
      - problem_chars: The key contains at least one problematic character, such
        as a dot or a dollar sign.
      - other: Anything that does not fit into the above types.
    '''
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            return 'lower'
        elif lower_colon.search(element.attrib['k']):
            return 'lower_colon'
        elif alpha.search(element.attrib['k']):
            return 'alpha_with_upper'
        elif word_plus_colon.search(element.attrib['k']):
            return 'word_plus_colon'
        elif problemchars.search(element.attrib['k']):
            return 'problem_chars'
        else:
            print 'Unidentified type for key "{}"'.format(element.attrib['k'])
            return 'other'

def process_map(filename):
    '''
    Counts the number of keys belonging to each type (as determined by the
    function key_type) in the given input file.
    '''
    keys = Counter()
    for _, element in logging_itr(ET.iterparse(filename)):
        ktype = key_type(element)
        if ktype is not None:
            keys[ktype] += 1

    return keys

if __name__ == "__main__":
    keys = process_map('cincinnati_ohio.osm')
    pprint.pprint(keys.most_common())
