"""
=========================================================================
ProcFL_test.py
=========================================================================
Includes test cases for the functional level TinyRV0 processor.

Author : Shunning Jiang, Yanghui Ou
  Date : June 12, 2019
"""
import random

import pytest

#from ..ProcFL import ProcFL
from examples.ex03_proc.ProcFL import ProcFL

from pymtl3 import *

from .import (
    inst_add,
    inst_sub,
    inst_mul,
    inst_sll,
    inst_slt,
    inst_sltu,
    inst_sra,
    inst_srl,
    inst_and,
    inst_or,
    inst_xor,
    
    inst_addi,
    inst_andi,
    inst_ori,
    inst_xori,
    inst_slli,
    inst_srli,
    inst_srai,
    inst_slti,
    inst_sltiu,
    
    inst_auipc,
    inst_lui,
    
    inst_lw,
    inst_lb,
    inst_lh,
    inst_lbu,
    inst_lhu,
    inst_sw,
    inst_sh,
    inst_sb,
    
    inst_jal,
    inst_jalr,
    
    inst_beq,
    inst_bne,
    inst_bge,
    inst_bgeu,
    inst_blt,
    inst_bltu,
    
    inst_csr,

    inst_xcel,
)
from .harness import TestHarness, asm_test, assemble

random.seed(0xdeadbeef)


#-------------------------------------------------------------------------
# ProcFL_Tests
#-------------------------------------------------------------------------
# We group all our test cases into a class so that we can easily reuse
# these test cases in our CL and RTL tests. We can simply inherit from
# this test class and overwrite the ProcType of the test class.

class ProcFL_Tests:

  # [setup_class] will be called by pytest before running all the tests in
  # the test class. Here we specify the type of the processor that is used
  # in all test cases. We can easily reuse all these test cases in simply
  # by creating a new test class that inherits from this class and
  # overwrite the setup_class to provide a different processor type.
  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcFL

  # [run_sim] is a helper function in the test suite that creates a
  # simulator and runs test. We can overwrite this function when
  # inheriting from the test class to apply different passes to the DUT.
  def run_sim( s, th, gen_test, max_cycles=10000 ):

    th.elaborate()

    # Assemble the program
    mem_image = assemble( gen_test() )

    # Load the program into memory
    th.load( mem_image )

    # Create a simulator and run simulation
    th.apply( SimulationPass )
    th.sim_reset()

    print()
    ncycles = 0
    while not th.done() and ncycles < max_cycles:
      th.tick()
      print("{:3}: {}".format( ncycles, th.line_trace() ), end="") #for better debug view
      ncycles += 1

    # Force a test failure if we timed out
    assert ncycles < max_cycles

  #-----------------------------------------------------------------------
  # add
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_add.gen_add_basic_test ) ,
    asm_test( inst_add.gen_dest_dep_test  ) ,
    asm_test( inst_add.gen_src0_dep_test  ) ,
    asm_test( inst_add.gen_src1_dep_test  ) ,
    asm_test( inst_add.gen_srcs_dep_test  ) ,
    asm_test( inst_add.gen_srcs_dest_test ) ,
    asm_test( inst_add.gen_value_test     ) ,
    asm_test( inst_add.gen_random_test    ) ,
  ])
  def test_add( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_add_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_add.gen_random_test )
  
  #-------------------------------------------------------------------------
  # sub
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sub.gen_basic_test     ) , 
    asm_test( inst_sub.gen_dest_dep_test  ) ,
    asm_test( inst_sub.gen_src0_dep_test  ) ,
    asm_test( inst_sub.gen_src1_dep_test  ) ,
    asm_test( inst_sub.gen_srcs_dep_test  ) ,
    asm_test( inst_sub.gen_srcs_dest_test ) ,
    asm_test( inst_sub.gen_value_test     ) ,
    asm_test( inst_sub.gen_random_test    ) ,  
  ])

  def test_sub( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_sub_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_sub.gen_random_test )
    
  #-------------------------------------------------------------------------
  # mul
  #-------------------------------------------------------------------------


  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_mul.gen_basic_test     ) , 
    asm_test( inst_mul.gen_dest_dep_test  ) ,
    asm_test( inst_mul.gen_src0_dep_test  ) ,
    asm_test( inst_mul.gen_src1_dep_test  ) ,
    asm_test( inst_mul.gen_srcs_dep_test  ) ,
    asm_test( inst_mul.gen_srcs_dest_test ) ,
    asm_test( inst_mul.gen_value_test     ) ,
    asm_test( inst_mul.gen_random_test    ) ,  
  ])
  def test_mul( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_mul_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_mul.gen_random_test )   
    
  #-----------------------------------------------------------------------
  # sll
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sll.gen_basic_test     ) ,
    asm_test( inst_sll.gen_random_test    ) ,
  ])
  def test_sll( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_sll_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_sll.gen_random_test )    
    
  #-------------------------------------------------------------------------
  # slt
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slt.gen_basic_test     ) ,
    asm_test( inst_slt.gen_dest_dep_test  ) ,
    asm_test( inst_slt.gen_src0_dep_test  ) ,
    asm_test( inst_slt.gen_src1_dep_test  ) ,
    asm_test( inst_slt.gen_srcs_dep_test  ) ,
    asm_test( inst_slt.gen_srcs_dest_test ) ,
    asm_test( inst_slt.gen_value_test     ) ,
    asm_test( inst_slt.gen_random_test    ) ,
  ])
  def test_slt( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_slt_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_slt.gen_random_test ) 
    
