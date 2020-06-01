import struct

from examples.ex03_proc.SparseMemoryImage import SparseMemoryImage, mk_section
from examples.ex03_proc.tinyrv0_encoding import assemble
from .proc_ubmark_prng_data import ref, src0, src1
from pymtl3 import *

c_vvadd_src0_ptr = 0x2000;
c_vvadd_src1_ptr = 0x3000;
c_vvadd_dest_ptr = 0x4000;
c_vvadd_size     = 10;
class ubmark_prng:

  # verification function, argument is a bytearray from TestMemory instance

  @staticmethod
  def verify(memory):

    is_pass = True
    first_failed = -1

    for i in range(c_vvadd_size):
      x = struct.unpack('i', memory[c_vvadd_dest_ptr + i * 4: c_vvadd_dest_ptr + (i + 1) * 4])[0]
      if not (x == ref[i]):
        is_pass = False
        first_faild = i
        print(" [ failed ] dest[{i}]: {x} != ref[{i}]: {ref} ".format(i=i, x=x, ref=ref[i]))
        return False

    if is_pass:
      print(" [ passed ]: prng")
      return True

  @staticmethod
  def gen_mem_image():

    # text section

    text = \
    """
    csrr x25, mngr2proc < 10
    csrr x26, mngr2proc < 0x2000
    csrr x27, mngr2proc < 0x3000 
    csrr x28, mngr2proc < 0x4000
    
    add x29, x0, x25
    #addi x2, x2, 120 # adjust stack size      
    
    #li x10, 3904692793
    # lui x10 953294
	# addi x10 x10 569
	addi x2, x2, 512 # adjust stack size
	lw x10,0(x26)
	
    jal x1, Start
    
    Start:
    addi    x2, x2, -28				# Adjust stack
    sw      x1, 24(x2)				# Save return address
    sw      x8, 20(x2)				# Save current fx1me pointer
    addi    x8, x2, 28				# Adjust fx1me pointer
    lw      x12, 12(x27)				# Load last value from array
    sw      x12, -8(x8)				# Save it for future use in loop
    lw      x12, 8(x27)				# Load third value from array			
    sw      x12, -12(x8)				# Save it for future use in loop
    lw      x12, 4(x27)				# Load second value from array
    sw      x12, -16(x8)				# Save it for future use in loop
    lw      x11, 0(x27)				# Load first value from array
    sw      x11, -20(x8)				# Save it for future use
    addi 	x16, x0, 0					# int out = 0

    addi    x11, x11, -1				# tabs[0]-1
    srl     x12, x10, x11				# seed>>(tabs[0]-1)
    andi    x12, x12, 1				# feedback = bit read from seed
    addi    x13, x0, 1				# int i=1
    jal     x0, FOR_FEEDBACK
    FOR_FEEDBACK:						# for(int i=1;i<4;i++)
    addi    x14, x0, 4			
    blt     x13, x14, CNT_FEEDBACK	# if i<4 count feedback value
    jal     x0,  CNT_SEED				# else go to counting seed value
    #x10 seed x11 tab[0] x12 feedback x13 i x14 4

    CNT_FEEDBACK:                          
    slli    x14, x13, 2				# i*4 - used for addressing
    addi    x17, x8, -20				# -20(x8) = address of first array element
    add     x14, x14, x17				# decode address of array element
    lw      x14, 0(x14)				# tabs[i]
    addi    x14, x14, -1				# (tabs[i]-1)
    srl     x15, x10, x14				# seed>>(tabs[1]-1))	
    andi    x15, x15, 1				# seed>>(tabs[1]-1))&1
    xor     x12, x12, x15				# feedback = feedback ^ ((seed>>(tabs[i]-1))&1);
    addi    x13, x13, 1				# i++	
    jal     x0,  FOR_FEEDBACK
    #x10 seed x11 tab[0] x12 feedback x13 i x14 tabs[i]-1 x15 seed>>(tabs[1]-1))&1 x17 -28 

    CNT_SEED:
    slli    x10, x10, 1				# seed = (seed<<1);
    or      x10, x10, x12				# seed |= feedback;

    addi    x13, x0, 31				# int i = 31
    jal     x0,  FOR_OUT
    FOR_OUT:                           
    blt     x13, x0, END				# if i<0 end function
    jal     x0,  CNT_OUT				# else count out value
    CNT_OUT:                           
    slli    x14, x16, 1				# (out << 1)		
    srl     x15, x10, x13				# (seed>>i)
    andi    x15, x15, 1				# ((seed>>i)&1)
    or      x16, x14, x15				# out = (out << 1) | ((seed>>i)&1);
    addi    x13, x13, -1				# i--
    jal     x0,  FOR_OUT
    END:

    sw x16, 0(x28)   
    addi  x28, x28, 4
    addi x10, x16 0			# start again with init value = out

    addi  x29, x29, -1
    beq   x29, x0, final
    jalr  x0, x1, 0				

    final:
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
    src1_section = mk_section(".data", c_vvadd_src1_ptr, src1)
    # load data

    mem_image.add_section( src0_section )
    mem_image.add_section( src1_section )

    return mem_image
