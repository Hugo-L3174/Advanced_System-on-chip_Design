from pymtl3 import *
from math import gcd
from pymtl3.passes.yosys import TranslationImportPass
import random


class GCDUnitFL(Component):
    def construct(s, type):
        s.in_a = InPort(type)
        s.in_b = InPort(type)

        s.out_result = OutPort(type)

        @s.update
        def step():
            s.out_result = gcd(s.in_a, s.in_b)


class GCDUnitRTL(Component):
    def construct(s, type):
        s.in_a = InPort(type)
        s.in_b = InPort(type)
        s.reset = InPort(b1)

        s.out = OutPort(type)

        s.state = Wire(b1)
        s.S0 = b1(0)
        s.S1 = b1(1)

        s.a = Wire(type)
        s.b = Wire(type)

        @s.update
        def state_update():
            if s.reset:
                s.state = s.S0
            else:
                s.state = s.S1

        @s.update
        def step():
            if s.state == s.S0:
                s.a = s.in_a
                s.b = s.in_b
            else:
                while True:
                    if s.a < s.b:
                        s.a, s.b = s.b, s.a
                    elif s.b != 0:
                        s.a -= s.b
                    else:
                        s.out = s.a
                        return


def test_fl():
    model = GCDUnitFL(b8)
    model.elaborate()
    sim = model.apply(SimpleSim)
    model.reset()

    randA = random.randint(0, 255)
    model.in_a = randA
    print(randA)

    randB = random.randint(0, 255)
    model.in_b = randB
    print(randB)

    model.tick()
    print(model.out_result)
    assert model.out_result == gcd(randA, randB)


def test_rtl():
    dut = GCDUnitRTL(b8)
    dut.elaborate()

    dut.yosis_translate_import = True
    dut = TranslationImportPass()(dut)

    # Create a simulator
    dut.dump_vcd = True
    dut.vcd_file_name = "gcd"
    dut.elaborate()
    dut.apply(SimulationPass)
    dut.sim_reset()

    randA = random.randint(0, 255)
    dut.in_a = b8(randA)
    print(randA)

    randB = random.randint(0, 255)
    dut.in_b = b8(randB)
    print(randB)
    dut.reset = b1(1)
    dut.tick()
    dut.reset = b1(0)
    dut.tick()
    assert dut.out == gcd(randA, randB)

# TODO: 10 iterations of same test
# TODO: Some more tests and documentation and comment

test_rtl()
