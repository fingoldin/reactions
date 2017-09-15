import csv
import os

data_dir = "data/general_outlabel/"

c = 0.01

for csv_file_path in os.listdir(data_dir):
    if not csv_file_path[-3:] == "log":
        continue

    csvfp = open(data_dir + csv_file_path, "r")

    reader = csv.DictReader(csvfp, delimiter=',')

    accuracy = 0.0

    for row in reader:
        acc = 1.0 - float(row["tree_min_objective"]) + c*float(row["tree_prefix_length"])
        if acc > accuracy:
            accuracy = acc

    print(csv_file_path + ":  " + str(accuracy))
