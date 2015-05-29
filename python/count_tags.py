#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the
tag name as the key and number of times this tag can be encountered in
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
import xml.etree.ElementTree as ET
import pprint
from collections import defaultdict

def logging_itr(itr, step=100000):
    for i, x in enumerate(itr, 1):
        if i % step == 0:
            print 'Finished {} items'.format(i)
            yield x

def count_tags(filename):
    counts = defaultdict(int)
    for event, elem in logging_itr(ET.iterparse(filename)):
        counts[elem.tag] += 1
        elem.clear()
    return dict(counts)

if __name__ == "__main__":
    tags = count_tags('cincinnati_ohio.osm')
    pprint.pprint(tags)
