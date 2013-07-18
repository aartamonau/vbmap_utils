import sys
import pylab

from utils import load_vbmap, simulate_failovers

def imbalance(vbmap):
    counts = {}
    for chain in vbmap:
        master = chain[0]

        if master is None:
            continue

        counts.setdefault(master, 0)
        counts[master] += 1

    minimum = min(counts.values())
    maximum = max(counts.values())

    return maximum - minimum

def average(items):
    return sum(items) / len(items)

def main():
    paths = sys.argv[1:]

    stats = {}

    for path in paths:
        sys.stderr.write("processing %s\n" % path)
        initial_vbmap = load_vbmap(path)

        for i, vbmap in enumerate(simulate_failovers(initial_vbmap)):
            stats.setdefault(i, []).append(imbalance(vbmap))

    x = sorted(stats.keys())
    y = [average(stats[i]) for i in x]

    pylab.figure()
    pylab.xticks(x)
    pylab.title("Average imbalance after failovers")
    pylab.xlabel("Number of failed over nodes")
    pylab.ylabel("Average maximum imbalance")
    pylab.legend()

    pylab.plot(x, y)

    pylab.show()

if __name__ == '__main__':
    main()
