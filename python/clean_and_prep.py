#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import codecs
import json
import os.path

from util import (defaultdict, lower, lower_colon, problemchars, street_type_re,
                  split_street, normalize_name, logging_itr)

"""
This file performs various cleaning operations on the input OSM file, then
transforms its shape to be suitable for importing into MongoDb.

The cleaning operations done are:
    - Fix incorrect street types using the mapping found in street_mapping.json
    - Normalize any unnormalized street names by removing unnecessary whitespace
      and fixing capitalization

The shape tranformation includes the following:
- Only 2 types of top level tags are processed: "node" and "way". Others are dropped.
- all attributes of "node" and "way" are turned into regular key/value pairs, except:
    - attributes in the CREATED array are dded under a key "created"
    - attributes for latitude and longitude are added to a "pos" array, where
      the values are floats
- if second level tag "k" value starts with "addr:", it is added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":",
  it is process the same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag is ignored.

For example, the following XML data:
<way id="209809850" visible="true" version="1" changeset="15353317" uid="674454">
  <nd ref="2199822281"/>
  <nd ref="2199822390"/>
  <tag k="addr:housenumber" v="1412"/>
  <tag k="addr:street" v="West Lexington St"/>
  <tag k="addr:street:name" v="Lexington"/>
  <tag k="addr:street:prefix" v="West"/>
  <tag k="addr:street:type" v="Street"/>
 </way>

would be transformed into the following JSON object:
{
  "id": "209809850"
  "visible": "true",
  "node_refs": ["2199822281", "2199822390"],
  "created": {
    "version": "1",
    "changeset": "15353317",
    "uid": "674454",
  },
  "address": {
    "housenumber": "1412"
    "street": "West Lexington Street",
  },
  "type": "way",
}
"""

with open('street_mapping.json') as f:
    STREET_MAPPING = json.load(f)

def update_name(name, mapping=STREET_MAPPING):
    '''
    Cleans the given street name by replacing any suffix as specified by the
    given mapping, removing excess whitespace, and fixing capitalization.
    '''
    name = normalize_name(name)

    street_base, street_type = split_street(name)
    if street_type is not None and street_type in mapping:
        name = street_base + mapping[street_type]

    return name

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
POS = [ "lat", "lon"]

def get_pos(element):
    '''
    Extracts the lat and lon from the given element and returns them as an
    array. If there is no lat or lon, returns None.
    '''
    lat, lon = POS
    try:
        return [float(element.attrib[lat]), float(element.attrib[lon])]
    except KeyError:
        return None
    except ValueError:
        print 'Invalid lat or lon in {}'.format(element.attrib)
        return None

def get_created(element):
    '''
    Returns the created dictionary for the given element.
    '''
    return {key: element.attrib[key] for key in CREATED if key in element.attrib}

def parse_attrib(element):
    '''
    Parses the attributes of the given element, and returns a node dictionary
    including a pos array rather than lat and lon elements and a nested created
    dictionary if appropriate.
    '''
    node = {k: v for k, v in element.attrib.items() if k not in CREATED and k not in POS}

    # Parse position
    pos = get_pos(element)
    if pos is not None:
        node['pos'] = pos

    # Parse created information
    created = get_created(element)
    if created:
        node['created'] = created

    return node

def parse_tags(tags):
    '''
    Parses the given tag elements and returns a node dictionary. Includes a nested
    address dictionary if appropriate.
    '''
    node = defaultdict(dict)
    for tag in tags:
        k, v = tag.attrib['k'], tag.attrib['v']
        m = lower_colon.search(k)
        if m:
            if m.group(1) == 'addr' and not lower_colon.match(m.group(2)):
                node['address'][m.group(2)] = v
        else:
            node[k] = v

    return dict(node)


def parse_nds(nds):
    '''
    Parses the given nd elements and returns a node dictionary contaning a
    node_refs array if there are any refs.
    '''
    node = defaultdict(list)
    for nd in nds:
        if 'ref' in nd.attrib:
            node['node_refs'].append(nd.attrib['ref'])
    return dict(node)

def fix_street_name(node):
    '''
    Updates the street name in the given node using the update_name function.
    '''
    street_name = node.get('address', {}).get('street')
    if street_name is not None:
        node['address']['street'] = update_name(street_name)


def shape_element(element):
    '''
    Turns the given element into a dictionary, transformed and cleaned as
    described in the file docstring.
    '''
    if element.tag == "node" or element.tag == "way":
        node = {'type': element.tag}

        node.update(parse_attrib(element))
        node.update(parse_tags(element.iter('tag')))
        node.update(parse_nds(element.iter('nd')))

        fix_street_name(node)

        return node
    else:
        return None


def basename(filename):
    '''
    Returns the basename of the given filename, without an extension.
    '''
    return os.path.splitext(filename)[0]


def process_map(file_in):
    '''
    Processes the given XML file as described in the file docstring. Writes
    output to a file with the same name, but a json extension.
    '''
    file_out = "{0}.json".format(basename(file_in))
    with codecs.open(file_out, "w") as fo:
        for _, element in logging_itr(ET.iterparse(file_in)):
            el = shape_element(element)
            if el:
                fo.write(json.dumps(el) + "\n")
            if element.tag not in ('tag', 'nd'):
                element.clear()

if __name__ == "__main__":
    process_map('cincinnati_ohio.osm')
