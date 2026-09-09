# INSTRUCTION SET ARCHITECTURE

## Instructions Table

| Mnemonic      | Opcode | subOp |           Pseudocode            |  Flags  | Cycles |
| :------------ | :----: | :---: | :-----------------------------: | :-----: | :----: |
| MOV REG, Imm  |  0x00  |   -   |           Rd <-- Imm            |    -    |   2    |
| MOV REG, REG  |  0x01  |   -   |            Rd <-- Rs            |    -    |   2    |
| MOV MARL, Imm |  0x02  |   0   |          MARL <-- Imm           |    -    |   2    |
| MOV MARH, Imm |  0x02  |   1   |          MARH <-- Imm           |    -    |   2    |
| MOV MARL, REG |  0x03  |   0   |           MARL <-- Rs           |    -    |   2    |
| MOV MARH, REG |  0x03  |   1   |           MARH <-- Rs           |    -    |   2    |
| LD REG, Imm   |  0x04  |   -   |         Rd <-- Mem[Imm]         |    -    |   2    |
| LD REG, MAR   |  0x05  |   -   |         Rd <-- Mem[MAR]         |    -    |   2    |
| LD REG, XY    |  0x06  |   -   |         Rd <-- Mem[XY]          |    -    |   2    |
| ST Imm, REG   |  0x07  |   -   |         Mem[Imm] <-- Rs         |    -    |   2    |
| ST MAR, REG   |  0x08  |   -   |         Mem[MAR] <-- Rs         |    -    |   2    |
| ST XY, REG    |  0x09  |   -   |         Mem[XY] <-- Rs          |    -    |   2    |
| PUSH REG      |  0x0A  |   -   | SP <-- SP - 1<br>Mem[SP] <-- Rs |    -    |   2    |
| POP REG       |  0x0B  |   -   | Rd <-- Mem[SP]<br>SP <-- SP + 1 |    -    |   2    |
| ADD A, REG    |  0x0C  |   -   |         Rd <-- Rd + Rs          | Z,C,N,V |   2    |
| ADD A, Imm    |  0x0D  |   -   |         Rd <-- Rd + Imm         | Z,C,N,V |   2    |
| ADC A, REG    |  0x0E  |   -   |      Rd <-- Rd + Rs + Cin       | Z,C,N,V |   2    |
| SUB A, REG    |  0x0F  |   -   |         Rd <-- Rd - Rs          | Z,C,N,V |   2    |
| SBC A, REG    |  0x10  |   -   |      Rd <-- Rd - Rs + Cin       | Z,C,N,V |   2    |
| AND A, REG    |  0x11  |   -   |                                 |         |        |
| AND A, Imm    |  0x12  |   -   |                                 |         |        |
| OR A, REG     |  0x13  |   -   |                                 |         |        |
| XOR A, REG    |  0x14  |   -   |                                 |         |        |
| INC A         |        |       |                                 |         |        |
| DEC A         |        |       |                                 |         |        |
| SHR A         |        |       |                                 |         |        |
| ROR A         |        |       |                                 |         |        |
| CP A          |        |       |                                 |         |        |
| CP A, Imm     |        |       |                                 |         |        |
| JZ MAR        |        |       |                                 |         |        |
| JNZ MAR       |        |       |                                 |         |        |
| JC MAR        |        |       |                                 |         |        |
| JNC MAR       |        |       |                                 |         |        |
| JN MAR        |        |       |                                 |         |        |
| JNN MAR       |        |       |                                 |         |        |
| JV MAR        |        |       |                                 |         |        |
| JMP MAR       |        |       |                                 |         |        |
|               |        |       |                                 |         |        |
|               |        |       |                                 |         |        |
|               |        |       |                                 |         |        |

## Pseudo-Instructions Table

nop, shl, rol --> simple 1 instruction
more complex instructions:
ld reg, imm16
st imm16, reg
jcc imm16
all pseudo-instructions will use mar as a default "volatile" register