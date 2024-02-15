import argparse
import numpy
import json

parser = argparse.ArgumentParser(description='Client for Task 2')
parser.add_argument('--file', type=str,
                    help='file path of data')
parser.add_argument('--idx', type=int,
                    help='idx of client')
args = parser.parse_args()
data = numpy.genfromtxt(args.file, delimiter=',')
data = data[args.idx * 25000: (args.idx + 1) * 25000]
res_sum = numpy.sum(data)
res_ave = numpy.average(data)
res_max = numpy.max(data)
res_min = numpy.min(data)
res_std = numpy.std(data)
data = {
    "container index": args.idx,
    "sum": res_sum,
    "average": res_ave,
    "max": res_max,
    "min": res_min,
    "standard deviation": res_std
}
print(json.dumps(data))
