from collections import namedtuple
import math
import random
import time
try: import graphviz
except ImportError: pass

inf = math.inf

def algebra(node):
    try:                   node.if0
    except AttributeError: return node.name
    return "{}({},{})".format(node.name, algebra(node.if0), algebra(node.if1))
    return "{}.{}({},{})".format(node.name, node.rank, algebra(node.if0), algebra(node.if1))

DIG = 10**5

def ids(node):
    try: node.if0
    except AttributeError: return "{}@{}".format(node.name, id(node)%DIG)
    return "{}@{}({},{})".format(node.name, id(node)%DIG, ids(node.if0), ids(node.if1))

# constant nodes are terminal -- they do not have if0 or if1
ConstantNode = namedtuple("ConstantNode", (
    'name',
    'rank',
    'value'))
ConstantNode.__repr__ = algebra

# choice nodes do not have a value in the absolute sense,
# only in the context of an environment
ChoiceNode = namedtuple("ChoiceNode", (
    'name',
    'rank',
    'if0',
    'if1' ))
ChoiceNode.__repr__ = algebra

const0 = ConstantNode('0', inf, 0)
const1 = ConstantNode('1', inf, 1)

def substitute(node, rank, value, definitions):
    if rank < node.rank: return node
    elif rank == node.rank:
        if value == 0:
            return node.if0
        else:
            return node.if1
    else:
        left = substitute(node.if0, rank, value)
        right = substitute(node.if1, rank, value)
        key = (node.name, node.rank, left, right)

def choice(index, if0, if1, definitions):
    """
    definitions: a dictionary of choice nodes, keyed by
    (index name, index rank, if0, if1)
    return root of standardized bdd

    definitions WILL BE MODIFIED IN PLACE
    """
    # dispose of trivial cases
    if if0 is if1:                      return if0
    if if0 is const0 and if1 is const1: return index
    if index is const0:                 return if0
    if index is const1:                 return if1
    top_node = index
    if if0.rank < top_node.rank:
        top_node = if0
    if if1.rank < top_node.rank:
        top_node = if1
    tree= list()
    tree.append([top_node.name, top_node.rank])
    stack = list()
    stack.append((index, if0, if1))
    while len(tree[0]) < 4:
        index, if0, if1 = stack[-1]
        if len(tree[-1]) == 2: #left
            name, rank = tree[-1]
            left_index = substitute(index, rank, const0)
            left_if0 = substitute(if0, rank, const0)
            left_if1 = substitute(if1, rank, const0)
            if left_if0 is left_if1:
                tree[-1].append(left_if0)
                continue
            if if0 is const0 and if1 is const1:
                tree[-1].append(left_index)
                continue
            if left_index is const0:
                tree[-1].append(left_if0)
                continue
            if left_index is const1:
                tree[-1].append(left_if1)
                continue

            top_node = left_index
            if left_if0.rank < top_node.rank:
                top_node = left_if0
            if left_if1.rank < top_node.rank:
                top_node left_= if1
            tree.append((top_node.name, top_node.rank))
            stack.append((left_index, left_if0, left_if1))
            continue
        elif len(tree[-1]) == 3: # right
            name, rank, _ = tree[-1]
            right_index = substitute(index, rank, const1)
            right_if0 = substitute(if0, rank, const1)
            right_if1 = substitute(if1, rank, const1)
            if right_if0 is right_if1:
                tree[-1].append(right_if0)
                continue
            if if0 is const0 and if1 is const1:
                tree[-1].append(right_index)
                continue
            if right_index is const0:
                tree[-1].append(right_if0)
                continue
            if right_index is const1:
                tree[-1].append(right_if1)
                continue

            top_node = right_index
            if right_if0.rank < top_node.rank:
                top_node = right_if0
            if right_if1.rank < top_node.rank:
                top_node right_= if1
            tree.append((top_node.name, top_node.rank))
            stack.append((right_index, right_if0, right_if1))
            continue
        else: # done
            key = tree.pop()
            stack.pop()
            try:
                choice_node = definitions[key]
            except KeyError:
                choice_node = ChoiceNode(*key)
                definitions[key] = choice_node
            tree[-1].append(choice_node)
