.data
  n: .word 6           #choose number of iterations
  
.text

  main: 
    lw a0,n
    jal ra, fib         #call the fib function
    sw a0, 0(sp)        #result on stack
    j final
    
  fib: 
    addi sp, sp,-12     #save all values and return adress
    sw ra, 0(sp)
    sw s0, 4(sp)
    sw s1, 8(sp)
    

    mv s0, a0
    beq x0,s0, done     #get out of this loop if current one is equal to zero
    li t0, 1
    beq t0,s0, done     #same if current one is equal to one
    
    addi a0, s0, -1     #do the loop with n-1
    jal fib
    mv s1,s2            #when we gout out of this loop we put the result of the loop in s1
    addi a0,s0, -2      #do the loop with n-2
    jal fib
    add s2,s2,s1        #when we get out, we add the final term of this (n-1)+(n-2) iteration
    j end
    
  done: 
    mv s2,s0            #value of the term is 0 or 1  
    j end
    
  end:
    mv a0,s2           #load result in a0
    lw s1,8(sp)        #restore all values and stack pointer
    lw s0,4(sp)
    lw ra,0(sp)
    addi sp,sp,12
    jr ra
    
  final:
    nop

# Maybe TODO: Add some syscalls and ecalls
