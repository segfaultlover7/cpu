# CONTROL BITS

# EPROM 1:

PC_INC   = 0   # increment the pc
nPC_LD   = 1   # load the pc (for jmps)
PC_OE    = 2   # pc outputs data to the address bus
nPCL_OE  = 3   # pc outputs the lower byte to the data bus
nPCH_OE  = 4   # pc outputs the higher byte to the data bus
nIR_LD   = 5   # load the data from ROM the instruction register
nIRD_OE  = 6   # output the lower byte of the ir to the data bus
nIRA_OE  = 7   # output the lower byte of the ir to the address bus (LB)
nHBA_OE   = 8   # forces the higher byte of the address bus to 0x00
nMPC_RST = 9   # reset the microprogram counter (end of instruction)
MEM_RD   = 10  # read memory bus (ROM/RAM/FB/MMIO)
MEM_WR   = 11  # write in memory bus (RAM/FB/MMIO)
nMAR_LD  = 12  # load from data bus into the lower byte of the MAR
nMAR_OE  = 13  # output the entire MAR to the address bus
REG_LD   = 14  # register file load enable
REG_OE   = 15  # register file output enable

# EPROM 2:

nXY_INC   = 16  # increment the XY register pair
XY_DIR   = 17  # 0 = INC, 1 = DEC
nXYA_OE  = 18  # XY register pair output to the address bus
A_SEL    = 19  # multiplexor selector for the input of the accumulator. 0 = data bus, 1 = alu
ALU_S0   = 20  # alu select line 0
ALU_S1   = 21  # alu select line 1
ALU_S2   = 22  # alu select line 2
nALU_OE  = 23  # output the result of the alu to the data bus
ALU_CIN  = 24  # carry in on the lowest alu chip
nSHR_OE  = 25  # output a shift right of the accumulator
SHR_IN0  = 26  # bit 0 of the shr buffer; 0 = SHR, 1 = ROR
nFL_OE   = 27  # outputs the flag register to the data bus
nFL_LD   = 28  # loads the flag register
FL_SEL   = 29  # mux that selects the flag register input between ALU and data bus (only first 4 flags)
nSEI     = 30  # set interrupts
nCLI     = 31  # clear interrupts

# EPROM 3:

FB       = 32  # force B (break flag) to 1. used to distinguish hardware from software interrupts
nSP_INC  = 33  # increment the SP register
SP_DIR   = 34  # 0 = INC, 1 = DEC
nSP_LD   = 35  # load data from the address bus to the sp
nSP_OE   = 36  # output SP to the address bus
nSPL_OE  = 37  # output SPL to the data bus
nSPH_OE  = 38  # output SPH to the data bus


# active low mask:

active_low_mask = (
    (1 << nPC_LD)   | (1 << nPCL_OE)  | (1 << nPCH_OE)   |
    (1 << nIR_LD)   | (1 << nIRD_OE)  | (1 << nIRA_OE)   |
    (1 << nMPC_RST) | (1 << nMAR_LD)  | (1 << nMAR_OE)   |
    (1 << nALU_OE)  | (1 << nSHR_OE)  | (1 << nFL_OE)    |
    (1 << nFL_LD)   | (1 << nSEI)     | (1 << nCLI)      |
    (1 << nSP_INC)  | (1 << nSP_LD)   | (1 << nSP_OE)    |
    (1 << nSPL_OE)  | (1 << nSPH_OE)  | (1 << nXYA_OE)   |
    (1 << nHBA_OE)  | (1 << nXY_INC)
)

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
        i_flag = bool((addr >> 15) & 1)

        base_opcode = (opcode >> 3) & 0x1F # bits 7:3
        sub_opcode  = opcode & 0x07 # bits 2:0

        control_word = 0

        # microstep 0: instruction fetch (always the same)
        if microstep == 0:
            control_word |= (1 << MEM_RD)
            control_word |= (1 << nIR_LD)

        # from microstep 1 and onwards:
        else:

            # overlapped fetch-execute pipeline: inc pc in parallel with the instruction
            if microstep == 1:
                control_word |= (1 << PC_INC)

            # instruction encoding
            if base_opcode == 0:  # MOV reg, imm8
                if microstep == 1:
                    control_word |= (1 << nIRD_OE)
                    control_word |= (1 << REG_LD)
                    control_word |= (1 << nMPC_RST)

            if base_opcode == 1:  # MOV reg, reg
                if microstep == 1:
                    control_word |= (1 << REG_OE)
                    control_word |= (1 << REG_LD)
                    control_word |= (1 << nMPC_RST)

            if base_opcode == 2:  # MOV MARL/MARH, imm8
                if microstep == 1:
                    control_word |= (1 << nIRD_OE)
                    control_word |= (1 << nMAR_LD)
                    control_word |= (1 << nMPC_RST)

            if base_opcode == 3:  # MOV MARL/MARH, reg
                if microstep == 1:
                    control_word |= (1 << REG_OE)
                    control_word |= (1 << nMAR_LD)
                    control_word |= (1 << nMPC_RST)

            if base_opcode == 4:  # LD reg, zp(imm8)
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

            if base_opcode == 23:  # INC XY
                if microstep == 1:
                    control_word |= (1 << nXY_INC)
                    control_word |= (1 << nMPC_RST)

            if base_opcode == 24:  # DEC XY
                if microstep == 1:
                    control_word |= (1 << nXY_INC)
                    control_word |= (1 << XY_DIR)
                    control_word |= (1 << nMPC_RST)


            if base_opcode == 31:
                if sub_opcode == 0:
                    control_word |= (1 << nMPC_RST) # to do - BRK

                if sub_opcode == 1:
                    control_word |= (1 << nMPC_RST) # to do - PUSHF



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
