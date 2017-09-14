import csv

in_data = open("data/raw_data.csv", "r")
out_data = open("data/clean_raw_data.csv", "w")

def clean(bitvector):
	return ''.join(i for i in bitvector if i == '0' or i == '1')

reader = csv.DictReader(in_data, delimiter=',')

out_data.write("id,r1_formulas,r2_formulas,p_formulas,p2_formulas,r1_fps,r2_fps,p1_fps,p2_fps\n")

writer = csv.writer(out_data, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_MINIMAL)

bits_per_vector = 881

for row in reader:
    row["r1_fps"] = clean(row["r1_fps"])
    assert(len(row["r1_fps"]) == bits_per_vector)
    row["r2_fps"] = clean(row["r2_fps"])
    assert(len(row["r2_fps"]) == bits_per_vector)
    row["p1_fps"] = clean(row["p1_fps"])
    assert(len(row["p1_fps"]) == bits_per_vector)
    row["p2_fps"] = clean(row["p2_fps"])
    assert(len(row["p2_fps"]) == bits_per_vector)

    out_row = []

    for key,val in row.items():
        out_row.append(val)

    writer.writerow(out_row)
