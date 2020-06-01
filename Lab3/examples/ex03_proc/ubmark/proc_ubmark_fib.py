import struct

from examples.ex03_proc.SparseMemoryImage import SparseMemoryImage, mk_section
from examples.ex03_proc.tinyrv0_encoding import assemble
from .proc_ubmark_fib_data import ref, src0
from pymtl3 import *

c_vvadd_src0_ptr = 0x2000;
c_vvadd_dest_ptr = 0x3000;
c_vvadd_size     = 10;
class ubmark_fib:

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
      print(" [ passed ]: fib")
      return True

  @staticmethod
  def gen_mem_image():

    # text section

    text = \
    """
  csrr x25, mngr2proc < 10
  csrr x26, mngr2proc < 0x2000
  csrr x27, mngr2proc < 0x3000
  
    add x28, x0, x25
    addi x2, x2, 120 # adjust stack size
    jal x0, main
   
   main:
    lw x10,0(x26)
    addi  x26, x26, 4
    jal x1, fib         #call the fib function
    sw x10, 0(x2)        #result on stack
    sw x10, 0(x27)        #save to array
    addi  x27, x27, 4
    addi  x28, x28, -1
    bne   x28, x0, main
    jal x0, final
    
  fib: 
    addi x2, x2,-12     #save all values and return adress
    sw x1, 0(x2)
    sw x8, 4(x2)
    sw x9, 8(x2)

    addi x8, x10, 0
    beq x0,x8, done     #get out of this loop if current one is equal to zero
    addi x5, x0, 1
    beq x5,x8, done     #same if current one is equal to one
    
    addi x10, x8, -1     #do the loop with n-1
    jal x1, fib
    addi x9,x18, 0            #when we gout out of this loop we put the result of the loop in s1
    addi x10,x8, -2      #do the loop with n-2
    jal x1, fib
    add x18,x18,x9        #when we get out, we add the final term of this (n-1)+(n-2) iteration
    jal x0, end
    
  done: 
    addi x18,x8, 0            #value of the term is 0 or 1  
    jal x0, end
    
  end:
    addi x10,x18, 0           #load result in a0
    lw x9,8(x2)        #restore all values and stack pointer
    lw x8,4(x2)
    lw x1,0(x2)
    addi x2,x2,12
    jalr x0, x1, 0
    
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

    # load data

    mem_image.add_section( src0_section )

    return mem_image
