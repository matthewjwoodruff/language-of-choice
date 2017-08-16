from collections import namedtuple
import math
import random
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
    counter = 0
    nodes = [graph]
    try:
        dot = graphviz.Digraph(name)
    except NameError: return
    while len(nodes) > 0:
        next_nodes = set()
        for node in nodes:
            #dot.node(str(id(node)), "{}.{}".format(node.name, node.rank))
            dot.node(str(id(node)), "{}".format(node.name))
            counter += 1
            try:
                if node.if0 is const0:
                    #zero = str(random.random())
                    #dot.node(zero, "0")
                    #dot.edge(str(id(node)), zero, label='0')
                    pass
                elif node.if0 is const1:
                    one = str(random.random())
                    dot.node(one, "1")
                    dot.edge(str(id(node)), one, label='0')
                else:
                    dot.edge(str(id(node)), str(id(node.if0)), label='0')
                    next_nodes.add(node.if0)

                if node.if1 is const0:
                    #zero = str(random.random())
                    #dot.node(zero, "0")
                    #dot.edge(str(id(node)), zero, label='1')
                    pass
                elif node.if1 is const1:
                    one = str(random.random())
                    dot.node(one, "1")
                    dot.edge(str(id(node)), one, label='1')
                else:
                    dot.edge(str(id(node)), str(id(node.if1)), label='1')
                    next_nodes.add(node.if1)
            except AttributeError: pass
        nodes = next_nodes

    print("{} nodes in {}".format(counter, name))
    dot.render(name, view=False)

# A Possibly More Realistic Example?
# Let's say we want to do a round-robin tournament among
# N teams across M days.  Each team may play at most once
# in a day.

# Combining the loops helps because of the overlapping
# variables.  But I think we can do better.

def make_variables(teams, days):
    variables = list()
    rank = 0
    for dd in range(days):
        for ii in range(teams):
            for jj in range(ii+1,teams):
                name = "{}{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj), dd)
                variables.append(variable(name, rank))
                rank += 1
            name = "{}B{}".format(chr(ord('a')+ii), dd)
            variables.append(variable(name, rank))
            rank += 1
    return variables

def make_constraint_graph(teams, days, variables):
    all_components = list()
    for tt in range(teams):
        for dd in range(days):
            team = str(chr(ord('a')+tt))

            components = sorted([v for v in variables if team in v.name and str(dd) in v.name], key=lambda v: v.rank)
            #print("(tt, dd) ({}, {}): {}".format(tt, dd, components))
            all_components.append(components)

        for uu in range(tt+1,teams):
            match = "{}{}".format(chr(ord('a')+tt), chr(ord('a')+uu))
            components = sorted([v for v in variables if match in v.name], key=lambda v: v.rank)
            #print("(tt, uu) ({}, {}): {}".format(tt, uu, components))
            all_components.append(components)

    all_components.sort(key=lambda c: c[0].rank, reverse=True)
    constraint = const1
    components_considered = set()
    try:
        while len(all_components) > 0:
            overlaps = [len(components_considered.intersection(components)) for components in all_components]
            biggest_overlap = max(overlaps)
            components_having_biggest_overlap = [c for c,o in zip(all_components, overlaps) if o == biggest_overlap]
            chbo = components_having_biggest_overlap
            # break tie by taking shortest
            lengths = [len(c) for c in chbo]
            shortest = min(lengths)
            shortest_chbos = [c for c,n in zip(chbo, lengths) if n == shortest]
            # break tie by taking last-ranked first variable
            ranks = [c[0].rank for c in shortest_chbos]
            maxrank = max(ranks)
            last_ranked = [c for c,r in zip(shortest_chbos, ranks) if r == maxrank]
            # if there's still a tie, just take the first one
            components = last_ranked[0]
            only_one = choice(at_most_n(1, components), const0, at_least_n(1, components))
            constraint = choice(constraint, const0, only_one)
            all_components = [c for c in all_components if c is not components]
            print("{}: {}".format(len(all_components), len(choice_nodes)))
    except KeyboardInterrupt:
        pass
    return constraint

