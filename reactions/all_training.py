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
    if fn[-5:] == "label":
        log = data_dir + fn[:-6] + ".log"
        opt = data_dir + fn[:-6] + ".opt"
        if not os.path.isfile(log) or not os.path.isfile(opt):
        	pycorels.run(l, data_dir + fn, c = c, max_num_nodes=maxnodes, log_file=log, opt_file=opt, verbosity="log,label,progress")
