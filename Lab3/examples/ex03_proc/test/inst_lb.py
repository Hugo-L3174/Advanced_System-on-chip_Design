#=========================================================================
# lb
# - Summary   : Load byte from memory
# - Assembly  : lb rd, imm(rs1)
# - Semantics : R[rd] = sext( M_1B[ R[rs1] + sext(imm) ] )
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
    csrr x1, mngr2proc < 0x00002001
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lb   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x2 > 0x00000003

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [

    gen_ld_dest_dep_test( 5, "lb", 0x2000, 0x00000003 ),
    gen_ld_dest_dep_test( 4, "lb", 0x2001, 0x00000007 ),
    gen_ld_dest_dep_test( 3, "lb", 0x2002, 0x0000000b ),
    gen_ld_dest_dep_test( 2, "lb", 0x2003, 0x0000003f ),
    gen_ld_dest_dep_test( 1, "lb", 0x2004, 0xffffff83 ),
    gen_ld_dest_dep_test( 0, "lb", 0x2005, 0xffffffc7 ),

    gen_byte_data([
      0x03,
      0x07,
      0x0b,
      0x3f,
      0x83,
      0xc7,
    ])

  ]

#-------------------------------------------------------------------------
# gen_base_dep_test
#-------------------------------------------------------------------------

def gen_base_dep_test():
  return [

    gen_ld_base_dep_test( 5, "lb", 0x2000, 0x00000003 ),
    gen_ld_base_dep_test( 4, "lb", 0x2001, 0x00000007 ),
    gen_ld_base_dep_test( 3, "lb", 0x2002, 0x0000000b ),
    gen_ld_base_dep_test( 2, "lb", 0x2003, 0x0000003f ),
    gen_ld_base_dep_test( 1, "lb", 0x2004, 0xffffff83 ),
    gen_ld_base_dep_test( 0, "lb", 0x2005, 0xffffffc7 ),

    gen_byte_data([
      0x03,
      0x07,
      0x0b,
      0x3f,
      0x83,
      0xc7,
    ])

  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_ld_base_eq_dest_test( "lb", 0x2000, 0x04 ),
    gen_byte_data([ 0x04 ])
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    # test positive offsets

    gen_ld_value_test("lb",  0, 0x00002000, 0x00000001),
    gen_ld_value_test("lb",  1, 0x00002000, 0x00000002),
    gen_ld_value_test("lb",  2, 0x00002000, 0x0000000f),
    gen_ld_value_test("lb",  3, 0x00002000, 0x0000003c),
    gen_ld_value_test("lb",  4, 0x00002000, 0xffffff81),
    gen_ld_value_test("lb",  5, 0x00002000, 0xffffffcc),

    # test negative offsets

    gen_ld_value_test("lb", -5, 0x00002005, 0x00000001),
    gen_ld_value_test("lb", -4, 0x00002005, 0x00000002),
    gen_ld_value_test("lb", -3, 0x00002005, 0x0000000f),
    gen_ld_value_test("lb", -2, 0x00002005, 0x0000003c),
    gen_ld_value_test("lb", -1, 0x00002005, 0xffffff81),
    gen_ld_value_test("lb",  0, 0x00002005, 0xffffffcc),

    gen_byte_data([
      0x01,
      0x02,
      0x0f,
      0x3c,
      0x81,
      0xcc,
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

    base   = Bits( 32, 0x2000 + b )
    offset = Bits( 16, (a - b) )
    # result is sign extended
    result = data[a] if data[a] >= 0 and data[a] < 0x80 else 0xffffff00 + data[a]

    asm_code.append( gen_ld_value_test( "lb", offset.int(), base.uint(), result ) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_byte_data( data ) )
  return asm_code
