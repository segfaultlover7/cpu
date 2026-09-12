i dont know where to put this yet so i will write it here.

Initially, Jump instructions were only possible as indirect, meaning that if I wanted to jump to a label, the only possible way to do so in 1 line of code was to let the assembler handle it and treat it as a pseudo-instruction which decodes into three instructions:

MOV MARH, LABEL_HIGH
MOV MARL, LABEL_LOW
JCC/JMP MAR

This solution had many problems.
First of all, it was the slowest, because it had to execute 3 whole instructions just for a jump label.
Second, if a conditional jump's condition is NOT met, the instruction would still take as long as if the condition is met, purely because it would be checked at the last instruction.
And third, and by far most importantly, if an interrupt is triggered, since it synchronizes on the microstep 0 (as well as other conditions), it could happen that the first or second instructions (loading MAR) are performed, and once the routine is finished and everything gets popped back, since the MAR is not pushed onto the stack, the values would be lost and therefore the instruction would be incorrect.

### THE SOLUTION

Native 2-word jumps.
Now, not only the indirect jumps (JMP MAR, JMP XY) are in the instruction set, but the direct jumps are not treated as a pseudoinstruction, they are a 2-word instruction.
Because the ROM can only read a word at a time, an instruction with a 16bit immediate must be done in two words.

It would be decoded like this:
· word 1: instruction opcode + label_high
· word 2: instruction opcode + label_low

This way, all three problems from before are fixed, because, since it's treated as two instructions, the microsteps are less, but also, because the condition check is done at the beginning, if conditions are not met, it quickly increments the pc again to point at the next instruction, and most importantly, since it is treated as 1 instruction, the microprogram counter is not reset until the entire instruction is performed, meaning that if interrupt happens on the middle of the execution, it would wait until the instruction is finished, eliminating MAR register corruption.