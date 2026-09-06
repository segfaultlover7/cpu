# CONTROL BITS

# EPROM 1:

PC_INC   = 0   # increment the pc
nPC_LD   = 1   # load the pc (for jmps)
PC_OE   = 2   # pc outputs data to the address bus
nPCL_OE  = 3   # pc outputs the lower byte to the data bus
nPCH_OE  = 4   # pc outputs the higher byte to the data bus
nIR_LD   = 5   # load the data from ROM the instruction register
nIRDB_OE = 6   # output the lower byte of the ir to the data bus
nMPC_RST = 7   # reset the microprogram counter (end of instruction)
MEM_RD   = 8   # read memory bus (ROM/RAM/FB/MMIO)
MEM_WR   = 9  # write in memory bus (RAM/FB/MMIO)
nMAR_LD  = 10  # load from data bus into the lower byte of the MAR
nMAR_OE  = 11  # output the entire MAR to the address bus
REG_LD   = 12  # register file load enable
REG_OE   = 13  # register file output enable
XY_INC   = 14  # increment the XY register pair
XY_DIR   = 15  # 0 = INC, 1 = DEC

# EPROM 2:

XY_AOE   = 16  # XY register pair output to the address bus
A_SEL    = 17  # multiplexor selector for the input of the accumulator. 0 = data bus, 1 = alu
ALU_S0   = 18  # alu select line 0
ALU_S1   = 19  # alu select line 1
ALU_S2   = 20  # alu select line 2
nALU_OE  = 21  # output the result of the alu to the data bus
ALU_CIN  = 22  # carry in on the lowest alu chip
nSHR_OE  = 23  # output a shift right of the accumulator
SHR_IN0  = 24  # bit 0 of the shr buffer; 0 = SHR, 1 = ROR
nFL_OE   = 25  # outputs the flag register to the data bus
nFL_LD   = 26  # loads the flag register
FL_SEL   = 27  # mux that selects the flag register input between ALU and data bus (only first 4 flags)
nSEI     = 28  # set interrupts
nCLI     = 29  # clear interrupts
FB       = 30  # force B (break flag) to 1. used to distinguish hardware from software interrupts
nSP_INC  = 31  # increment the SP register

# EPROM 3:

SP_DIR   = 32  # 0 = INC, 1 = DEC
nSP_LD   = 33  # load data from the address bus to the sp


# active low mask:

active_low_mask = (
    (1 << nPC_LD)   | (1 << nPCL_OE)  |
    (1 << nPCH_OE)  | (1 << nIR_LD)   | (1 << nIRDB_OE)  |
    (1 << nMPC_RST) | (1 << nMAR_LD)  | (1 << nMAR_OE)   |
    (1 << nALU_OE)  | (1 << nSHR_OE)  | (1 << nFL_OE)    |
    (1 << nFL_LD)   | (1 << nSEI)     | (1 << nCLI)      |
    (1 << nSP_INC)  | (1 << nSP_LD)
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
            if base_opcode == 1:  # MOV $A, $imm8
                if microstep == 1:
                    control_word |= (1 << nIRDB_OE)
                    control_word |= (1 << REG_LD)
                    control_word |= (1 << nMPC_RST)

            if base_opcode == 2:  # MOV $reg, $reg
                if microstep == 1:
                    control_word |= (1 << REG_OE)
                    control_word |= (1 << REG_LD)
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
