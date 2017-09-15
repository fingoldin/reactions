import os
import pycorels

data_dir = "data/general_outlabel/"
bout_file = data_dir + "general_p1_bit.out"
#eout_file = data_dir + "expanded.out"

maxnodes = 1000000
cardinality = 2
min_support = 0.02
c = 0.01
gates = 2

l = pycorels.fastmine(bout_file, cardinality, min_support, gates)

for fn in os.listdir(data_dir):
    if fn[-5:] == "label": #and fn == "general_p1_bit18.label":
        pycorels.run(l, data_dir + fn, c = c, max_num_nodes=maxnodes, log_file=(data_dir + fn[:-6] + ".log"), verbosity="log")
