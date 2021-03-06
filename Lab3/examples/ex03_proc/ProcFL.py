"""
==========================================================================
ProcFL
==========================================================================
TinyRV0 FL proc.

Author : Shunning Jiang
  Date : June 14, 2019
"""

from pymtl3 import *
from pymtl3.stdlib.ifcs.GetGiveIfc import GetIfcFL
from pymtl3.stdlib.ifcs.mem_ifcs import MemMasterIfcFL
from pymtl3.stdlib.ifcs.SendRecvIfc import SendIfcFL
from pymtl3.stdlib.ifcs.xcel_ifcs import XcelMasterIfcFL
from pymtl3.stdlib.ifcs.XcelMsg import mk_xcel_msg

from .tinyrv0_encoding import RegisterFile, TinyRV0Inst, disassemble_inst


class ProcFL( Component ):

  def construct( s ):

    # Interface, Buffers to hold request/response messages

    s.commit_inst = OutPort( Bits1 )

    s.imem = MemMasterIfcFL()
    s.dmem = MemMasterIfcFL()
    s.xcel = XcelMasterIfcFL( *mk_xcel_msg( 5, 32 ) )

    s.proc2mngr = SendIfcFL()
    s.mngr2proc = GetIfcFL()

    # Internal data structures

    s.PC = b32( 0x200 )

    s.R = RegisterFile(32)
    s.raw_inst = None

    @s.update
    def up_ProcFL():
      if s.reset:
        s.PC = b32( 0x200 )
        return

      s.commit_inst = Bits1( 0 )

      try:
        s.raw_inst = s.imem.read( s.PC, 4 ) # line trace

        inst = TinyRV0Inst( s.raw_inst )
        inst_name = inst.name
        
  #-----------------------------------------------------------------------
  # Register-register arithmetic, logical, and comparison instructions
  #-----------------------------------------------------------------------        
        if   inst_name == "nop":
          s.PC += 4
        elif inst_name == "add":
          s.R[inst.rd] = s.R[inst.rs1] + s.R[inst.rs2]
          s.PC += 4
        elif inst_name == "sub":
          s.R[inst.rd] = s.R[inst.rs1] - s.R[inst.rs2]
          s.PC += 4
        elif inst_name == "mul":
          s.R[ inst.rd ] = s.R[inst.rs1] * s.R[inst.rs2]
          s.PC += 4
        elif inst_name == "sll":
          s.R[inst.rd] = s.R[inst.rs1] << (s.R[inst.rs2] & 0x1F)
          s.PC += 4
        elif inst_name == "slt":
          s.R[inst.rd] = s.R[inst.rs1].int() < s.R[inst.rs2].int()
          s.PC += 4
        elif inst_name == "sltu":  
          s.R[inst.rd] = s.R[inst.rs1] < s.R[inst.rs2]
          s.PC += 4
        elif inst_name == "sra":  
          s.R[inst.rd] = s.R[inst.rs1].int() >> (s.R[inst.rs2].uint() & 0x1F) 
          s.PC += 4  
        elif inst_name == "srl":
          s.R[inst.rd] = s.R[inst.rs1] >> (s.R[inst.rs2].uint() & 0x1F)
          s.PC += 4
        elif inst_name == "and":
          s.R[inst.rd] = s.R[inst.rs1] & s.R[inst.rs2]
          s.PC += 4
        elif inst_name == "or":
          s.R[inst.rd] = s.R[inst.rs1] | s.R[inst.rs2]
          s.PC += 4  
        elif inst_name == "xor":  
          s.R[inst.rd] = s.R[inst.rs1] ^ s.R[inst.rs2]
          s.PC += 4  
  #-----------------------------------------------------------------------
  # Register-immediate arithmetic, logical, and comparison instructions
  #-----------------------------------------------------------------------  
        elif inst_name == "addi":
          s.R[inst.rd] = s.R[inst.rs1] + sext( inst.i_imm, 32 )
          s.PC += 4
        elif inst_name == "andi":
          s.R[inst.rd] = s.R[inst.rs1] & sext( inst.i_imm, 32 )
          s.PC += 4 
        elif inst_name == "ori":  
          s.R[inst.rd] = s.R[inst.rs1] | sext( inst.i_imm, 32 )
          s.PC += 4
        elif inst_name == "xori":
          s.R[inst.rd] = s.R[inst.rs1] ^ sext( inst.i_imm, 32 )
          s.PC += 4
        elif inst_name == "slli":
          s.R[inst.rd] = s.R[inst.rs1] << inst.shamt
          s.PC += 4
        elif inst_name == "srli":
          s.R[inst.rd] = s.R[inst.rs1] >> inst.shamt
          s.PC += 4
        elif inst_name == "srai":
          s.R[inst.rd] = s.R[inst.rs1].int() >> inst.shamt.uint()
          s.PC += 4
        elif inst_name == "slti":
          s.R[inst.rd] = s.R[inst.rs1].int() < inst.i_imm.int()
          s.PC += 4
        elif inst_name == "sltiu":
          s.R[inst.rd] = s.R[inst.rs1] < sext( inst.i_imm, 32 )
          s.PC += 4
  #-----------------------------------------------------------------------
  # Other instructions
  #-----------------------------------------------------------------------    
        elif inst_name == "auipc":
          s.R[inst.rd] = inst.u_imm + s.PC
          s.PC += 4
        elif inst_name == "lui":
          s.R[inst.rd] = inst.u_imm
          s.PC += 4
  #-----------------------------------------------------------------------
  # Load/store instructions
  #----------------------------------------------------------------------- 
        elif inst_name == "sh":
          addr = s.R[inst.rs1] + sext( inst.s_imm, 32 )
          #s.M[addr:addr+2] = s.R[inst.rs2][0:16]
          s.dmem.write(addr, 2, s.R[inst.rs2][0:16])
          s.PC += 4
        elif inst_name == "sb":
          addr = s.R[inst.rs1] + sext( inst.s_imm, 32 )
          #s.M[addr] = s.R[inst.rs2][0:8]
          s.dmem.write(addr, 1, s.R[inst.rs2][0:8])
          s.PC += 4
        elif inst_name == "sw":
          addr = s.R[inst.rs1] + sext( inst.s_imm, 32 )
          s.dmem.write( addr, 4, s.R[inst.rs2] )
          s.PC += 4
        elif inst_name == "lw":
          addr = s.R[inst.rs1] + sext( inst.i_imm, 32 )
          s.R[inst.rd] = s.dmem.read( addr, 4 )
          s.PC += 4
        elif inst_name == "lb":
          addr = s.R[inst.rs1] + sext( inst.i_imm, 32 )
          dmem_data = s.dmem.read( addr, 1 )[0:8]
          s.R[inst.rd] = sext( dmem_data, 32 )
          s.PC += 4
        elif inst_name == "lbu":
          addr = s.R[inst.rs1] + sext( inst.i_imm, 32 )
          dmem_data = s.dmem.read( addr, 1 )[0:8]
          s.R[inst.rd] = zext( dmem_data, 32 )
          s.PC += 4 
        elif inst_name == "lh":
          addr = s.R[inst.rs1] + sext( inst.i_imm, 32 )
          dmem_data = s.dmem.read( addr, 2 )[0:16]
          s.R[inst.rd] = sext( dmem_data, 32 )
          s.PC += 4
        elif inst_name == "lhu": 
          addr = s.R[inst.rs1] + sext( inst.i_imm, 32 )
          dmem_data = s.dmem.read( addr, 2 )[0:16]
          s.R[inst.rd] = zext( dmem_data, 32 )
          s.PC += 4    
  #-----------------------------------------------------------------------
  # Unconditional jump instructions
  #-----------------------------------------------------------------------   
        elif inst_name == "jal":
          s.R[inst.rd] = s.PC + 4
          s.PC = s.PC + sext( inst.j_imm, 32 )
        elif inst_name == "jalr":
          temp = s.R[inst.rs1] + sext( inst.i_imm, 32 )
          s.R[inst.rd] = s.PC + 4
          s.PC = temp & 0xFFFFFFFE
  #-----------------------------------------------------------------------
  # Conditional branch instructions
  #-----------------------------------------------------------------------
        elif inst_name == "bne":
          if s.R[inst.rs1] != s.R[inst.rs2]:
            s.PC = s.PC + sext( inst.b_imm, 32 )
          else:
            s.PC += 4
        elif inst_name == "beq":
          if s.R[inst.rs1] == s.R[inst.rs2]:
            s.PC = s.PC + sext( inst.b_imm, 32 )
          else:
            s.PC += 4
        elif inst_name == "blt":
          if s.R[inst.rs1].int() < s.R[inst.rs2].int():
            s.PC = s.PC + sext( inst.b_imm, 32 )
          else:
            s.PC += 4
        elif inst_name == "bge":
          if s.R[inst.rs1].int() >= s.R[inst.rs2].int():
            s.PC = s.PC + sext( inst.b_imm, 32 )
          else:
            s.PC += 4
        elif inst_name == "bltu":
          if s.R[inst.rs1] < s.R[inst.rs2]:
            s.PC = s.PC + sext( inst.b_imm, 32 )
          else:
            s.PC += 4
        elif inst_name == "bgeu":
          if s.R[inst.rs1] >= s.R[inst.rs2]:
            s.PC = s.PC + sext( inst.b_imm, 32 )
          else:
            s.PC += 4
        elif inst_name == "csrw":
          if   inst.csrnum == 0x7C0:
            s.proc2mngr( s.R[inst.rs1] )
          elif 0x7E0 <= inst.csrnum <= 0x7FF:
            s.xcel.write( inst.csrnum[0:5], s.R[inst.rs1] )
          else:
            raise TinyRV2Semantics.IllegalInstruction(
              "Unrecognized CSR register ({}) for csrw at PC={}" \
                .format(inst.csrnum.uint(),s.PC) )
          s.PC += 4
        elif inst_name == "csrr":
          if   inst.csrnum == 0xFC0:
            s.R[inst.rd] = s.mngr2proc()
          elif 0x7E0 <= inst.csrnum <= 0x7FF:
            s.R[inst.rd] = s.xcel.read( inst.csrnum[0:5] )
          else:
            raise TinyRV2Semantics.IllegalInstruction(
              "Unrecognized CSR register ({}) for csrr at PC={}" \
                .format(inst.csrnum.uint(),s.PC) )

          s.PC += 4

      except:
        print( "Unexpected error at PC={:0>8s}!".format( str(s.PC) ) )
        raise

      s.commit_inst = b1( 1 )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    if s.commit_inst:
      return "[{:0>8s} {: <24}]".format( str(s.PC), disassemble_inst( s.raw_inst ) )
    return "[{}]".format( "#".ljust(33) )
