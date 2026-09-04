Each instruction is a 16-bit word, that when loaded into the instruction register, is divided into two. IRLB (bits 0:7) works as the payload, while IRHB (bits 8-15) works as the control.
# BIT ENCODING

Every register is hardwired to a specific bit position, given by the first 3 bits of the IRHB (bits 8-10). This way, every time an instruction requires a certain register to be the destination of information that's on the data bus, the decodification is done instantaneously on the register file.

The rest of the IRHB (bits 11-15) are connected to the control unit. This bits are the actual opcode, meaning that with 5 bits, there's a total of 32 possible instructions.

For the IRLB (bits 0-7), normally they are all connected to the data bus with a buffer in between, which is activated when an immediate value is needed somewhere in the CPU, however, the last 3 bits (bits 5-7) are also hardwired into the register file to the register source bits.

The connections are as following:

![Instruction Set](notes/Attachments/(DISCARDED)ins_set.png)
# TABLE OF INSTRUCTION CLASSES & BIT ENCODING

| Instruction class                         | Opcode [15:11] | Rdst [10:8]            | Rsrc [7:5]  | Imm [7:0]      |
| ----------------------------------------- | -------------- | ---------------------- | ----------- | -------------- |
| **Dual Register** <br>`ADD R1, R2`        | 5-bit Op       | Target Rdst            | Source Rsrc | (ignored)      |
| **Register-immediate** <br>`MOV R1, 0x12` | 5-bit Op       | Target Rdst            | (ignored)   | 8-bit data     |
| **Single-Register** <br>`INC R1, PUSH R2` | 5-bit Op       | Target Rdst            | (ignored)   | (ignored)      |
| **Conditional Jump** <br>`JZ 0x80`        | 5-bit Op       | Conditional Code (0-7) | (ignored)   | Target address |
| **No-operand** <br>`NOP, HALT`            | 5-bit Op       | (ignored)              | (ignored)   | (ignored)      |

# Issues & why was it discarded
The problem with this approach is that, only having 32 instructions was a major constraint, because the amount of instructions I need for every module to work and also a handful amount of qol instructions for the programmer is insufficient.

When making the previous table, I realized that, if I connected all 8 bits of IRHB to the opcode, while using the same bit connection as before, I could make use of those instructions that ignore the destination and IRLB (No-operand instructions).

That's why, the next Instruction set: [[05 Orthogonal Fixed Encoding with Opcode Extension]] was needed in order to have all of the instructions I need.