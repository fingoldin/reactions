import numpy as np
import mine

din = "data/clean_csv"
dout = "data/"
prefix = "all_"
max_cardinality = 1
min_support=0.02

for i in range(bits_per_vector):
    froot = "data_p1_bit" + str(i)

    mine.mine_binary(din=din, froot=froot,
                    max_cardinality=max_cardinality,
                    min_support=min_support, prefix=prefix)
