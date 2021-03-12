"""
First laboratory assignment in 'Artificial Intelligence' study.

>> STATE SPACE SEARCH <<

@author ftodoric
@date 26/03/2020
"""

import time

# global variables
visited_states = []


def main():
    start_time = time.time()

    # data structures
    init_state = ""
    fin_states = []
    init_state_not_found = True
    fin_states_not_found = True
    trans_function = {}
    total_transitions = 0
    heuristic_function = {}

    # parsing state space descriptor
    with open("./resources/istra.txt", encoding="utf-8") as state_space_descriptor:
        for line in state_space_descriptor:
            if line.startswith('#'):
                continue
            if init_state_not_found:
                init_state = line.strip()
                init_state_not_found = False
                continue
            elif fin_states_not_found:
                fin_states = line.strip().split(" ")
                fin_states_not_found = False
                continue
            else:
                temp = line.strip().split(": ")
                if len(temp) != 1:
                    trans_function[temp[0]] = temp[1].split(" ")
                    total_transitions += len(temp[1].split(" "))
                else:
                    trans_function[temp[0]] = []

    # parsing heuristic function descriptor
    with open("./resources/istra_pessimistic_heuristic.txt", encoding="utf-8") as heuristic_function_descriptor:
        for line in heuristic_function_descriptor:
            if line.startswith("#"):
                continue
            temp = line.strip().split(": ")
            heuristic_function[temp[0]] = float(temp[1])

    # data structure print
    print("Start state:", init_state)
    print("End state(s):", fin_states)
    print("State space size:", len(trans_function))
    print("Total transitions:", total_transitions, end="\n\n")

    # ALGORITHMS:
    # BFS
    print("RUNNING BFS:")
    current_node = bfs(init_state, trans_function, fin_states)

    print("States visited:", len(visited_states))
    if current_node is not None:
        path = []
        while current_node is not None:
            path.append(current_node)
            current_node = current_node.get_parent()

        path.reverse()
        print("Found path of length", len(path), end=":\n")
        for i in range(len(path) - 1):
            print(path[i].get_state(), "=>")
        print(path[len(path) - 1].get_state())
    else:
        print("Search failed!")
    print()

    # UCS
    print("RUNNING UCS:")
    current_node = ucs(init_state, trans_function, fin_states)

    print("States visited:", len(visited_states))
    total_cost = current_node.get_cost()
    if current_node is not None:
        path = []
        while current_node is not None:
            path.append(current_node)
            current_node = current_node.get_parent()

        path.reverse()
        print("Found path of length", len(path),
              "with total cost of", total_cost, end=":\n")
        for i in range(len(path) - 1):
            print(path[i].get_state(), "=>")
        print(path[len(path) - 1].get_state())
    else:
        print("Search failed!")
    print()

    # A*
    print("RUNNING ASTAR:")
    current_node = a_star(init_state, trans_function,
                          fin_states, heuristic_function)

    print("States visited:", len(visited_states))
    total_cost = current_node.get_cost()
    if current_node is not None:
        path = []
        while current_node is not None:
            path.append(current_node)
            current_node = current_node.get_parent()

        path.reverse()
        print("Found path of length", len(path),
              "with total cost of", total_cost, end=":\n")
        for i in range(len(path) - 1):
            print(path[i].get_state(), "=>")
        print(path[len(path) - 1].get_state())
    else:
        print("Search failed!")
    print()

    # heuristic check
    is_optimistic(trans_function, heuristic_function, fin_states)
    print()
    is_consistent(trans_function, heuristic_function)

    print()
    print("Time elapsed: {:.4f}s".format(time.time() - start_time))


def bfs(init_state, trans_function, fin_states):
    global visited_states
    visited_states = set()

    queue = [Node(init_state, 0, None, 0)]
    while len(queue) != 0:
        node = queue.pop(0)

        visited_states.add(node.get_state())

        if node.get_state() in fin_states:
            return node

        for n in expand(node, trans_function):
            queue.append(n)

    return None


def ucs(init_state, trans_function, fin_states):
    global visited_states
    visited_states = []

    open_list = [Node(init_state, 0, None, 0)]
    while len(open_list) != 0:
        node = open_list.pop(0)

        if node.get_state() not in visited_states:
            visited_states.append(node.get_state())

        if node.get_state() in fin_states:
            return node

        for n in expand(node, trans_function):
            open_list.append(n)
            open_list = sort_by_cost(open_list)
    return None


