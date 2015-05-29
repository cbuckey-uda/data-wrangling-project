"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
import re
import pprint

from util import defaultdict, logging_itr

OSMFILE = "cincinnati_ohio.osm"
street_type_re = re.compile(r'^(.*\s)(\S+\.?)$', re.IGNORECASE)

class LimitedSet(set):
    def __init__(self, *args, **kwargs):
        n = None
        if 'n' in kwargs:
            n = kwargs['n']
            del[kwargs['n']]

        super(LimitedSet, self).__init__(*args, **kwargs)
        self.n = n

    def add(self, x):
        if self.n is None or len(self) < self.n:
            super(LimitedSet, self).add(x)


# expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
#             "Trail", "Parkway", "Commons"]
expected = []

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road"
            }

def split_street(street_name):
    m = street_type_re.search(street_name)
    if m:
        return m.group(1), m.group(2)
    else:
        return street_name, None


def get_street_type(street_name):
    _, street_type = split_street(street_name)
    if street_type is not None and street_type not in expected:
        return street_type
    else:
        return None

def get_street_name(elem):
    if elem.attrib.get('k') == 'addr:street':
        return elem.attrib['v']
    else:
        return None


def get_unexpected_street_types(osmfile):
    street_types = defaultdict(lambda: LimitedSet(n=5))
    for _, elem in logging_itr(ET.iterparse(osmfile)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                name = get_street_name(tag)
                if name is not None:
                    street_type = get_street_type(name)
                    if street_type is not None:
                        street_types[street_type].add(name)
        if elem.tag != 'tag':
            elem.clear()

    return street_types


def update_name(name, mapping):

    street_base, street_type = split_street(name)
    if street_type is not None and street_type in mapping:
        name = street_base + mapping[street_type]

    return name


def test():
    st_types = audit(OSMFILE)
    assert len(st_types) == 3
    pprint.pprint(st_types)

if __name__ == '__main__':
    st_types = get_unexpected_street_types(OSMFILE)
    pprint.pprint(st_types)

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            if name == "West Lexington St.":
                assert better_name == "West Lexington Street"
            if name == "Baldwin Rd.":
                assert better_name == "Baldwin Road"
