# MEMORY ADDRESS REGISTER

The Memory Address Register (or MAR) is a 16-bit register used to communicate between the data bus and the address bus. Without this register, the CPU could not perform 16-bit jumps or access the entire RAM.

Unlike the XY register, this is a more "volatile" register, because it is used by the CPU implicitly to perform some operations, as well as some pseudoinstructions.

In order to load data into it, it must be done separately in the lower byte (MARL) and the higher byte (MARH). 

To save instructions, a decoder looks at the bit 8 and decides whether to store in the MARL or the MARH (bit 8 = 0 --> MARL, bit 8 = 1 --> MARH).