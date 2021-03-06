#=========================================================================
# sltiu
#=========================================================================

import random

from pymtl3 import *
from .inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sltiu x3, x1, 6
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """
#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------
def gen_dest_dep_test():
  return [
    gen_rimm_dest_dep_test( 5, "sltiu",   1,  1,  0 ),
    gen_rimm_dest_dep_test( 4, "sltiu",   2,  1,  0 ),
    gen_rimm_dest_dep_test( 3, "sltiu",   3,  1,  0 ),
    gen_rimm_dest_dep_test( 2, "sltiu",   4,  1,  0 ),    
    gen_rimm_dest_dep_test( 1, "sltiu",   5,  1,  0 ),
    gen_rimm_dest_dep_test( 0, "sltiu",   6,  1,  0 ),
  ]
#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "sltiu",   7,  1,   0 ),
    gen_rimm_src_dep_test( 4, "sltiu",   8,  1,   0 ),
    gen_rimm_src_dep_test( 3, "sltiu",   9,  1,   0 ),
    gen_rimm_src_dep_test( 2, "sltiu",  10,  1,   0 ),
    gen_rimm_src_dep_test( 1, "sltiu",  11,  1,   0 ),
    gen_rimm_src_dep_test( 0, "sltiu",  12,  1,   0 ),
  ]
#-------------------------------------------------------------------------
# gen_src_eq_dest_test
#-------------------------------------------------------------------------
def gen_src_eq_dest_test():
  return [
    gen_rimm_src_eq_dest_test(  "sltiu",  19, 20,   1 ),
    gen_rimm_src_eq_dest_test(  "sltiu",  20,  1,   0 ),
    gen_rimm_src_eq_dest_test(  "sltiu",   1, 21,   1 ),
    gen_rimm_src_eq_dest_test(  "sltiu",   1, 22,   1 ),
    gen_rimm_src_eq_dest_test(  "sltiu",  23,  1,   0 ),
    gen_rimm_src_eq_dest_test(  "sltiu",  24,  1,   0 ),
  ]
#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rimm_value_test( "sltiu", 0x00000000, 0x00000000, 0x00000000 ),
    gen_rimm_value_test( "sltiu", 0x00000011, 0x00000001, 0x00000000 ),
    gen_rimm_value_test( "sltiu", 0x00000003, 0x00000007, 0x00000001 ),
  ]
#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    src = Bits( 32, random.randint(0,0xffffffff) )
    imm = Bits( 12, random.randint(0,0xfff) )
    if src<sext(imm,32):
     dest = Bits( 32, 1 )
    else:
     dest = Bits( 32, 0 )
    asm_code.append( gen_rimm_value_test( "sltiu", src.uint(), imm.uint(), dest.uint() ) )
  return asm_code
