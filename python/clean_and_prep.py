#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import codecs
import json

from util import defaultdict, lower, lower_colon, problemchars, split_street, normalize_name

"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB.

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to
update the street names before you save them to JSON.

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings.
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""

with open('street_mapping.json') as f:
    STREET_MAPPING = json.load(f)

def update_name(name, mapping=STREET_MAPPING):
    name = normalize_name(name)

    street_base, street_type = split_street(name)
    if street_type is not None and street_type in mapping:
        name = street_base + mapping[street_type]

    return name

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
POS = [ "lat", "lon"]


def shape_element(element):
    if element.tag == "node" or element.tag == "way":
        node = defaultdict(dict)
        node['type'] = element.tag

        try:
            node['pos'] = [float(element.attrib[POS[0]]), float(element.attrib[POS[1]])]
        except KeyError:
            pass
        except ValueError:
            print 'Invalid lat or lon in {}'.format(element.attrib)

        for key, value in element.attrib.items():
            if key in CREATED:
                node['created'][key] = value
            elif key not in POS:
                node[key] = value

        for tag in element.iter('tag'):
            try:
                (k, v) = (tag.attrib['k'], tag.attrib['v'])
            except KeyError:
                print 'No k and v in attrib {}'.format(tag.attrib)
                continue
            if not problemchars.search(k):
                m = lower_colon.search(k)
                if m:
                    if m.group(1) == 'addr' and not lower_colon.match(m.group(2)):
                        node['address'][m.group(2)] = v
                else:
                    node[k] = v

        if element.tag == 'way':
            node = defaultdict(list, node)
            for nd in element.iter('nd'):
                if 'ref' in nd.attrib:
                    node['node_refs'].append(nd.attrib['ref'])

        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
            if element.tag != 'tag':
                element.clear()
    return data

if __name__ == "__main__":
    data = process_map('example.osm', True)
    pprint.pprint(data)
