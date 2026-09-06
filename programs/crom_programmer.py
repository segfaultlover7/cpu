
# CONTROL BITS

# EPROM 1:

PC_INC   = 0   # increment the pc
nPC_LD   = 1   # load the pc (for jmps)
nPC_OE   = 2   # pc outputs data to the address bus
nPCL_OE  = 3   # pc outputs the lower byte to the data bus
nPCH_OE  = 4   # pc outputs the higher byte to the data bus
nIR_LD   = 5   # load the data from ROM the instruction register
nIRDB_OE = 6   # output the lower byte of the ir to the data bus
nIRAB_OE = 7   # output the lower byte of the ir to the address bus
nMPC_RST = 8   # reset the microprogram counter (end of instruction)
MEM_RD   = 9   # read memory bus (ROM/RAM/FB/MMIO)
MEM_WR   = 10  # write in memory bus (RAM/FB/MMIO)
nMARL_LD = 11  # load from data bus into the lower byte of the MAR
nMARH_LD = 12  # load from data bus into the high byte of the MAR (fix this in digital, only one, select via hardware)
nMAR_OE  = 13  # output the entire MAR to the address bus
REG_LD   = 14  # register file load enable
REG_OE   = 15  # register file output enable

# EPROM 2:

XY_INC   = 16  # increment the XY register pair
XY_DIR   = 17  # 0 = INC, 1 = DEC
XY_AOE   = 18  # XY register pair output to the address bus
A_SEL    = 19  # multiplexor selector for the input of the accumulator. 0 = data bus, 1 = alu
ALU_S0   = 20  # alu select line 0
ALU_S1   = 21  # alu select line 1
ALU_S2   = 22  # alu select line 2
nALU_OE  = 23  # output the result of the alu to the data bus
ALU_CIN  = 24  # carry in on the lowest alu chip
nSHR_OE  = 25  # output a shift right of the accumulator
SHR_IN0  = 26  # bit 0 of the shr buffer; 0 = SHR, 1 = ROR


