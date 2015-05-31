#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re

from util import logging_itr

"""
This file finds the number of unique users who have contributed to this map.
"""

def get_user(element):
    '''
    Returns the user id associated with the given element.
    '''
    return element.attrib.get('uid')


def process_map(filename):
    '''
    Returns a set of all users who have contributed to the given file.
    '''
    users = set()
    for _, element in logging_itr(ET.iterparse(filename)):
        user_id = get_user(element)
        if user_id is not None:
            users.add(user_id)
        element.clear()

    return users

if __name__ == "__main__":
    users = process_map('cincinnati_ohio.osm')
    print '{} users contributed'.format(len(users))
