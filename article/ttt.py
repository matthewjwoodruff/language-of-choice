def average(ns):
    ns = list(ns)
    return float(sum(ns)) / len(ns)

def memoize(f):
    def memo_f(*args):
        try: return memo_f._memos[args]
        except KeyError:
            memo_f._memos[args] = value = f(*args)
            return value
    memo_f._memos = dict()
    return memo_f

ways_to_win = (0o700, 0o070, 0o007, 0o444, 0o222, 0o111, 0o421, 0o124)
def is_won(grid):
    p, q = grid
    return any(way == (way & q) for way in ways_to_win)

def apply_move(grid, move):
    p, q = grid
    bit = 1 << move
    return (q, p|bit) if 0 == (bit & (p | q)) else None

def successors(grid):
    return filter(None, (apply_move(grid, move) for move in range(9)))

@memoize
def drunk_value(grid):
    if is_won(grid): return -1
    succs = list(successors(grid))
    return -average(map(drunk_value, succs)) if succs else 0

@memoize
def evaluate(grid):
    if is_won(grid): return -1
    succs = list(successors(grid))
    return -min(map(evaluate, succs)) if succs else 0

def max_play(grid):
    return min(successors(grid), key=lambda succ: (evaluate(succ), drunk_value(succ)))

empty_grid = (0, 0)
def exhaust(human_to_move):
    for AI_to_move in successors(human_to_move):
        succs = list(successors(AI_to_move))
        if succs is not None and len(succs) > 0:
            all_responses[AI_to_move] = response = max_play(AI_to_move)
            exhaust(response)
        else:
            all_responses[AI_to_move] = tuple(reversed(AI_to_move))
all_responses = dict()
exhaust(empty_grid)
print("There are {} games under max_play".format(len(all_responses)))

####

class Node(object):
    def evaluate(self, env):
        abstract
    def __call__(self, if0, if1):
        return Choice(self, if0, if1)

class ConstantNode(Node):
    def __init__(self, value): self.value = value
    def __repr__(self): return repr(self.value)
    def evaluate(self, env): return self.value

class VariableNode(Node):
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
    def evaluate(self, env): return env[self]

class ChoiceNode(Node):
    def __init__(self, index, if0, if1):
        self.index, self.if0, self.if1 = index, if0, if1
    def __repr__(self):
        return "%r(%r, %r)" % (self.index, self.if0, self.if1)
    def evaluate(self, env):
        branch = (self.if0, self.if1)[self.index.evaluate(env)]
        return branch.evaluate(env)

Variable = VariableNode
Constant = memoize(ConstantNode)
const0,const1 = Constant(0), Constant(1)

#def Choice(index, if0, if1):
#    if if0 == if1:
#        return if0
#    elif (if0, if1) == (const0, const1):
#        return index
#    else:
#        return ChoiceNode(index, if0, if1)

Choice = memoize(ChoiceNode)


squares = range(9)
def combine(xs, os): return tuple(xs) + tuple(os)

XO_variables = combine((Variable("x{}".format(k)) for k in squares),
                       (Variable("o{}".format(k)) for k in squares))

def XO_values(os_xs):
    Os, Xs = os_xs
    return combine(((Xs>>k)&1 for k in squares),
                   ((Os>>k)&1 for k in squares))

Choice._memos.clear()

O_tables = [{grid: (Os2 >>square)&1
    for grid, (_, Os2) in all_responses.items()}
    for square in range(9)]
O_nodes = [express(XO_variables, {XO_values(grid): value
                                 for grid, value in table.items()})
           for table in O_tables]

print("{} memos".format(len(Choice._memos)))
