#x13 a , x14 b, x15 c
	Start:
		blt x13,x14,Switch
        addi x16,x0,0
        beq x14,x16, Subtract
    Switch:
    	addi x15,x13,0
        addi x13,x14,0
        addi x14,x15,0
    Subtract: 
    	sub x13,x13,x14       
        
    addi a0 x0 1        # print_int ecall
	addi a1 x13 0       
ecall


 
#########FIBBONACI
		.data
        msg_1a: .asciiz "FIB("
        msg_1b: .asciiz ") = "
      
        .text
        
        # Initialize fib (n) with value n = ...
        li t0, 9				 		
        sw t0, 0(sp)				# Write initial value to stack
        
        addi x16, sp, 0				# Save sp beginning address
        
        # Print some strings
        li a0, 4        			# print_string ecall
		la a1, msg_1a
  		ecall 
        li a0, 1        			# print_int ecall
		addi a1, t0, 0
  		ecall 
        li a0, 4        			# print_string ecall
		la a1, msg_1b
  		ecall 
        
Fib:  	# Beginning of functional code
		addi sp, sp, -8 			# Adjust stack for 2 items
        sw   ra, 4(sp)				# Save ra address
        sw   fp, 0(sp)				# Save frame point address
        addi  fp, sp, 8				# Set up fp as frame pointer
        
    	# Compare n with 2
    	lw   t0, 0(fp)        		# t0 holds the argument n

		slti t1, t0, 2 				# Check if t0 < 2
        beq  t1, zero, Alg 			# if t0 >= 2 -> go to algorithm
         
	    addi x13, zero, 1			# if n < 2 then Fib(n)=1
        j End						# End recurrency
    		
Alg:  	# n >= 2
    	addi t0, t0, -1				# Calculate fib(n - 1)

    	# Set up to call Fib with argument n - 1
                              		
      	addi sp, sp, -4    			# Allocate space for arguments
      	sw   t0, 0(sp)	        	# n - 1 is our argument - save it
      	jal  Fib                	# Call Fib procedure

      	# Clean up after calling fib with argument n - 1
      	addi sp, sp, 4      		# Pop off the argument

      	# x13 holds the result of fib(n - 1)
      	add  t1, x13, zero  		# Put the result into t1

        # Calculate fib(n - 2)
        lw   t0, 0(fp)        		# t0 holds the argument n
        addi t0, t0, -2     		# Calculate n - 2

        # Set up to call Fib with argument n - 2
        addi sp, sp, -4     		# Allocate space for saved register
        sw   t1, 0(sp)	        	# Save t1 (the result of fib(n - 1))
        addi sp, sp, -4     		# Allocate space for arguments
        sw   t0, 0(sp)	        	# n - 2 is our argument
        jal  Fib                	# Call the Fib procedure

        # Clean up after calling fib with argument n - 2
        addi sp, sp, 4      		# Pop off the argument
        lw   t1, 0(sp)	        	# Restore t1 (the result of fib(n - 1))
		addi sp, sp, 4      		# Deallocate space for saved register

      	# x13 holds the result of fib(n - 2)
      	add  x13, t1, x13   	 	# Result is fib(n - 1) + fib(n - 2)

    
End: 	lw   ra, 4(sp)         		# Restore ra
      	lw   fp, 0(sp)				# Restore frame pointer
      	addi sp, sp, 8				# Deallocate space
        
        addi x15, sp, 0				# Save current sp address
        
    	beq x15, x16, Exit			# Compare current sp addr
        							# with sp beginning address
    	jr   ra 					
    
Exit:   							# End of exit code
    	li a0 1        		# print_int ecall
		addi a1 x13 0       
  ecall      
  		li a0 11        		# print_char ecall
		li a1 '\n'
  ecall
  		

        
        addi x15, sp, 0				#save current sp address
        
    	beq x15, x16, Exit			#compare current sp addr
        							#with sp beginning address
                       		   
    	jr   ra 
    
Exit:   							# End of exit code
    	addi a0 zero 1        		# print_int ecall
		addi a1 x13 0       
  ecall      
  		addi a0 zero 11        		# print_char ecall
		addi a1 zero '\n'
  ecall
  		

###################################################
Pseudorandom
 
        .data
		array:        .word   1, 2, 22, 32
        .text
        li a0, 3904692793
		jal Start
Start:
        addi    sp, sp, -28				# Adjust stack
        sw      ra, 24(sp)				# Save return address
        sw      s0, 20(sp)				# Save current frame pointer
        addi    s0, sp, 28				# Adjust frame pointer
        la      a1, array				# Load array to register
        lw      a2, 12(a1)				# Load last value from array
        sw      a2, -8(s0)				# Save it for future use in loop
        lw      a2, 8(a1)				# Load third value from array			
        sw      a2, -12(s0)				# Save it for future use in loop
        lw      a2, 4(a1)				# Load second value from array
        sw      a2, -16(s0)				# Save it for future use in loop
        lw      a1, array				# Load first value from array
        sw      a1, -20(s0)				# Save it for future use
        mv 	a6 zero					# int out = 0
 	       
        addi    a1, a1, -1				# tabs[0]-1
        srl     a2, a0, a1				# seed>>(tabs[0]-1)
        andi    a2, a2, 1				# feedback = bit read from seed
        addi    a3, zero, 1				# int i=1
		j .FOR_FEEDBACK
.FOR_FEEDBACK:						# for(int i=1;i<4;i++)
        addi    a4, zero, 4			
        blt     a3, a4, .CNT_FEEDBACK	# if i<4 count feedback value
        j       .CNT_SEED				# else go to counting seed value
#a0 seed a1 tab[0] a2 feedback a3 i a4 4
        
.CNT_FEEDBACK:                          
        slli    a4, a3, 2				# i*4 - used for addressing
        addi    a7, s0, -20				# -20(s0) = address of first array element
        add     a4, a4, a7				# decode address of array element
        lw      a4, 0(a4)				# tabs[i]
        addi    a4, a4, -1				# (tabs[i]-1)
        srl     a5, a0, a4				# seed>>(tabs[1]-1))	
        andi    a5, a5, 1				# seed>>(tabs[1]-1))&1
        xor     a2, a2, a5				# feedback = feedback ^ ((seed>>(tabs[i]-1))&1);
        addi    a3, a3, 1				# i++	
        j       .FOR_FEEDBACK
#a0 seed a1 tab[0] a2 feedback a3 i a4 tabs[i]-1 a5 seed>>(tabs[1]-1))&1 a7 -28 
       
.CNT_SEED:
        slli    a0, a0, 1				# seed = (seed<<1);
        or      a0, a0, a2				# seed |= feedback;
            
        addi    a3, zero, 31				# int i = 31
        j       .FOR_OUT
.FOR_OUT:                           
        blt     a3, zero, .END				# if i<0 end function
        j       .CNT_OUT				# else count out value
.CNT_OUT:                           
        slli    a4, a6, 1				# (out << 1)		
        srl     a5, a0, a3				# (seed>>i)
        andi    a5, a5, 1				# ((seed>>i)&1)
        or      a6, a4, a5				# out = (out << 1) | ((seed>>i)&1);
        addi    a3, a3, -1				# i--
        j       .FOR_OUT
.END:

        addi a0 zero 1        		# print_int ecall
        addi a1 a6 0      
	ecall      
	addi a0 zero 11 	       	# print_char ecall
	addi a1 zero '\n'
	ecall
        addi a0 a6 0			# start again with init value = out
        ret				
        
############# LINE

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
