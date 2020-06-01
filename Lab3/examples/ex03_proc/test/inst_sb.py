#=========================================================================
# sb
# - Summary   : Store byte into memory
# - Assembly  : sh rs2, imm(rs1)
# - Semantics : M_1B[ R[rs1] + sext(imm) ] = R[rs2][0:8]
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
    sb   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > 0x010203ef

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [

    gen_sd_dest_dep_test( 5, "sh", 0x2000, 0x03, 0x03 ),
    gen_sd_dest_dep_test( 4, "sh", 0x2004, 0x07, 0x07 ),
    gen_sd_dest_dep_test( 3, "sh", 0x2008, 0x0b, 0x0b ),
    gen_sd_dest_dep_test( 2, "sh", 0x200c, 0x0f, 0x0f ),
    gen_sd_dest_dep_test( 1, "sh", 0x2010, 0x13, 0x13 ),
    gen_sd_dest_dep_test( 0, "sh", 0x2014, 0x17, 0x17 ),

    gen_word_data([
      0x02,
      0x88,
      0xdb,
      0xef,
      0x43,
      0x37,
    ])

  ]
#-------------------------------------------------------------------------
# gen_shord_dep_test
#-------------------------------------------------------------------------

def gen_sword_dep_test():
  return [

    gen_sd_sword_dep_test( 5, "sh", 0x2000, 0x03, 0x03 ),
    gen_sd_sword_dep_test( 4, "sh", 0x2004, 0x07, 0x07 ),
    gen_sd_sword_dep_test( 3, "sh", 0x2008, 0x0b, 0x0b ),
    gen_sd_sword_dep_test( 2, "sh", 0x200c, 0x0f, 0x0f ),
    gen_sd_sword_dep_test( 1, "sh", 0x2010, 0x13, 0x13 ),
    gen_sd_sword_dep_test( 0, "sh", 0x2014, 0x17, 0x17 ),

    gen_word_data([
      0x03,
      0x07,
      0x0b,
      0x0f,
      0x13,
      0x17,
    ])

  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_sd_sword_eq_dest_test( "sh", 0x2000, 0x04, 0x04 ),
    gen_word_data([ 0x04 ])
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    # Test positive offsets

    gen_sd_value_test( "sh",   0, 0x00002000, 0xef, 0xef ),
    gen_sd_value_test( "sh",   4, 0x00002000, 0x03, 0x03 ),
    gen_sd_value_test( "sh",   8, 0x00002000, 0x07, 0x07 ),
    gen_sd_value_test( "sh",  12, 0x00002000, 0x0b, 0x0b ),
    gen_sd_value_test( "sh",  16, 0x00002000, 0x0f, 0x0f ),
    gen_sd_value_test( "sh",  20, 0x00002000, 0xfe, 0xfe ),

    # Test negative offsets

    gen_sd_value_test( "sh", -20, 0x00002014, 0xef, 0xef ),
    gen_sd_value_test( "sh", -16, 0x00002014, 0x03, 0x03 ),
    gen_sd_value_test( "sh", -12, 0x00002014, 0x07, 0x07 ),
    gen_sd_value_test( "sh",  -8, 0x00002014, 0x0b, 0x0b ),
    gen_sd_value_test( "sh",  -4, 0x00002014, 0x0f, 0x0f ),
    gen_sd_value_test( "sh",   0, 0x00002014, 0xfe, 0xfe ),

    # Test positive offset with unaligned base

    gen_sd_value_test( "sh",   1, 0x00001fff, 0xef, 0xef ),
    gen_sd_value_test( "sh",   5, 0x00001fff, 0x03, 0x03 ),
    gen_sd_value_test( "sh",   9, 0x00001fff, 0x07, 0x07 ),
    gen_sd_value_test( "sh",  13, 0x00001fff, 0x0b, 0x0b ),
    gen_sd_value_test( "sh",  17, 0x00001fff, 0x0f, 0x0f ),
    gen_sd_value_test( "sh",  21, 0x00001fff, 0xfe, 0xfe ),

    # Test negative offset with unaligned base

    gen_sd_value_test( "sh", -21, 0x00002015, 0xef, 0xef ),
    gen_sd_value_test( "sh", -17, 0x00002015, 0x03, 0x03 ),
    gen_sd_value_test( "sh", -13, 0x00002015, 0x07, 0x07 ),
    gen_sd_value_test( "sh",  -9, 0x00002015, 0x0b, 0x0b ),
    gen_sd_value_test( "sh",  -5, 0x00002015, 0x0f, 0x0f ),
    gen_sd_value_test( "sh",  -1, 0x00002015, 0xfe, 0xfe ),

    gen_word_data([
      0xef,
      0x03,
      0x07,
      0x0b,
      0x0f,
      0xfe,
    ])

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():

  # Generate some random data

  data = []
  for i in range(128):
    data.append( random.randint(0,0xff) )
  # Generate random accesses to this data

  asm_code = []
  for i in range(100):

    a = random.randint(0,127)
    b = random.randint(0,127)
    	
    base   = Bits( 32, 0x2000 + (4*b) )
    offset = Bits( 16, (4*(a - b)) )    
    sword  = Bits( 32, random.randint(0,0xff))
    result = sword.uint()

    asm_code.append( gen_sd_value_test( "sb", offset.int(), base.uint(), sword.uint(), result ) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_word_data( data ) )
  return asm_code
