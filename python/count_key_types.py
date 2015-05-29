#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re

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


lower = re.compile(r'^[a-z_]*$')
lower_colon = re.compile(r'^[a-z_]*:[a-z_]*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element):
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            return 'lower'
        elif lower_colon.search(element.attrib['k']):
            return 'lower_colon'
        elif problemchars.search(element.attrib['k']):
            return 'problem_chars'
        else:
            return 'other'

def process_map(filename):
    keys = Counter()
    for _, element in logging_itr(ET.iterparse(filename)):
        ktype = key_type(element)
        if ktype is not None:
            keys[key_type(element)] += 1

    return keys

if __name__ == "__main__":
    keys = process_map('cincinnati_ohio.osm')
    pprint.pprint(keys.most_common())
