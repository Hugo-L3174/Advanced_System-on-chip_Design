#=========================================================================
# lhu
# - Summary   : Load half word unsigned from memory
# - Assembly  : lw rd, imm(rs1)
# - Semantics : R[rd] = zext( M_2B[ R[rs1] + sext(imm) ] )
# - Format    : I-type, I-immediate
#=========================================================================

import random

from pymtl3 import *
from .inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x00002000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lhu   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x2 > 0x00000304

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [

    gen_ld_dest_dep_test( 5, "lhu", 0x2000, 0x00000203 ),
    gen_ld_dest_dep_test( 4, "lhu", 0x2002, 0x00000607 ),
    gen_ld_dest_dep_test( 3, "lhu", 0x2004, 0x00000a0b ),
    gen_ld_dest_dep_test( 2, "lhu", 0x2006, 0x00000e0f ),
    gen_ld_dest_dep_test( 1, "lhu", 0x2008, 0x00008213 ),
    gen_ld_dest_dep_test( 0, "lhu", 0x200a, 0x0000f617 ),

    gen_hword_data([
      0x0203,
      0x0607,
      0x0a0b,
      0x0e0f,
      0x8213,
      0xf617,
    ])

  ]

#-------------------------------------------------------------------------
# gen_base_dep_test
#-------------------------------------------------------------------------

def gen_base_dep_test():
  return [

    gen_ld_base_dep_test( 5, "lhu", 0x2000, 0x00000203 ),
    gen_ld_base_dep_test( 4, "lhu", 0x2002, 0x00000607 ),
    gen_ld_base_dep_test( 3, "lhu", 0x2004, 0x00000a0b ),
    gen_ld_base_dep_test( 2, "lhu", 0x2006, 0x00000e0f ),
    gen_ld_base_dep_test( 1, "lhu", 0x2008, 0x00008213 ),
    gen_ld_base_dep_test( 0, "lhu", 0x200a, 0x0000f617 ),

    gen_hword_data([
      0x0203,
      0x0607,
      0x0a0b,
      0x0e0f,
      0x8213,
      0xf617,
    ])

  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_ld_base_eq_dest_test( "lhu", 0x2000, 0x0304 ),
    gen_hword_data([ 0x0304 ])
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    # Test positive offsets

    gen_ld_value_test( "lhu",   0, 0x00002000, 0x0000beef ),
    gen_ld_value_test( "lhu",   2, 0x00002000, 0x00000203 ),
    gen_ld_value_test( "lhu",   4, 0x00002000, 0x00000607 ),
    gen_ld_value_test( "lhu",   6, 0x00002000, 0x00000a0b ),
    gen_ld_value_test( "lhu",   8, 0x00002000, 0x00000e0f ),
    gen_ld_value_test( "lhu",  10, 0x00002000, 0x0000cafe ),

    # Test negative offsets

    gen_ld_value_test( "lhu", -10, 0x0000200a, 0x0000beef ),
    gen_ld_value_test( "lhu",  -8, 0x0000200a, 0x00000203 ),
    gen_ld_value_test( "lhu",  -6, 0x0000200a, 0x00000607 ),
    gen_ld_value_test( "lhu",  -4, 0x0000200a, 0x00000a0b ),
    gen_ld_value_test( "lhu",  -2, 0x0000200a, 0x00000e0f ),
    gen_ld_value_test( "lhu",   0, 0x0000200a, 0x0000cafe ),

    # Test positive offset with unaligned base

    gen_ld_value_test( "lhu",   1, 0x00001fff, 0x0000beef ),
    gen_ld_value_test( "lhu",   3, 0x00001fff, 0x00000203 ),
    gen_ld_value_test( "lhu",   5, 0x00001fff, 0x00000607 ),
    gen_ld_value_test( "lhu",   7, 0x00001fff, 0x00000a0b ),
    gen_ld_value_test( "lhu",   9, 0x00001fff, 0x00000e0f ),
    gen_ld_value_test( "lhu",  11, 0x00001fff, 0x0000cafe ),

    # Test negative offset with unaligned base

    gen_ld_value_test( "lhu", -11, 0x0000200b, 0x0000beef ),
    gen_ld_value_test( "lhu",  -9, 0x0000200b, 0x00000203 ),
    gen_ld_value_test( "lhu",  -7, 0x0000200b, 0x00000607 ),
    gen_ld_value_test( "lhu",  -5, 0x0000200b, 0x00000a0b ),
    gen_ld_value_test( "lhu",  -3, 0x0000200b, 0x00000e0f ),
    gen_ld_value_test( "lhu",  -1, 0x0000200b, 0x0000cafe ),

    gen_hword_data([
      0xbeef,
      0x0203,
      0x0607,
      0x0a0b,
      0x0e0f,
      0xcafe,
    ])

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():

  # Generate some random data

  data = []
  for i in range(128):
    data.append( random.randint(0,0xffff) )

  # Generate random accesses to this data

  asm_code = []
  for i in range(100):

    a = random.randint(0,127)
    b = random.randint(0,127)

    base   = Bits( 32, 0x2000 + (2*b) )
    offset = Bits( 16, (2*(a - b)) )
    result = data[a]

    asm_code.append( gen_ld_value_test( "lhu", offset.int(), base.uint(), result ) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_hword_data( data ) )
  return asm_code
