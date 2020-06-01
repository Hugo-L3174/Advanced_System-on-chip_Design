import struct

from examples.ex03_proc.SparseMemoryImage import SparseMemoryImage, mk_section
from examples.ex03_proc.tinyrv0_encoding import assemble
from .proc_ubmark_gcd_data import ref, src0, src1
from pymtl3 import *

c_vvadd_src0_ptr = 0x2000;
c_vvadd_src1_ptr = 0x3000;
c_vvadd_dest_ptr = 0x4000;
c_vvadd_size     = 50;
class ubmark_gcd:

  # verification function, argument is a bytearray from TestMemory instance

  @staticmethod
  def verify(memory):

    is_pass = True

    for i in range(c_vvadd_size):
      x = struct.unpack('i', memory[c_vvadd_dest_ptr + i * 4: c_vvadd_dest_ptr + (i + 1) * 4])[0]
      if not (x == ref[i]):
        is_pass = False
        print(" [ failed ] dest[{i}]: {x} != ref[{i}]: {ref} ".format(i=i, x=x, ref=ref[i]))
        return False

    if is_pass:
      print(" [ passed ]: gcd")
      return True

  @staticmethod
  def gen_mem_image():

    # text section

    text = \
    """
  csrr x1, mngr2proc < 50
  csrr x2, mngr2proc < 0x2000
  csrr x3, mngr2proc < 0x3000
  csrr x4, mngr2proc < 0x4000
 
    add   x9, x0, x1
    jal x0, start

  start:
    lw    x6, 0(x2)
    lw    x7, 0(x3) 
    addi  x2, x2, 4
    addi  x3, x3, 4
    jal x0, loop
    
  loop:
    bge x6, x7, elseif
    addi x28, x6, 0
    addi x6, x7, 0
    addi x7, x28, 0
    jal x0, loop

  elseif:
    beq x7, x0, else
    sub x6, x6, x7
    jal x0, loop

  else:
    addi x5, x6, 0
    sw   x5, 0(x4)
    addi  x4, x4, 4
    addi  x9, x9, -1
    bne   x9, x0, start
    jal x0, end
    
  end:
    csrw  proc2mngr, x0 > 0
    nop
    nop
    nop
    nop
    nop
    nop
    """

    mem_image = assemble( text )

    # load data by manually create data sections using binutils

    src0_section = mk_section( ".data", c_vvadd_src0_ptr, src0 )
    src1_section = mk_section( ".data", c_vvadd_src1_ptr, src1 )

    # load data

    mem_image.add_section( src0_section )
    mem_image.add_section( src1_section )

    return mem_image
