from sys import argv

"""
Second laboratory assignment in 'Artificial Intelligence' study.

>> AUTOMATED THEOREM PROVING <<

@author ftodoric
@date 25/04/2020
"""


def subset_of(clause1, clause2):
    for literal in clause1:
        if literal not in clause2:
            return False
    return True


def negate(literal):
    if literal[0] == "~":
        return literal[1:]
    else:
        return "~" + literal


def negate_formula(formula):
    new_clauses = []
    for literal in formula:
        new_clauses += [[negate(literal)]]
    return new_clauses


def remove_duplicates(clauses):
    res = []
    for clause in clauses:
        if clause not in res:
            res.append(clause)
    return res


def check_clauses(clauses):
    clauses = remove_duplicates(clauses)
    to_be_removed = []

    for clause1 in clauses:
        for literal in clause1:
            if negate(literal) in clause1 and clause1 not in to_be_removed:
                to_be_removed.append(clause1)
                break
        for clause2 in clauses:
            if clause1 == clause2:
                continue
            if subset_of(clause1, clause2) and clause2 not in to_be_removed:
                to_be_removed.append(clause2)

    for clause in to_be_removed:
        clauses.remove(clause)

    return clauses


def pl_resolve(first, second):
    derived = []
    found = False
    if len(first) == 1 and len(second) == 1 and first[0] == negate(second[0]):
        return ["NIL"]
    for literal in first:
        if negate(literal) in second:
            found = True
    if found:
        for literal in first:
            if negate(literal) not in second:
                derived += [literal]
        for literal in second:
            if negate(literal) not in first:
                derived += [literal]
    return derived


def select_clauses(premises, sos):
    selected = []
    for premise in premises:
        for s in sos:
            selected += [(premise, s)]
    for i in range(len(sos) - 1):
        for j in range(i + 1, len(sos)):
            selected += [(sos[i], sos[j])]
    return selected


def pl_resolution(premises, goal_formula):
    sos = negate_formula(goal_formula)
    line_counter = 1
    while True:
        new = []
        sos = check_clauses(sos)
        # print(sos)
        for pair in select_clauses(premises, sos):
            # print("Pair", pair)
            resolvents = pl_resolve(pair[0], pair[1])
            # print("Resolvents:", resolvents)
            if "NIL" in resolvents:
                print("true")
                return
            if len(resolvents) != 0:
                new += [resolvents]
            # print(new)
        new = check_clauses(new)
        subset = True
        # print(new)
        # print(sos)
        # print(premises)
        for clause in new:
            if (clause not in sos):
                subset = False
                break
        if subset:
            print("false")
            return
        sos += new


def main():
    if len(argv) < 3 or len(argv) > 5:
        print(
            "Usage: solution.py podzadatak path-to-clauses [path-to-user-commands] [verbose]")
        return

    assignment = argv[1]
    file_path = argv[2]
    # usr-commands & verbose

    # print(assignment, file_path)

    premises = []
    with open(file_path, encoding="utf-8") as clause_list_file:
        for line in clause_list_file:
            if line.startswith("#"):
                continue
            premises += [line.strip().lower().split(" v ")]
    goal_formula = premises[len(premises) - 1]
    premises.remove(premises[len(premises) - 1])
    # print("Premises:", premises)
    # print("Goal:", goal_formula)

    test = [["a", "b", "~a"], ["~f", "b", "c"], ["b", "c"], ["~f", "b", "c"], ["f", "~c"], ["a", "z"], ["b", "~b"],
            ["z", "a", "i"], ["a", "b", "~a"]]

    pl_resolution(premises, goal_formula)


main()
