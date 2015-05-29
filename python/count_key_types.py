#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import regex

from collections import Counter
from util import logging_itr

"""
Your task is to explore the data a bit more.
Before you process the data and add it into MongoDB, you should
check the "k" value for each "<tag>" and see if they can be valid keys in MongoDB,
as well as see if there are any other potential problems.

We have provided you with 3 regular expressions to check for certain patterns
in the tags. As we saw in the quiz earlier, we would like to change the data model
and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with problematic characters.
Please complete the function 'key_type'.
"""


lower = regex.compile(ur'^[\p{Ll}_]*$')
alpha = regex.compile(ur'^[\p{L}_]*$')
word_plus_colon = regex.compile(ur'^[\w:]*$')
lower_colon = regex.compile(ur'^[\p{Ll}_]*:[\p{Ll}_:]*$')
problemchars = regex.compile(ur'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element):
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
    keys = Counter()
    for _, element in logging_itr(ET.iterparse(filename)):
        ktype = key_type(element)
        if ktype is not None:
            keys[ktype] += 1

    return keys

if __name__ == "__main__":
    keys = process_map('cincinnati_ohio.osm')
    pprint.pprint(keys.most_common())
