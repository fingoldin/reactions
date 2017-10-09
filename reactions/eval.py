import pycorels
import os

num_rules_to_test = 17
test_out_file = "data/test.out"
opt_dir = "data/train/"
label_dir = "data/test/"
max_bits = 881



test_out_list = pycorels.tolist(test_out_file)

for rule_to_test in range(num_rules_to_test):
    output_p1 = []
    key_p1 = []

    for bit in range(max_bits):
        opt_file = opt_dir + "p1_bit" + str(bit) + ".opt"
        label_file = label_dir + "p1_bit" + str(bit) + ".label"
        if os.path.isfile(opt_file):
            opt_rules = open(opt_file, "r").read().split(";")
            for opt_rule in opt_rules:
                opt_rule = opt_rule.split("~", 1);
                opt_rule_features = opt_rule[0]
                opt_rule_pred = opt_rule[1]

                if opt_rule_features == "default":
                    output_p1.append(str(opt_rule_pred))
                    break

                for rule in test_out_list:
                    if rule[0] == opt_rule_features and rule[1][rule_to_test] == 1:
                        output_p1.append(str(opt_rule_pred))
                        break
                else:
                    continue
                break
        else:
            output_p1.append("0")

        if os.path.isfile(label_file):
            label_list = pycorels.tolist(label_file)
            key_p1.append(str(int(label_list[1][1][rule_to_test])))
        else:
            key_p1.append("0")

    print("\n\n\nFor reaction #" + str(rule_to_test + 1) + ":\n")

    incorrect = 0
    for bit in range(max_bits):
        if output_p1[bit] != key_p1[bit]:
            incorrect += 1

    print("Model result: ")
    print("".join(output_p1))

    print("Actual product: ")
    print("".join(key_p1))

    print("Num bits incorrect: " + str(incorrect))
