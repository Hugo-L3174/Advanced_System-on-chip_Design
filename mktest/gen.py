from math import gcd
from random import randint
import sys

def prng(seed):
    tabs = [1, 2, 22, 32]
    # convert int32 to array of bits[bit0,...,bit31]
    bits = [int(x, 2) for x in reversed(format(seed, "032b"))]
    # calculate new input from feedback xor tree
    feedback = bits[tabs[0] - 1]
    for i in tabs[1:]:
        feedback = feedback ^ bits[i - 1]
    bits = [feedback] + bits[:-1]
        # build integer from bits
    out = 0
    for bit in reversed(bits):
        out = (out << 1) | bit
    return out


listA = []
listB = []
listC = []

for i in range(int(sys.argv[1])):
    a = randint(0, 4096)
    b = randint(0, 4096)
    c = prng(a)
    listA.append(a)
    listB.append(b)
    listC.append(c)

print("src0 = " + str(listA))
print("src1 = " + str(listB))
print("ref = " + str(listC))