#-------------------------------------------------------------------------
# sltu
#-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sltu.gen_basic_test     ) ,
    asm_test( inst_sltu.gen_dest_dep_test  ) ,
    asm_test( inst_sltu.gen_src0_dep_test  ) ,
    asm_test( inst_sltu.gen_src1_dep_test  ) ,
    asm_test( inst_sltu.gen_srcs_dep_test  ) ,
    asm_test( inst_sltu.gen_srcs_dest_test ) ,
    asm_test( inst_sltu.gen_value_test     ) ,
    asm_test( inst_sltu.gen_random_test    ) ,
  ])    
  def test_sltu( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_sltu_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_sltu.gen_random_test ) 
    
  #-------------------------------------------------------------------------
  # sra
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sra.gen_basic_test     ) ,
    asm_test( inst_sra.gen_dest_dep_test  ) ,
    asm_test( inst_sra.gen_src0_dep_test  ) ,
    asm_test( inst_sra.gen_src1_dep_test  ) ,
    asm_test( inst_sra.gen_srcs_dep_test  ) ,
    asm_test( inst_sra.gen_srcs_dest_test ) ,
    asm_test( inst_sra.gen_value_test     ) ,
    asm_test( inst_sra.gen_random_test    ) ,
  ])  
  def test_sra( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_sra_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_sra.gen_random_test ) 
    
  #-----------------------------------------------------------------------
  # srl
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srl.gen_basic_test     ) ,
    asm_test( inst_srl.gen_dest_dep_test  ) ,
    asm_test( inst_srl.gen_src0_dep_test  ) ,
    asm_test( inst_srl.gen_src1_dep_test  ) ,
    asm_test( inst_srl.gen_srcs_dep_test  ) ,
    asm_test( inst_srl.gen_srcs_dest_test ) ,
    asm_test( inst_srl.gen_value_test     ) ,
    asm_test( inst_srl.gen_random_test    ) ,
  ])
  def test_srl( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_srl_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_srl.gen_random_test )    
    
  #-----------------------------------------------------------------------
  # and
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_and.gen_basic_test     ) ,
    asm_test( inst_and.gen_dest_dep_test  ) ,
    asm_test( inst_and.gen_src0_dep_test  ) ,
    asm_test( inst_and.gen_src1_dep_test  ) ,
    asm_test( inst_and.gen_srcs_dep_test  ) ,
    asm_test( inst_and.gen_srcs_dest_test ) ,
    asm_test( inst_and.gen_value_test     ) ,
    asm_test( inst_and.gen_random_test    ) ,
  ])
  def test_and( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )
  def test_and_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_and.gen_random_test )  
    
  #-------------------------------------------------------------------------
  # or
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_or.gen_basic_test     ) ,
    asm_test( inst_or.gen_dest_dep_test  ) ,
    asm_test( inst_or.gen_src0_dep_test  ) ,
    asm_test( inst_or.gen_src1_dep_test  ) ,
    asm_test( inst_or.gen_srcs_dep_test  ) ,
    asm_test( inst_or.gen_srcs_dest_test ) ,
    asm_test( inst_or.gen_value_test     ) ,
    asm_test( inst_or.gen_random_test    ) ,
  ])  
  def test_or( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )
  def test_or_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_or.gen_random_test )
    
  #-------------------------------------------------------------------------
  # xor
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_xor.gen_basic_test     ) ,
    asm_test( inst_xor.gen_dest_dep_test  ) ,
    asm_test( inst_xor.gen_src0_dep_test  ) ,
    asm_test( inst_xor.gen_src1_dep_test  ) ,
    asm_test( inst_xor.gen_srcs_dep_test  ) ,
    asm_test( inst_xor.gen_srcs_dest_test ) ,
    asm_test( inst_xor.gen_value_test     ) ,
    asm_test( inst_xor.gen_random_test    ) ,
  ])
  def test_xor( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_xor_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_xor.gen_random_test ) 
    
  #-------------------------------------------------------------------------
  # addi
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_addi.gen_basic_test     ),
    asm_test( inst_addi.gen_dest_dep_test  ),
    asm_test( inst_addi.gen_src_dep_test   ),
    asm_test( inst_addi.gen_srcs_dest_test ),
    asm_test( inst_addi.gen_value_test     ),
    asm_test( inst_addi.gen_random_test    ),
  ])
  def test_addi( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_addi_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_addi.gen_random_test )    
    
  #-----------------------------------------------------------------------
  # andi
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_andi.gen_basic_test ) ,
    asm_test( inst_andi.gen_dest_dep_test  ) ,
    asm_test( inst_andi.gen_src_dep_test   ) ,
    asm_test( inst_andi.gen_srcs_dest_test ) ,
    asm_test( inst_andi.gen_value_test     ) ,
    asm_test( inst_andi.gen_random_test    ) ,
  ])
  def test_andi( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_andi_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_andi.gen_random_test )    
    
  #-------------------------------------------------------------------------
  # ori
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_ori.gen_basic_test     ) ,
    asm_test( inst_ori.gen_dest_dep_test  ) ,
    asm_test( inst_ori.gen_src_dep_test   ) ,
    asm_test( inst_ori.gen_srcs_dest_test ) ,
    asm_test( inst_ori.gen_value_test     ) ,
    asm_test( inst_ori.gen_random_test    ) ,
  ])  
  def test_ori( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_ori_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_ori.gen_random_test )  
    
  #-------------------------------------------------------------------------
  # xori
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_xori.gen_basic_test     ) ,
    asm_test( inst_xori.gen_dest_dep_test  ) ,
    asm_test( inst_xori.gen_src_dep_test   ) ,
    asm_test( inst_xori.gen_srcs_dest_test ) ,
    asm_test( inst_xori.gen_value_test     ) ,
    asm_test( inst_xori.gen_random_test    ) ,
  ])  
  def test_xori( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_xori_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_xori.gen_random_test ) 
    
  #-------------------------------------------------------------------------
  # slli
  #-------------------------------------------------------------------------
 
  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slli.gen_basic_test       ) ,
    asm_test( inst_slli.gen_dest_dep_test    ) ,
    asm_test( inst_slli.gen_src_dep_test     ) ,
    asm_test( inst_slli.gen_src_eq_dest_test ) ,
    asm_test( inst_slli.gen_value_test       ) ,
    asm_test( inst_slli.gen_random_test      ) ,
  ])  
  def test_slli( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_slli_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_slli.gen_random_test ) 
    
  #-------------------------------------------------------------------------
  # srli
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srli.gen_basic_test       ) ,
    asm_test( inst_srli.gen_dest_dep_test    ) ,
    asm_test( inst_srli.gen_src_dep_test     ) ,
    asm_test( inst_srli.gen_src_eq_dest_test ) ,
    asm_test( inst_srli.gen_value_test       ) ,
    asm_test( inst_srli.gen_random_test      ) ,
  ])
  def test_srli( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_srli_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_srli.gen_random_test )

  #-------------------------------------------------------------------------
  # srai
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srai.gen_basic_test       ) ,
    asm_test( inst_srai.gen_src_dep_test     ) ,
    asm_test( inst_srai.gen_src_eq_dest_test ) ,
    asm_test( inst_srai.gen_value_test       ) ,
    asm_test( inst_srai.gen_random_test      ) ,
  ])
  def test_srai( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_srai_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_srai.gen_random_test )
    
  #-------------------------------------------------------------------------
  # slti
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slti.gen_basic_test      ) ,
    asm_test( inst_slti.gen_dest_dep_test   ) ,
    asm_test( inst_slti.gen_src_dep_test    ) ,
    asm_test( inst_slti.gen_src_eq_dest_test) ,
    asm_test( inst_slti.gen_value_test      ) , 
    asm_test( inst_slti.gen_random_test     ) ,  
  ])
  def test_slti( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_slti_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_slti.gen_random_test )


  #-------------------------------------------------------------------------
  # sltiu
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sltiu.gen_basic_test       ) ,
    asm_test( inst_sltiu.gen_dest_dep_test    ) ,
    asm_test( inst_sltiu.gen_src_dep_test     ) ,
    asm_test( inst_sltiu.gen_src_eq_dest_test ) ,
    asm_test( inst_sltiu.gen_value_test       ) ,
    asm_test( inst_sltiu.gen_random_test      ) ,
  ])
  def test_sltiu( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_sltiu_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_sltiu.gen_random_test )
    
  #-----------------------------------------------------------------------
  # auipc
  #-----------------------------------------------------------------------    
    
  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_auipc.gen_basic_test    ) , 
    asm_test( inst_auipc.gen_dest_dep_test ) , 
    asm_test( inst_auipc.gen_value_test    ) , 
    asm_test( inst_auipc.gen_random_test   ) ,
  ])
  def test_auipc( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_auipc_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_auipc.gen_random_test )

  #-------------------------------------------------------------------------
  # lui
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_lui.gen_basic_test    ) ,
    asm_test( inst_lui.gen_dest_dep_test ) ,
    asm_test( inst_lui.gen_value_test    ) ,
  ])
  def test_lui( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_lui_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_lui.gen_random_test )

  #-----------------------------------------------------------------------
  # lw
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_lw.gen_basic_test     ),
    asm_test( inst_lw.gen_dest_dep_test  ),
    asm_test( inst_lw.gen_base_dep_test  ),
    asm_test( inst_lw.gen_srcs_dest_test ),
    asm_test( inst_lw.gen_value_test     ),
    asm_test( inst_lw.gen_random_test    ),
  ])
  def test_lw( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_lw_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_lw.gen_random_test )

  #-------------------------------------------------------------------------
  # lb
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize("name,test", [
    asm_test(inst_lb.gen_basic_test     ),
    asm_test(inst_lb.gen_dest_dep_test  ),
    asm_test(inst_lb.gen_base_dep_test  ),
    asm_test(inst_lb.gen_srcs_dest_test ),
    asm_test(inst_lb.gen_value_test     ),
    asm_test(inst_lb.gen_random_test    )
  ])
  def test_lb( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_lb_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_lb.gen_random_test )

  #-------------------------------------------------------------------------
  # lh
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize("name,test", [
    asm_test(inst_lh.gen_basic_test),
    asm_test(inst_lh.gen_dest_dep_test  ),
    asm_test(inst_lh.gen_base_dep_test  ),
    asm_test(inst_lh.gen_srcs_dest_test ),
    asm_test(inst_lh.gen_value_test     ),
    asm_test(inst_lh.gen_random_test    )
  ])
  def test_lh( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_lh_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_lh.gen_random_test )
    
  #-------------------------------------------------------------------------
  # lbu
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize("name,test", [
    asm_test(inst_lbu.gen_basic_test     ),
    asm_test(inst_lbu.gen_dest_dep_test  ),
    asm_test(inst_lbu.gen_base_dep_test  ),
    asm_test(inst_lbu.gen_srcs_dest_test ),
    asm_test(inst_lbu.gen_value_test     ),
    asm_test(inst_lbu.gen_random_test    )
  ])
  def test_lbu( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_lbu_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_lbu.gen_random_test )

  #-------------------------------------------------------------------------
  # lhu
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize("name,test", [
    asm_test(inst_lhu.gen_basic_test),
    asm_test(inst_lhu.gen_dest_dep_test  ),
    asm_test(inst_lhu.gen_base_dep_test  ),
    asm_test(inst_lhu.gen_srcs_dest_test ),
    asm_test(inst_lhu.gen_value_test     ),
    asm_test(inst_lhu.gen_random_test    )
  ])
  def test_lhu( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_lhu_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_lhu.gen_random_test )

  #-------------------------------------------------------------------------
  # sw
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sw.gen_basic_test     ),
    asm_test( inst_sw.gen_dest_dep_test  ) ,
    asm_test( inst_sw.gen_sword_dep_test ) ,
    asm_test( inst_sw.gen_srcs_dest_test ) ,
    asm_test( inst_sw.gen_value_test     ) ,
    asm_test( inst_sw.gen_random_test    ) ,
  ])
  def test_sw( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_sw_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_sw.gen_random_test )

  #-------------------------------------------------------------------------
  # sh
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sh.gen_basic_test     ),
    asm_test( inst_sh.gen_dest_dep_test  ) ,
    asm_test( inst_sh.gen_sword_dep_test ) ,
    asm_test( inst_sh.gen_srcs_dest_test ) ,
    asm_test( inst_sh.gen_value_test     ) ,
    asm_test( inst_sh.gen_random_test    ) ,
  ])
  def test_sh( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_sh_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_sh.gen_random_test )

  #-------------------------------------------------------------------------
  # sb
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sb.gen_basic_test     ),
    asm_test( inst_sb.gen_dest_dep_test  ) ,
    asm_test( inst_sb.gen_sword_dep_test ) ,
    asm_test( inst_sb.gen_srcs_dest_test ) ,
    asm_test( inst_sb.gen_value_test     ) ,
    asm_test( inst_sb.gen_random_test    ) ,
  ])
  def test_sb( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_sb_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_sb.gen_random_test )
    
  #-------------------------------------------------------------------------
  # jal
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jal.gen_basic_test        ) ,
    asm_test( inst_jal.gen_nops_dep_taken_test),
    asm_test( inst_jal.gen_random_test),
  ])
  def test_jal( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_jal_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_jal.gen_random_test )

  #-------------------------------------------------------------------------
  # jalr
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jalr.gen_basic_test  ),
    asm_test( inst_jalr.gen_nops_dep_taken_test),
    asm_test( inst_jalr.gen_random_test),
  ])
  def test_jalr( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_jalr_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_jalr.gen_random_test )
    
  #-----------------------------------------------------------------------
  # bne
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bne.gen_basic_test             ),
    asm_test( inst_bne.gen_src0_dep_taken_test    ),
    asm_test( inst_bne.gen_src0_dep_nottaken_test ),
    asm_test( inst_bne.gen_src1_dep_taken_test    ),
    asm_test( inst_bne.gen_src1_dep_nottaken_test ),
    asm_test( inst_bne.gen_srcs_dep_taken_test    ),
    asm_test( inst_bne.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bne.gen_src0_eq_src1_test      ),
    asm_test( inst_bne.gen_value_test             ),
    asm_test( inst_bne.gen_random_test            ),
  ])
  def test_bne( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_bne_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_bne.gen_random_test )

  #-------------------------------------------------------------------------
  # beq
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_beq.gen_basic_test ) ,
    asm_test( inst_beq.gen_src0_dep_taken_test    ),
    asm_test( inst_beq.gen_src0_dep_nottaken_test ),
    asm_test( inst_beq.gen_src1_dep_taken_test    ),
    asm_test( inst_beq.gen_src1_dep_nottaken_test ),
    asm_test( inst_beq.gen_srcs_dep_taken_test    ),
    asm_test( inst_beq.gen_srcs_dep_nottaken_test ),
    asm_test( inst_beq.gen_src0_eq_src1_test      ), 
    asm_test( inst_beq.gen_value_test             ),
    asm_test( inst_beq.gen_random_test            ), 
  ])
  def test_beq( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_beq_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_beq.gen_random_test )

  #-------------------------------------------------------------------------
  # bge
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bge.gen_basic_test             ),
    asm_test( inst_bge.gen_src0_dep_taken_test    ),
    asm_test( inst_bge.gen_src0_dep_nottaken_test ),
    asm_test( inst_bge.gen_src1_dep_taken_test    ),
    asm_test( inst_bge.gen_src1_dep_nottaken_test ),
    asm_test( inst_bge.gen_srcs_dep_taken_test    ),
    asm_test( inst_bge.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bge.gen_src0_eq_src1_test      ), 
    asm_test( inst_bge.gen_value_test             ),
    asm_test( inst_bge.gen_random_test            ),   
  ])
  def test_bge( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_bge_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_bge.gen_random_test )

  #-------------------------------------------------------------------------
  # bgeu
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bgeu.gen_basic_test             ),
    asm_test( inst_bgeu.gen_src0_dep_taken_test    ),
    asm_test( inst_bgeu.gen_src0_dep_nottaken_test ),
    asm_test( inst_bgeu.gen_src1_dep_taken_test    ),
    asm_test( inst_bgeu.gen_src1_dep_nottaken_test ),
    asm_test( inst_bgeu.gen_srcs_dep_taken_test    ),
    asm_test( inst_bgeu.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bgeu.gen_src0_eq_src1_test      ), 
    asm_test( inst_bgeu.gen_value_test             ),
    asm_test( inst_bgeu.gen_random_test            ),   
  ])
  def test_bgeu( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_bgeu_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_bgeu.gen_random_test )

  #-------------------------------------------------------------------------
  # blt
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_blt.gen_basic_test             ),
    asm_test( inst_blt.gen_src0_dep_taken_test    ),
    asm_test( inst_blt.gen_src0_dep_nottaken_test ),
    asm_test( inst_blt.gen_src1_dep_taken_test    ),
    asm_test( inst_blt.gen_src1_dep_nottaken_test ),
    asm_test( inst_blt.gen_srcs_dep_taken_test    ),
    asm_test( inst_blt.gen_srcs_dep_nottaken_test ),
    asm_test( inst_blt.gen_src0_eq_src1_test      ), 
    asm_test( inst_blt.gen_value_test             ),
    asm_test( inst_blt.gen_random_test            ),  
  ])
  def test_blt( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_blt_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_blt.gen_random_test )
    
  #-------------------------------------------------------------------------
  # bltu
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bltu.gen_basic_test             ),
    asm_test( inst_bltu.gen_src0_dep_taken_test    ),
    asm_test( inst_bltu.gen_src0_dep_nottaken_test ),
    asm_test( inst_bltu.gen_src1_dep_taken_test    ),
    asm_test( inst_bltu.gen_src1_dep_nottaken_test ),
    asm_test( inst_bltu.gen_srcs_dep_taken_test    ),
    asm_test( inst_bltu.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bltu.gen_src0_eq_src1_test      ), 
    asm_test( inst_bltu.gen_value_test             ),
    asm_test( inst_bltu.gen_random_test            ),  
  ])
  def test_bltu( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_bltu_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_bltu.gen_random_test )
    
    
  #-----------------------------------------------------------------------
  # csr
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_csr.gen_basic_test      ),
    asm_test( inst_csr.gen_bypass_test     ),
    asm_test( inst_csr.gen_value_test      ),
    asm_test( inst_csr.gen_random_test     ),
  ])
  def test_csr( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_csr_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_csr.gen_random_test )

  #-----------------------------------------------------------------------
  # xcel
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_xcel.gen_basic_test ),
    asm_test( inst_xcel.gen_multiple_test ),
  ])
  def test_xcel( s, name, test, dump_vcd ):
    th = TestHarness( s.ProcType )
    s.run_sim( th, test )

  def test_xcel_rand_delays( s, dump_vcd ):
    th = TestHarness( s.ProcType, src_delay=3, sink_delay=14,
                      mem_stall_prob =0.5, mem_latency=3 )
    s.run_sim( th, inst_xcel.gen_multiple_test )
