from pymtl3 import *
from pymtl3.passes.yosys import TranslationImportPass
import random


def fib(i):
    if i > 1:
        x = fib(i - 1) + fib(i - 2)
    else:
        x = i
    return x


def fibI(n):
    x = 0
    y = 1
    z = 1
    for i in range(0, n):
        x = y
        y = z
        z = x + y
    return x


class FibonacciUnitFL(Component):
    def construct(s, type):
        s.input = InPort(type)
        s.output = OutPort(type)

        @s.update
        def update():
            s.output = fib(s.input)


class FibonacciUnit(Component):
    def construct(s, type):
        s.input = InPort(type)
        s.trigger = InPort(b1)
        s.output = OutPort(type)

        s.w_x = Wire(type)
        s.w_y = Wire(type)
        s.w_z = Wire(type)
        s.w_i = Wire(type)

        @s.update
        def update():
            if s.trigger:
                s.w_x = type(0)
                s.w_y = type(1)
                s.w_z = type(1)
                s.w_i = type(0)
            else:
                for i in range(0, s.input):
                    s.w_i += type(1)
                    s.w_x = s.w_y
                    s.w_y = s.w_z
                    s.w_z = s.w_x + s.w_y
                s.output = s.w_x


def test_fl():
    model = FibonacciUnit(b16)
    model.elaborate()
    sim = model.apply(SimpleSim)
    model.reset()

    model.input = 10
    model.trigger = 1

    while model.ready == 0:
        model.tick()
        #  TODO: Set in_new to 0  after init ?
    print(model.output)


def test_rtl():
    dut = FibonacciUnit(b16)
    dut.elaborate()

    dut.yosis_translate_import = True
    dut = TranslationImportPass()(dut)

    # Create a simulator
    dut.dump_vcd = True
    dut.vcd_file_name = "fibonacci"
    dut.elaborate()
    dut.apply(SimulationPass)
    dut.sim_reset()

    randA = random.randint(0, 15)
    dut.input = b8(randA)
    print(randA)

    dut.trigger = b1(1)
    dut.tick()
    dut.trigger = b1(0)
    dut.tick()
    print(dut.output)
    assert dut.output == fib(randA)

# TODO: Write test with a loop of ten tests
test_rtl()
