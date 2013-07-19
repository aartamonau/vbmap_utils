import sys
import pylab

from os import path
from glob import glob
from optparse import OptionParser

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

def plot(name, (x, average, percentiles), output_dir):
    pylab.figure()
    pylab.xticks(x)
    pylab.title("Average imbalance after failovers (%s)" % name)
    pylab.xlabel("Number of failed over nodes")
    pylab.ylabel("Average maximum imbalance")

    for p, data in zip(PERCENTILES, percentiles):
        pylab.plot(x, data, label='%dth percentile' % p)

    pylab.plot(x, average, linewidth=3, label='average')
    pylab.legend(mode="expand", frameon=False, fontsize='x-small')

    if output_dir is not None:
        filepath = path.join(output_dir, "%s.png" % name)
        pylab.savefig(filepath, dpi=250)
        sys.stderr.write("saved %s\n" % filepath)

def main():
    parser = OptionParser()
    parser.add_option("-o", "--output-directory",
                      dest="output_directory", default=None)

    (options, args) = parser.parse_args()

    all_stats = {}

    for datapath in args:
        if not path.isdir(datapath):
            continue

        name = path.basename(path.normpath(datapath))
        paths = glob(path.join(datapath, "*"))

        all_stats[name] = process_dataset(name, paths)

    for name, stats in all_stats.items():
        plot(name, stats, options.output_directory)

    if options.output_directory is None:
        pylab.show()

if __name__ == '__main__':
    main()
