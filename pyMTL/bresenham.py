import random
import time

# import pygame

from pymtl3 import *
from pymtl3.passes.yosys import TranslationImportPass
import random


# s = 1000
# width = s
# height = s
#
# screen = pygame.display.set_mode((width, height))
#
#
# def random_lines():
#    sum = 0
#    for x in range(1000):
#        start = time.time()
#        r = random.randint(0, 255)
#        g = random.randint(0, 255)
#        b = random.randint(0, 255)
#        x0 = random.randint(0, width - 1)
#        x1 = random.randint(0, width - 1)
#        y0 = random.randint(0, height - 1)
#        y1 = random.randint(0, height - 1)
#        line(x0, y0, x1, y1, r, g, b)
#        pygame.display.flip()
#        sum += 1. / (time.time() - start)
#    print(sum / 1000)
#
#
# def line(x0, y0, x1, y1, r, g, b):
#    dx = abs(x1 - x0)
#    dy = abs(y1 - y0)
#    sx = 1 if x0 < x1 else -1
#    sy = 1 if y0 < y1 else -1
#    err = (dx >> 1) if dx > dy else -(dy >> 1)
#
#    while 1:
#        screen.set_at((x0, y0), (r, g, b))
#        # print "(" + str(x0) + "," + str(y0) + "),(" + str(x1) + "," + str(y1) + ")"
#        if (x0 == x1) & (y0 == y1):
#            break
#        e2 = err
#        if e2 > -dx:
#            err -= dy
#            x0 += sx
#        if e2 < dy:
#            err += dx
#            y0 += sy

def line2(x0, y0, x1, y1):
    arr = [0] * 32
    result = [0] * 2
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    if (x0 < x1):
        sx = 1;
    else:
        sx = -1;

    if (y0 < y1):
        sy = 1;
    else:
        sy = -1;

    if (dx > dy):
        err = (dx >> 1);
    else:
        err = -(dy >> 1);

    while (1):

        arr[y0 - 1] |= 1 << (x0 - 1);
        # print("{0:32b}".format(arr[y0-1]))

        #       print('x1:', x1, 'y1:', "%d" %(y1))
        if ((x0 == x1) & (y0 == y1)):
            break;

        e2 = err;
        if (e2 > -dx):
            err -= dy;
            x0 += sx;

        if (e2 < dy):
            err += dx;
            y0 += sy;

        # print('x0:', x0, 'y0:', "%d" %(y0))
    result[0] = x0
    result[1] = y0
    #    for i in range(0 , 31):
    #      #  for j in range(0 , 31):
    #       #    print( ((arr[i]>>j)&1), ' ', end="")
    #      #  print(bin(arr[i]))
    #        print("{0:32b}".format(arr[i]))
    #        #print('')
    return result


class BresenhamUnitFL(Component):
    def construct(s, type):
        s.x0 = InPort(type)
        s.y0 = InPort(type)
        s.x1 = InPort(type)
        s.y1 = InPort(type)
        s.output_x = OutPort(type)
        s.output_y = OutPort(type)

        @s.update
        def calc():
            x0 = s.x0
            y0 = s.y0
            x1 = s.x1
            y1 = s.y1
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)

            if (x0 < x1):
                sx = 1;
            else:
                sx = -1;

            if (y0 < y1):
                sy = 1;
            else:
                sy = -1;

            if (dx > dy):
                err = (dx >> 1);
            else:
                err = -(dy >> 1);

            while (1):
                # print('x0:', x0, 'y0:', "%d" % (y0))
                s.output_x = x0
                s.output_y = y0
                if ((x0 == x1) & (y0 == y1)):
                    break;
                e2 = err;
                if (e2 > -dx):
                    err -= dy;
                    x0 += sx;
                if (e2 < dy):
                    err += dx;
                    y0 += sy;

