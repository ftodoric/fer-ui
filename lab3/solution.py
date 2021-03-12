from sys import argv
from math import log2
# from random import seed, randrange


def print_complex_list(complex_list):
    print("BEGIN")
    for lst in complex_list:
        for item in lst:
            print(item, end=" ")
        print()
    print("END")


class Node:
    def __init__(self, feature_name, list_of_doubles):
        self._feature_name = feature_name
        # double - (feature_value, Node/Leaf)
        self._list_of_doubles = list_of_doubles

    def get_node_as_text(self):
        node_string = "Node("
        node_string += self._feature_name + ", {"
        for double in self._list_of_doubles:
            node_string += "(" + double[0] + ", " + \
                double[1].get_node_as_text() + ")"
        return node_string + "})"

    def get_type(self):
        return "Node"

    def get_feature(self):
        return self._feature_name

    def get_double(self, feature_value):
        for db in self._list_of_doubles:
            if db[0] == feature_value:
                return db[1]
        return None


class Leaf:
    def __init__(self, class_label):
        self._class_label = class_label

    def get_node_as_text(self):
        return "Leaf(" + self._class_label + ")"

    def get_type(self):
        return "Leaf"

    def get_class_label(self):
        return self._class_label


class ID3:
    _output_depths = []
    _test_result = []

    def __init__(self, hyperparameters):
        self._hyperparameters = hyperparameters

    def get_hyperparameters(self):
        return self._hyperparameters

    def most_frequent_class(self, D):
        class_dict = {}
        for line in D:
            if line[-1] not in class_dict:
                class_dict[line[-1]] = 1
            else:
                class_dict[line[-1]] += 1

        max_freq = -1
        max_key = ""
        for key in class_dict:
            if class_dict[key] > max_freq:
                max_freq = class_dict[key]
                max_key = key

        return max_key

    def filter_dataset_by_feature_value(self, D, X, feature, feature_value):
        # print(X, feature, feature_value)
        # print_complex_list(D)
        feature_index = X.index(feature)
        filtered = []
        for line in D:
            temp = []
            if feature_value == line[feature_index]:
                for i in range(len(line)):
                    if i != feature_index:
                        temp.append(line[i])
            if len(temp) != 0:
                filtered.append(temp)

        # print_complex_list(filtered)
        return filtered

    def filter_dataset_by_class_label(self, D, class_label):
        filtered = []
        for line in D:
            if class_label == line[-1]:
                filtered.append(line)

        return filtered

    def get_entropy(self, list_of_numbers):
        total_sum = 0
        for number in list_of_numbers:
            total_sum += number

        if total_sum == 0:
            return log2(len(list_of_numbers))

        E = 0
        for number in list_of_numbers:
            if number == 0:
                continue
            E += (number/total_sum)*log2(number/total_sum)
        return -E

    def find_feature_IG(self, feature, D, X, Y):
        # print(feature)
        # print_complex_list(D)
        # print(X)
        feature_index = X.index(feature)
        E_D_dict = {}  # for calculation of parent node entropy
        E_expected_list = []  # for calculation of expected entropy
        for feature_value in self._values_by_feature[feature]:
            class_dict = {}
            for cl in Y:
                class_dict[cl] = 0
            for line in D:
                if feature_value == line[feature_index]:
                    class_dict[line[-1]] += 1
            for key in class_dict:
                if key not in E_D_dict:
                    E_D_dict[key] = class_dict[key]
                else:
                    E_D_dict[key] += class_dict[key]
            E_expected_list.append(class_dict)
        # print(feature)
        # print(E_D_dict)
        # print(E_expected_list)

        list_of_num = []
        for key in E_D_dict:
            list_of_num.append(E_D_dict[key])
        total_sum = 0
        for num in list_of_num:
            total_sum += num
        # print(list_of_num)
        ED = self.get_entropy(list_of_num)
        # print(ED)

        E_list = []
        for dic in E_expected_list:
            list_of_num = []
            sum = 0
            for key in dic:
                list_of_num.append(dic[key])
                sum += dic[key]
            E_list.append(self.get_entropy(list_of_num) * (sum)/(total_sum))
        # print(ED)
        # print(E_list)

        IG = ED
        # print(feature)
        # print(IG)
        # print(E_list)
        # print("ED:", ED)
        for item in E_list:
            IG -= item
            # print("Item:", item)

        # print(IG)
        return IG

    def maxIG(self, D, X, Y):
        max_IG = -1
        feature_with_maxIG = ""
        for feature in X[:-1]:
            IG = self.find_feature_IG(feature, D, X, Y)
            if self._hyperparameters["mode"] == "ig":
                print("IG({})={}".format(feature, IG), end=" ")
            if IG > max_IG:
                max_IG = IG
                feature_with_maxIG = feature
        if self._hyperparameters["mode"] == "ig":
            print()

        return feature_with_maxIG

    def fit(self, train_dataset):
        self._output_depths = []
        # X - feature names / attributes
        X = train_dataset[0]

        # D - dataset for training
        D = D_parent = train_dataset[1:]

        # Y - class labels
        Y = []
        for lst in D:
            if lst[-1] not in Y:
                Y.append(lst[-1])

        # getting all feature values
        # dictionnairy -> {feature: [feature_values]}
        self._values_by_feature = {}
        for feature in X:
            self._values_by_feature[feature] = []
        for line in D:
            for i in range(len(X)):
                if line[i] not in self._values_by_feature[X[i]]:
                    self._values_by_feature[X[i]].append(line[i])

        # training / building decision tree
        self._root = self._build_id3(D, D_parent, X, Y, 0)
        # print(self._root.get_node_as_text())
        for i in range(len(self._output_depths)):
            if i != len(self._output_depths) - 1:
                print("{}:{},".format(
                    self._output_depths[i][0], self._output_depths[i][1]), end=" ")
            else:
                print("{}:{}".format(
                    self._output_depths[i][0], self._output_depths[i][1]))

    def _build_id3(self, D, D_parent, X, Y, depth):
        dataset_empty = True
        # print_complex_list(D)
        for line in D:
            if len(line) != 1:
                dataset_empty = False
                break
        if dataset_empty:
            v = self.most_frequent_class(D_parent)
            return Leaf(v)

        v = self.most_frequent_class(D)

        filtered_D = self.filter_dataset_by_class_label(D, v)
        # print_complex_list(D)
        # print()
        # print_complex_list(filtered_D)
        if len(X) == 0 or D == filtered_D:
            return Leaf(v)

        # print(D, "\n", X)
        # print_complex_list(D)
        # print("X:", X)
        x = self.maxIG(D, X, Y)
        # print(x)

        self._output_depths.append((depth, x))

        subtrees = []
        # print(x)
        for v in self._values_by_feature[x]:
            X_except_x = [item for item in X if item != x]
            # print(v)
            t = self._build_id3(
                self.filter_dataset_by_feature_value(D, X, x, v), D, X_except_x, Y, depth + 1)

            subtrees.append((v, t))
        return Node(x, subtrees)

    def predict(self, test_dataset):
        X = test_dataset[0][:-1]
        D = []
        for line in test_dataset:
            temp = []
            for i in range(len(line)):
                if i != len(line)-1:
                    temp.append(line[i])
            D.append(temp)
        D.pop(0)

        values_dict = {}
        for line in D:
            for i in range(len(line)):
                values_dict[X[i]] = line[i]

            # print(values_dict)
            self.search_dec_tree(self._root, values_dict)

        return self._test_result

    def search_dec_tree(self, node, values_dict):
        feature = node.get_feature()
        value = values_dict[feature]
        node_or_leaf = node.get_double(value)
        if node_or_leaf == None:
            self._test_result.append("najčešća klasa")
        if node_or_leaf.get_type() == "Node":
            self.search_dec_tree(node_or_leaf, values_dict)
            return
        self._test_result.append(node_or_leaf.get_class_label())
        return


