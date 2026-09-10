# CONTROL BITS

# EPROM 1:

PC_INC   = 0    # increment the pc
nPC_LD   = 1    # load the pc (for jmps)
PC_OE    = 2    # pc outputs data to the address bus
nPCL_OE  = 3    # pc outputs the lower byte to the data bus
nPCH_OE  = 4    # pc outputs the higher byte to the data bus
nIR_LD   = 5    # load the data from ROM the instruction register
nIRD_OE  = 6    # output the lower byte of the ir to the data bus
nIRA_OE  = 7    # output the lower byte of the ir to the address bus (LB)
nHBA_OE  = 8    # forces the higher byte of the address bus to 0x00
nMPC_RST = 9    # reset the microprogram counter (end of instruction)
MEM_RD   = 10   # read memory bus (ROM/RAM/FB/MMIO)
MEM_WR   = 11   # write in memory bus (RAM/FB/MMIO)
nMARL_LD = 12   # load from data bus into the lower byte of the MAR
nMARH_LD = 13   # load from data bus into the higher byte of the MAR
nMAR_OE  = 14   # output the MAR to the address bus
REG_LD   = 15   # register file load enable

# EPROM 2:

REG_OE   = 16   # register file output enable
nXY_INC  = 17   # increment the XY register pair
XY_DIR   = 18   # 0 = INC, 1 = DEC
nXYA_OE  = 19   # XY register pair output to the address bus
A_SEL    = 20   # multiplexor selector for the input of the accumulator. 0 = data bus, 1 = alu
ALU_S0   = 21   # alu select line 0
ALU_S1   = 22   # alu select line 1
ALU_S2   = 23   # alu select line 2
nALU_OE  = 24   # output the result of the alu to the data bus
ALU_CIN  = 25   # carry in on the lowest alu chip
nSHR_OE  = 26   # output a shift right of the accumulator
SHR_IN0  = 27   # bit 0 of the shr buffer; 0 = SHR, 1 = ROR
nFL_OE   = 28   # outputs the flag register to the data bus
nFL_LD   = 29   # loads the flag register
FL_SEL   = 30   # mux that selects the flag register input between ALU and data bus (only first 4 flags)
B_SET    = 31   # force B (break flag) to 1. used to distinguish hardware from software interrupts

# EPROM 3:

I_SET    = 32   # force I (interrupt flag) to 1. used in SEI/CLI instructions
I_WRITE  = 33   # write the value of I_SET onto the 7474 flipflop
nSP_INC  = 34   # increment the SP register
SP_DIR   = 35   # 0 = INC, 1 = DEC
nSP_LD   = 36   # load data from the address bus to the sp
nSP_OE   = 37   # output SP to the address bus
nSPL_OE  = 38   # output SPL to the data bus
nSPH_OE  = 39   # output SPH to the data bus
nCLR_IRQ = 40   # clears the latch of the IRQ pending
nV_OE    = 41   # output the interrupt vector to the address bus
V_B0     = 42   # toggles bit 0 of the interrupt vector 0xFFFE/0xFFFF


# active low mask:

active_low_mask = (
    (1 << nPC_LD)   | (1 << nPCL_OE)  | (1 << nPCH_OE)   |
    (1 << nIR_LD)   | (1 << nIRD_OE)  | (1 << nIRA_OE)   |
    (1 << nHBA_OE)  | (1 << nMPC_RST) | (1 << nMARL_LD)  |
    (1 << nMARH_LD) | (1 << nMAR_OE)  | (1 << nXY_INC)   |
    (1 << nXYA_OE)  | (1 << nALU_OE)  | (1 << nSHR_OE)   |
    (1 << nFL_OE)   | (1 << nFL_LD)   | (1 << nSP_INC)   |
    (1 << nSP_LD)   | (1 << nSP_OE)   | (1 << nSPL_OE)   |
    (1 << nSPH_OE)  | (1 << nCLR_IRQ) | (1 << nV_OE)
)