class BresenhamUnitRTL(Component):
    def construct(s, type):
        s.trigger = InPort(b1)
        s.x0 = InPort(type)
        s.y0 = InPort(type)
        s.x1 = InPort(type)
        s.y1 = InPort(type)
        s.valid = OutPort(b1)
        s.output_x = OutPort(type)
        s.output_y = OutPort(type)

        s.state = Wire(b2)
        s.S0 = b3(0)
        s.S1 = b3(1)
        s.S2 = b3(2)
        s.S3 = b3(3)
        s.nextState = Wire(b2)

        s.w_x0 = Wire(type)
        s.w_y0 = Wire(type)
        s.w_x1 = Wire(type)
        s.w_y1 = Wire(type)

        s.w_valid = Wire(b1)

        s.w_dx = Wire(type)
        s.w_dy = Wire(type)

        s.w_sx = Wire(type)
        s.w_sy = Wire(type)

        s.w_err = Wire(type)
        s.w_e2 = Wire(type)

        @s.update
        def update():

            if s.reset:
                s.state = s.S0
                s.w_valid = b1(0)
                s.w_x0 = type(0)
                s.w_y0 = type(0)
                s.w_x1 = type(0)
                s.w_y1 = type(0)
                s.w_dx = type(0)
                s.w_dy = type(0)
            else:
                s.state = s.nextState

                if s.state == s.S0:
                    if s.trigger:               #assign initial values
                        s.w_valid = b1(0)
                        s.w_x0 = s.x0
                        s.w_y0 = s.y0
                        s.w_x1 = s.x1
                        s.w_y1 = s.y1
                        s.w_dx = s.x1 - s.x0
                        s.w_dy = s.y1 - s.y0
                        s.nextState = s.S1
                    else:
                        s.nextState = s.S0

                #  "The less than and greater than  operators  always  treat  the  operands  as  un-signed"
                # www.csl.cornell.edu/courses/ece4750/handouts/ece4750-tut3-pymtl.pdf page 9
                elif s.state == s.S1:
                    if s.w_dx[5] == 0:          # if dx >= 0 (i don't know how to parametrize that part)
                        s.w_sx = type(1)
                    else:
                        s.w_dx = 0 - s.w_dx     # else abs(dx)
                        s.w_sx = type(-1)
                    if s.w_dy[5] == 0:          # if dy >= 0
                        s.w_sy = type(1)
                    else:
                        s.w_dy = 0 - s.w_dy     # else abs(dy)
                        s.w_sy = type(-1)
                    s.nextState = s.S2
                elif s.state == s.S2:
                    if s.w_dx > s.w_dy:         # both values >=0
                        s.w_err = s.w_dx >> 1
                    else:
                        s.w_err = 0 - (s.w_dy >> 1) # err can have neg value
                    s.nextState = s.S3
                elif s.state == s.S3:
                    s.w_e2 = s.w_err
                    if s.w_e2[5] == 0:          # if e2 > 0
                                                # then we dont need to check if (e2 > -dx) - it is
                        s.w_err -= s.w_dy       # no problem with two's complement arithmetics
                        s.w_x0 += s.w_sx
                        if (s.w_e2 < s.w_dy):   # no problem with this comparison - e2 always >= 0
                            s.w_err += s.w_dx
                            s.w_y0 += s.w_sy
                    else:                       # here we know that e2 < 0 and (0 - dx) < 0
                        if s.w_e2 > (0-s.w_dx): # and we can compare two "negative" vals normal way
                            s.w_err -= s.w_dy
                            s.w_x0 += s.w_sx
                                                # here we know that e2 < 0 and dy > 0
                        s.w_err += s.w_dx       # then we dont need to check if (e2 < dy) - it is
                        s.w_y0 += s.w_sy
                    if (s.w_x0 == s.w_x1) & (s.w_y0 == s.w_y1): #check if algorithm has finished
                        s.w_valid = b1(1)
                        s.nextState = s.S0
                    else:
                        s.nextState = s.S3

            s.output_x = s.w_x0
            s.output_y = s.w_y0
            s.valid = s.w_valid

def test_fl():
    model = BresenhamUnitFL(b6)
    model.elaborate()
    sim = model.apply(SimpleSim)
    for i in range(1, 100):
        model.reset()
        randA = random.randint(1, 32)
        randB = random.randint(1, 32)
        randC = random.randint(1, 32)
        randD = random.randint(1, 32)
        model.x0 = randA
        model.y0 = randB
        model.x1 = randC
        model.y1 = randD
        print('x0:', randA, 'y0:', randB, 'x1:', randC, 'y1:', randD)
        model.tick()
        print('output_x: ', model.output_x)
        print('output_y: ', model.output_y)
        print("")
        result = line2(randA, randB, randC, randD)
        assert model.output_x == result[0]
        assert model.output_y == result[1]


def test_rtl():

    dut = BresenhamUnitRTL(b6)
    dut.elaborate()

    dut.yosis_translate_import = True
    dut = TranslationImportPass()(dut)

    # Create a simulator
    dut.dump_vcd = True
    dut.vcd_file_name = "Bresenham"
    dut.elaborate()
    dut.apply(SimulationPass)
    dut.sim_reset()
    for i in range(1, 100):

        randA = random.randint(1, 32)
        randB = random.randint(1, 32)
        randC = random.randint(1, 32)
        randD = random.randint(1, 32)

        dut.x0 = b6(randA)
        dut.y0 = b6(randB)
        dut.x1 = b6(randC)
        dut.y1 = b6(randD)
        print('x0:', randA, 'y0:', randB, 'x1:', randC, 'y1:', randD)
        dut.tick()
        dut.trigger = b1(1)
        dut.tick()
        dut.trigger_i = b1(0)
        while dut.valid == b1(0):
            dut.tick()
        print('output_x: ', "%d" % (dut.output_x))
        print('output_y: ', "%d" % (dut.output_y))
        print('')
        result = line2(randA, randB, randC, randD)
        assert dut.output_x == result[0]
        assert dut.output_y == result[1]


# random_lines()
# pygame.quit()

test_fl()
test_rtl()
