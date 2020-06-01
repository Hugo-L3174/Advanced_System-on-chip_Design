"""
========================================================================
 TinyRV0 Instruction Type
========================================================================
 Instruction types are similar to message types but are strictly used
 for communication within a TinyRV0-based processor. Instruction
 "messages" can be unpacked into the various fields as defined by the
 TinyRV0 ISA, as well as be constructed from specifying each field
 explicitly. The 32-bit instruction has different fields depending on
 the format of the instruction used. The following are the various
 instruction encoding formats used in the TinyRV0 ISA.

  31          25 24   20 19   15 14    12 11          7 6      0
 | funct7       | rs2   | rs1   | funct3 | rd          | opcode |  R-type
 | imm[11:0]            | rs1   | funct3 | rd          | opcode |  I-type, I-imm
 | imm[11:5]    | rs2   | rs1   | funct3 | imm[4:0]    | opcode |  S-type, S-imm
 | imm[12|10:5] | rs2   | rs1   | funct3 | imm[4:1|11] | opcode |  S-type, B-imm


Author : Shunning Jiang
  Date : June 14, 2019
"""

from pymtl3 import *

# -------------------------------------------------------------------------
# TinyRV0 Instruction Fields
# -------------------------------------------------------------------------

OPCODE = slice(0, 7)
FUNCT3 = slice(12, 15)
FUNCT7 = slice(25, 32)

RD = slice(7, 12)
RS1 = slice(15, 20)
RS2 = slice(20, 25)
SHAMT = slice(20, 25)

I_IMM = slice(20, 32)
CSRNUM = slice(20, 32)

S_IMM0 = slice(7, 12)
S_IMM1 = slice(25, 32)

B_IMM0 = slice(8, 12)
B_IMM1 = slice(25, 31)
B_IMM2 = slice(7, 8)
B_IMM3 = slice(31, 32)

U_IMM = slice(12, 32)

J_IMM0 = slice(21, 31)
J_IMM1 = slice(20, 21)
J_IMM2 = slice(12, 20)
J_IMM3 = slice(31, 32)




# -------------------------------------------------------------------------
# TinyRV0 Instruction Definitions
# -------------------------------------------------------------------------

NOP = b8(0)   # 00000000000000000000000000000000

LW = b8(3)    # ?????????????????010?????0000011
SW = b8(8)    # ?????????????????010?????0100011

SLL = b8(9)   # 0000000??????????001?????0110011
SRL = b8(11)  # 0000000??????????101?????0110011
ADD = b8(15)  # 0000000??????????000?????0110011
SUB = b8(17)  # 0100000??????????000?????0110011
AND = b8(24)  # 0000000??????????111?????0110011
SLT = b8(29)  # 0000000??????????010?????0110011
SLTU = b8(30) # 0000000??????????011?????0110011
OR = b8(32)   # 0000000??????????110?????0110011
XOR = b8(33)  # 0000000??????????100?????0110011
SRA = b8(34)  # 0100000??????????101?????0110011

CSRR = b8(46)  # ????????????00000010?????1110011
CSRW = b8(47)  # ?????????????????001000001110011

SLTI = b8(18)  # ?????????????????010?????0010011
SLTIU = b8(19) # ?????????????????011?????0010011
ANDI = b8(20)  # ?????????????????111?????0010011
ADDI = b8(16)  # ?????????????????000?????0010011
ORI = b8(21)   # ?????????????????110?????0010011
XORI = b8(22)  # ?????????????????100?????0010011
SLLI = b8(23)  # 0000000??????????001?????0010011
SRLI = b8(25)  # 0000000??????????101?????0010011
SRAI = b8(26)  # 0100000??????????101?????0010011

AUIPC = b8(28) # ?????????????????????????0010111

LUI = b8(27)   # ?????????????????????????0110111

JAL = b8(35)   # ?????????????????????????1101111
JALR = b8(48)  # ?????????????????000?????1100111

BEQ = b8(37)  # ?????????????????000?????1100011
BNE = b8(31)  # ?????????????????001?????1100011
BLT = b8(38)  # ?????????????????100?????1100011
BGE = b8(39)  # ?????????????????101?????1100011
BLTU = b8(52) # ?????????????????110?????1100011
BGEU = b8(53) # ?????????????????111?????1100011

LB = b8(40)   # ?????????????????000?????0000011
LBU = b8(41)  # ?????????????????100?????0000011
LH = b8(42)   # ?????????????????001?????0000011
LHU = b8(43)  # ?????????????????101?????0000011

SB = b8(44)   # ?????????????????000?????0100011
SH = b8(45)   # ?????????????????001?????0100011

MUL = b8(49) # 0000001??????????000?????0110011


# CSRRX for accelerator
CSRRX = b8(36)  # 0111111?????00000010?????1110011

# ZERO inst
ZERO = b8(51)

# -------------------------------------------------------------------------
# TinyRV0 Instruction Disassembler
# -------------------------------------------------------------------------

