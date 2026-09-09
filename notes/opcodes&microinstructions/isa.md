# INSTRUCTION SET ARCHITECTURE

## Instructions Table

| Mnemonic      | Opcode | subOp |               Pseudocode               |  Flags  | Cycles |
| :------------ | :----: | :---: | :------------------------------------: | :-----: | :----: |
| MOV REG, Imm  |  0x00  |   -   |               Rd <-- Imm               |    -    |   2    |
| MOV REG, REG  |  0x01  |   -   |               Rd <-- Rs                |    -    |   2    |
| MOV MARL, Imm |  0x02  |   0   |              MARL <-- Imm              |    -    |   2    |
| MOV MARH, Imm |  0x02  |   1   |              MARH <-- Imm              |    -    |   2    |
| MOV MARL, REG |  0x03  |   0   |              MARL <-- Rs               |    -    |   2    |
| MOV MARH, REG |  0x03  |   1   |              MARH <-- Rs               |    -    |   2    |
| LD REG, Imm   |  0x04  |   -   |            Rd <-- Mem[Imm]             |    -    |   2    |
| LD REG, MAR   |  0x05  |   -   |            Rd <-- Mem[MAR]             |    -    |   2    |
| LD REG, XY    |  0x06  |   -   |             Rd <-- Mem[XY]             |    -    |   2    |
| ST Imm, REG   |  0x07  |   -   |            Mem[Imm] <-- Rs             |    -    |   2    |
| ST MAR, REG   |  0x08  |   -   |            Mem[MAR] <-- Rs             |    -    |   2    |
| ST XY, REG    |  0x09  |   -   |             Mem[XY] <-- Rs             |    -    |   2    |
| PUSH REG      |  0x0A  |   -   |    Mem[SP] <-- Rs<br>SP <-- SP - 1     |    -    |   2    |
| POP REG       |  0x0B  |   -   |    SP <-- SP + 1<br>Rd <-- Mem[SP]     |    -    |   2    |
| ADD A, REG    |  0x0C  |   -   |              A <-- A + Rs              | Z,C,N,V |   2    |
| ADD A, Imm    |  0x0D  |   -   |             A <-- A + Imm              | Z,C,N,V |   2    |
| ADC A, REG    |  0x0E  |   -   |           A <-- A + Rs + Cin           | Z,C,N,V |   2    |
| SUB A, REG    |  0x0F  |   -   |              A <-- A - Rs              | Z,C,N,V |   2    |
| SBC A, REG    |  0x10  |   -   |           A <-- A - Rs + Cin           | Z,C,N,V |   2    |
| AND A, REG    |  0x11  |   -   |              A <-- A & Rs              |   Z,N   |   2    |
| AND A, Imm    |  0x12  |   -   |             A <-- A & Imm              |   Z,N   |   2    |
| OR A, REG     |  0x13  |   -   |             A <-- A \| Rs              |   Z,N   |   2    |
| XOR A, REG    |  0x14  |   -   |            A <-- Rd (+) Rs             |   Z,N   |   2    |
| INC A         |  0x15  |   -   |           A <-- A + 0 + Cin            | Z,C,N,V |   2    |
| DEC A         |  0x16  |   -   |              A <-- A - FF              | Z,C,N,V |   2    |
| SHR A         |  0x17  |   -   |              A <-- A >> 1              |  Z,N,V  |   2    |
| ROR A         |  0x18  |   -   |           A <-- {C, A[7:1]}            |  Z,N,V  |   2    |
| CP A, REG     |  0x19  |   -   |                 A - Rs                 | Z,C,N,V |   2    |
| CP A, Imm     |  0x1A  |   -   |                A - Imm                 | Z,C,N,V |   2    |
| JZ MAR        |  0x1B  |  0x0  |       if (Z == 1):<br>PC <-- MAR       |    -    |   2    |
| JNZ MAR       |  0x1B  |  0x1  |       if (Z == 0):<br>PC <-- MAR       |    -    |   2    |
| JC MAR        |  0x1B  |  0x2  |       if (C == 1):<br>PC <-- MAR       |    -    |   2    |
| JNC MAR       |  0x1B  |  0x3  |       if (C == 0):<br>PC <-- MAR       |    -    |   2    |
| JN MAR        |  0x1B  |  0x4  |       if (N == 1):<br>PC <-- MAR       |    -    |   2    |
| JNN MAR       |  0x1B  |  0x5  |       if (N == 0):<br>PC <-- MAR       |    -    |   2    |
| JV MAR        |  0x1B  |  0x6  |       if (V == 1):<br>PC <-- MAR       |    -    |   2    |
| JMP MAR       |  0x1B  |  0x7  |               PC <-- MAR               |    -    |   2    |
| JZ XY         |  0x1C  |  0x0  |       if (Z == 1):<br>PC <-- XY        |    -    |   2    |
| JNZ XY        |  0x1C  |  0x1  |       if (Z == 0):<br>PC <-- XY        |    -    |   2    |
| JC XY         |  0x1C  |  0x2  |       if (C == 1):<br>PC <-- XY        |    -    |   2    |
| JNC XY        |  0x1C  |  0x3  |       if (C == 0):<br>PC <-- XY        |    -    |   2    |
| JN XY         |  0x1C  |  0x4  |       if (N == 1):<br>PC <-- XY        |    -    |   2    |
| JNN XY        |  0x1C  |  0x5  |       if (N == 0):<br>PC <-- XY        |    -    |   2    |
| JV XY         |  0x1C  |  0x6  |       if (V == 1):<br>PC <-- XY        |    -    |   2    |
| JMP XY        |  0x1C  |  0x7  |               PC <-- XY                |    -    |   2    |
| INC XY        |  0x1D  |  0x0  |                 XY + 1                 |    -    |   2    |
| DEC XY        |  0x1D  |  0x1  |                 XY - 1                 |    -    |   2    |
| CALL MAR      |  0x1D  |  0x2  | SP - 1<br>Mem[SP] <-- PC<br>PC <-- MAR |    -    |   4    |
| CALL XY       |  0x1D  |  0x3  | SP - 1<br>Mem[SP] <-- PC<br>PC <-- XY  |    -    |   4    |
| MOV SP, MAR   |  0x1E  |  0x0  |               SP <-- MAR               |    -    |   3    |
| MOV MAR, SP   |  0x1E  |  0x1  |               MAR <-- SP               |    -    |   3    |
| MOV SP, XY    |  0x1E  |  0x2  |               SP <-- XY                |    -    |   3    |
| INC SP        |  0x1E  |  0x3  |                 SP + 1                 |    -    |   2    |
| DEC SP        |  0x1E  |  0x4  |                 SP - 1                 |    -    |   2    |
| MOV X, SPH    |  0x1E  |  0x6  |               X <-- SPH                |    -    |   2    |
| MOV Y, SPL    |  0x1E  |  0x7  |               Y <-- SPL                |    -    |   2    |
| BRK           |  0x1F  |  0x0  |                B = 1 (?                |    -    |   2    |
| PUSHF         |  0x1F  |  0x1  |        Mem[SP] <-- FR<br>SP - 1        |    -    |   2    |
| POPF          |  0x1F  |  0x2  |        SP + 1<br>FR <-- Mem[SP]        |    -    |   2    |
| RET           |  0x1F  |  0x3  |                                        |    -    |        |
| RETI          |  0x1F  |  0x4  |                                        |    -    |        |
| SEI           |  0x1F  |  0x5  |                 I = 1                  |    -    |        |
| CLI           |  0x1F  |  0x6  |                 I = 0                  |    -    |        |
| HALT          |  0x1F  |  0x7  |                HALT mPC                |    -    |        |
## Pseudo-Instructions Table

nop, shl, rol --> simple 1 instruction
more complex instructions:
ld reg, imm16
st imm16, reg
jcc imm16
all pseudo-instructions will use mar as a default "volatile" register


