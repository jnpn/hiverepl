'''
tree { node ; children ; leaf? }

dfs , bfs

repl/s path &rest {
  .     show node
  N RET down child
  ..    up
  ! S   sto
  < S   rcl
  / S   seek
  : S   seek*
}
'''
import hivex
import datetime as d

class Tree:

    def root(self):
        pass

    def hive(self):
        pass

    def node(self):
        pass

    def children(self):
        pass

    def is_leaf(self):
        pass

def unroot(fn):
    hive = hivex.Hivex(fn)
    root = Node(hive.root(), hive)
    return root

class Node(Tree):

    def __init__(self, inode, hive):
        super().__init__()
        self.inode = inode
        self.HIVE = hive

    def hive(self):
        return self.HIVE

    def root(self):
        return self.hive().root()

    def node(self):
        return self.inode

    def children(self):
        H = self.hive()
        return [Node(n, self.hive()) for n in H.node_children(self.node())]

    # predicates

    def is_leaf(self):
        return len(self.children()) == 0

    def is_root(self):
        return self.node() == self.root()

    # display

    def __repr__(self):
        # name, leaf|node[, type, value]
        name = self.hive().node_name(self.node())
        num = self.node()
        kind = '.' if self.is_leaf() else ''
        return f'{name} {num}{kind}'

DEBUG = True

def debug(o):
    if DEBUG:
        print(o)

HIVEFN = "/media/noob/ACER320/Users/ACER/NTUSER.DAT"
H = hivex.Hivex(HIVEFN)

def root():
    return H.root()

def hdir(node):
    for n in H.node_children(node):
        print(f'{n: >12}:{H.node_name(n)}')

def hchildren(node):
    return [(n, H.node_name(n)) for n in H.node_children(node)]

def hshow(nodes):
    for idx, (node, name) in enumerate(nodes):
        print(f'{idx: >3}{node: >12}:{name}')

def hkv(value):
    return H.value_key(value), H.value_type(value), H.value_value(value)

def simp(n,l=10):
    return n if len(n) < l else n[:l-1] + '...'

def fst(t):
    return t[0]

def snd(t):
    return t[1]


def hrepl(root):
    ###
    # so many side effects it's unreal
    ###
    n = root
    paths = {}
    history = []
    run = True
    while run:
        children = hchildren(n)
        hshow(children)
        print('paths:', [k for k in paths.keys()])
        print('state:',n, [simp(H.node_name(n)) for n in history], len(children))
        ans = input('> ')
        lans = ans.split()
        debug(lans)
        for op in lans:
            if 'q' in op or 'Q' in op:
                run = False
            if op.startswith('s'):
                paths[op[1:]] = history[:]
                history = []
                n = root
            if op.startswith('S'):
                history = paths[op[1:]]
                n = history[-1]
            elif op == '?':
                print('show values ?')
            else:
                print(op)
                if op.isdigit():
                    d = int(op)
                    n = fst(children[d])
                    history.append(n)
                elif len(op) == 0:
                    n = fst(children[0])
                    history.append(n)
                elif op == 'r':
                    n = root
                    history = []
                    print('.reset')
                elif op == '..':
                    if len(history) > 1:
                        history.pop()
                        n = history[-1]
                        print('.up')
                    elif len(history) == 1:
                        n = root
                        history = []
                        print('.uptop')
                    else:
                        n = root
                        history = []
                        print('!top')
        if lans == []:
            n = fst(children[0])
            history.append(n)

def run():
    hrepl(root())
