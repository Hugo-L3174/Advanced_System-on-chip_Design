import struct

from examples.ex03_proc.SparseMemoryImage import SparseMemoryImage, mk_section
from examples.ex03_proc.tinyrv0_encoding import assemble
from .proc_ubmark_bresenham_data import ref, src0
from pymtl3 import *

c_vvadd_src0_ptr = 0x2000;
c_vvadd_dest_ptr = 0x3000;
c_vvadd_size     = 3;
class ubmark_bresenham:

  # verification function, argument is a bytearray from TestMemory instance

  @staticmethod
  def verify(memory):

    is_pass = True
    first_failed = -1

    for i in range(c_vvadd_size*32):
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
    csrr x25, mngr2proc < 3
    csrr x26, mngr2proc < 0x2000
    csrr x27, mngr2proc < 0x3000
    
    add x28, x0, x25  # Load number of tests 
    addi    x2, x2, 256 
	jal x0, Start
	
    ############# BRESENHAM

		# only values from range 1-32 !!!
		
Start:		
        lw x10,0(x26)						# Load value to x0 
        lw x11,4(x26)						# Load value to y0
        lw x12,8(x26)						# Load value to x1
        lw x13,12(x26) 						# Load value to y1
        addi x26, x26, 16       

       
        addi    x2, x2, -156			# Adjust stack
        sw      x1, 172(x2)				# Save return address
        sw      x8, 168(x2)				# Save previous frame pointer
        
        addi    x8, x2, 140				# Adjust frame pointer  

        sw      x10, 0(x9)				# Save x0
        sw      x11, 4(x9)				# Save y0
        sw      x12, 8(x9)				# Save x1
        sw      x13, 12(x9)				# Save y1

        sub     x10, x10, x12				# dx = x0 - x1
        sw      x10, 16(x9)			# save dx			
        blt     x10, x0, .ABS_DX		# if dx < 0 count abs(dx)
        jal     x0, .CNT_DY					# else go to dy init
.ABS_DX:
        sub     x10, x0, x10			# Reverse value
        sw      x10, 16(x9)			# save abs(dx)
        jal     x0, .CNT_DY					# go to dy init
.CNT_DY:
        sub     x11, x11, x13				# dy = y0 - y1
        sw      x11, 20(x9)			# dy = y0 - y1			
        blt     x11, x0, .ABS_DY
        jal     x0, .CNT_SX
.ABS_DY:
        sub     x11, x0, x11			# Reverse value
        sw      x11, 20(x9)			# save abs(dy)
        jal     x0, .CNT_SX

.CNT_SX:
        lw      x10, 0(x9)				# load x0 
        
        bge     x10, x12, .SX_NEG			# if (x0 < x1) sx = -1
        addi    x10, x0, 1				# else sx = 1
        sw      x10, 24(x9)			# save sx
        jal     x0,  .CNT_SY       
.SX_NEG:
        addi    x10, x0, -1			# sx = -1
        sw      x10, 24(x9)			# save sx
        jal     x0, .CNT_SY
       
.CNT_SY:
        lw      x10, 4(x9)				# Load y0
        
        bge     x10, x13, .SY_NEG			# if (y0 < y1) sy = -1	
        addi    x10, x0, 1				# else sy = 1
        sw      x10, 28(x9)			# save sx
        jal     x0, .DX_VS_DY
.SY_NEG:
        addi    x10, x0, -1			# sy = -1
        sw      x10, 28(x9)			# save sy
        jal     x0, .DX_VS_DY
        
.DX_VS_DY:
        lw      x10, 16(x9)			# load dx
        blt     x11, x10, .SET_ERR		# if dy < dx then err = (dx>>1)
        srai    x11, x11, 1				# else (dy>>1)
        sub     x11, x0, x11			# err = - (dy>>1)
        sw      x11, 32(x9)			# save err
        jal     x0,  .LOOP
.SET_ERR:
        srai    x10, x10, 1				# err = (dx>>1)
        sw      x10, 32(x9)			# save err
        jal     x0, .LOOP

.LOOP:                               
        lw      x10, 0(x9)				# Load x0
        addi    x10, x10, -1				# x0-1
        addi    x11, x0, 1				# prepare value 1
        sll     x10, x11, x10				# shift 1 left (x0-1) times
        lw      x11, 4(x9)				# Load y0 
        slli    x11, x11, 2				# multiply by 4 to use as address
        addi    x12, x8, -152			# get proper address in stack
        add     x11, x11, x12				# count targeted address in stack
        lw      x12, -4(x11)				# get value of arr[y0-1]
        or      x10, x10, x12				# or it with 1<<(x0-1)
        sw      x10, -4(x11)				# save the result in the same place
        
        lw      x10, 0(x9)				# Load x0
        lw      x11, 8(x9)				# Load x1
        bne     x10, x11, .CONTINUE		# if(x0!=x1) continue loop
        lw      x10, 4(x9)				# Load y0 (y1 is still in x13)
        bne     x10, x13, .CONTINUE		# if(y0!=y1) continue loop
        jal     x0,  .BREAK					# else BREAK LOOP!!!!!!!!

