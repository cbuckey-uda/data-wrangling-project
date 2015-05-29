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
import regex
import pprint

from util import defaultdict, logging_itr

OSMFILE = "cincinnati_ohio.osm"
street_type_re = regex.compile(ur'^(.*\s)(\S+\.?)$', regex.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

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
    if street_type is not None:
        return street_type
    else:
        return None

def get_street_name(elem):
    if elem.attrib.get('k') == 'addr:street':
        return elem.attrib['v']
    else:
        return None


def get_street_name_and_type(elem):
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

non_whitespace_re = regex.compile(ur'\S+')
def normalize_name(name):
    '''
    Returns a version of the given name with normalized whitespace (no leading
    or trailing whitespace, and all other whitespace areas collapsed to one
    space) and each word is capitalized.
    '''
    def capitalize(s):
        '''
        Sets the first character of s to be uppercase. Differs from
        str.capitalize in that it does **not** set other letters to lowercase
        if they are not already.

        Does not change words with fewer than 4 characters.
        '''
        if len(s) >= 4:
            return s[0].upper() + s[1:]
        else:
            return s

    return ' '.join(map(capitalize, non_whitespace_re.findall(name)))


def update_name(name, mapping):
    street_base, street_type = split_street(name)
    if street_type is not None and street_type in mapping:
        name = street_base + mapping[street_type]

    return name

if __name__ == '__main__':
    st_types, unnorm_sts = audit(OSMFILE)
    pprint.pprint(st_types)
    pprint.pprint(unnorm_sts)
