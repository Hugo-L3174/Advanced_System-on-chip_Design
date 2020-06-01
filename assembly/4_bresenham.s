############# BRESENHAM

		# only values from range 1-32 !!!
        li a0, 1						# Load value to x0 
        li a1, 1						# Load value to y0
        li a2, 32						# Load value to x1
        li a3, 32 						# Load value to y1
        j Start

Start:
        addi    sp, sp, -176			# Adjust stack
        sw      ra, 172(sp)				# Save return address
        sw      s0, 168(sp)				# Save previous frame pointer
        addi    s0, sp, 176				# Adjust frame pointer
        sw      a0, -12(s0)				# Save x0
        sw      a1, -16(s0)				# Save y0
        sw      a2, -20(s0)				# Save x1
        sw      a3, -24(s0)				# Save y1

        sub     a0, a0, a2				# dx = x0 - x1
        sw      a0, -156(s0)			# save dx			
        blt     a0, zero, .ABS_DX		# if dx < 0 count abs(dx)
        j       .CNT_DY					# else go to dy init
.ABS_DX:
        sub     a0, zero, a0			# Reverse value
        sw      a0, -156(s0)			# save abs(dx)
        j       .CNT_DY					# go to dy init
.CNT_DY:
        sub     a1, a1, a3				# dy = y0 - y1
        sw      a1, -160(s0)			# dy = y0 - y1			
        blt     a1, zero, .ABS_DY
        j       .CNT_SX
.ABS_DY:
        sub     a1, zero, a1			# Reverse value
        sw      a1, -160(s0)			# save abs(dy)
        j       .CNT_SX

.CNT_SX:
        lw      a0, -12(s0)				# load x0 
        
        bge     a0, a2, .SX_NEG			# if (x0 < x1) sx = -1
        addi    a0, zero, 1				# else sx = 1
        sw      a0, -164(s0)			# save sx
        j       .CNT_SY       
.SX_NEG:
        addi    a0, zero, -1			# sx = -1
        sw      a0, -164(s0)			# save sx
        j       .CNT_SY
       
.CNT_SY:
        lw      a0, -16(s0)				# Load y0
        
        bge     a0, a3, .SY_NEG			# if (y0 < y1) sy = -1	
        addi    a0, zero, 1				# else sy = 1
        sw      a0, -168(s0)			# save sx
        j       .DX_VS_DY
.SY_NEG:
        addi    a0, zero, -1			# sy = -1
        sw      a0, -168(s0)			# save sy
        j       .DX_VS_DY
        
.DX_VS_DY:
        lw      a0, -156(s0)			# load dx
        #lw      a1, -160(s0)			# dy still in a1
        blt     a1, a0, .SET_ERR		# if dy < dx then err = (dx>>1)
        srai    a1, a1, 1				# else (dy>>1)
        sub     a1, zero, a1			# err = - (dy>>1)
        sw      a1, -172(s0)			# save err
        j       .LOOP
.SET_ERR:
        srai    a0, a0, 1				# err = (dx>>1)
        sw      a0, -172(s0)			# save err
        j       .LOOP

.LOOP:                               
        lw      a0, -12(s0)				# Load x0
        addi    a0, a0, -1				# x0-1
        addi    a1, zero, 1				# prepare value 1
        sll     a0, a1, a0				# shift 1 left (x0-1) times
        lw      a1, -16(s0)				# Load y0 
        slli    a1, a1, 2				# multiply by 4 to use as address
        addi    a2, s0, -152			# get proper address in stack
        add     a1, a1, a2				# count targeted address in stack
        lw      a2, -4(a1)				# get value of arr[y0-1]
        or      a0, a0, a2				# or it with 1<<(x0-1)
        sw      a0, -4(a1)				# save the result in the same place
        
        lw      a0, -12(s0)				# Load x0
        lw      a1, -20(s0)				# Load x1
        bne     a0, a1, .CONTINUE		# if(x0!=x1) continue loop
        lw      a0, -16(s0)				# Load y0 (y1 is still in a3)
        bne     a0, a3, .CONTINUE		# if(y0!=y1) continue loop
        j       .BREAK					# else BREAK LOOP!!!!!!!!

.CONTINUE:                              
        lw      a0, -172(s0)			# load err
        sw      a0, -176(s0)			# save it as e2 for future use
        lw      a1, -156(s0)			# load dx
        sub     a1, zero, a1			# -dx
        blt     a1, a0, .CONDITION_1	# if(-dx < e2)
        j       .NEXT_COND
.CONDITION_1:                             
        lw      a1, -160(s0)			# Load dy
        sub     a0, a0, a1				# err -= dy
        sw      a0, -172(s0)			# save err
        lw      a0, -164(s0)			# load sx
        lw      a1, -12(s0)				# load x0
        add     a1, a1, a0				# x0 += sx 
        sw      a1, -12(s0)				# save x0
        j       .NEXT_COND
.NEXT_COND:                             
        lw      a0, -176(s0)			# load e2
        lw      a1, -160(s0)			# load dy
        blt     a0, a1, .CONDITION_2		# if(e2 < dy) 
        j       .LOOP					# else do another LOOP iteration 
.CONDITION_2:                               
        lw      a0, -156(s0)			# Load dx
        lw      a1, -172(s0)			# Load err
        add     a1, a1, a0				# err += dx;
        sw      a1, -172(s0)			# save err
        lw      a0, -168(s0)			# load sy
        lw      a1, -16(s0)				# load y0
        add     a1, a1, a0				# y0 += sy;				
        sw      a1, -16(s0)				# save y0
        j       .LOOP

.BREAK:
		addi a0 zero 1        		# print_int ecall
		lw a1 -152(s0)      
  		ecall 
        addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -148(s0)      
  		ecall 
        addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -144(s0)      
  		ecall 
        addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -140(s0)      
  		ecall 
        addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -136(s0)      
  		ecall 
        addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -132(s0)      
  		ecall 
        addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -128(s0)      
  		ecall 
        addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -124(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -120(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -116(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -112(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -108(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -104(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -100(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -96(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -92(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -88(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -84(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -80(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -76(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -72(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -68(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -64(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -60(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -56(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -52(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -48(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -44(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -40(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -36(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -32(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
        addi a0 zero 1        		# print_int ecall
        lw a1 -28(s0)      
  		ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  		ecall