# flags

def check_condition(sub_opcode, z, c, n, v):
    conditions = {
        0: c,        # JC
        1: not c,    # JNC
        2: z,        # JZ
        3: not z,    # JNZ
        4: n,        # JN
        5: not n,    # JNN
        6: v,        # JV
        7: True      # JMP
    }
    return conditions.get(sub_opcode, False)


# generating the microcode for the eproms

total_address = 1 << 16

def gen_microcode():
    eprom1 = [0] * total_address
    eprom2 = [0] * total_address
    eprom3 = [0] * total_address

    for addr in range(total_address):
        opcode = addr & 0xFF #bits 0-7
        microstep = (addr >> 8) & 0x07 #bits 8-10

        z_flag = bool((addr >> 11) & 1)
        c_flag = bool((addr >> 12) & 1)
        n_flag = bool((addr >> 13) & 1)
        v_flag = bool((addr >> 14) & 1)

        irq_pending = bool((addr >> 15) & 1)

        base_opcode = (opcode >> 3) & 0x1F # bits 7:3
        sub_opcode  = opcode & 0x07 # bits 2:0

        control_word = 0

        # interrupt sequence:
        if irq_pending:
            if microstep == 0: # push PCH to stack
                control_word |= (1 << PC_OE)
                control_word |= (1 << nPCH_OE)
                control_word |= (1 << nSP_OE)
                control_word |= (1 << nSP_INC)
                control_word |= (1 << SP_DIR)
                control_word |= (1 << MEM_WR)
            elif microstep == 1: # push PCL to stack
                control_word |= (1 << PC_OE)
                control_word |= (1 << nPCL_OE)
                control_word |= (1 << nSP_OE)
                control_word |= (1 << nSP_INC)
                control_word |= (1 << SP_DIR)
                control_word |= (1 << MEM_WR)
            elif microstep == 2: # push flags, B = 0
                control_word |= (1 << PC_OE)
                control_word |= (1 << nFL_OE)
                control_word |= (1 << nSP_OE)
                control_word |= (1 << nSP_INC)
                control_word |= (1 << SP_DIR)
                control_word |= (1 << MEM_WR)
            elif microstep == 3: # fetch vector low (0xFFFE)
                control_word |= (1 << PC_OE)
                control_word |= (1 << nV_OE)
                control_word |= (1 << MEM_RD)
                control_word |= (1 << nIR_LD)
            elif microstep == 4: # save in MARL the vector low
                control_word |= (1 << nIRD_OE)
                control_word |= (1 << nMARL_LD)
            elif microstep == 5: # fetch vector high (0xFFFF)
                control_word |= (1 << PC_OE)
                control_word |= (1 << nV_OE)
                control_word |= (1 << V_B0)
                control_word |= (1 << MEM_RD)
                control_word |= (1 << nIR_LD)
            elif microstep == 6: # save in MARH the vector high
                control_word |= (1 << nIRD_OE)
                control_word |= (1 << nMARH_LD)
            elif microstep == 7: # load MAR into PC, disable I, clear hardware latch
                control_word |= (1 << PC_OE)
                control_word |= (1 << nPC_LD)
                control_word |= (1 << nMAR_OE)
                control_word |= (1 << I_SET)
                control_word |= (1 << I_WRITE)
                control_word |= (1 << nCLR_IRQ)
                control_word |= (1 << nMPC_RST)
        else:
                # microstep 0: instruction fetch (always the same)
            if microstep == 0:
                    control_word |= (1 << MEM_RD)
                    control_word |= (1 << nIR_LD)

                # from microstep 1 and onwards:
            else:

                # overlapped fetch-execute pipeline: inc pc in parallel with the instruction
                if microstep == 1:
                    control_word |= (1 << PC_INC)

                # evaluate condition for current address flag
                take_jump = check_condition(sub_opcode, z_flag, c_flag, n_flag, v_flag)

                # instruction encoding
                if base_opcode == 0:  # MOV REG
                    if microstep == 1:
                        control_word |= (1 << nIRD_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 1:  # MOV REG, REG
                    if microstep == 1:
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 2:
                    if sub_opcode == 0: # MOV MARL, Imm
                        if microstep == 1:
                            control_word |= (1 << nIRD_OE)
                            control_word |= (1 << nMARL_LD)
                            control_word |= (1 << nMPC_RST)

                    elif sub_opcode == 1: # MOV MARH, Imm
                        if microstep == 1:
                            control_word |= (1 << nIRD_OE)
                            control_word |= (1 << nMARL_LD)
                            control_word |= (1 << nMPC_RST)

                if base_opcode == 3:
                    if sub_opcode == 0: # MOV MARL, REG
                        if microstep == 1:
                            control_word |= (1 << REG_OE)
                            control_word |= (1 << nMARL_LD)
                            control_word |= (1 << nMPC_RST)

                    elif sub_opcode == 1: # MOV MARH, REG
                        if microstep == 1:
                            control_word |= (1 << REG_OE)
                            control_word |= (1 << nMARL_LD)
                            control_word |= (1 << nMPC_RST)

                if base_opcode == 4:  # LD reg, Imm
                    if microstep == 1:
                        control_word |= (1 << PC_OE)
                        control_word |= (1 << nIRA_OE)
                        control_word |= (1 << nHBA_OE)
                        control_word |= (1 << MEM_RD)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 5:  # LD reg, MAR
                    if microstep == 1:
                        control_word |= (1 << PC_OE)
                        control_word |= (1 << nMAR_OE)
                        control_word |= (1 << MEM_RD)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 6:  # LD reg, XY
                    if microstep == 1:
                        control_word |= (1 << PC_OE)
                        control_word |= (1 << nXYA_OE)
                        control_word |= (1 << MEM_RD)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 7:  # ST zp(imm8), reg
                    if microstep == 1:
                        control_word |= (1 << PC_OE)
                        control_word |= (1 << nIRA_OE)
                        control_word |= (1 << nHBA_OE)
                        control_word |= (1 << MEM_WR)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 8:  # ST MAR, reg
                    if microstep == 1:
                        control_word |= (1 << PC_OE)
                        control_word |= (1 << nMAR_OE)
                        control_word |= (1 << MEM_WR)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 9:  # ST XY, reg
                    if microstep == 1:
                        control_word |= (1 << PC_OE)
                        control_word |= (1 << nXYA_OE)
                        control_word |= (1 << MEM_WR)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 10: # PUSH reg
                    if microstep == 1:
                        control_word |= (1 << PC_OE)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << nSP_OE)
                        control_word |= (1 << nSP_INC)
                        control_word |= (1 << SP_DIR)
                        control_word |= (1 << MEM_WR)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 11: # POP reg
                    if microstep == 1:
                        control_word |= (1 << PC_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << nSP_OE)
                        control_word |= (1 << nSP_INC)
                        control_word |= (1 << MEM_RD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 12:  # ADD A, reg
                    if microstep == 1:
                        control_word |= (1 << ALU_S0)
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 13:  # ADD A, imm8
                    if microstep == 1:
                        control_word |= (1 << ALU_S0)
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << nIRD_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 14:  # ADC A, reg
                    if microstep == 1:
                        control_word |= (1 << ALU_S0)
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << ALU_CIN)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 15:  # SUB A, reg
                    if microstep == 1:
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << ALU_CIN)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 16:  # SBC A, reg
                    if microstep == 1:
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 17:  # AND A, reg
                    if microstep == 1:
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << ALU_S2)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 18:  # AND A, imm8
                    if microstep == 1:
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << ALU_S2)
                        control_word |= (1 << nIRD_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 19:  # OR A, reg
                    if microstep == 1:
                        control_word |= (1 << ALU_S0)
                        control_word |= (1 << ALU_S2)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 20:  # XOR A, reg
                    if microstep == 1:
                        control_word |= (1 << ALU_S2)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 21:  # INC A
                    if microstep == 1:
                        control_word |= (1 << ALU_S0)
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << ALU_CIN)
                        control_word |= (1 << nIRD_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 22:  # DEC A
                    if microstep == 1:
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << nIRD_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << A_SEL)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 23:  # SHR A
                    if microstep == 1:
                        control_word |= (1 << nSHR_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 24:  # ROR A
                    if microstep == 1:
                        control_word |= (1 << nSHR_OE)
                        control_word |= (1 << REG_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 25:  # CP A, reg
                    if microstep == 1:
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << ALU_CIN)
                        control_word |= (1 << REG_OE)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 26:  # CP A, imm
                    if microstep == 1:
                        control_word |= (1 << ALU_S1)
                        control_word |= (1 << ALU_CIN)
                        control_word |= (1 << nIRD_OE)
                        control_word |= (1 << nFL_LD)
                        control_word |= (1 << nMPC_RST)

                if base_opcode == 27:  # JCC MAR # CORRECT THE FORMAT
                    if microstep == 1:
                        if sub_opcode == 0: # JZ (JMP if z)
                            control_word |= (1 << PC_OE)
                            control_word |= (1 << nPC_LD)
                            control_word |= (1 << nMAR_OE)
                            control_word |= (1 << nMPC_RST)

                        if sub_opcode == 1: # JNZ (JMP if not z)
                            control_word |= (1 << nMPC_RST)

                        if sub_opcode == 7: # JMP
                            control_word |= (1 << PC_OE)
                            control_word |= (1 << nPC_LD)
                            control_word |= (1 << nMAR_OE)
                            control_word |= (1 << nMPC_RST)

                if base_opcode == 28: # JCC XY
                    if microstep == 1:
                        if sub_opcode == 7: # JMP
                            control_word |= (1 << PC_OE)
                            control_word |= (1 << nPC_LD)
                            control_word |= (1 << nXYA_OE)
                            control_word |= (1 << nMPC_RST)

                if base_opcode == 29:  # Pointers and Subroutine # CORRECT THE FORMAT + ADD RET
                    if microstep == 1:
                        if sub_opcode == 0:  # INC XY
                            control_word |= (1 << nXY_INC)
                            control_word |= (1 << nMPC_RST)

                        if sub_opcode == 1:  # DEC XY
                            control_word |= (1 << nXY_INC)
                            control_word |= (1 << XY_DIR)
                            control_word |= (1 << nMPC_RST)

                        else:
                            control_word |= (1 << PC_OE)
                            control_word |= (1 << nPCL_OE)
                            control_word |= (1 << nSP_INC)
                            control_word |= (1 << SP_DIR)
                            control_word |= (1 << nSP_OE)
                            control_word |= (1 << MEM_WR)

                            if microstep == 2:
                                control_word |= (1 << PC_OE)
                                control_word |= (1 << nPCH_OE)
                                control_word |= (1 << nSP_INC)
                                control_word |= (1 << SP_DIR)
                                control_word |= (1 << nSP_OE)
                                control_word |= (1 << MEM_WR)

                            if microstep == 3:
                                control_word |= (1 << PC_OE)
                                control_word |= (1 << PC_LD)

                                if sub_opcode == 2:         # CALL MAR
                                    control_word |= (1 << nMAR_OE)

                                if sub_opcode == 3:         # CALL XY
                                    control_word |= (1 << nXYA_OE)

                                control_word |= (1 << nMPC_RST)

                if base_opcode == 30: # Stack Pointer operations
                    if sub_opcode == 0: # MOV SP, MAR
                        if microstep == 1:
                            pass
                        elif microstep == 2:
                            control_word |= (1 << PC_OE)
                            control_word |= (1 << nMAR_OE)
                            control_word |= (1 << nSP_LD)
                            control_word |= (1 << nMPC_RST)

                    elif sub_opcode == 1: # MOV MAR, SP
                        if microstep == 1:
                            control_word |= (1 << nSPL_OE)
                            control_word |= (1 << nMARL_LD)
                        elif microstep == 2:
                            control_word |= (1 << nSPH_OE)
                            control_word |= (1 << nMARH_LD)
                            control_word |= (1 << nMPC_RST)

                    elif sub_opcode == 2: # MOV SP, XY
                        if microstep == 1:
                            pass
                        elif microstep == 2:
                            control_word |= (1 << PC_OE)
                            control_word |= (1 << nXYA_OE)
                            control_word |= (1 << nSP_LD)
                            control_word |= (1 << nMPC_RST)

                    elif sub_opcode == 3: # INC SP
                        if microstep == 1:
                            control_word |= (1 << nSP_INC)
                            control_word |= (1 << nMPC_RST)

                    elif sub_opcode == 4: # DEC SP
                        if microstep == 1:
                            control_word |= (1 << nSP_INC)
                            control_word |= (1 << SP_DIR)
                            control_word |= (1 << nMPC_RST)

                    elif sub_opcode == 6: # MOV X, SPH
                        if microstep == 1:
                            control_word |= (1 << nSPH_OE)
                            control_word |= (1 << REG_LD)
                            control_word |= (1 << nMPC_RST)

                    elif sub_opcode == 7: # MOV Y, SPL
                        if microstep == 1:
                            control_word |= (1 << nSPL_OE)
                            control_word |= (1 << REG_LD)
                            control_word |= (1 << nMPC_RST)

                if base_opcode == 31: # CORRECT THE FORMAT
                    if microstep == 1:
                        if sub_opcode == 0:   # BRK
                            control_word |= (1 << nMPC_RST)

                        if sub_opcode == 3:   # RET
                            control_word |= (1 << PC_OE)
                            control_word |= (1 << nSP_INC)
                            control_word |= (1 << nSP_OE)
                            control_word |= (1 << MEM_RD)
                            control_word |= (1 << nMARH_LD)
                            if microstep == 2:
                                control_word |= (1 << PC_OE)
                                control_word |= (1 << nSP_INC)
                                control_word |= (1 << nSP_OE)
                                control_word |= (1 << MEM_RD)
                                control_word |= (1 << nMARL_LD)
                            if microstep == 3:
                                control_word |= (1 << PC_OE)
                                control_word |= (1 << nPC_LD)
                                control_word |= (1 << nMAR_OE)
                                control_word |= (1 << nMPC_RST)

                    if sub_opcode == 0:
                        control_word |= (1 << nMPC_RST) # to do - BRK

                    if sub_opcode == 1:
                        control_word |= (1 << nMPC_RST) # to do - PUSHF

                    if sub_opcode == 5: # SEI
                        control_word |= (1 << I_SET)
                        control_word |= (1 << I_WRITE)
                        control_word |= (1 << nMPC_RST)

                    if sub_opcode == 6:
                        control_word |= (1 << I_WRITE)
                        control_word |= (1 << nMPC_RST)

        f_control_word = control_word ^ active_low_mask

        eprom1[addr] = f_control_word & 0xFFFF
        eprom2[addr] = (f_control_word >> 16) & 0xFFFF
        eprom3[addr] = (f_control_word >> 32) & 0xFFFF

    return eprom1, eprom2, eprom3


def save_digitalhex(filename, data):
    with open(filename, "w") as f:
        f.write("v2.0 raw\n")
        for val in data:
            f.write(f"{val:04X}\n")

if __name__ == "__main__":
    e1, e2, e3 = gen_microcode()

    save_digitalhex("eprom1.hex", e1)
    save_digitalhex("eprom2.hex", e2)
    save_digitalhex("eprom3.hex", e3)
