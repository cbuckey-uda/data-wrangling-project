#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re

from util import logging_itr

"""
Your task is to explore the data a bit more.
The first task is a fun one - find out how many unique users
have contributed to the map in this particular area!

The function process_map should return a set of unique user IDs ("uid")
"""

def get_user(element):
    return element.attrib.get('uid')


def process_map(filename):
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
