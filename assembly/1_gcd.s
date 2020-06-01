.data
  a: .word 3528
  b: .word 3780
  
.text

  lw t1, a
  lw t2, b
  
  loop:
    bge t1, t2, elseif
    mv t3, t1
    mv t1, t2
    mv t2, t3
    j loop
  
  elseif:
    beqz t2, else
    sub t1, t1, t2
    j loop
  
  else:
    mv t0, t1
    j end
  
  end:
    nop