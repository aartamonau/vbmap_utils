#!/usr/bin/env python2

from simplejson import load
from itertools import chain

import pylab

def load_vbmap(path):
    with open(path) as f:
        return load(f)

def extract_masters(vbmap):
    transmap = zip(*vbmap['map'])
    return transmap[0]

def extract_replicas(vbmap):
    transmap = zip(*vbmap['map'])
    return transmap[1:]

def extract_nodes(vbmap):
    result = set()
    for chain in vbmap['map']:
        result.update(chain)

    return sorted(result)

def hist(chain, nodes):
    return [nodes[n] for n in chain]

def main():
    vbmap = load_vbmap('vbmap.json')

    masters = extract_masters(vbmap)
    replicas = extract_replicas(vbmap)

    nodes = extract_nodes(vbmap)
    nodes_count = len(nodes)

    nodes_dict = dict((n, i) for i, n in enumerate(nodes))

    pylab.figure()
    pylab.subplot(211)
    pylab.xticks([i + 0.5 for i in xrange(nodes_count)], nodes)

    plots = [hist(masters, nodes_dict)] + \
            [hist(r, nodes_dict) for r in replicas]
    labels = ['master'] + ['replica %d' % i for i in xrange(len(replicas))]

    pylab.hist(plots, bins=xrange(nodes_count + 1), label=labels)
    pylab.title("Histogram of number of vbuckets")
    pylab.xlabel("Nodes")
    pylab.ylabel("Number of vbuckets")
    pylab.legend()

    pylab.subplot(212)
    pylab.xticks([i + 0.5 for i in xrange(nodes_count)], nodes)

    all_replicas = list(chain(*replicas))
    pylab.hist(hist(all_replicas, nodes_dict), bins=xrange(nodes_count + 1),
               label='all replicas', rwidth=0.5)
    pylab.title("Histogram of number of replica vbuckets")
    pylab.xlabel("Nodes")
    pylab.ylabel("Number of vbuckets")
    pylab.legend()

    pylab.show()

if __name__ == '__main__':
    main()
