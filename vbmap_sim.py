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

PERCENTILES = [20, 40, 60, 70, 80, 90, 95, 100]

def percentiles(items):
    n = len(items)
    items = sorted(items)

    return [items[int(round(p * n / 100.0)) - 1] for p in PERCENTILES]

def main():
    paths = sys.argv[1:]

    stats = {}

    for path in paths:
        sys.stderr.write("processing %s\n" % path)
        initial_vbmap = load_vbmap(path)

        for i, vbmap in enumerate(simulate_failovers(initial_vbmap)):
            stats.setdefault(i, []).append(imbalance(vbmap))

    x = sorted(stats.keys())

    pylab.figure()
    pylab.xticks(x)
    pylab.title("Average imbalance after failovers")
    pylab.xlabel("Number of failed over nodes")
    pylab.ylabel("Average maximum imbalance")

    percentiles_plots = zip(*[percentiles(stats[i]) for i in x])

    for p, plot in zip(PERCENTILES, percentiles_plots):
        pylab.plot(x, plot, label='%dth percentile' % p)
    pylab.plot(x, [average(stats[i]) for i in x], linewidth=3, label='average')

    pylab.legend()

    pylab.show()

if __name__ == '__main__':
    main()
