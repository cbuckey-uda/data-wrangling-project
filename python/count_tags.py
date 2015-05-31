#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file counts how many of each tag is present in the given XML file.
"""
import xml.etree.cElementTree as ET
import pprint

from collections import defaultdict
from util import logging_itr

def count_tags(filename):
    '''
    Returns a dictionary mapping all tags present in the given file to the
    number of times they occur.
    '''
    counts = defaultdict(int)
    for event, elem in logging_itr(ET.iterparse(filename)):
        counts[elem.tag] += 1
        elem.clear()
    return dict(counts)

if __name__ == "__main__":
    tags = count_tags('cincinnati_ohio.osm')
    pprint.pprint(tags)
