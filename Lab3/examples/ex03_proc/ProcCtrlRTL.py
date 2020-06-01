"""
==========================================================================
ProcCtrlRTL.py
==========================================================================
Control logic for the RTL TinyRV0 processor.

Author : Shunning Jiang
  Date : June 13, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs.XcelMsg import XcelMsgType

from .TinyRV0InstRTL import *


class ProcCtrl(Component):

    def construct(s):

        XcelMsgType_READ = XcelMsgType.READ
        XcelMsgType_WRITE = XcelMsgType.WRITE

        # ---------------------------------------------------------------------
        # Interface
        # ---------------------------------------------------------------------

        # imem ports

        s.imemreq_en = OutPort(Bits1)
        s.imemreq_rdy = InPort(Bits1)
        s.imemresp_en = OutPort(Bits1)
        s.imemresp_rdy = InPort(Bits1)
        s.imemresp_drop = OutPort(Bits1)

        # dmem ports
        s.dmemreq_en = OutPort(Bits1)
        s.dmemreq_rdy = InPort(Bits1)
        s.dmemreq_type = OutPort(Bits4)
        s.dmemresp_en = OutPort(Bits1)
        s.dmemresp_rdy = InPort(Bits1)

        # mngr ports

        # Get interface
        s.mngr2proc_en = OutPort(Bits1)
        s.mngr2proc_rdy = InPort(Bits1)

        # Send interface
        s.proc2mngr_en = OutPort(Bits1)
        s.proc2mngr_rdy = InPort(Bits1)

        # Send interface
        s.xcelreq_rdy = InPort(Bits1)
        s.xcelreq_en = OutPort(Bits1)
        s.xcelreq_type = OutPort(Bits1)

        # Get interface
        s.xcelresp_rdy = InPort(Bits1)
        s.xcelresp_en = OutPort(Bits1)

        # Control signals (ctrl->dpath)

        s.reg_en_F = OutPort(Bits1)
        s.pc_sel_F = OutPort(Bits2)

        s.reg_en_D = OutPort(Bits1)
        s.op1_byp_sel_D = OutPort(Bits2)
        s.op2_byp_sel_D = OutPort(Bits2)

        s.op1_sel_D = OutPort(Bits1)
        s.op2_sel_D = OutPort(Bits2)
        s.imm_type_D = OutPort(Bits3)

        s.reg_en_X = OutPort(Bits1)
        s.alu_fn_X = OutPort(Bits5)

        s.reg_en_M = OutPort(Bits1)
        s.wb_result_sel_M = OutPort(Bits2)
        s.mask_sel_M = OutPort(Bits3)

        s.reg_en_W = OutPort(Bits1)
        s.rf_waddr_W = OutPort(Bits5)
        s.rf_wen_W = OutPort(Bits1)
        s.mask_sel_W = OutPort(Bits3)
        s.dmemreq_type_W = OutPort(Bits2)

        # Status signals (dpath->ctrl)

        s.inst_D = InPort(Bits32)
        s.ne_X = InPort(Bits1)
        # Output val_W for counting

        s.commit_inst = OutPort(Bits1)

        # -----------------------------------------------------------------------
        # Control unit logic
        # -----------------------------------------------------------------------
        # We follow this principle to organize code for each pipeline stage in
        # the control unit.  Register enable logics should always at the
        # beginning. It followed by pipeline registers. Then logic that is not
        # dependent on stall or squash signals. Then logic that is dependent on
        # stall or squash signals. At the end there should be signals meant to
        # be passed to the next stage in the pipeline.

        # ---------------------------------------------------------------------
        # Valid, stall, and squash signals
        # ---------------------------------------------------------------------
        # We use valid signal to indicate if the instruction is valid.  An
        # instruction can become invalid because of being squashed or
        # stalled. Notice that invalid instructions are microarchitectural
        # events, they are different from archtectural no-ops. We must be
        # careful about control signals that might change the state of the
        # processor. We should always AND outgoing control signals with valid
        # signal.

        s.val_F = Wire(Bits1)
        s.val_D = Wire(Bits1)
        s.val_X = Wire(Bits1)
        s.val_M = Wire(Bits1)
        s.val_W = Wire(Bits1)

        # Managing the stall and squash signals is one of the most important,
        # yet also one of the most complex, aspects of designing a pipelined
        # processor. We will carefully use four signals per stage to manage
        # stalling and squashing: ostall_A, osquash_A, stall_A, and squash_A.

        # We denote the stall signals _originating_ from stage A as
        # ostall_A. For example, if stage A can stall due to a pipeline
        # harzard, then ostall_A would need to factor in the stalling
        # condition for this pipeline harzard.

        s.ostall_F = Wire(Bits1)  # can ostall due to imemresp_val
        # can ostall due to mngr2proc_val or other hazards
        s.ostall_D = Wire(Bits1)
        s.ostall_X = Wire(Bits1)  # can ostall due to dmemreq_rdy
        s.ostall_M = Wire(Bits1)  # can ostall due to dmemresp_val
        s.ostall_W = Wire(Bits1)  # can ostall due to proc2mngr_rdy

        # The stall_A signal should be used to indicate when stage A is indeed
        # stalling. stall_A will be a function of ostall_A and all the ostall
        # signals of stages in front of it in the pipeline.

        s.stall_F = Wire(Bits1)
        s.stall_D = Wire(Bits1)
        s.stall_X = Wire(Bits1)
        s.stall_M = Wire(Bits1)
        s.stall_W = Wire(Bits1)

        # We denote the squash signals _originating_ from stage A as
        # osquash_A. For example, if stage A needs to squash the stages behind
        # A in the pipeline, then osquash_A would need to factor in this
        # squash condition.

        s.osquash_D = Wire(Bits1)  # can osquash due to unconditional jumps
        s.osquash_X = Wire(Bits1)  # can osquash due to taken branches

        # The squash_A signal should be used to indicate when stage A is being
        # squashed. squash_A will _not_ be a function of osquash_A, since
        # osquash_A means to squash the stages _behind_ A in the pipeline, but
        # not to squash A itself.

        s.squash_F = Wire(Bits1)
        s.squash_D = Wire(Bits1)

        # ---------------------------------------------------------------------
        # F stage
        # ---------------------------------------------------------------------

        @s.update
        def comb_reg_en_F():
            s.reg_en_F = ~s.stall_F | s.squash_F

        @s.update_ff
        def reg_F():
            if s.reset:
                s.val_F <<= b1(0)
            elif s.reg_en_F:
                s.val_F <<= b1(1)

        # forward declaration of branch (no jump) logic

        s.pc_redirect_X = Wire(Bits1)

        # pc sel logic

        @s.update
        def comb_PC_sel_F():
            if s.pc_redirect_X:
                s.pc_sel_F = b2(1)  # branch target
            else:
                s.pc_sel_F = b2(0)  # use pc+4

        s.next_val_F = Wire(Bits1)

        @s.update
        def comb_F_squash():
            s.squash_F = s.val_F & (s.osquash_D | s.osquash_X)
            s.imemresp_drop = s.squash_F

        @s.update
        def comb_F():

            # ostall due to imemresp

            s.ostall_F = s.val_F & ~s.imemresp_rdy

            # stall and squash in F stage

            s.stall_F = s.val_F & (s.ostall_F | s.ostall_D | s.ostall_X |
                                   s.ostall_M | s.ostall_W)

            # imem req is special, it actually be sent out _before_ the F
            # stage, we need to send memreq everytime we are getting squashed
            # because we need to redirect the PC. We also need to factor in
            # reset. When we are resetting we shouldn't send out imem req.

            s.imemreq_en = ~s.reset & (~s.stall_F | s.squash_F) & s.imemreq_rdy
            s.imemresp_en = ~s.stall_F | s.squash_F

            # We drop the mem response when we are getting squashed

            s.next_val_F = s.val_F & ~s.stall_F & ~s.squash_F

        # ---------------------------------------------------------------------
        # D stage
        # ---------------------------------------------------------------------

        @s.update
        def comb_reg_en_D():
            s.reg_en_D = ~s.stall_D | s.squash_D

        @s.update_ff
        def reg_D():
            if s.reset:
                s.val_D <<= Bits1(0)
            elif s.reg_en_D:
                s.val_D <<= s.next_val_F

        # Decoder, translate 32-bit instructions to symbols

        s.inst_type_decoder_D = DecodeInstType()(in_=s.inst_D)

        # Signals generated by control signal table

        s.inst_val_D = Wire(Bits1)
        s.br_type_D = Wire(Bits2)
        s.rs1_en_D = Wire(Bits1)
        s.rs2_en_D = Wire(Bits1)
        s.alu_fn_D = Wire(Bits5)
        s.dmemreq_type_D = Wire(Bits2)
        s.rf_wen_pending_D = Wire(Bits1)
        s.rf_waddr_sel_D = Wire(Bits3)
        s.csrw_D = Wire(Bits1)
        s.csrr_D = Wire(Bits1)
        s.proc2mngr_en_D = Wire(Bits1)
        s.mngr2proc_D = Wire(Bits1)
        s.wb_result_sel_D = Wire(Bits2)
        s.xcelreq_D = Wire(Bits1)
        s.mask_sel_D = Wire(Bits3)

        # actual waddr, selected base on rf_waddr_sel_D

        s.rf_waddr_D = Wire(Bits5)
        s.xcelreq_type_D = Wire(Bits1)

        # Control signal table

        # Y/N parameters
        n = b1(0)
        y = b1(1)

        # Branch type
        br_x = b2(0)  # don't care
        br_na = b2(0)  # N/A, not branch
        br_ne = b2(1)  # branch not equal
        br_rs1 = b2(2) # branch for jalr

        # Op1 mux select
        op1_x = b1(0)  # don't care
        op1_rf = b1(0)  # use data from RF
        op1_pc = b1(1)  # use pc

        # Op2 mux select
        bm_x = b2(0)  # don't care
        bm_rf = b2(0)  # use data from RF
        bm_imm = b2(1)  # use imm
        bm_csr = b2(2)  # use mngr2proc/numcores/coreid based on csrnum
        bm_jal = b2(3)  # use pc

        # IMM type
        imm_x = b3(0)  # don't care
        imm_i = b3(0)  # I-imm
        imm_s = b3(1)  # S-imm
        imm_b = b3(2)  # B-imm
        imm_u = b3(3)  # U-imm
        imm_j = b3(4)  # J-imm

        # ALU func

        alu_x = b5(0)
        alu_cp0 = b5(0)  # copy in0
        alu_bne = b5(0)
        alu_cp1 = b5(1)  # copy in1
        alu_beq = b5(1)
        alu_add = b5(2)
        alu_sll = b5(3)
        alu_srl = b5(4)
        alu_and = b5(5)
        alu_sub = b5(6)
        alu_or = b5(7)
        alu_xor = b5(8)
        alu_mul = b5(9)
        alu_slt = b5(10)
        alu_sltu = b5(11)
        alu_sra = b5(12)
        alu_jal = b5(13)
        alu_lui = b5(14)
        alu_auipc = b5(15)
        alu_jalr = b5(16)
        alu_bge = b5(17)
        alu_blt = b5(18)
        alu_bgeu = b5(19)
        alu_bltu = b5(20)

        # Memory request type
        nr = b2(0)
        ld = b2(1)
        st = b2(2)

        # X stage result mux select

        xm_x = b2(0)  # don't care
        xm_a = b2(0)  # Arithmetic
        xm_m = b2(1)  # Multiplier
        xm_p = b2(2)  # Pc+4

        # Write-back mux select

        wm_x = b2(0)
        wm_a = b2(0)
        wm_m = b2(1)
        wm_c = b2(2)

        # Mask select

        msk_x = b3(0)
        msk_hu = b3(1)
        msk_bu = b3(2)
        msk_h = b3(3)
        msk_b = b3(4)

        # Control signal

        s.cs = Wire(Bits26)


        # control signal table

        @s.update
        def comb_control_table_D():
            inst = s.inst_type_decoder_D.out
            #                   br     rs1 imm    op1    op2    rs2 alu      dmm wbmux rf  cs cs
            #               val type    en type   muxsel muxsel  en fn       typ sel   wen rr rw
            if inst == NOP:
                s.cs = concat(msk_x, y, br_na, n, imm_x, op1_x, bm_x, n, alu_x, nr, wm_a, n, n, n)
            elif inst == CSRRX:
                s.cs = concat(msk_x, y, br_na, n, imm_i, op1_x, bm_imm, n, alu_cp1, nr, wm_c, y, y, n)
            elif inst == CSRR:
                s.cs = concat(msk_x, y, br_na, n, imm_i, op1_x, bm_csr, n, alu_cp1, nr, wm_a, y, y, n)
            elif inst == CSRW:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, n, alu_cp0, nr, wm_a, n, n, y)
            elif inst == ADD:
                s.cs = concat(msk_x, y, br_na, y, imm_x, op1_x, bm_rf, y, alu_add, nr, wm_a, y, n, n)
            elif inst == SUB:
                s.cs = concat(msk_x, y, br_na, y, imm_x, op1_x, bm_rf, y, alu_sub, nr, wm_a, y, n, n)
            elif inst == SLL:
                s.cs = concat(msk_x, y, br_na, y, imm_x, op1_x, bm_rf, y, alu_sll, nr, wm_a, y, n, n)
            elif inst == SRL:
                s.cs = concat(msk_x, y, br_na, y, imm_x, op1_x, bm_rf, y, alu_srl, nr, wm_a, y, n, n)
            elif inst == SRA:
                s.cs = concat(msk_x, y, br_na, y, imm_x, op1_x, bm_rf, y, alu_sra, nr, wm_a, y, n, n)
            elif inst == ADDI:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, n, alu_add, nr, wm_a, y, n, n)
            elif inst == LW:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, n, alu_add, ld, wm_m, y, n, n)
            elif inst == SW:
                s.cs = concat(msk_x, y, br_na, y, imm_s, op1_x, bm_imm, y, alu_add, st, wm_m, n, n, n)
            elif inst == BNE:
                s.cs = concat(msk_x, y, br_ne, y, imm_b, op1_x, bm_rf, y, alu_bne, nr, wm_x, n, n, n)
            elif inst == BEQ:
                s.cs = concat(msk_x, y, br_ne, y, imm_b, op1_x, bm_rf, y, alu_beq, nr, wm_x, n, n, n)
            elif inst == AND:
                s.cs = concat(msk_x, y, br_na, y, imm_x, op1_x, bm_rf, y, alu_and, nr, wm_a, y, n, n)
            elif inst == MUL:
                s.cs = concat(msk_x, y, br_na, y, imm_x, op1_x, bm_rf, y, alu_mul, nr, wm_a, y, n, n)
            elif inst == ANDI:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, y, alu_and, nr, wm_a, y, n, n)
            elif inst == OR:
                s.cs = concat(msk_x, y, br_na, y, imm_x, op1_x, bm_rf, y, alu_or, nr, wm_a, y, n, n)
            elif inst == ORI:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, y, alu_or, nr, wm_a, y, n, n)
            elif inst == XOR:
                s.cs = concat(msk_x, y, br_na, y, imm_x, op1_x, bm_rf, y, alu_xor, nr, wm_a, y, n, n)
            elif inst == XORI:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, y, alu_xor, nr, wm_a, y, n, n)
            elif inst == SLLI:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, y, alu_sll, nr, wm_a, y, n, n)
            elif inst == SRLI:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, y, alu_srl, nr, wm_a, y, n, n)
            elif inst == SRAI:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, y, alu_sra, nr, wm_a, y, n, n)
            elif inst == SLT:
                 s.cs = concat(msk_x, y, br_na, y, imm_s, op1_x, bm_rf, y,  alu_slt, nr, wm_a, y, n, n)
            elif inst == SLTU:
                 s.cs = concat(msk_x, y, br_na, y, imm_s, op1_x, bm_rf, y,  alu_sltu, nr, wm_a, y, n, n)
            elif inst == SLTI:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, y, alu_slt, nr, wm_a, y, n, n)
            elif inst == SLTIU:
                s.cs = concat(msk_x, y, br_na, y, imm_i, op1_x, bm_imm, y, alu_sltu, nr, wm_a, y, n, n)
            elif inst == BLT:
                s.cs = concat(msk_x, y, br_ne, y, imm_b, op1_x, bm_rf, y, alu_blt, nr, wm_x, n, n, n)
            elif inst == BGE:
                s.cs = concat(msk_x, y, br_ne, y, imm_b, op1_x, bm_rf, y, alu_bge, nr, wm_x, n, n, n)
            elif inst == BLTU:
                s.cs = concat(msk_x, y, br_ne, y, imm_b, op1_x, bm_rf, y, alu_bltu, nr, wm_x, n, n, n)
            elif inst == BGEU:
                s.cs = concat(msk_x, y, br_ne, y, imm_b, op1_x, bm_rf, y, alu_bgeu, nr, wm_x, n, n, n)
            elif inst == AUIPC:
                s.cs = concat(msk_x, y, br_na, y, imm_u, op1_pc, bm_imm, n, alu_auipc, nr, wm_a, y, n, n)
            elif inst == LUI:
                s.cs = concat(msk_x, y, br_na, y, imm_u, op1_x, bm_imm, n, alu_lui, nr, wm_a, y, n, n)
            elif inst == JAL:
                s.cs = concat(msk_x, y, br_ne, n, imm_j, op1_pc, bm_x, n, alu_jal, nr, wm_a, y, n, n)
            elif inst == JALR: # todo
                s.cs = concat(msk_x, y, br_rs1, n, imm_i, op1_x, bm_x, n, alu_jalr, nr, wm_a, y, n, n)
            elif inst == LB:
                s.cs = concat(msk_b, y, br_na, y, imm_i, op1_x, bm_imm, n, alu_add, ld, wm_m, y, n, n)
            elif inst == LBU:
                s.cs = concat(msk_bu, y, br_na, y, imm_i, op1_x, bm_imm, n, alu_add, ld, wm_m, y, n, n)
            elif inst == LH:
                s.cs = concat(msk_h, y, br_na, y, imm_i, op1_x, bm_imm, n, alu_add, ld, wm_m, y, n, n)
            elif inst == LHU:
                s.cs = concat(msk_hu, y, br_na, y, imm_i, op1_x, bm_imm, n, alu_add, ld, wm_m, y, n, n)
            # elif inst == SB:
            # elif inst == SH:

            # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

            else:
                s.cs = concat(msk_x, y, br_x, n, imm_x, op1_x, bm_x, n, alu_x, nr, wm_x, n, n, n)


            s.mask_sel_D = s.cs[23:26]
            s.inst_val_D = s.cs[22:23]
            s.br_type_D = s.cs[20:22]
            s.rs1_en_D = s.cs[19:20]
            s.imm_type_D = s.cs[16:19]
            s.op1_sel_D = s.cs[15:16]
            s.op2_sel_D = s.cs[13:15]
            s.rs2_en_D = s.cs[12:13]
            s.alu_fn_D = s.cs[7:12]
            s.dmemreq_type_D = s.cs[5:7]
            s.wb_result_sel_D = s.cs[3:5]
            s.rf_wen_pending_D = s.cs[2:3]
            s.csrr_D = s.cs[1:2]
            s.csrw_D = s.cs[0:1]
            

            # setting the actual write address

            s.rf_waddr_D = s.inst_D[RD]

            # csrr/csrw logic

            s.proc2mngr_en_D = s.csrw_D & (s.inst_D[CSRNUM] == CSR_PROC2MNGR)
            s.mngr2proc_D = s.csrr_D & (s.inst_D[CSRNUM] == CSR_MNGR2PROC)

            # accelerator
            if s.csrr_D and (s.inst_D[CSRNUM] != CSR_MNGR2PROC):
                s.xcelreq_type_D = XcelMsgType_READ
                s.xcelreq_D = b1(1)

            elif s.csrw_D and (s.inst_D[CSRNUM] != CSR_PROC2MNGR):
                s.xcelreq_type_D = XcelMsgType_WRITE
                s.xcelreq_D = b1(1)
            else:
                s.xcelreq_type_D = b1(0)
                s.xcelreq_D = b1(0)

        # forward wire declaration for hazard checking

        s.rf_waddr_X = Wire(Bits5)
        s.rf_waddr_M = Wire(Bits5)

        # ostall due to hazards

        s.ostall_ld_X_rs1_D = Wire(Bits1)
        s.ostall_ld_X_rs2_D = Wire(Bits1)

        s.ostall_xcel_X_rs1_D = Wire(Bits1)
        s.ostall_xcel_X_rs2_D = Wire(Bits1)

        s.ostall_hazard_D = Wire(Bits1)

        # ostall due to mngr2proc

        s.ostall_mngr_D = Wire(Bits1)

        # bypassing logic

        byp_d = b2(0)
        byp_x = b2(1)
        byp_m = b2(2)
        byp_w = b2(3)

        @s.update
        def comb_bypass_D():

            s.op1_byp_sel_D = byp_d

            if s.rs1_en_D:

                if s.val_X & (s.inst_D[RS1] == s.rf_waddr_X) & (s.rf_waddr_X != b5(0)) \
                        & s.rf_wen_pending_X:
                    s.op1_byp_sel_D = byp_x
                elif s.val_M & (s.inst_D[RS1] == s.rf_waddr_M) & (s.rf_waddr_M != b5(0)) \
                        & s.rf_wen_pending_M:
                    s.op1_byp_sel_D = byp_m
                elif s.val_W & (s.inst_D[RS1] == s.rf_waddr_W) & (s.rf_waddr_W != b5(0)) \
                        & s.rf_wen_pending_W:
                    s.op1_byp_sel_D = byp_w

            s.op2_byp_sel_D = byp_d

            if s.rs2_en_D:

                if s.val_X & (s.inst_D[RS2] == s.rf_waddr_X) & (s.rf_waddr_X != b5(0)) \
                        & s.rf_wen_pending_X:
                    s.op2_byp_sel_D = byp_x
                elif s.val_M & (s.inst_D[RS2] == s.rf_waddr_M) & (s.rf_waddr_M != b5(0)) \
                        & s.rf_wen_pending_M:
                    s.op2_byp_sel_D = byp_m
                elif s.val_W & (s.inst_D[RS2] == s.rf_waddr_W) & (s.rf_waddr_W != b5(0)) \
                        & s.rf_wen_pending_W:
                    s.op2_byp_sel_D = byp_w

        # hazards checking logic
        # Although bypassing is added, we might still have RAW when there is
        # lw instruction in X stage

        @s.update
        def comb_hazard_D():
            s.ostall_ld_X_rs1_D = s.rs1_en_D & s.val_X & s.rf_wen_pending_X \
                & (s.inst_D[RS1] == s.rf_waddr_X) & (s.rf_waddr_X != b5(0)) \
                & (s.dmemreq_type_X == ld)
         #   print("s.rs1_en_D", s.rs1_en_D, "s.val_X", s.val_X, "s.rf_wen_pending_X", s.rf_wen_pending_X)
            s.ostall_ld_X_rs2_D = s.rs2_en_D & s.val_X & s.rf_wen_pending_X \
                & (s.inst_D[RS2] == s.rf_waddr_X) & (s.rf_waddr_X != b5(0)) \
                & (s.dmemreq_type_X == ld)

            s.ostall_xcel_X_rs1_D = s.rs1_en_D & s.val_X & s.rf_wen_pending_X \
                & (s.inst_D[RS1] == s.rf_waddr_X) & (s.rf_waddr_X != b5(0)) \
                & s.xcelreq_X

            s.ostall_xcel_X_rs2_D = s.rs2_en_D & s.val_X & s.rf_wen_pending_X \
                & (s.inst_D[RS2] == s.rf_waddr_X) & (s.rf_waddr_X != b5(0)) \
                & s.xcelreq_X

            s.ostall_hazard_D = s.ostall_ld_X_rs1_D | s.ostall_ld_X_rs2_D | \
                s.ostall_xcel_X_rs1_D | s.ostall_xcel_X_rs2_D
        s.next_val_D = Wire(Bits1)

        @s.update
        def comb_D():

            # ostall due to mngr2proc not ready
            # This is get, rdy means we can get the message
            s.ostall_mngr_D = s.mngr2proc_D & ~s.mngr2proc_rdy
            # put together all ost: all conditions
            s.ostall_D = s.val_D & (s.ostall_mngr_D | s.ostall_hazard_D)

            # stall in D stage
            s.stall_D = s.val_D & (
                s.ostall_D | s.ostall_X | s.ostall_M | s.ostall_W)
            #print("s.ostall_D: ",s.ostall_D, "s.ostall_X: ",s.ostall_X, "s.ostall_M: ",s.ostall_M, "s.ostall_W: ",s.ostall_W )
            # D won't osquash
            # squash in D stage
            s.squash_D = s.val_D & s.osquash_X

            # next valid bit
            s.next_val_D = s.val_D & ~s.stall_D & ~s.squash_D

            # enable signal for send/get interface
            s.mngr2proc_en = s.val_D & ~s.stall_D & ~s.squash_D & s.mngr2proc_D

        # ---------------------------------------------------------------------
        # X stage
        # ---------------------------------------------------------------------

        @s.update
        def comb_reg_en_X():
            s.reg_en_X = ~s.stall_X

        s.inst_type_X = Wire(Bits8)
        s.rf_wen_pending_X = Wire(Bits1)
        s.proc2mngr_en_X = Wire(Bits1)
        s.dmemreq_type_X = Wire(Bits2)
        s.wb_result_sel_X = Wire(Bits2)
        s.br_type_X = Wire(Bits2)
        s.xcelreq_X = Wire(Bits1)
        s.xcelreq_type_X = Wire(Bits1)
        s.mask_sel_X = Wire(Bits3)


        @s.update_ff
        def reg_X():
            if s.reset:
                s.val_X <<= b1(0)
            elif s.reg_en_X:
                s.val_X <<= s.next_val_D
                s.rf_wen_pending_X <<= s.rf_wen_pending_D
                s.inst_type_X <<= s.inst_type_decoder_D.out
                s.alu_fn_X <<= s.alu_fn_D
                s.rf_waddr_X <<= s.rf_waddr_D
                s.proc2mngr_en_X <<= s.proc2mngr_en_D
                s.dmemreq_type_X <<= s.dmemreq_type_D
                s.wb_result_sel_X <<= s.wb_result_sel_D
                s.br_type_X <<= s.br_type_D
                s.xcelreq_X <<= s.xcelreq_D
                s.xcelreq_type_X <<= s.xcelreq_type_D
                s.mask_sel_X <<= s.mask_sel_D

        # Branch logic

        @s.update
        def comb_br_X():
            s.pc_redirect_X = s.val_X & ((s.br_type_X == br_ne)| (s.br_type_X == br_rs1)) & s.ne_X

        s.ostall_dmem_X = Wire(Bits1)
        s.ostall_xcel_X = Wire(Bits1)

        s.next_val_X = Wire(Bits1)

        s.prev = Wire(Bits1)

        @s.update
        def comb_X():

            # ostall due to dmemreq

            s.ostall_dmem_X = (s.dmemreq_type_X != nr) & ~s.dmemreq_rdy | (~s.dmemresp_prev & s.dmemresp_rdy) | (~s.dmemresp_prev2 & s.dmemresp_prev) | (~s.dmemresp_prev3 & s.dmemresp_prev2) | (~s.dmemresp_prev4 & s.dmemresp_prev3)
            # ostall due to xcelreq
            s.ostall_xcel_X = s.xcelreq_X & ~s.xcelreq_rdy  # This is send
            s.dmemresp_prev4 = s.dmemresp_prev3
            s.dmemresp_prev3 = s.dmemresp_prev2
            s.dmemresp_prev2 = s.dmemresp_prev
            s.dmemresp_prev = s.dmemresp_rdy
            s.ostall_X = s.val_X & (s.ostall_dmem_X | s.ostall_xcel_X  )

            # stall in X stage

            s.stall_X = s.val_X & (s.ostall_X | s.ostall_M | s.ostall_W)
            # osquash due to taken branches
            # Note that, in the same combinational block, we have to calculate
            # s.stall_X first then use it in osquash_X. Several people have
            # stuck here just because they calculate osquash_X before stall_X!

            s.osquash_X = s.val_X & ~s.stall_X & s.pc_redirect_X

            # send dmemreq enable if not stalling

            s.dmemreq_en = s.val_X & ~s.stall_X & (s.dmemreq_type_X != nr)

            s.dmemreq_type = b4(s.dmemreq_type_X == st)  # 0-load/DC, 1-store

            # send xcelreq enable if not stalling

            s.xcelreq_en = s.val_X & ~s.stall_X & s.xcelreq_X
            s.xcelreq_type = s.xcelreq_type_X

            # next valid bit

            s.next_val_X = s.val_X & ~s.stall_X

        # ---------------------------------------------------------------------
        # M stage
        # ---------------------------------------------------------------------

        @s.update
        def comb_reg_en_M():
            s.reg_en_M = ~s.stall_M

        s.inst_type_M = Wire(Bits8)
        s.rf_wen_pending_M = Wire(Bits1)
        s.proc2mngr_en_M = Wire(Bits1)
        s.dmemreq_type_M = Wire(Bits2)
        s.xcelreq_M = Wire(Bits1)

        @s.update_ff
        def reg_M():
            if s.reset:
                s.val_M <<= b1(0)
            elif s.reg_en_M:
                s.val_M <<= s.next_val_X
                s.rf_wen_pending_M <<= s.rf_wen_pending_X
                s.inst_type_M <<= s.inst_type_X
                s.rf_waddr_M <<= s.rf_waddr_X
                s.proc2mngr_en_M <<= s.proc2mngr_en_X
                s.dmemreq_type_M <<= s.dmemreq_type_X
                s.wb_result_sel_M <<= s.wb_result_sel_X
                s.xcelreq_M <<= s.xcelreq_X
                s.mask_sel_M <<= s.mask_sel_X


        s.ostall_xcel_M = Wire(Bits1)
        s.ostall_dmem_M = Wire(Bits1)
        s.next_val_M = Wire(Bits1)
        s.dmemresp_prev = Wire(Bits1)
        s.dmemresp_prev2 = Wire(Bits1)
        s.dmemresp_prev3 = Wire(Bits1)
        s.dmemresp_prev4 = Wire(Bits1)

        @s.update
        def comb_M():

            # ostall due to xcel resp or dmem resp
            s.ostall_xcel_M = (s.xcelreq_M & ~s.xcelresp_rdy)
            s.ostall_dmem_M = (s.dmemreq_type_M != nr) & ~s.dmemresp_rdy

         #   print("s.ostall_dmem_M: ", s.ostall_dmem_M)
         #   print("s.dmemreq_type_M",s.dmemreq_type_M)
         #   print("dmemresp_rdy:", s.dmemresp_rdy)

            s.ostall_M = s.val_M & (s.ostall_dmem_M | s.ostall_xcel_M)

            # stall in M stage

            s.stall_M = s.val_M & (s.ostall_M | s.ostall_W)

            # dmemresp/xcelresp get enable if not stalling

            s.dmemresp_en = s.val_M & ~s.stall_M & (s.dmemreq_type_M != nr)
            s.xcelresp_en = s.val_M & ~s.stall_M & s.xcelreq_M

            # next valid bit

            s.next_val_M = s.val_M & ~s.stall_M

        # ---------------------------------------------------------------------
        # W stage
        # ---------------------------------------------------------------------

        @s.update
        def comb_reg_en_W():
            s.reg_en_W = ~s.stall_W

        s.inst_type_W = Wire(Bits8)
        s.proc2mngr_en_W = Wire(Bits1)
        s.rf_wen_pending_W = Wire(Bits1)

        @s.update_ff
        def reg_W():
            if s.reset:
                s.val_W <<= b1(0)
            elif s.reg_en_W:
                s.val_W <<= s.next_val_M
                s.rf_wen_pending_W <<= s.rf_wen_pending_M
                s.inst_type_W <<= s.inst_type_M
                s.rf_waddr_W <<= s.rf_waddr_M
                s.proc2mngr_en_W <<= s.proc2mngr_en_M
                s.mask_sel_W <<= s.mask_sel_M
                s.dmemreq_type_W <<= s.dmemreq_type_M
                #print("s.dmemreq_type_W: ", s.dmemreq_type_W)

        s.ostall_proc2mngr_W = Wire(Bits1)

        @s.update
        def comb_W():

            # set RF write enable if valid

            s.rf_wen_W = s.val_W & s.rf_wen_pending_W

            # ostall due to proc2mngr

            s.ostall_W = s.val_W & s.proc2mngr_en_W & ~s.proc2mngr_rdy

            # stall in W stage

            s.stall_W = s.val_W & s.ostall_W

            # proc2mngr send is enabled if not stalling

            s.proc2mngr_en = s.val_W & ~s.stall_W & s.proc2mngr_en_W

            s.commit_inst = s.val_W & ~s.stall_W
