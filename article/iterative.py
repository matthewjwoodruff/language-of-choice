from collections import namedtuple
import math
inf = math.inf

def algebra(node):
    try:                   node.if0
    except AttributeError: return node.name
    return "{}({},{})".format(node.name, algebra(node.if0), algebra(node.if1))

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

choice_nodes = dict()

def variable(name, rank):
    key = (name, rank, const0, const1)
    try:
        return choice_nodes[key]
    except KeyError:
        node = ChoiceNode(*key)
        choice_nodes[key] = node
        return node

def collapse_irrelevant(index, if0, if1):
    if if0 is if1: return if0
    key = (index.name, index.rank, if0, if1)
    try: return choice_nodes[key]
    except KeyError:
        node = ChoiceNode(*key)
        choice_nodes[key] = node
        return node

def substitute(node, rank, value):
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
        try: return choice_nodes[key]
        except KeyError:
            node = ChoiceNode(key)
            choice_nodes[key] = node
            return node

def choice(index, if0, if1):
    try:
        if if0.value == 0:
            if if1.value == 0:
                return const0
            elif if1.value == 1:
                return index
        elif if0.value == 1 and if1.value == 1:
            return const1
    except AttributeError: pass
    try:
        if index.value == 0: return if0
        if index.value == 1: return if1
    except AttributeError: pass
    minimum_rank_node = index
    for node in (if0, if1):
        if node.rank < minimum_rank_node.rank:
            minimum_rank_node = node
    rank = minimum_rank_node.rank
    left  = choice(substitute(index, rank, 0),
                   substitute(if0,   rank, 0),
                   substitute(if1,   rank, 0))
    right = choice(substitute(index, rank, 1),
                   substitute(if0,   rank, 1),
                   substitute(if1,   rank, 1))

    new_index = variable(minimum_rank_node.name, minimum_rank_node.rank)
    new_node = collapse_irrelevant(new_index, left, right)

    return new_node

import random

# A Possibly More Realistic Example?
# Let's say we want to do a round-robin tournament among
# N teams across M days.  Each team may play at most once
# in a day.
choice_nodes.clear()

def at_least_n(limit, vars):
    nvars = len(vars)
    # trivial failure
    if nvars < limit: return const0
    # trivial success
    if limit <= 0: return const1
    vars = sorted(vars, key=lambda v: v.rank)
    constraint = [const0 for _ in range(limit)]
    constraint.append(const1)

    index = nvars - 1
    while index >= 0:
        variable = vars[index]
        index -= 1
        for ii in range(len(constraint) - 1):
            left = constraint[ii]
            right = constraint[ii+1]
            if left is not right:
                constraint[ii] = choice(variable, left, right)
    return constraint[0]

def at_most_n(limit, vars):
    nvars = len(vars)
    # trivial failure
    if limit < 0: return const0
    # trivial success
    if limit > nvars: return const1
    vars = sorted(vars, key=lambda v: v.rank)
    constraint = [const1 for _ in range(limit + 1)]
    constraint.append(const0)
    index = nvars - 1
    while index >= 0:
        variable = vars[index]
        index -= 1
        for ii in range(len(constraint) - 1):
            left = constraint[ii]
            right = constraint[ii+1]
            if left is not right:
                constraint[ii] = choice(variable, left, right)
    return constraint[0]

def viz(graph, name):
    nodes = [graph]
    dot = graphviz.Digraph(name)
    while len(nodes) > 0:
        next_nodes = set()
        for node in nodes:
            dot.node(str(id(node)), node.name)
            try:
                if node.if0 is const0:
                    zero = str(random.random())
                    dot.node(zero, "0")
                    dot.edge(str(id(node)), zero, label='0')
                elif node.if0 is const1:
                    one = str(random.random())
                    dot.node(one, "1")
                    dot.edge(str(id(node)), one, label='0')
                else:
                    dot.edge(str(id(node)), str(id(node.if0)), label='0')
                    next_nodes.add(node.if0)

                if node.if1 is const0:
                    zero = str(random.random())
                    dot.node(zero, "0")
                    dot.edge(str(id(node)), zero, label='1')
                elif node.if1 is const1:
                    one = str(random.random())
                    dot.node(one, "1")
                    dot.edge(str(id(node)), one, label='1')
                else:
                    dot.edge(str(id(node)), str(id(node.if1)), label='1')
                    next_nodes.add(node.if1)
            except AttributeError: pass
        nodes = next_nodes

    dot.render(name, view=False)
    print(name)

# Combining the loops helps because of the overlapping
# variables.  But I think we can do better.

choice_nodes.clear()

def make_problem(teams, days):
    variables = list()
    rank = 0
    for dd in range(M):
        for ii in range(N):
            for jj in range(ii+1,N):
                name = "{}{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj), dd)
                variables.append(variable(name, rank))
                rank += 1
            name = "{}B{}".format(chr(ord('a')+ii), dd)
            variables.append(variable(name, rank))
    return variables

N = 6
M = 5 # can also do 6, but as the graph relaxes to a tree things take longer
variables = make_problem(N, M)

all_components = list()
for ii in range(N):
    for dd in range(M):
        team = str(chr(ord('a')+ii))
        components = [v for v in variables if team in v.name and str(dd) in v.name]
        all_components.append(components)

    for jj in range(ii+1,N):
        match = "{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj))
        components = [v for v in variables if team in v.name and str(dd) in v.name]
        all_components.append(components)

all_components.sort(key=lambda c: c[0].rank, reverse=True)
constraint = const1
for components in all_components:
    only_one = choice(at_most_n(1, components), const0, at_least_n(1, components))
    constraint = choice(constraint, const0, only_one)
try:
    import graphviz
    name = "both_constraints_{}_{}".format(M, N)
    viz3(constraint, name)
except ImportError: pass

# Oh heck yes.  That's blazingly faster.  Moral of the
# story: build the graph in a way that helps standardize it.

