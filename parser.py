import sys

# parse walls from level file

walls = {}
boardfile = open(sys.argv[1]).read()
header, boardfile = boardfile.split("\n", 1) # discard header

for line in boardfile.splitlines():
    if not line.strip(): continue
    x,y,w,h,movable = [int(x) for x in line.split()]

    if movable == 0: # here, only walls are relevant
        walls[(x, y)] = (w,h)

# parse parameters

m = []
n = []
o = []

Y_DELTA = 108 # lines until structures are repeating
m1_pos = (5, 198)
n1_pos = (377, 318)
o1_pos = (575, 198)

def parseParameter(positions, check, params):
    x = positions[0]
    for i in range(64):
        y = positions[1] + i * Y_DELTA
        assert((x, y) in walls)
        wall = walls[(x, y)]
        param = 1 if check(wall) else 0
        params.append(param)

def checkParam(wall):
    w, h = wall
    return h < 4

parseParameter(m1_pos, checkParam, m)
parseParameter(n1_pos, checkParam, n)
parseParameter(o1_pos, checkParam, o)

print('m: {}'.format(m))
print('n: {}'.format(n))
print('o: {}'.format(o))