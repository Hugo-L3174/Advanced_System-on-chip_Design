from pymtl3 import *
from pymtl3.passes.yosys import TranslationImportPass
import random
# README: Just used the function prng in a Component to test if this works and it does. Maybe we think too complicated?
# Maybe we have to change it, when transforming to RTL.

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

class PrngUnitFL(Component):
    def construct(s, type):
        s.input = InPort(type)
        s.output = OutPort(type)

        @s.update
        def calc():
            s.output = prng(s.input)


class PrngUnit(Component):
    def construct(s, type):
        s.input = InPort(type)
        s.output = OutPort(type)
        
        s.tap0 = Bits1(1)
        s.tap1 = Bits2(2)
        s.tap2 = Bits5(22)
        s.tap3 = Bits6(32)
        
        @s.update
        def update():
            if s.reset: 
                s.output = type(0)
            else: 
                s.output = (s.input<<1)|(((s.input>>(s.tap0-1)&1)^((s.input>>(s.tap1-1))&1))^((s.input>>(s.tap2-1))&1))^((s.input>>(s.tap3-1))&1)
                
def test_fl():
    model = PrngUnitFL(b32)
    model.elaborate()
    sim = model.apply(SimpleSim)
    model.reset()
    
    randA = random.randint(0, 4294967295)
    #model.input = 3904692793
    model.input = randA
    print('FL input     :',"%d" %(model.input))
    for i in range(1,10):
        model.tick()
        model.input = model.output
        print('FL output',i,' :',"%d" %(model.input))
    print("")

    
def test_rtl():
    dut = PrngUnit(b32)
    dut.elaborate()

    dut.yosis_translate_import = True
    dut = TranslationImportPass()(dut)

    # Create a simulator
    dut.dump_vcd = True
    dut.vcd_file_name = "PRNG"
    dut.elaborate()
    dut.apply(SimulationPass)
    dut.sim_reset()   
    
    randA = random.randint(0, 4294967295)
   # dut.input = b32(3904692793)
    dut.input = b32(randA)
    print('RTL input    :',"%d" %(dut.input))
    for i in range(1 , 10):
        dut.tick()
        dut.input = dut.output
        print('RTL output',i,':',"%d" %(dut.input))
    assert dut.output == prng(prng(prng(prng(prng(prng(prng(prng(prng(randA)))))))))
    
test_fl()
test_rtl()