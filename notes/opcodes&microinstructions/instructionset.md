# INSTRUCTION SET

Cycles represent the "steps" in the micro-program counter. Since every time it resets, it goes to 0, cycles start at 0. These cycle is exactly the same in every single instruction, since it only fetches the data from the ROM to the instruction register safely.
###  $01 --> MOV A, $imm8

| Cycle | Control bits                       |
| ----- | ---------------------------------- |
| 0     | MEM_RD, nIR_LD                     |
| 1     | PC_INC, nIRDB_OE, REG_LD, nMPC_RST |
### $02 --> MOV $reg, $reg

Works with the accumulator implicitely.

| Cycle | Control bits                     |
| ----- | -------------------------------- |
| 0     | MEM_RD, nIR_LD                   |
| 1     | PC_INC, REG_LD, REG_OE, nMPC_RST |
### $03 --> MOV MARL/MARH, $imm8

When programming, the assembler will read the format, if it's MARL, the bit 8 of the instruction register which points to the selector of the MAR will be a 0. If it's MARH, the bit will be 1.

| Cycle | Control bits                        |
| ----- | ----------------------------------- |
| 0     | MEM_RD, nIR_LD                      |
| 1     | PC_INC, nIRDB_OE, nMAR_LD, nMPC_RST |
### $04 --> MOV MARL/MARH, $reg


4 ld reg, zp(8) 
5 ld reg, mar(16)
6 ld reg, XY
7 st zp(8), reg
8 st mar(16), reg
9 st XY, reg
8 push reg
9 pop reg
10 add A, reg
11 adi A, imm
12 adc A, reg
13 sub A, reg
14 sbc A, reg
15 and A, reg
16 ani A, imm
17 or A, reg
18 xor A, reg
19 inc A
20 dec A
21 inc XY
22 dec XY
23 ror A (must add rol A as a pseudoinstruction ADC A, A)
24 shr A(must add shl as a pseudoinstruction ADD A, A)
25 cp A, reg
26 cpi A, imm
30 jcc mar (jmp will be 111 decode condition)
31 call mar
32 zero-operand instructions
32.1 brk (nop is add a, a as a pseudoinstruction)
32.2 pushf
32.3 popf
32.4 ret
32.5 rti
32.6 cli
32.7 sei
32.8 halt

