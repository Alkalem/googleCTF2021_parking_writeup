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