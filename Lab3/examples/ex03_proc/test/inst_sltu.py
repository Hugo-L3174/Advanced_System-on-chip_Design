#=========================================================================
# sltu
#=========================================================================

import random

from pymtl3 import *
from .inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 4
    csrr x2, mngr2proc < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sltu x3, x1, x2
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
    gen_rr_dest_dep_test( 5, "sltu",   1,  1,  0 ),
    gen_rr_dest_dep_test( 4, "sltu",   2,  1,  0 ),
    gen_rr_dest_dep_test( 3, "sltu",    3,  1,  0 ),
    gen_rr_dest_dep_test( 2, "sltu",    4,  1,  0 ),    
    gen_rr_dest_dep_test( 1, "sltu",   5,  1,  0 ),
    gen_rr_dest_dep_test( 0, "sltu",   6,  1,  0 ),
  ]
#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sltu",   7,  1,   0 ),
    gen_rr_src0_dep_test( 4, "sltu",   8,  1,   0 ),
    gen_rr_src0_dep_test( 3, "sltu",   9,  1,   0 ),
    gen_rr_src0_dep_test( 2, "sltu",  10,  1,   0 ),
    gen_rr_src0_dep_test( 1, "sltu",  11,  1,   0 ),
    gen_rr_src0_dep_test( 0, "sltu",  12,  1,   0 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sltu",  13,  1,   0 ),
    gen_rr_src1_dep_test( 4, "sltu",  14,  1,   0 ),
    gen_rr_src1_dep_test( 3, "sltu",   1, 15,   1 ),
    gen_rr_src1_dep_test( 2, "sltu",   1, 16,   1 ),
    gen_rr_src1_dep_test( 1, "sltu",  17,  1,   0 ),
    gen_rr_src1_dep_test( 0, "sltu",  18,  1,   0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sltu",  19,  1,   0 ),
    gen_rr_srcs_dep_test( 4, "sltu",  20,  1,   0 ),
    gen_rr_srcs_dep_test( 3, "sltu",   1, 21,   1 ),
    gen_rr_srcs_dep_test( 2, "sltu",   1, 22,   1 ),
    gen_rr_srcs_dep_test( 1, "sltu",  23,  1,   0 ),
    gen_rr_srcs_dep_test( 0, "sltu",  24,  1,   0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sltu", 25, 1, 0 ),
    gen_rr_src1_eq_dest_test( "sltu", 26, 1, 0 ),
    gen_rr_src0_eq_src1_test( "sltu", 27, 0 ),
    gen_rr_srcs_eq_dest_test( "sltu", 28, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "sltu", 0x00000000, 0x00000000, 0x00000000 ),
    gen_rr_value_test( "sltu", 0x00000011, 0x00000001, 0x00000000 ),
    gen_rr_value_test( "sltu", 0x00000003, 0x00000007, 0x00000001 ),

    gen_rr_value_test( "sltu", 0x7fffffff, 0xffff8000, 0x00000001 ),
    gen_rr_value_test( "sltu", 0x80000000, 0x70000000, 0x00000000 ),

    gen_rr_value_test( "sltu", 0x0000f0f0, 0xf0f00000, 0x00000001 ),
    gen_rr_value_test( "sltu", 0xf0f00000, 0x0000ffff, 0x00000000 ),
    gen_rr_value_test( "sltu", 0xffffffff, 0xffffffff, 0x00000000 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    if src0<src1:
      dest = Bits( 32, 1 )
    else:
      dest = Bits( 32, 0 )
    asm_code.append( gen_rr_value_test( "sltu", src0.uint(), src1.uint(), dest.uint()) )
  return asm_code


