# INSTRUCTION SET

Cycles represent the "steps" in the micro-program counter. Since every time it resets, it goes to 0, cycles start at 0. These cycle is exactly the same in every single instruction, since it only fetches the data from the ROM to the instruction register safely.
###  $00 --> MOV $reg, $imm8

| Cycle | Control bits                       |
| ----- | ---------------------------------- |
| 0     | MEM_RD, nIR_LD                     |
| 1     | PC_INC, nIRDB_OE, REG_LD, nMPC_RST |
### $01 --> MOV $reg, $reg

Works with the accumulator implicitely.

| Cycle | Control bits                     |
| ----- | -------------------------------- |
| 0     | MEM_RD, nIR_LD                   |
| 1     | PC_INC, REG_LD, REG_OE, nMPC_RST |
### $02 --> MOV MARL/MARH, $imm8

When programming, the assembler will read the format, if it's MARL, the bit 8 of the instruction register which points to the selector of the MAR will be a 0. If it's MARH, the bit will be 1.

| Cycle | Control bits                        |
| ----- | ----------------------------------- |
| 0     | MEM_RD, nIR_LD                      |
| 1     | PC_INC, nIRDB_OE, nMAR_LD, nMPC_RST |
### $03 --> MOV MARL/MARH, $r

| Cycle | Control bits                      |
| ----- | --------------------------------- |
| 0     | MEM_RD, nIR_LD                    |
| 1     | PC_INC, REG_OE, nMAR_LD, nMPC_RST |
### $04 --> LD $r, zp(8)

Load the data from the zero-page RAM address range to a register

| Cycle | Control bits                                 |
| ----- | ------------------------------------------ |
| 0     | MEM_RD, nI                                   |
| 1 PC_INC, nIRA_OE, nHBA_OE, MEM_RD, nMPC_RST D,  E,  |
### $05 --> LD $reg, MAR

Load the data of address (MAR) of RAM into a register

| Cycle | Control bits                             |
| ----- | ---------------------------------------- |
| 0     | MEM_RD, nIR_LD                           |
| 1     | PC_INC, PC_OE, nMAR_OE, MEM_RD, nMPC_RST |
### $06 --> LD $reg, XY

| Cycle | Control bits                            |
| ----- | --------------------------------------- |
| 0     | MEM_RD, nIR_LD                          |
| 1     | PC_INC, PC_OE, XY_AOE, MEM_RD, nMPC_RST |
### $07 --> ST zp(8), $reg


7 st zp(8), reg
8 st mar(16), reg
9 st XY, reg
10 push reg
11 pop reg
12 add A, reg
13 adi A, imm
14 adc A, reg
15 sub A, reg
16 sbc A, reg
17 and A, reg
18 ani A, imm
19 or A, reg
20 xor A, reg
21 inc A
22 dec A
23 inc XY
24 dec XY
25 ror A (must add rol A as a pseudoinstruction ADC A, A)
26 shr A(must add shl as a pseudoinstruction ADD A, A)
27 cp A, reg
28 cpi A, imm
29 jcc mar (jmp will be 111 decode condition)
30 call mar

## $31 --> Zero-Operand Instructions

This operations only rely on using the opcode and do not need to use any registers or immediate data from the instruction. For this, with 1 instruction opcode, 8 sub-opcodes are fetched from the 3 lowest bits of the IRHB:
### · 1 --> BRK

| Cycle | Control bits     |
| ----- | ---------------- |
| 0     | MEM_RD, nIR_LD   |
| 1     | PC_INC, nMPC_RST |
### · 2 --> PUSHF

### · 3 --> POPF

### · 4 --> RET
### · 5 --> RTI
### · 6 --> CLI
### · 7 --> SEI

### · 8 --> HALT
