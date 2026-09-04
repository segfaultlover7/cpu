Instructions are loaded directly from memory into two 8-bit registers. The lower one, called IRLB holds bits `[7:0]`, while the higher one, IRHB holds bits `[15:8]`.

This division is done so that the IRLB is the one outputting the data onto the data-bus only when the buffer allows it, and IRHB is constantly outputting its data to the control unit.

# BIT ENCODING
The previously mentioned bit division is not complete. In order to complete dual-register instructions, if using 8 bits for the opcode, the instructions would run out fast. Imagine, for a `MOV Rdst, Rsrc`, if all total possibilities of registers were done, there would be 2⁸ (64) instructions JUST for that `MOV` instruction.

This is solved by hard-wiring some bits to a decoder inside the register file, for both the source and destination.

The way these bits are allocated is the following:

- Bits `[15:8]` --> Opcode
- Bits `[10:8]` --> Destination Register Select (Rdst)
- Bits `[7:5]`  --> Source Register Select (Rsrc)
- Bits `[7:0]`  --> Immediate 8-bit data

![[Pasted image 20260903205937.png|353]]

# TABLE OF INSTRUCTION CLASSES & BIT ENCODING

| Instruction class                         | Opcode [15:8] | Rdst [10:8]            | Rsrc [7:5]  | Imm [7:0]      |
| ----------------------------------------- | ------------- | ---------------------- | ----------- | -------------- |
| **Dual Register** <br>`ADD R1, R2`        | 5-bit Op      | Target Rdst            | Source Rsrc | (ignored)      |
| **Register-immediate** <br>`MOV R1, 0x12` | 5-bit Op      | Target Rdst            | (ignored)   | 8-bit data     |
| **Single-Register** <br>`INC R1, PUSH R2` | 5-bit Op      | Target Rdst            | (ignored)   | (ignored)      |
| **Conditional Jump** <br>`JZ 0x80`        | 5-bit Op      | Conditional Code (0-7) | (ignored)   | Target address |
| **No-operand** <br>`NOP, HALT`            | 8-bit Op      | (ignored)              | (ignored)   | (ignored)      |

As seen in the table, the bit encoding is really similar to [[04 Uniform High-Byte Bit Instruction Set (DISCARDED)]], but the change on the no-operand instructions is 
what gives 8 extra sub-instructions per instruction.
Instruction set: [[Instruction set]] 