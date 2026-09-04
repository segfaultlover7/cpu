The register file consists of 7, 8-bit GPRs, from which the first 5 are regular registers and the last two work as a up/down counter and can output data to the address bus in 1 cycle.

As explained in [[05 Orthogonal Fixed Encoding with Opcode Extension]], bits `[10:8]` are connected to the demux of the register destination, and bits `[7:5]` are connected to the demux of the source register. Since they are 3 bits wide, the demux gives up to 2³ (8) possible combinations. Out of the 8, the first one (or default) is the accumulator, shown in the [[ALU]]. The 7 left are the registers which can be seen here:

![[rfile.png]]

The decision to have both X and Y registers be up/down counters is explained: [[06 Registers X and Y INC arithmetic]].