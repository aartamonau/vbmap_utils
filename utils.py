from simplejson import load
from random import shuffle

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

def promote_replicas(vbmap, node):
    result = []
    for chain in vbmap:
        new_chain = [n for n in chain if n != node]
        if len(new_chain) != len(chain):
            new_chain.append(-1)

        result.append(new_chain)

    return result

def simulate_failovers(vbmap):
    vbmap = vbmap['map']
    nodes = extract_nodes(vbmap)
    nodes_count = len(nodes)

    failures = nodes[:]
    shuffle(failures)
    failures = failures[1:]

    vbmaps = [vbmap]
    for node in failures:
        vbmap = promote_replicas(vbmap, node)
        vbmaps.append(vbmap)

    return vbmaps