def a_star(init_state, trans_function, fin_states, heuristic_function):
    global visited_states
    visited_states = []

    open_list = [Node(init_state, 0, None, 0)]
    closed = []
    open_and_closed = []

    while len(open_list) != 0:
        node = open_list.pop(0)

        if node.get_state() not in visited_states:
            visited_states.append(node.get_state())

        if node.get_state() in fin_states:
            return node

        closed.append(node)
        for n in open_list:
            open_and_closed.append(n)
        for n in closed:
            open_and_closed.append(n)

        for n in expand(node, trans_function):
            n.set_h_cost(heuristic_function[n.get_state()])
            same_node = None
            for m in open_and_closed:
                if n.get_state() == m.get_state():
                    same_node = m
                    break
            if same_node is not None:
                if same_node.get_cost() < n.get_cost():
                    continue
                else:
                    open_and_closed.remove(same_node)
            open_list.append(n)
            open_list = sort_by_heuristic_cost(open_list)

    return None


def expand(node, trans_function):
    new_nodes = []

    if node.get_state() in trans_function:
        successors = trans_function[node.get_state()]

        for successor in successors:
            temp = successor.split(",")
            new_node = Node(temp[0], node.get_depth() + 1,
                            node, node.get_cost() + float(temp[1]))
            new_nodes.append(new_node)

        return new_nodes
    else:
        return []


def sort_by_cost(nodes):
    # sorted_nodes = []

    for i in range(len(nodes)):
        for j in range(0, len(nodes) - i - 1):
            if nodes[j].get_cost() > nodes[j + 1].get_cost():
                nodes[j], nodes[j + 1] = nodes[j + 1], nodes[j]

    """while len(nodes) != 0:
        min_cost = nodes[0].get_cost()
        chosen = nodes[0]
        for node in nodes:
            if node.get_cost() < min_cost:
                min_cost = node.get_cost()
                chosen = node
        sorted_nodes.append(chosen)
        nodes.remove(chosen)"""

    return nodes


def sort_by_heuristic_cost(nodes):
    sorted_nodes = []

    while len(nodes) != 0:
        min_cost = nodes[0].get_cost() + nodes[0].get_h_cost()
        chosen = nodes[0]
        for node in nodes:
            h_value = node.get_h_cost()
            if node.get_cost() + h_value < min_cost:
                min_cost = node.get_cost() + h_value
                chosen = node
        sorted_nodes.append(chosen)
        nodes.remove(chosen)

    return sorted_nodes


def is_optimistic(trans_function, heuristic_function, fin_states):
    print("Checking if heuristic is optimistic.")

    not_optimistic = False
    for state in heuristic_function:
        current_node = ucs(state, trans_function, fin_states)
        total_cost = current_node.get_cost()
        if float(heuristic_function[state]) > total_cost:
            not_optimistic = True
            print("[ERR] h(", end="")
            print(state, end=") > h*: ")
            print(float(heuristic_function[state]), ">", total_cost)
    if not_optimistic:
        print("Heuristic is not optimistic.")
    else:
        print("Heuristic is optimistic.")


def is_consistent(trans_function, heuristic_function):
    print("Checking if heuristic is consistent.")
    consistent = True
    for state in heuristic_function:
        # if state not in trans_function:
        #    continue
        successors = trans_function[state]
        for successor in successors:
            successor_state = successor.split(",")[0]
            c = float(successor.split(",")[1])
            if heuristic_function[state] > heuristic_function[successor_state] + c:
                consistent = False
                print("[ERR] h(", end="")
                print(state, end=") > h(")
                print(successor_state, end=") + c: ")
                print(heuristic_function[state], ">",
                      heuristic_function[successor_state], "+", c)
    if consistent:
        print("Heuristic is consistent.")
    else:
        print("Heuristic is not consistent.")


class Node:
    # state
    # depth
    # parent
    # cost
    # heuristic cost

    def __init__(self, state, depth, parent, cost):
        self.__state = state
        self.__depth = depth
        self.__parent = parent
        self.__cost = cost
        self.__heuristic_cost = 0

    def get_state(self):
        return self.__state

    def get_depth(self):
        return self.__depth

    def get_parent(self):
        return self.__parent

    def get_cost(self):
        return self.__cost

    def set_h_cost(self, value):
        self.__heuristic_cost = value

    def get_h_cost(self):
        return self.__heuristic_cost


main()
