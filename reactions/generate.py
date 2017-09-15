import os
import csv
import pycorels
import numpy as np

base_all_out_file = "data/all.out"
expanded_all_out_file = "data/expanded.out"
train_out_file = "data/train.out"
test_out_file = "data/test.out"
#eout_file = data_dir + "expanded.out"

train_dir = "data/train/"
test_dir = "data/test/"
csv_dir = "data/clean_csv/"

min_accuracy = 0.95

maxnodes = [100, 1000, 10000, 100000, 1000000, 10000000]
cardinality = 2
min_support = 0.001
c = 0.01
gates = 2
map_type = 0

train_test_split = 120


def csplit(rules, indices):

    indices_or_sections = []
    out = []
    numsections = 0

    if not isinstance(indices, list):
        nsamples = len(rules[0][1])
        for i in range(1, indices):
            indices_or_sections.append(int(round(i * nsamples / indices)))

        numsections = indices;
    else:
        indices_or_sections = indices
        numsections = len(indices_or_sections) + 1

    for i in range(numsections):
        out.append([])

    #print(indices_or_sections)

    i = 0
    for rule in rules:
        splitlist = np.split(rule[1], indices_or_sections)

        j = 0
        for j in range(len(splitlist)):
            out[j].append((rule[0], splitlist[j]))

    return out

all_labels_dict = {}
train_labels_dict = {}
test_labels_dict = {}

out_written = False
for csv_file_path in os.listdir(csv_dir):
    p1_bit = csv_file_path[5:-4]

    if not out_written:
        outfp = open(base_all_out_file, "w")

    csvfp = open(csv_dir + csv_file_path, "r")

    reader = csv.DictReader(csvfp, delimiter=',')

    rules = {}
    label1 = []
    label0 = []

    sample_id = 0
    for row in reader:
        for features,sample_bit in row.items():
            if features[:6] == "p1_bit":
                label1.append(sample_bit)
            elif not out_written:
                if features not in rules:
                    rules[features] = []

                rules[features].append(sample_bit)

        sample_id = sample_id + 1


    if not out_written:
        for features,captured_vector in rules.items():
            line = "{" + features + "} "
            for bit in captured_vector:
                line += str(bit) + " "

            line += "\n"

            outfp.write(line)

        out_written = True

    for bit in label1:
        if bit == "1":
            label0.append(0)
        else:
            label0.append(1)

    all_labels_dict[p1_bit] =[("{" + p1_bit + "=0}", np.array(label0)), ("{" + p1_bit + "=1}", np.array(label1))]
    train_labels_dict[p1_bit],test_labels_dict[p1_bit] = csplit(all_labels_dict[p1_bit], [train_test_split])

    pycorels.tofile(train_labels_dict[p1_bit], train_dir + p1_bit + ".label")
    pycorels.tofile(test_labels_dict[p1_bit], test_dir + p1_bit + ".label")


    #print(labels_dict)

#if not os.path.isfile(expanded_all_out_file):
expanded_all_out_list = pycorels.fastmine(base_all_out_file, cardinality, min_support, gates)
pycorels.tofile(expanded_all_out_list, expanded_all_out_file)

#if not os.path.isfile(train_out_file) or not os.path.isfile(test_out_file):
train_out_list,test_out_list = csplit(expanded_all_out_list, [train_test_split])

#print(train_out_list)

pycorels.tofile(train_out_list, train_out_file)
pycorels.tofile(test_out_list, test_out_file)

for p1_bit,labels in train_labels_dict.items():
    log = train_dir + p1_bit + ".log"
    opt = train_dir + p1_bit + ".opt"
    for nnodes in maxnodes:
        a = pycorels.run(train_out_file, labels, c = c, max_num_nodes=nnodes, map_type = map_type, log_file=log, opt_file=opt, verbosity="log,progress")

        if a > min_accuracy:
            print("Accuracy: " + str(a))
            continue