# >>> ENTRY POINT <<<<<<<<<<<<<<<<<<<<<<<<<
# file names
train_filename = argv[1]
test_filename = argv[2]
config_filename = argv[3]

# data structures
train_dataset = []
test_dataset = []

# hyperparameters with it's default values
# max_depth = None indicates infinite tree size
hyperparameters = {"mode": "", "model": "", "max_depth": None,
                   "num_trees": 1, "feature_ratio": 1.0, "example_ratio": 1.0}

# parsing descriptor files
with open(train_filename, "r", encoding="utf8") as file:
    for line in file:
        train_dataset.append(line.strip().split(","))

with open(test_filename, "r", encoding="utf8") as file:
    for line in file:
        test_dataset.append(line.strip().split(","))

with open(config_filename, "r", encoding="utf8") as file:
    for line in file:
        name = line.strip().split("=")[0]
        value = line.strip().split("=")[1]
        if name == "mode":
            hyperparameters[name] = value
        elif name == "model":
            hyperparameters[name] = value
        elif name == "max_depth" and value != "-1":
            hyperparameters[name] = value
        elif name == "num_trees":
            hyperparameters[name] = int(value)
        elif name == "feature_ratio":
            hyperparameters[name] = float(value)
        elif name == "example_ratio":
            hyperparameters[name] = float(value)

# print_complex_list(train_dataset)
# print_complex_list(test_dataset)
# print(hyperparameters)

# print(test_dataset)
model = ID3(hyperparameters)
model.fit(train_dataset)
predictions = model.predict(test_dataset)

for prediction in predictions:
    print(prediction, end=" ")
print()

total_num_of_cases = len(test_dataset) - 1
# print(total_cases)
correct_num_of_cases = 0
# print_complex_list(test_dataset)
for i in range(len(predictions)):
    if predictions[i] == test_dataset[i+1][-1]:
        correct_num_of_cases += 1
# print(correct_cases)

# accuracy
print(round(correct_num_of_cases/total_num_of_cases, 5))

class_labels = []
correct_cases = []
for case in test_dataset[1:]:
    correct_cases.append(case[-1])
    if case[-1] not in class_labels:
        class_labels.append(case[-1])
class_labels = sorted(class_labels, key=str.lower)

realXpredicted = []
for i in range(total_num_of_cases):
    realXpredicted.append((correct_cases[i], predictions[i]))
# print(realXpredicted)

err_matrix_count = {}
for case1 in class_labels:
    for case2 in class_labels:
        err_matrix_count[(case1, case2)] = 0

for tuple2 in realXpredicted:
    # print(tuple2)
    err_matrix_count[tuple2] += 1

# print(err_matrix_count)

# error matrix
for real in class_labels:
    for prediction in class_labels:
        print(err_matrix_count[(real, prediction)], end=" ")
    print()