inst_dict = {
    NOP: "nop", #
    LW: "lw",#
    SW: "sw",#
    SLL: "sll",#
    SRL: "srl",#
    ADD: "add",#
    SUB: "sub",#
    ADDI: "addi",#
    AUIPC: "auipc",
    AND: "and",#
    BNE: "bne",#
    CSRR: "csrr",#
    CSRW: "csrw",#
    CSRRX: "csrrx",#
    ZERO: "????",
    SLTI: "slti",
    SLTIU: "sltiu",
    ANDI: "andi",#
    ORI: "ori",#
    XORI: "xori",#
    SLLI: "slli",
    SRLI: "srli",#
    SRAI: "srai",
    LUI: "lui",
    SLT: "slt",
    SLTU: "sltu",
    OR: "or",#
    XOR: "xor",#
    SRA: "sra",
    JAL: "jal",
    JALR: "jalr",
    BEQ: "beq",
    BLT: "blt",
    BGE: "bge",
    BLTU: "bltu",
    BGEU: "bgeu",
    LB: "lb",
    LBU: "lbu",
    LH: "lh",
    LHU: "lhu",
    SB: "sb",
    SH: "sh",
    MUL: "mul"
}

# -------------------------------------------------------------------------
# CSR registers
# -------------------------------------------------------------------------

# R/W
CSR_PROC2MNGR = b12(0x7C0)

# R/O
CSR_MNGR2PROC = b12(0xFC0)


# -----------------------------------------------------------------------
# DecodeInstType
# -----------------------------------------------------------------------
# TinyRV0 Instruction Type Decoder

class DecodeInstType(Component):

    # Interface

    def construct(s):

        s.in_ = InPort(Bits32)
        s.out = OutPort(Bits8)

        @s.update
        def comb_logic():

            s.out = b8(ZERO)

            if s.in_ == 0b10011:
                s.out = NOP
            elif s.in_[OPCODE] == b7(0b0110011):
                if s.in_[FUNCT3] == b3(0b000):
                    if s.in_[FUNCT7] == b7(0b0100000):
                        s.out = SUB
                    elif s.in_[FUNCT7] == b7(0b0000000):
                        s.out = ADD
                    elif s.in_[FUNCT7] == b7(0b0000001):
                        s.out = MUL
                elif s.in_[FUNCT3] == b3(0b001):
                    s.out = SLL
                elif s.in_[FUNCT3] == b3(0b111):
                    s.out = AND
                elif s.in_[FUNCT3] == b3(0b010):
                    s.out = SLT
                elif s.in_[FUNCT3] == b3(0b011):
                    s.out = SLTU
                elif s.in_[FUNCT3] == b3(0b110):
                    s.out = OR
                elif s.in_[FUNCT3] == b3(0b100):
                    s.out = XOR
                elif s.in_[FUNCT3] == b3(0b101):
                    if s.in_[FUNCT7] == b7(0b0100000):
                        s.out = SRA
                    elif s.in_[FUNCT7] == b7(0b0000000):
                        s.out = SRL

            elif s.in_[OPCODE] == b7(0b0010011):
                if s.in_[FUNCT3] == b3(0b000):
                    s.out = ADDI
                elif s.in_[FUNCT3] == b3(0b010):
                    s.out = SLTI
                elif s.in_[FUNCT3] == b3(0b011):
                    s.out = SLTIU
                elif s.in_[FUNCT3] == b3(0b111):
                    s.out = ANDI
                elif s.in_[FUNCT3] == b3(0b110):
                    s.out = ORI
                elif s.in_[FUNCT3] == b3(0b100):
                    s.out = XORI
                elif s.in_[FUNCT3] == b3(0b001):
                    s.out = SLLI
                elif s.in_[FUNCT3] == b3(0b101):
                    if s.in_[FUNCT7] == b7(0b0100000):
                        s.out = SRAI
                    elif s.in_[FUNCT7] == b7(0b0000000):
                        s.out = SRLI

            elif s.in_[OPCODE] == b7(0b0100011):
                if s.in_[FUNCT3] == b3(0b010):
                    s.out = SW
                elif s.in_[FUNCT3] == b3(0b000):
                    s.out = SB
                elif s.in_[FUNCT3] == b3(0b001):
                    s.out = SH

            elif s.in_[OPCODE] == b7(0b0000011):
                if s.in_[FUNCT3] == b3(0b010):
                    s.out = LW
                elif s.in_[FUNCT3] == b3(0b000):
                    s.out = LB
                elif s.in_[FUNCT3] == b3(0b100):
                    s.out = LBU
                elif s.in_[FUNCT3] == b3(0b001):
                    s.out = LH
                elif s.in_[FUNCT3] == b3(0b101):
                    s.out = LHU

            elif s.in_[OPCODE] == b7(0b1100011):
                if s.in_[FUNCT3] == b3(0b001):
                    s.out = BNE
                elif s.in_[FUNCT3] == b3(0b000):
                    s.out = BEQ
                elif s.in_[FUNCT3] == b3(0b100):
                    s.out = BLT
                elif s.in_[FUNCT3] == b3(0b101):
                    s.out = BGE
                elif s.in_[FUNCT3] == b3(0b110):
                    s.out = BLTU
                elif s.in_[FUNCT3] == b3(0b111):
                    s.out = BGEU

            elif s.in_[OPCODE] == b7(0b1101111):
                s.out = JAL
            elif s.in_[OPCODE] == b7(0b1100111):
                s.out = JALR
            elif s.in_[OPCODE] == b7(0b0010111):
                s.out = AUIPC
            elif s.in_[OPCODE] == b7(0b0110111):
                s.out = LUI
            elif s.in_[OPCODE] == b7(0b1110011):
                if s.in_[FUNCT3] == b3(0b001):
                    s.out = CSRW

                elif s.in_[FUNCT3] == b3(0b010):
                    if s.in_[FUNCT7] == b7(0b0111111):
                        s.out = CSRRX
                    else:
                        s.out = CSRR