.CONTINUE:                              
        lw      x10, 32(x9)			# load err
        sw      x10, 36(x9)			# save it as e2 for future use
        lw      x11, 16(x9)			# load dx
        sub     x11, x0, x11			# -dx
        blt     x11, x10, .CONDITION_1	# if(-dx < e2)
        jal     x0,  .NEXT_COND
.CONDITION_1:                             
        lw      x11, 20(x9)			# Load dy
        sub     x10, x10, x11				# err -= dy
        sw      x10, 32(x9)			# save err
        lw      x10, 24(x9)			# load sx
        lw      x11, 0(x9)				# load x0
        add     x11, x11, x10				# x0 += sx 
        sw      x11, 0(x9)				# save x0
        jal     x0,  .NEXT_COND
.NEXT_COND:                             
        lw      x10, 36(x9)			# load e2
        lw      x11, 20(x9)			# load dy
        blt     x10, x11, .CONDITION_2		# if(e2 < dy) 
        jal     x0,  .LOOP					# else do another LOOP itex1tion 
.CONDITION_2:                               
        lw      x10, 16(x9)			# Load dx
        lw      x11, 32(x9)			# Load err
        add     x11, x11, x10				# err += dx;
        sw      x11, 32(x9)			# save err
        lw      x10, 28(x9)			# load sy
        lw      x11, 4(x9)				# load y0
        add     x11, x11, x10				# y0 += sy;				
        sw      x11, 4(x9)				# save y0
        jal     x0, .LOOP

.BREAK:        
		lw x11 -152(x8)    
		sw x11 0(x27)  
		lw x11 -148(x8)    
		sw x11 4(x27)  
		lw x11 -144(x8)    
		sw x11 8(x27)  
		lw x11 -140(x8)    
		sw x11 12(x27)  
		lw x11 -136(x8)    
		sw x11 16(x27)  
		lw x11 -132(x8)    
		sw x11 20(x27)  
		lw x11 -128(x8)    
		sw x11 24(x27)  
		lw x11 -124(x8)    
		sw x11 28(x27)  
		lw x11 -120(x8)    
		sw x11 32(x27)  
		lw x11 -116(x8)    
		sw x11 36(x27)  
		lw x11 -112(x8)    
		sw x11 40(x27)  
		lw x11 -108(x8)    
		sw x11 44(x27)  
		lw x11 -104(x8)    
		sw x11 48(x27)  
		lw x11 -100(x8)    
		sw x11 52(x27)  
		lw x11 -96(x8)    
		sw x11 56(x27)  
		lw x11 -92(x8)    
		sw x11 60(x27)  
		lw x11 -88(x8)    
		sw x11 64(x27)  
		lw x11 -84(x8)    
		sw x11 68(x27) 
		lw x11 -80(x8)    
		sw x11 72(x27) 
		lw x11 -76(x8)    
		sw x11 76(x27) 
		lw x11 -72(x8)    
		sw x11 80(x27) 
		lw x11 -68(x8)    
		sw x11 84(x27) 
		lw x11 -64(x8)    
		sw x11 88(x27) 
		lw x11 -60(x8)    
		sw x11 92(x27) 
		lw x11 -56(x8)    
		sw x11 96(x27) 
		lw x11 -52(x8)    
		sw x11 100(x27) 
		lw x11 -48(x8)    
		sw x11 104(x27) 
		lw x11 -44(x8)    
		sw x11 108(x27) 
		lw x11 -40(x8)    
		sw x11 112(x27) 
		lw x11 -36(x8)    
		sw x11 116(x27) 
		lw x11 -32(x8)    
		sw x11 120(x27) 
		lw x11 -28(x8)    
		sw x11 124(x27) 
		 
		addi  x27, x27, 128   # test counter
  		addi  x28, x28, -1
  		
  		sw x0 -152(x8)        # clear memory
  		sw x0 -148(x8)
  		sw x0 -144(x8)
  		sw x0 -140(x8)
  		sw x0 -136(x8)
  		sw x0 -132(x8)
  		sw x0 -128(x8)
  		sw x0 -124(x8)
  		sw x0 -120(x8)
  		sw x0 -116(x8)
  		sw x0 -112(x8)
  		sw x0 -108(x8)
  		sw x0 -104(x8)
  		sw x0 -100(x8)
  		sw x0 -96(x8)
  		sw x0 -92(x8)
  		sw x0 -88(x8)
  		sw x0 -84(x8)
  		sw x0 -80(x8)
  		sw x0 -76(x8)
  		sw x0 -72(x8)
  		sw x0 -68(x8)
  		sw x0 -64(x8)
  		sw x0 -60(x8)
  		sw x0 -56(x8)
  		sw x0 -52(x8)
  		sw x0 -48(x8)
  		sw x0 -44(x8)
  		sw x0 -40(x8)
  		sw x0 -36(x8)
  		sw x0 -32(x8)
  		sw x0 -28(x8)		
  		
  		addi  x2, x2, 156    # move back stack
        bne   x28, x0, Start #start again

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
