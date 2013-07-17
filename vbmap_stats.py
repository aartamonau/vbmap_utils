#!/usr/bin/env python2

import math

from simplejson import load
from itertools import chain
from random import shuffle

import pylab

def load_vbmap(path):
    with open(path) as f:
        return load(f)

def extract_masters(vbmap):
    transmap = zip(*vbmap)
    return transmap[0]

def extract_replicas(vbmap):
    transmap = zip(*vbmap)
    return transmap[1:]

def extract_nodes(vbmap):
    result = set()
    for chain in vbmap:
        result.update(chain)

    return sorted(result)

def extract_tags(vbmap, nodes):
    tags = vbmap['tags']
    return dict((n, tags[i]) for i, n in enumerate(sorted(nodes)))

def hist(chain, nodes):
    return [nodes[n] for n in chain]

def tag_replication_counts(vbmap, nodes, tags_list, tags):
    counts = []
    for tag in tags_list:
        tag_counts = []

        for i, node in enumerate(nodes):
            replicas = set()

            for chain in vbmap:
                if chain[0] != node:
                    continue

                replicas.update(r for r in chain[1:] if tags[r] == tag)

            tag_counts.append(len(replicas))

        counts.append(tag_counts)

    return counts

def promote_replicas(vbmap, node):
    result = []
    for chain in vbmap:
        new_chain = [n for n in chain if n != node]
        if len(new_chain) != len(chain):
            new_chain.append(-1)

        result.append(new_chain)

    return result

def simulate(vbmap):
    vbmap = vbmap['map']
    nodes = extract_nodes(vbmap)
    nodes_count = len(nodes)

    failures = nodes[:]
    shuffle(failures)
    failures = failures[1:]

    pylab.figure()

    charts_count = len(failures) + 1
    rows = cols = int(math.ceil(math.sqrt(charts_count)))

    def plot(vbmap, chart):
        pylab.subplot(rows, cols, chart)
        masters = [n for n in extract_masters(vbmap) if n != -1]

        pylab.xticks([i + 0.5 for i in xrange(nodes_count)], nodes)
        pylab.hist(masters, bins=xrange(nodes_count + 1))
        pylab.xlabel("Nodes")
        pylab.ylabel("Number of vbuckets")
        pylab.legend()

    chart = 1
    plot(vbmap, chart)
    chart += 1

    for node in failures:
        vbmap = promote_replicas(vbmap, node)
        plot(vbmap, chart)
        chart += 1

def main():
    vbmap = load_vbmap('vbmap.json')

    masters = extract_masters(vbmap['map'])
    replicas = extract_replicas(vbmap['map'])

    nodes = extract_nodes(vbmap['map'])
    nodes_count = len(nodes)

    nodes_dict = dict((n, i) for i, n in enumerate(nodes))

    tags = extract_tags(vbmap, nodes)
    tags_list = sorted(set(tags.values()))
    tags_count = len(tags_list)

    pylab.figure()
    pylab.subplot(211)
    pylab.xticks([i + 0.5 for i in xrange(nodes_count)], nodes)

    plots = [hist(masters, nodes_dict)] + \
            [hist(r, nodes_dict) for r in replicas]
    labels = ['master'] + ['replica %d' % i for i in xrange(len(replicas))]

    pylab.hist(plots, bins=xrange(nodes_count + 1), label=labels)
    pylab.title("Number of vbuckets per node")
    pylab.xlabel("Nodes")
    pylab.ylabel("Number of vbuckets")
    pylab.legend()

    pylab.subplot(212)
    pylab.xticks([i + 0.5 for i in xrange(nodes_count)], nodes)

    all_replicas = list(chain(*replicas))
    pylab.hist(hist(all_replicas, nodes_dict), bins=xrange(nodes_count + 1),
               label='all replicas', rwidth=0.5)
    pylab.title("Number of replica vbuckets per node")
    pylab.xlabel("Nodes")
    pylab.ylabel("Number of vbuckets")
    pylab.legend()

    pylab.figure()
    pylab.subplot(211)

    plots = [[tags[n] for n in masters]] + \
            [[tags[n] for n in r] for r in replicas]

    pylab.hist(plots, bins=xrange(tags_count + 1), label=labels)

    pylab.xticks([i + 0.5 for i in xrange(tags_count)], tags_list)
    pylab.title("Number of vbuckets per tag")
    pylab.xlabel("Tags")
    pylab.ylabel("Number of vbuckets")
    pylab.legend()

    pylab.subplot(212)
    pylab.xticks([i + 0.5 for i in xrange(nodes_count)], nodes)
    pylab.title("Number of nodes each node replicates to per tag")
    pylab.xlabel("Nodes")
    pylab.ylabel("Number of replica nodes")

    tags_repcounts = tag_replication_counts(vbmap['map'], nodes, tags_list, tags)

    plots = []
    for tag_counts in tags_repcounts:
        plot = []

        for node, count in enumerate(tag_counts):
            plot.extend([node] * count)
        plots.append(plot)

    pylab.hist(plots, bins=xrange(nodes_count + 1), label=map(str, tags))
    pylab.legend()

    simulate(vbmap)

    pylab.show()

if __name__ == '__main__':
    main()
