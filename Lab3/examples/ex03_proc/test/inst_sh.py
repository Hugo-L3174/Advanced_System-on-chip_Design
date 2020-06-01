#=========================================================================
# sh
# - Summary   : Store half word into memory
# - Assembly  : sh rs2, imm(rs1)
# - Semantics : M_2B[ R[rs1] + sext(imm) ] = R[rs2][0:16]
# - Format    : S-type, S-immediate
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
    csrr x2, mngr2proc < 0xdeadbeef
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sh   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > 0x0102beef

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [

    gen_sd_dest_dep_test( 5, "sh", 0x2000, 0x0203, 0x0203 ),
    gen_sd_dest_dep_test( 4, "sh", 0x2004, 0x0607, 0x0607 ),
    gen_sd_dest_dep_test( 3, "sh", 0x2008, 0x0a0b, 0x0a0b ),
    gen_sd_dest_dep_test( 2, "sh", 0x200c, 0x0e0f, 0x0e0f ),
    gen_sd_dest_dep_test( 1, "sh", 0x2010, 0x1213, 0x1213 ),
    gen_sd_dest_dep_test( 0, "sh", 0x2014, 0x1617, 0x1617 ),

    gen_word_data([
      0x0202,
      0x0688,
      0x0adb,
      0x0eef,
      0x1543,
      0x7937,
    ])

  ]
#-------------------------------------------------------------------------
# gen_shord_dep_test
#-------------------------------------------------------------------------

def gen_sword_dep_test():
  return [

    gen_sd_sword_dep_test( 5, "sh", 0x2000, 0x0203, 0x0203 ),
    gen_sd_sword_dep_test( 4, "sh", 0x2004, 0x0607, 0x0607 ),
    gen_sd_sword_dep_test( 3, "sh", 0x2008, 0x0a0b, 0x0a0b ),
    gen_sd_sword_dep_test( 2, "sh", 0x200c, 0x0e0f, 0x0e0f ),
    gen_sd_sword_dep_test( 1, "sh", 0x2010, 0x1213, 0x1213 ),
    gen_sd_sword_dep_test( 0, "sh", 0x2014, 0x1617, 0x1617 ),

    gen_word_data([
      0x0203,
      0x0607,
      0x0a0b,
      0x0e0f,
      0x1213,
      0x1617,
    ])

  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_sd_sword_eq_dest_test( "sh", 0x2000, 0x0304, 0x0304 ),
    gen_word_data([ 0x9304 ])
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    # Test positive offsets

    gen_sd_value_test( "sh",   0, 0x00002000, 0xbeef, 0xbeef ),
    gen_sd_value_test( "sh",   4, 0x00002000, 0x0203, 0x0203 ),
    gen_sd_value_test( "sh",   8, 0x00002000, 0x0607, 0x0607 ),
    gen_sd_value_test( "sh",  12, 0x00002000, 0x0a0b, 0x0a0b ),
    gen_sd_value_test( "sh",  16, 0x00002000, 0x0e0f, 0x0e0f ),
    gen_sd_value_test( "sh",  20, 0x00002000, 0xcafe, 0xcafe ),

    # Test negative offsets

    gen_sd_value_test( "sh", -20, 0x00002014, 0xbeef, 0xbeef ),
    gen_sd_value_test( "sh", -16, 0x00002014, 0x0203, 0x0203 ),
    gen_sd_value_test( "sh", -12, 0x00002014, 0x0607, 0x0607 ),
    gen_sd_value_test( "sh",  -8, 0x00002014, 0x0a0b, 0x0a0b ),
    gen_sd_value_test( "sh",  -4, 0x00002014, 0x0e0f, 0x0e0f ),
    gen_sd_value_test( "sh",   0, 0x00002014, 0xcafe, 0xcafe ),

    # Test positive offset with unaligned base

    gen_sd_value_test( "sh",   1, 0x00001fff, 0xbeef, 0xbeef ),
    gen_sd_value_test( "sh",   5, 0x00001fff, 0x0203, 0x0203 ),
    gen_sd_value_test( "sh",   9, 0x00001fff, 0x0607, 0x0607 ),
    gen_sd_value_test( "sh",  13, 0x00001fff, 0x0a0b, 0x0a0b ),
    gen_sd_value_test( "sh",  17, 0x00001fff, 0x0e0f, 0x0e0f ),
    gen_sd_value_test( "sh",  21, 0x00001fff, 0xcafe, 0xcafe ),

    # Test negative offset with unaligned base

    gen_sd_value_test( "sh", -21, 0x00002015, 0xbeef, 0xbeef ),
    gen_sd_value_test( "sh", -17, 0x00002015, 0x0203, 0x0203 ),
    gen_sd_value_test( "sh", -13, 0x00002015, 0x0607, 0x0607 ),
    gen_sd_value_test( "sh",  -9, 0x00002015, 0x0a0b, 0x0a0b ),
    gen_sd_value_test( "sh",  -5, 0x00002015, 0x0e0f, 0x0e0f ),
    gen_sd_value_test( "sh",  -1, 0x00002015, 0xcafe, 0xcafe ),

    gen_word_data([
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
    	
    base   = Bits( 32, 0x2000 + (4*b) )
    offset = Bits( 16, (4*(a - b)) )    
    sword  = Bits( 32, random.randint(0,0xffff))
    result = sword.uint()

    asm_code.append( gen_sd_value_test( "sh", offset.int(), base.uint(), sword.uint(), result ) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_word_data( data ) )
  return asm_code
