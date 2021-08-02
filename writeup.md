# Parking - From Rush hour to circuits
#### A write-up for Google CTF 2021 by Alkalem of the team KITCTF

In the beginning, we get this challenge description:
> It's so crowded today... Can you fit our car in?

and the following attachments:
* `game.py`
* `level1`
* `level2`
* `run.sh`

## TL;DR
Solving the challenge can be divided into three sections. First, we get a `game.py` which turns out to be a slightly modified version of Rush Hour with walls. We have to win `level2` to get the flag. Since this level is too large, we analyze the picture of the level that is generated at the beginning of the game. This marks the start of the second section. Now, we discover that the cars and walls form a circuit with a few repetitive structures of logic gates. Two blocks that are used particularly often are an equivalence gate and a structure consisting of two equivalence gates with a second output. From this circuit, we can deduce logic statements that need to be fulfilled for us to win. In the last section, we can solve these statements backward to find out the bits of our flag and calculate the flag as defined in the `game.py`. This gets us the flag.

## The game
The challenge description does not contain much useful information, so I started by viewing the provided resources. 
The challenge provides a game (`game.py`), two levels (`level1` and `level2`), and a shell script to start the game (`run.sh`).

If you know the game "Rush hour" and tried to solve this challenge, you might have noticed its similarity to the provided game. "Rush hour" is a puzzle game, with a board size of 6x6. Each puzzle has a starting configuration, and the player has to find a way to move one car across the board. The program we have been given implements a modified version of "Rush hour".

The python program starts by parsing a level from the file provided as the first command-line argument. We learn that the file structure is the following:
1. `<width> <height>`: the dimension of the board
2. `<x> <y> <width> <height> <movable>`: position, dimensions and type of a game object. `movable` can have values from `-2` to `1`. Meanings of these values:
    * `-2`: The object is the target car. Only one should exist. It is printed in red.
    * `-1`: A flag car. Multiple can exist. Are printed in green.
    * `0`: Walls. Not movable, printed in brown.
    * `1`: Normal cars, printed in gray.
3. Any number of repetitions of 2.

Next, the game prints a starting message to `stdout`. If the constant `DRAW` is `True` (the default state), the game saves the level as a picture before the first move (see the picture for `level1` in the next section) and shows the current state as a plotted figure after each move. 

