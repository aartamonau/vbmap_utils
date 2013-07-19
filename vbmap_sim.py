import sys
import pylab

from os import path
from glob import glob
from optparse import OptionParser
from itertools import chain

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

def process_dataset(name, paths):
    samples = {}

    for path in paths:
        sys.stderr.write("processing %s\n" % path)

        initial_vbmap = load_vbmap(path)
        for i, vbmap in enumerate(simulate_failovers(initial_vbmap)):
            samples.setdefault(i, []).append(imbalance(vbmap))

    x = sorted(samples.keys())
    avrg = [average(samples[i]) for i in x]
    percs = zip(*[percentiles(samples[i]) for i in x])

    return (x, avrg, percs)

def plot(name, (x, average, percentiles), ymax):
    pylab.figure()
    pylab.ylim(ymax=ymax)
    pylab.xticks(x)
    pylab.title("Average imbalance after failovers (%s)" % name)
    pylab.xlabel("Number of failed over nodes")
    pylab.ylabel("Average maximum imbalance")

    for p, data in zip(PERCENTILES, percentiles):
        pylab.plot(x, data, label='%dth percentile' % p)

    pylab.plot(x, average, linewidth=3, label='average')
    pylab.legend(mode="expand", frameon=False, fontsize='x-small')

def main():
    parser = OptionParser()
    parser.add_option("-o", "--output-directory",
                      dest="output_directory", default=None)

    (options, args) = parser.parse_args()

    all_stats = {}
    ymax = 0

    for datapath in args:
        if not path.isdir(datapath):
            continue

        name = path.basename(path.normpath(datapath))
        paths = glob(path.join(datapath, "*"))

        _, average, percentiles = stats = process_dataset(name, paths)
        all_stats[name] = stats

        ymax = max(ymax, max(chain(average, *percentiles)))

    for name, stats in all_stats.items():
        plot(name, stats, ymax + 1)

        if options.output_directory is not None:
            filepath = path.join(options.output_directory, "%s.png" % name)
            pylab.savefig(filepath, dpi=250)
            sys.stderr.write("saved %s\n" % filepath)

    if options.output_directory is None:
        pylab.show()

if __name__ == '__main__':
    main()
