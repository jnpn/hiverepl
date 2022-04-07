'''
tree { node ; children ; leaf? }

dfs , bfs

repl/s path &rest {
  .     show node
  N RET down child
  ..    up
  ! S   sto
  @ S   rcl
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

    def from_inode(self, inode):
        return Node(inode, self.hive())

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
        lim = 16
        name = self.hive().node_name(self.node())
        name = name if len(name) < lim else name[:14] + '...'
        num = self.node()
        kind = '.' if self.is_leaf() else ''
        return f'{name} {num}{kind}'

class Treewalk():
    def __init__(self, tree):
        self.tree = tree
        self.path = [tree]
        self.mem = {}

    def top(self):
        if len(self.path) > 0:
            return self.path[-1]

    def rst(self, mem_too=False):
        self.path = [self.tree]
        if mem_too:
            self.meme = {}

    def up(self):
        if len(self.path) > 0:
            return self.path.pop()

    def down(self, node):
        self.path.append(node)

    def sto(self, name):
        self.mem[name] = self.path[:]
        self.rst()

    def rcl(self, name):
        if name in self.mem:
            self.path = self.mem[name][:]

    def __repr__(self):
        a = f'path: {self.path}'
        b = f'-----'
        return '\n'.join([a,b])

def wepl(treewalk):
    '''
    .     show node
    N RET down child
    ..    up
    ! S   sto
    @ S   rcl
    / S   seek
    : S   seek*
    '''
    while True:
        print(treewalk)
        ans = input("> ")
        if ans == ".":
            print(treewalk.top())
        if ans == ",":
            for i,n in enumerate(treewalk.top().children()):
                print(i,n)
        elif ans.isdigit():
            n = int(ans)
            c = treewalk.top().children()[n]
            treewalk.down(c)
        elif ans == "q":
            break
        elif ans == "r":
            treewalk.rst()
            print('soft reset')
        elif ans == "rr":
            treewalk.rst(mem_too=True)
            print('hard reset')
        elif ans == "..":
            c = treewalk.up()
            print(c)
        elif ans == "!":
            print('TODO sto "..."')
            name = '...'
            treewalk.sto(name)
        elif ans == "@":
            print('TODO rcl "..."')
            name = '...'
            treewalk.rcl(name)
        elif ans == "/ S":
            print('TODO', 'search first')
        elif ans == ": S":
            print('TODO', 'search all')
        else:
            print(ans, '?')

DEBUG = True

def debug(o):
    if DEBUG:
        print(o)

HIVEFN = "/media/noob/ACER320/Users/ACER/NTUSER.DAT"
H = hivex.Hivex(HIVEFN)