The game can be played using the interactive mode or the terminal. The interactive mode allows moving one car in any direction by one field. This is done by clicking a car in the plot and dragging it in the direction of movement. The terminal takes commands of the format `<which> <dirx> <diry>` where `which` is the number of a car (determined by the car's position in the level file) and `dirx` and `diry` are the move distances in the respective directions. The game first tests whether a move is valid and, if so, moves the selected car and possibly reprints the figure. 

A move is valid, if the moved car does not collide with walls or other cars at the new position, and if the car can move in the specified direction. A car can not move horizontally if its width is `1`, and not move vertically if its height is `1`. (This validity check has some funny consequences, see the last section)

After each move the game checks, whether the player has won. This is the case if the target car was moved to a different position. On a win, the game prints the flag and exits. The flag is calculated from the position of the flag cars in the winning configuration. Each flag car contributes one bit, `1` if the current position differs from the starting position, `0` otherwise. The bits are ordered by the occurrence of the cars in the level file, grouped into bytes (for each byte the bit order is inverted), and converted to chars. The chars are framed with `CTF{<chars>}`. 
In conclusion, a real level should have exactly one winning configuration and a flag car count which is a multiple of `8`.

There are solvers for "Rush hour" (e.g. [see this article](https://www.michaelfogleman.com/rush/)), but they can take very long to find an optimal solution, even for small board sizes. 
Our version of the game additionally adds walls and special cars, the flag cars, and the target car. Additionally, we only have to move the target car by one field. This version would need a modified solver.

We now know the rules of the game and have an understanding of the provided program. To win the game, we have to move the target car. To find out the flag, we have to know the flag car positions for the winning configuration. To solve the challenge we could play `level2`, perhaps automated, until we reach the winning configuration or we could try to use a solver. But let us analyze the levels and the shell script first.

## The levels
From the shell script, we can deduce that `level1` is an easy level for testing, while `level2` contains the actual challenge. Furthermore, `level1` should be started with the environment `FLAG=0` to skip flag calculation.

`level1` has a dimension of 7x7, only one flag car and 5 cars in total. This level can be solved by hand and can be used to understand the rules and the program. Nevertheless, it is completely separate from `level2` and does not help with its solution. Its image is included to illustrate an exemplary level structure.
![initial1.png](initial1.png "An upscaled version of the initial configuration of \"level1\"")

The second level has a dimension of 655x7159, contains 64 flag cars, 1.106.761 walls, and 320.768 cars in total. This suggests, that a general solver might not be applicable for this level.  We also can not play and win this level by hand. For that reason, I used the level structure to reduce the problem complexity and write an efficient solver. The number of flag cars results in 8 chars in the flag which we have to find out. The number of walls suggests, that our options of moving cars might be heavily restricted. 

Next, I let the program generate the image for `level2` to examine its structure (included as `initial2.png`, too large for the write-up). Afterwards, I analyzed the structure of this level.

## The circuit
Looking at the structure of the `level2`, we immediately see many repetitive structures. Looking more closely, we find out that this structure resembles a circuit. This explains why the challenge is categorized as a hardware challenge. We do not have to play the game. We can analyze this circuit and deduce the 64 flag car bits to solve the challenge.

I included an illustration of the described structures at the end of the section.

The first structures we can observe are corridors surrounded by walls filled with cars in a way that all cars can be moved by one field if there is a free field at one end. These structures correspond to cables and can also only have two states, having a gap which makes the cars movable or not having one. I defined the former as signal value `1` and the latter as `0`.

The second type of structure is an intersection of two corridors. It is designed in a way, that the two intersecting corridors do not influence each others state. It corresponds to unconnected cables.

Then, we also have corridors splitting into two. The output corridors carry the same signal as the input corridor. This structure corresponds to branching cables.

Lastly, we have two structures corresponding to logic gates, an AND-gate, and an OR-gate. They work like their circuit counterparts, only with gaps instead of voltages as signals and with moving cars instead of flowing electrons.

From here on I will use the circuit terminology and describe the circuit structure of the level at a greater scale.
In the circuit, cables are grouped into pairs, one carrying the positive signal and one the negated signal. I defined that the upper-right cables carry the positive signal.
There are several inputs to the circuit, most of which are constant parameters, and the 64 flag cars as variable inputs. We have one output, the cable with the target car, which shall have the value `1`. 
At this scale, the cables and AND-/OR-gates mostly form two different blocks connected by cable pairs and a few additional AND-gates.

The first block is an equivalence-gate. From the inputs `a` and `b` it first computes `a ^ b (1), a ^ !b (2), !a ^ b (3) and !a ^ !b (4)` using four AND-gates and then ORs (1) and (4) together to output `x := a <-> b`.
![block1.png](block1.png "An equivalence gate in the level")

The second block uses the first one twice and adds a few additional cables and gates. We have three inputs `a`, `b`, and `c` as well as two outputs `x` and `y`. In the first section `z1 := a <-> c` and `z2 := a v c` are computed. Then, the first output is computed as `x := z1 <-> b`. From the second equivalence-gate, we also get `z3 := z1 v b`. The second output is computed as `y := z2 ^ z3`.
![block2.png](block2.png "A block of the second type in the level")

The circuit is ordered into 5 columns each containing 64 blocks of the same sort. The columns alternate between equivalence-gates and the second block, starting with equivalence-gates. As inputs, we have the variable flag car positions and 64 parameters in the first column. In the fourth and fifth columns, two additional sets of 64 parameters provide one input each. The remaining inputs are either outputs from the same or the previous column or are `1`. The positive output of the fifth column is linked with AND-gates to form the circuit output, the target signal.

In the following scan, you can see my illustration of the above section.
![circuits.jpg](circuits.jpg "My illustrations of the circuit structure of \"level2\"")

## The solver
To solve the challenge, I wrote a python script. It takes the parameters as inputs and calculates the flag by calculating the inputs necessary for the winning configuration in reverse, column by column. The parameters passed as input were read from the circuit by hand.

The solver uses three utility functions. Two of them calculate one unknown input for one of the two blocks when the outputs and the other inputs are known. The last one is a version of `printflag()` which is slightly modified from the original program to take a list of bits as input.

To solve the first block, one has to return the given input, if the output is `1`, and negate the input otherwise. To solve the second block this is used in two stages. First `z1` is calculated, then `a`. With all the inputs we can then calculate the second output `y`.

The solver calculates the unknown inputs starting with the last column. The inputs of the previously processed column are used as outputs of the next. For columns 2-4 the blocks have to be solved in a loop because the results for one block have to be used for the next one. Between column 4 and column 3 the inputs are rotated, because the last input of column 4 is the first input of column 3. When a flag car is not moved, its flag bit will be `1`, but the input to the first equivalence-gate will be `0`. For this reason, the flag bits are the negated inputs of the first column. Once the flag bits are calculated, the third utility function calculates and prints the flag.


``` python
BITS = 64

m = [1, 0,0,0,0, 1, 0,0, 1,1,1,1,1,1, 0,0,0, 1, 0,0, 1, 0, 1, 0, 1, 0,0,0,0, 1, 0,0, 1, 0,0,0,0, 1, 0,0, 1,1,1,1,1,1, 0,0,0, 1, 0,0, 1, 0, 1, 0, 1, 0,0,0,0, 1, 0,0]
n = [0,0,0, 1, 0,0, 1,1, 0,0, 1,1, 0, 1,1,1, 0,0,0, 1, 0,0, 1,1, 0,0, 1,1, 0, 1,1,1, 0,0,0, 1, 0,0, 1,1, 0,0, 1,1, 0, 1,1,1, 0,0,0, 1, 0,0, 1,1, 0,0, 1,1, 0, 1,1,1]
o = [1, 0, 1, 0, 1,1,1,1,1,1, 0, 1,1,1,1, 0,0,0, 1,1, 0,0, 1, 0, 1,1,1, 0, 1, 0, 1, 0,0, 1, 0, 1, 0, 1, 0, 1, 0, 1,1,1,1, 0, 1, 0,0, 1, 0, 1, 0, 1,1,1, 0,0,0,0,0, 1,1,1]

p = 1
q = 1
r = 1
s = 1

target = 1

### Functions ###

def solveBlock1For(a, x):
    return a if x else int(not a)

def solveBlock2For(b, c, x):
    z1 = solveBlock1For(b, x)
    a = solveBlock1For(c, z1)
    z2 = a or c
    z3 = z1 or b
    return (int(a), int(z2 and z3))

def printflag(flag_bits):
    # if os.environ.get("FLAG") == "0":
    #    print("<flag would be here if on real level>")
    #    return
    bits = ""
    for bit in flag_bits:
        # orig_xy = flagblocks[fl]
        # new_xy = tuple(blocks[fl][:2])
        # bit = 0 if orig_xy == new_xy else 1
        bits += str(bit)

    flag = b"CTF{"
    while bits:
        byte, bits = bits[:8], bits[8:]
        flag += bytes([ int(byte[::-1], 2) ])
    flag += b"}"
    
    print(flag)

def main():
    assert len(m) == BITS
    assert len(n) == BITS
    assert len(o) == BITS

    z = [solveBlock1For(a, target) for a in o]
    print(z)
    
    y = [None] * BITS
    for i in range(BITS):
        global s
        a, s = solveBlock2For(s, n[i], z[i])
        y[(i + 1) % BITS] = a
    print(y)

    x = [None] * BITS
    for i in range(BITS)[::-1]:
        global r
        r = solveBlock1For(r, y[i])
        x[i] = r
    print(x)

    w = [None] * 64
    for i in range(BITS):
        global p, q
        p, q = solveBlock2For(q, p, x[i])
        w[i] = p
    print(w)

    flag_bits = [int(not solveBlock1For(m[i], w[i])) for i in range(BITS)]
    print(flag_bits)
    printflag(flag_bits)



if __name__ == '__main__':
    main()
```

When this solver is run, it calculates the input list from right to left and in the end prints the flag: `CTF{2TheBr1m}`.

## Concluding Notes
This write-up is quite detailed, but it does not describe the problems we had as a team while solving the challenge and does not list dead ends. Therefore, I want to note for others who struggled with this challenge: It took us longer to solve the challenge than to simply work through the steps in this write-up. I struggled a few hours with the circuit to remember my knowledge of logic gates and recognize the gates which are used. Additionally, it took me a while to parse the parameters by hand. When I first ran the solver, two of the parameter bits were wrong, so I got `CTF{2TheBr\x11m}`. I excluded such problems from the above write-up to make it easier to read.

Here, I want to discuss some consequences of the implementation of `can_move()` in `game.py`. Technically, cars of dimension 1x1 would not be able to move, but this does not occur in the provided levels. An actual problem is, that the game allows teleportation of a car in its moving direction. The game does not check for collisions on the traveling path. If this is used in `level2`, the solution is no longer unique and the shortest possible solution is way shorter. In this level, cars could be teleported between intersections at the same height. You could create a gap of 2 squares at an intersection at the left side of the level and teleport a 2x1-car from an intersection at the right end of the level into this gap. If this bug is used, the flag printed in the end probably makes no sense, although the game says you have won. In conclusion, this bug does not help with finding the flag, but I mention it here because I found it funny.

In the end, I want to mention a few ideas on automating the solving process of the challenge. In theory, it might be possible to use a constraint solver, if the positions of the cars could be translated into constraints just using the input file. However, none of us had an idea on how to implement this approach. So, we did not try to use it. One step that took quite a while and is very error-prone is the parsing of the parameters. This could be automated if we take the organization of the input file into account. Here is a script that parses the parameters from the input file. (I found out the positions of the relevant walls by painting walls and cars green). I wrote this after the end of the CTF just as a proof of concept:

``` python
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
```

Thank you for reading this write-up. I hope you find it clear to understand. I really enjoyed playing this challenge, and I hope you can, too. Hopefully, I could help you overcome problems you might have had when trying to solve this challenge or show you an alternative solution to try out yourself.
Thanks to the challenge authors for creating this great challenge! Special thanks go to everyone who proofread this write-up and send me feedback to improve it!