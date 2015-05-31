'''
A utility file containing functions used by more than one script.
'''

import collections
import regex

# These are regexes used to classify key types and clean street names.
lower = regex.compile(ur'^[\p{Ll}_]*$')
alpha = regex.compile(ur'^[\p{L}_]*$')
word_plus_colon = regex.compile(ur'^[\w:]*$')
lower_colon = regex.compile(ur'^([\p{Ll}_]*):([\p{Ll}_:]*)$')
problemchars = regex.compile(ur'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = regex.compile(ur'^(.*\s)(\S+\.?)$', regex.IGNORECASE)
non_whitespace_re = regex.compile(ur'\S+')

def logging_itr(itr, step=500000):
    '''
    Generates a iterable identical to the given itr, but for every "step"
    elements, a message is logged.
    '''
    for i, x in enumerate(itr, 1):
        if i % step == 0:
            print 'Finished {} items'.format(i)
        yield x


class defaultdict(collections.defaultdict):
    '''
    A collections.defaultdict that can be pretty-printed.
    '''
    __repr__ = dict.__repr__

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

def split_street(street_name):
    '''
    Returns the street_name and street_type for the given street_name if they
    exist. If either does not exist, returns None.
    '''
    m = street_type_re.search(street_name)
    if m:
        return m.group(1), m.group(2)
    else:
        return street_name, None
