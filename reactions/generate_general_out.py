import pycorels
import csv
import os
import numpy as np

data_dir = "data/clean_csv/"
out_dir = "data/general_outlabel/"

out_written = False
out_path = out_dir + "general_p1_bit.out"

for csv_file_path in os.listdir(data_dir):
    p1_bit = csv_file_path[5:-4]

    label_path = out_dir + "general_" + p1_bit + ".label"
    if not out_written:
        outfp = open(out_path, "w")
    labelfp = open(label_path, "w")
    csvfp = open(data_dir + csv_file_path, "r")

    reader = csv.DictReader(csvfp, delimiter=',')

    rules = {}
    label = []

    sample_id = 0
    for row in reader:
        for features,sample_bit in row.items():
            if features[:6] == "p1_bit":
                label.append(sample_bit)
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

    #print("Generated " + out_path)

    line0 = "{" + p1_bit + "=0} "
    line1 = "{" + p1_bit + "=1} "

    for bit in label:
        if bit == '1':
            line0 += "0 "
        else:
            line0 += "1 "
        line1 += str(bit) + " "

    labelfp.write(line0 + "\n" + line1 + "\n")

    print("Generated " + label_path)
