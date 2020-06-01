"""
==========================================================================
MiscRTL.py
==========================================================================
Miscellaneous components for building the RTL processor.

Author : Shunning Jiang
  Date : June 13, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.rtl import RegRst

from .TinyRV0InstRTL import *

# State Constants

SNOOP = Bits1(0)
WAIT = Bits1(1)


# -------------------------------------------------------------------------
# DropUnit
# -------------------------------------------------------------------------
# Drop Unit drops a transaction between any two models connected by
# using the val-rdy handshake protocol. It receives a drop signal as an
# input and if the drop signal is high, it will drop the next message
# it sees.

class DropUnitRTL(Component):

    def construct(s, Type):

        s.drop = InPort(Bits1)
        s.in_ = RecvIfcRTL(Type)
        s.out = SendIfcRTL(Type)

        s.in_.msg //= s.out.msg

        s.snoop_state = RegRst(Bits1, reset_value=0)

        @s.update
        def state_transitions():
            curr_state = s.snoop_state.out

            s.snoop_state.in_ = curr_state

            if s.snoop_state.out == SNOOP:
                # we wait if we haven't received the response yet
                if s.drop & (~s.out.rdy | ~s.in_.en):
                    s.snoop_state.in_ = WAIT

            elif s.snoop_state.out == WAIT:
                # we are done waiting if the response arrives
                if s.in_.en:
                    s.snoop_state.in_ = SNOOP

        @s.update
        def state_output_val():
            if s.snoop_state.out == SNOOP:
                # if in is enabled, s.in_.rdy and s.out.rdy must be True
                s.out.en = s.in_.en & ~s.drop

            elif s.snoop_state.out == WAIT:
                s.out.en = b1(0)

            else:
                s.out.en = b1(0)

        @s.update
        def state_output_rdy():
            if s.snoop_state.out == SNOOP:
                s.in_.rdy = s.out.rdy

            elif s.snoop_state.out == WAIT:
                s.in_.rdy = b1(1)

            else:
                s.in_.rdy = b1(1)


# -------------------------------------------------------------------------
# Generate intermediate (imm) based on type
# -------------------------------------------------------------------------

class ImmGenRTL(Component):

    # Interface

    def construct(s):
        dtype = mk_bits(32)

        s.imm_type = InPort(Bits3)
        s.inst = InPort(dtype)
        s.imm = OutPort(dtype)

        @s.update
        def up_immgen():
            s.imm = dtype(0)

            # Always sext!
            if s.imm_type == b3(0):  # I-type
                s.imm = concat(sext(s.inst[I_IMM], 32))

            elif s.imm_type == b3(2):  # B-type
                s.imm = concat(sext(s.inst[B_IMM3], 20),
                               s.inst[B_IMM2],
                               s.inst[B_IMM1],
                               s.inst[B_IMM0],
                               Bits1(0))

            elif s.imm_type == b3(1):  # S-type
                s.imm = concat(sext(s.inst[S_IMM1], 27),
                               s.inst[S_IMM0])
            elif s.imm_type == b3(3):  # U-type
                s.imm = concat(sext(s.inst[U_IMM], 32))
            elif s.imm_type == b3(4):  # J-type
                s.imm = concat(sext(s.inst[J_IMM3], 12),
                               s.inst[J_IMM2],
                               s.inst[J_IMM1],
                               s.inst[J_IMM0],
                               Bits1(0))


# -------------------------------------------------------------------------
# ALU
# -------------------------------------------------------------------------

class AluRTL(Component):

    def construct(s, nbits=32):
        dtype = mk_bits(nbits)

        s.in0 = InPort(dtype)
        s.in1 = InPort(dtype)
        s.fn = InPort(Bits5)

        s.out = OutPort(dtype)
        s.ops_ne = OutPort(Bits1)

        @s.update
        def comb_logic():
            if s.fn == b5(0):
                s.out = s.in0                                   # COPY OP0
                #print(" s.out: ", s.out)
                s.ops_ne = s.in0 != s.in1                       # BNE
            elif s.fn == b5(1):
                s.out = s.in1                                   # COPY OP1
                s.ops_ne = s.in0 == s.in1                       # BEQ
            elif s.fn == b5(2):
                s.out = s.in0 + s.in1                           # ADD
                print("add: ", s.out)
            elif s.fn == b5(3):
                s.out = s.in0 << s.in1[0:5]                     # SLL
            elif s.fn == b5(4):
                s.out = s.in0 >> s.in1[0:5]                     # SRL
            elif s.fn == b5(5):
                s.out = s.in0 & s.in1                           # AND
            elif s.fn == b5(6):
                s.out = s.in0 - s.in1                           # SUB
            elif s.fn == b5(7):
                s.out = s.in0 | s.in1                           # OR
            elif s.fn == b5(8):
                s.out = s.in0 ^ s.in1                           # XOR
            elif s.fn == b5(9):
                s.out = s.in0 * s.in1                           # MUL
            elif s.fn == b5(10):                                # SLT
                if (s.in0 < s.in1):
                    if (s.in1 > 0x7FFFFFFF):
                        if(s.in0 > 0x7FFFFFFF):
                            s.out = b32(1)
                        else:
                            s.out = b32(0)
                    else:
                        s.out = b32(1)
                elif(s.in0 > 0x7FFFFFFF):
                    if (s.in1 > 0x7FFFFFFF):
                        s.out = b32(0)
                    else:
                        s.out = b32(1)
                else:
                    s.out = b32(0)
            elif s.fn == b5(11):                                # SLTU
                if (s.in0 < s.in1):
                    s.out = b32(1)
                else:
                    s.out = b32(0)

            elif s.fn == b5(12):                                # SRA
                if (s.in0 > 0x7FFFFFFF):
                    s.out = (s.in0 >> s.in1[0:5]) | (
                        b32(0xFFFFFFFF) << (b32(32)-s.in1[0:5]))
                else:
                    s.out = s.in0 >> s.in1[0:5]                 # SRL
            elif s.fn == b5(13):                                # JAL
                s.out = s.in0 + b32(4)
                s.ops_ne = s.in0 != s.in1
            elif s.fn == b5(14):                                # LUI
                s.out = s.in1 << 12
            elif s.fn == b5(15):                                # AUIPC
                s.out = s.in0 + (s.in1 << 12)
            elif s.fn == b5(16):  # todo IMPLEMENTATION
                s.out = (s.in0 & 0xFFFFFFFE) + b32(4)
          #      print("jalr out: ", s.out)
            elif s.fn == b5(17):                                # BGE
                if s.in1 > 0x7FFFFFFF:
                    if s.in0 > 0x7FFFFFFF:
                        s.ops_ne = s.in0 >= s.in1
                    else:
                        s.ops_ne = s.in1 >= s.in0
                elif s.in0 > 0x7FFFFFFF:
                    s.ops_ne = s.in1 >= s.in0
                else:
                    s.ops_ne = s.in0 >= s.in1
            elif s.fn == b5(18):                                # BLT
                if s.in1 > 0x7FFFFFFF:
                    if s.in0 > 0x7FFFFFFF:
                        s.ops_ne = s.in1 > s.in0
                    else:
                        s.ops_ne = s.in0 > s.in1
                elif s.in0 > 0x7FFFFFFF:
                    s.ops_ne = s.in0 > s.in1
                else:
                    s.ops_ne = s.in1 > s.in0
            elif s.fn == b5(19):                                # BGEU
                s.ops_ne = s.in0 >= s.in1
            elif s.fn == b5(20):                                # BLTU
                s.ops_ne = s.in1 > s.in0
            else:
                s.out = dtype(0)  # Unknown
                print("")
                print("   in0: ", s.in0, "in1: ", s.in1, "ge", s.ops_ne)
                print("")
               # s.ops_ne = s.in0 != s.in1

    def line_trace(s):
        op_dict = {0: " +", 1: "c0", 2: "c1", 3: "<< ", 4: " &"}
        return "[{}({} ){} >>> {}]".format(s.in0, op_dict[int(s.fn)], s.in1, s.out)


class MaskRTL(Component):
    def construct(s, nbits=32):
        dtype = mk_bits(nbits)

        s.in0 = InPort(dtype)
        s.sel = InPort(Bits3)

        s.out = OutPort(dtype)
        @s.update
        def comb_logic():
            print("in", s.in0)
            if s.sel == b3(0):  # Just pass through
                s.out = dtype(s.in0)
            elif s.sel == b3(1):  # lhu
                s.out = dtype(s.in0[0:16])
                print(" lhu: ", s.out)
            elif s.sel == b3(2):  # lbu
                s.out = dtype(s.in0[0:8])
                print("lbu")
            elif s.sel == b3(3):  # lh
                if s.in0 > 0x7FFFFFFF:
                    s.out = dtype(s.in0[0:16])
                    print("lh")
                else:
                    s.out = b32(0xFFFF0000) + b32(s.in0[0:16])
                    print("lh2")
            elif s.sel == b3(4):  # lb
                if s.in0 > 0x7FFFFFFF:
                    s.out = dtype(s.in0[0:8])
                    print("lb")
                else:
                    s.out = b32(0xFFFFFF00) + b32(s.in0[0:8])
                    print("lb2")
