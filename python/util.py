import collections

def logging_itr(itr, step=500000):
    for i, x in enumerate(itr, 1):
        if i % step == 0:
            print 'Finished {} items'.format(i)
        yield x


class defaultdict(collections.defaultdict):
    __repr__ = dict.__repr__