def make_constraint_graph_binary(teams, days, variables):
    constraints = list()
    for tt in range(teams):
        for dd in range(days):
            team = str(chr(ord('a')+tt))

            components = sorted([v for v in variables if team in v.name and str(dd) in v.name], key=lambda v: v.rank)
            only_one = choice(at_most_n(1, components), const0, at_least_n(1, components))
            constraints.append(only_one)

        for uu in range(tt+1,teams):
            match = "{}{}".format(chr(ord('a')+tt), chr(ord('a')+uu))
            components = sorted([v for v in variables if match in v.name], key=lambda v: v.rank)
            only_one = choice(at_most_n(1, components), const0, at_least_n(1, components))
            constraints.append(only_one)

    #if len(constraints) == 0:
    #    return const1
    #if len(constraints) == 1:
    #    return constraints[0]
    ## go down to the nearest power of 2 first because extra 
    #pp = 0
    #while 2**(pp+1) < len(constraints): pp += 1
#
    #while len(constraints) > 2**pp:

    while len(constraints) > 1:
        print("{}: {}".format(len(constraints), len(choice_nodes)))
        merged = [choice(constraints[2*i], const0, constraints[2*i+1]) for i in range(len(constraints) // 2)]
        if 2 * len(merged) < len(constraints): # len(constraints) is odd
            merged[-1] = choice(merged[-1], const0, constraints[-1])
            #merged = [choice(c, const0, constraints[-1]) for c in merged] # this takes the odd one into all
            #merged.insert(0, constraints[-1]) # this rotates the oddness
        constraints = merged
    return constraints[0]

choice_nodes.clear()

teams = 6
days = 5
variables = make_variables(teams, days)
print("{} variables: {}".format(len(variables), variables))
constraint_graph = make_constraint_graph_binary(teams, days, variables)
cgtext = repr(constraint_graph)
print("constraint graph {}".format(len(cgtext)))
name = "both_constraints_{}_{}".format(teams, days)
with open("{}.{}".format(name, "text"), 'w') as fp:
    fp.write(cgtext)
    fp.write("\n")
viz(constraint_graph, name)

'''
So, is this slow because it's a big problem, or is this
slow because stack frames are expensive?

Here's 4/3:

variables [ab0(0,1), ac0(0,1), ad0(0,1), aB0(0,1), bc0(0,1), bd0(0,1), bB0(0,1), cd0(0,1), cB0(0,1), dB0(0,1), ab1(0,1), ac1(0,1), ad1(0,1), aB1(0,1), bc1(0,1), bd1(0,1), bB1(0,1), cd1(0,1), cB1(0,1), dB1(0,1), ab2(0,1), ac2(0,1), ad2(0,1), aB2(0,1), bc2(0,1), bd2(0,1), bB2(0,1), cd2(0,1), cB2(0,1), dB2(0,1)]
0/18: 43
1/18: 75
2/18: 98
3/18: 138
4/18: 158
5/18: 190
6/18: 213
7/18: 253
8/18: 365
9/18: 506
10/18: 663
11/18: 928
12/18: 957
13/18: 1061
14/18: 1089
15/18: 1112
16/18: 1154
17/18: 1185

18 constraints.  Note the faster growth of the choice
dictionary compared with the following.

This is 5/5:

variables [ab0(0,1), ac0(0,1), ad0(0,1), ae0(0,1), aB0(0,1), bc0(0,1), bd0(0,1), be0(0,1), bB0(0,1), cd0(0,1), ce0(0,1), cB0(0,1), de0(0,1), dB0(0,1), eB0(0,1), ab1(0,1), ac1(0,1), ad1(0,1), ae1(0,1), aB1(0,1), bc1(0,1), bd1(0,1), be1(0,1), bB1(0,1), cd1(0,1), ce1(0,1), cB1(0,1), de1(0,1), dB1(0,1), eB1(0,1), ab2(0,1), ac2(0,1), ad2(0,1), ae2(0,1), aB2(0,1), bc2(0,1), bd2(0,1), be2(0,1), bB2(0,1), cd2(0,1), ce2(0,1), cB2(0,1), de2(0,1), dB2(0,1), eB2(0,1), ab3(0,1), ac3(0,1), ad3(0,1), ae3(0,1), aB3(0,1), bc3(0,1), bd3(0,1), be3(0,1), bB3(0,1), cd3(0,1), ce3(0,1), cB3(0,1), de3(0,1), dB3(0,1), eB3(0,1), ab4(0,1), ac4(0,1), ad4(0,1), ae4(0,1), aB4(0,1), bc4(0,1), bd4(0,1), be4(0,1), bB4(0,1), cd4(0,1), ce4(0,1), cB4(0,1), de4(0,1), dB4(0,1), eB4(0,1)]
0/35: 92
1/35: 136
2/35: 208
3/35: 240
4/35: 306
5/35: 332
6/35: 376
7/35: 448
8/35: 480
9/35: 546
10/35: 572
11/35: 616
12/35: 688
13/35: 720
14/35: 786
15/35: 812
16/35: 856
17/35: 928
18/35: 960
19/35: 1026
20/35: 1604


So it wouldn't appear that the absolute number of nodes
adequately explains the amount of time this is taking.
But perhaps the complexity of the graph.  Maybe I've got
my order wrong?

Here's 5/5 with everything ordered by the last rank in
the constraint rather than the first.
$ pypy3 iterative.py
variables [ab0(0,1), ac0(0,1), ad0(0,1), ae0(0,1), aB0(0,1), bc0(0,1), bd0(0,1), be0(0,1), bB0(0,1), cd0(0,1), ce0(0,1), cB0(0,1), de0(0,1), dB0(0,1), eB0(0,1), ab1(0,1), ac1(0,1), ad1(0,1), ae1(0,1), aB1(0,1), bc1(0,1), bd1(0,1), be1(0,1), bB1(0,1), cd1(0,1), ce1(0,1), cB1(0,1), de1(0,1), dB1(0,1), eB1(0,1), ab2(0,1), ac2(0,1), ad2(0,1), ae2(0,1), aB2(0,1), bc2(0,1), bd2(0,1), be2(0,1), bB2(0,1), cd2(0,1), ce2(0,1), cB2(0,1), de2(0,1), dB2(0,1), eB2(0,1), ab3(0,1), ac3(0,1), ad3(0,1), ae3(0,1), aB3(0,1), bc3(0,1), bd3(0,1), be3(0,1), bB3(0,1), cd3(0,1), ce3(0,1), cB3(0,1), de3(0,1), dB3(0,1), eB3(0,1), ab4(0,1), ac4(0,1), ad4(0,1), ae4(0,1), aB4(0,1), bc4(0,1), bd4(0,1), be4(0,1), bB4(0,1), cd4(0,1), ce4(0,1), cB4(0,1), de4(0,1), dB4(0,1), eB4(0,1)]
0/35: 92
1/35: 136
2/35: 174
3/35: 270
4/35: 342
5/35: 456
6/35: 704
7/35: 974
8/35: 1478
9/35: 2542

So maybe it didn't help?  But then again maybe it did?
You get over the initial hump faster or something?

So here's the full 5/5 that I allowed to run to completion:

0/35: 92
1/35: 136
2/35: 208
3/35: 240
4/35: 306
5/35: 332
6/35: 376
7/35: 448
8/35: 480
9/35: 546
10/35: 572
11/35: 616
12/35: 688
13/35: 720
14/35: 786
15/35: 812
16/35: 856
17/35: 928
18/35: 960
19/35: 1026
20/35: 1604
21/35: 2590
22/35: 4221
23/35: 7343
24/35: 12681
25/35: 21321
26/35: 36855
27/35: 36995
28/35: 49518
29/35: 49670
30/35: 59656
31/35: 59808
32/35: 59840
33/35: 64356
34/35: 64425

And here's if I order by overlap with current variables:

34: 92
33: 136
32: 208
31: 240
30: 306
29: 332
28: 376
27: 448
26: 480
25: 546
24: 572
23: 616
22: 688
21: 720
20: 786
19: 812
18: 856
17: 928
16: 960
15: 1026
14: 1604
13: 2590
12: 4221
11: 7343
10: 12681
9: 21321
8: 36855
7: 36995
6: 49518
5: 49670
4: 59656
3: 59808
2: 59840
1: 64356
0: 64425


Odd that it's exactly the same...

But is it my imagination or did this version go faster?

Here's a possibly even faster way:

$ python iterative.py
75 variables: [ab0(0,1), ac0(0,1), ad0(0,1), ae0(0,1), aB0(0,1), bc0(0,1), bd0(0,1), be0(0,1), bB0(0,1), cd0(0,1), ce0(0,1), cB0(0,1), de0(0,1), dB0(0,1), eB0(0,1), ab1(0,1), ac1(0,1), ad1(0,1), ae1(0,1), aB1(0,1), bc1(0,1), bd1(0,1), be1(0,1), bB1(0,1), cd1(0,1), ce1(0,1), cB1(0,1), de1(0,1), dB1(0,1), eB1(0,1), ab2(0,1), ac2(0,1), ad2(0,1), ae2(0,1), aB2(0,1), bc2(0,1), bd2(0,1), be2(0,1), bB2(0,1), cd2(0,1), ce2(0,1), cB2(0,1), de2(0,1), dB2(0,1), eB2(0,1), ab3(0,1), ac3(0,1), ad3(0,1), ae3(0,1), aB3(0,1), bc3(0,1), bd3(0,1), be3(0,1), bB3(0,1), cd3(0,1), ce3(0,1), cB3(0,1), de3(0,1), dB3(0,1), eB3(0,1), ab4(0,1), ac4(0,1), ad4(0,1), ae4(0,1), aB4(0,1), bc4(0,1), bd4(0,1), be4(0,1), bB4(0,1), cd4(0,1), ce4(0,1), cB4(0,1), de4(0,1), dB4(0,1), eB4(0,1)]
35: 670
18: 913
9: 1420
5: 2647
3: 6668
2: 8313
constraint graph 189890
5078 nodes in both_constraints_5_5

Or if I merge the extra constraint into the every other constraint:

python iterative.py
75 variables: [ab0(0,1), ac0(0,1), ad0(0,1), ae0(0,1), aB0(0,1), bc0(0,1), bd0(0,1), be0(0,1), bB0(0,1), cd0(0,1), ce0(0,1), cB0(0,1), de0(0,1), dB0(0,1), eB0(0,1), ab1(0,1), ac1(0,1), ad1(0,1), ae1(0,1), aB1(0,1), bc1(0,1), bd1(0,1), be1(0,1), bB1(0,1), cd1(0,1), ce1(0,1), cB1(0,1), de1(0,1), dB1(0,1), eB1(0,1), ab2(0,1), ac2(0,1), ad2(0,1), ae2(0,1), aB2(0,1), bc2(0,1), bd2(0,1), be2(0,1), bB2(0,1), cd2(0,1), ce2(0,1), cB2(0,1), de2(0,1), dB2(0,1), eB2(0,1), ab3(0,1), ac3(0,1), ad3(0,1), ae3(0,1), aB3(0,1), bc3(0,1), bd3(0,1), be3(0,1), bB3(0,1), cd3(0,1), ce3(0,1), cB3(0,1), de3(0,1), dB3(0,1), eB3(0,1), ab4(0,1), ac4(0,1), ad4(0,1), ae4(0,1), aB4(0,1), bc4(0,1), bd4(0,1), be4(0,1), bB4(0,1), cd4(0,1), ce4(0,1), cB4(0,1), de4(0,1), dB4(0,1), eB4(0,1)]
35: 670
17: 1351
8: 2632
4: 3949
2: 7917
constraint graph 189890
5078 nodes in both_constraints_5_5

The nice thing about this last approach is that you save a whole level of merging.

Or we could just merge it into the last constraint.
This saves the most on extraneous node creation:

python iterative.py
75 variables: [ab0(0,1), ac0(0,1), ad0(0,1), ae0(0,1), aB0(0,1), bc0(0,1), bd0(0,1), be0(0,1), bB0(0,1), cd0(0,1), ce0(0,1), cB0(0,1), de0(0,1), dB0(0,1), eB0(0,1), ab1(0,1), ac1(0,1), ad1(0,1), ae1(0,1), aB1(0,1), bc1(0,1), bd1(0,1), be1(0,1), bB1(0,1), cd1(0,1), ce1(0,1), cB1(0,1), de1(0,1), dB1(0,1), eB1(0,1), ab2(0,1), ac2(0,1), ad2(0,1), ae2(0,1), aB2(0,1), bc2(0,1), bd2(0,1), be2(0,1), bB2(0,1), cd2(0,1), ce2(0,1), cB2(0,1), de2(0,1), dB2(0,1), eB2(0,1), ab3(0,1), ac3(0,1), ad3(0,1), ae3(0,1), aB3(0,1), bc3(0,1), bd3(0,1), be3(0,1), bB3(0,1), cd3(0,1), ce3(0,1), cB3(0,1), de3(0,1), dB3(0,1), eB3(0,1), ab4(0,1), ac4(0,1), ad4(0,1), ae4(0,1), aB4(0,1), bc4(0,1), bd4(0,1), be4(0,1), bB4(0,1), cd4(0,1), ce4(0,1), cB4(0,1), de4(0,1), dB4(0,1), eB4(0,1)]
35: 670
17: 931
8: 1420
4: 2333
2: 5754
constraint graph 189890
5078 nodes in both_constraints_5_5


The other thing I like about the binary approach is that
it parallelizes.  And there's a lot of room to think of
heuristics that should allow more efficient merging.  Like,
should we prioritize related graphs because they give us
more pruning?  Or should we try to make graphs that merge
the most dissimilar choices so that we can get closer to
the ultimate standardized form faster?

Breaking news:

python iterative.py
105 variables: [ab0(0,1), ac0(0,1), ad0(0,1), ae0(0,1), af0(0,1), aB0(0,1), bc0(0,1), bd0(0,1), be0(0,1), bf0(0,1), bB0(0,1), cd0(0,1), ce0(0,1), cf0(0,1), cB0(0,1), de0(0,1), df0(0,1), dB0(0,1), ef0(0,1), eB0(0,1), fB0(0,1), ab1(0,1), ac1(0,1), ad1(0,1), ae1(0,1), af1(0,1), aB1(0,1), bc1(0,1), bd1(0,1), be1(0,1), bf1(0,1), bB1(0,1), cd1(0,1), ce1(0,1), cf1(0,1), cB1(0,1), de1(0,1), df1(0,1), dB1(0,1), ef1(0,1), eB1(0,1), fB1(0,1), ab2(0,1), ac2(0,1), ad2(0,1), ae2(0,1), af2(0,1), aB2(0,1), bc2(0,1), bd2(0,1), be2(0,1), bf2(0,1), bB2(0,1), cd2(0,1), ce2(0,1), cf2(0,1), cB2(0,1), de2(0,1), df2(0,1), dB2(0,1), ef2(0,1), eB2(0,1), fB2(0,1), ab3(0,1), ac3(0,1), ad3(0,1), ae3(0,1), af3(0,1), aB3(0,1), bc3(0,1), bd3(0,1), be3(0,1), bf3(0,1), bB3(0,1), cd3(0,1), ce3(0,1), cf3(0,1), cB3(0,1), de3(0,1), df3(0,1), dB3(0,1), ef3(0,1), eB3(0,1), fB3(0,1), ab4(0,1), ac4(0,1), ad4(0,1), ae4(0,1), af4(0,1), aB4(0,1), bc4(0,1), bd4(0,1), be4(0,1), bf4(0,1), bB4(0,1), cd4(0,1), ce4(0,1), cf4(0,1), cB4(0,1), de4(0,1), df4(0,1), dB4(0,1), ef4(0,1), eB4(0,1), fB4(0,1)]
45: 990
22: 1376
11: 2123
5: 4952
2: 37250
constraint graph 270572
6736 nodes in both_constraints_6_5


'''
