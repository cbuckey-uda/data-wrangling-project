"""
This file audits the OSMFILE by checking whether there are any unexpected street
suffixes, or whether there are any street names which would change upon
normalization. In both cases, it prints examples of any possibly messy street
names.
"""
import xml.etree.cElementTree as ET
import regex
import pprint

from util import defaultdict, logging_itr, split_street, normalize_name, street_type_re

OSMFILE = "cincinnati_ohio.osm"

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]



def get_street_type(street_name):
    '''
    Gets the type or suffix from the given street name. For example,
    get_street_type('Washington Ave.') would return 'Ave.'
    '''
    _, street_type = split_street(street_name)
    if street_type is not None:
        return street_type
    else:
        return None

def get_street_name(elem):
    '''
    If the given element is a tag specifying a street name, returns the street
    name. Otherwise, returns None.
    '''
    if elem.attrib.get('k') == 'addr:street':
        return elem.attrib['v']
    else:
        return None


def get_street_name_and_type(elem):
    '''
    Returns a tuple (name, type) with the street name and type, if they exist,
    for the given element. First finds the tag that specifies the street name,
    then extracts the street type. If either name or type does not exist, that
    element of the tuple will be None.
    '''
    for tag in elem.iter("tag"):
        street_name = get_street_name(tag)
        if street_name is not None:
            street_type = get_street_type(street_name)
            if street_type is not None:
                return street_name, street_type
            else:
                return street_name, None

    return None, None

def audit(osmfile):
    '''
    Performs the auditing operations on the given file. Returns a tuple
    (street_types, unnormalized_street_names), where street_types is a
    dictionary mapping unexpected street types to example street names with that
    type, and unnormalized_street_names is a set of street names that are not in
    normalized form.
    '''
    street_types = defaultdict(set)
    unnormalized_street_names = set()

    for _, elem in logging_itr(ET.iterparse(osmfile)):
        if elem.tag == "node" or elem.tag == "way":
            street_name, street_type = get_street_name_and_type(elem)

            # Check for unexpected street types
            if street_type is not None and street_type not in expected:
                street_types[street_type].add(street_name)

            # Check for badly capitalized streets
            if street_name is not None and street_name != normalize_name(street_name):
                unnormalized_street_names.add(street_name)

        if elem.tag != 'tag':
            elem.clear()

    return street_types, unnormalized_street_names

if __name__ == '__main__':
    st_types, unnorm_sts = audit(OSMFILE)
    pprint.pprint(st_types)
    pprint.pprint(unnorm_sts)
