   
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
