import collections
import regex

lower = regex.compile(ur'^[\p{Ll}_]*$')
alpha = regex.compile(ur'^[\p{L}_]*$')
word_plus_colon = regex.compile(ur'^[\w:]*$')
lower_colon = regex.compile(ur'^[\p{Ll}_]*:[\p{Ll}_:]*$')
problemchars = regex.compile(ur'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

non_whitespace_re = regex.compile(ur'\S+')

def logging_itr(itr, step=500000):
    for i, x in enumerate(itr, 1):
        if i % step == 0:
            print 'Finished {} items'.format(i)
        yield x


class defaultdict(collections.defaultdict):
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
