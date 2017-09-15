import csv
import copy

raw_data = "data/clean_raw_data.csv"

reader = csv.DictReader(open(raw_data), delimiter=',')

def clean(bitvector):
	return ''.join(i for i in bitvector if i == '0' or i == '1')

bits_per_vector = 881

useless_p1_bits = []

rows = []
for row in reader:
	rows.append(row)

useless0_r1 = []
useless1_r1 = []
useless0_r2 = []
useless1_r2 = []

useless_r1_bits = []
useless_r2_bits = []

for i in range(bits_per_vector):
	useless0_r1.append(True)
	useless1_r1.append(True)
	useless0_r2.append(True)
	useless1_r2.append(True)

for i in range(bits_per_vector):
	for row in rows:
		r1 = row["r1_fps"][i]
		if r1 == '0':
			useless1_r1[i] = False

		if r1 == '1':
			useless0_r1[i] = False

		r2 = row["r2_fps"][i]
		if r2 == '0':
			useless1_r2[i] = False

		if r2 == '1':
			useless0_r2[i] = False

	print("Checked bit " + str(i))

for i in range(bits_per_vector):
	if useless0_r1[i]:
		#print("r1 useless 0 (" + str(i) + ")")
		useless_r1_bits.append((0, i))
	elif useless1_r1[i]:
		print("r1 useless 1 (" + str(i) + ")")
		useless_r1_bits.append((1, i))

	if useless0_r2[i]:
		#print("r2 useless 0 (" + str(i) + ")")
		useless_r2_bits.append((0, i))
	elif useless1_r2[i]:
		print("r2 useless 1 (" + str(i) + ")")
		useless_r2_bits.append((1, i))

for row in rows:
	temp_r1 = ""
	temp_r2 = ""

	for i in range(bits_per_vector):
		if not (0, i) in useless_r1_bits and not (1, i) in useless_r1_bits:
			temp_r1 += row["r1_fps"][i]

		if not (0, i) in useless_r2_bits and not (1, i) in useless_r2_bits:
			temp_r2 += row["r2_fps"][i]

	row["r1_fps"] = temp_r1
	row["r2_fps"] = temp_r2

for i in range(bits_per_vector):
	count_ones = 0

	for row in rows:
		#print("p1_fps" + str(i) + ": " + clean(row["p1_fps"])[i])
		p1 = row["p1_fps"][i]
		if p1 == '0':
			useless1 = False
			if not useless0:
				break

		if p1 == '1':
			useless0 = False
			if not useless1:
				break

	if useless0:
		#print("p1 useless 0 (" + str(i) + ")")
		useless_p1_bits.append((0, i))
		continue

	if useless1:
		print("p1 useless 1 (" + str(i) + ")")
		useless_p1_bits.append((1, i))
		continue

	fname = "data/clean_csv/data_p1_bit" + str(i) + ".csv"
	file = open(fname, "w")
	writer = csv.writer(file, delimiter=',', quotechar='\'', quoting=csv.QUOTE_MINIMAL)

	features_list = []

	for j in range(bits_per_vector):
		if not (0, j) in useless_r1_bits and not (1, j) in useless_r1_bits:
			features_list.append("r1_bit" + str(j))

	for j in range(bits_per_vector):
		if not (0, j) in useless_r2_bits and not (1, j) in useless_r2_bits:
			features_list.append("r2_bit" + str(j))

	features_list.append("p1_bit" + str(i))

	writer.writerow(features_list)

	for row in rows:
		string_row = row["r1_fps"] + row["r2_fps"] + row["p1_fps"][i]

		list_row = list(string_row)

		#print(str(i) + "  " + str(len(string_row)) + "  " + str(len(features_list)))
		assert(len(list_row) == len(features_list))

		writer.writerow(list(string_row))

	print("Loaded p1_bit" + str(i) + " file")

print("Number of rule lists:" + str(bits_per_vector - len(useless_p1_bits)))
print("Number of rules per rule list:" + str(2 * bits_per_vector - (len(useless_r1_bits) + len(useless_r2_bits))))
