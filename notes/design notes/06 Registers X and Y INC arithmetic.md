Given the architecture, every arithmetic or logic instruction must pass through the accumulator and be stored there. Since X and Y work as a 16-bit pointer that is hardwired to the address bus, when an increment is needed, what must be done is:

`MOV A, Y` --> `INC A` --> `MOV Y, A`

Meaning that every time an increment for the pointer is needed, 3 whole instructions must be performed, which is quite slow and must be changed.

That's why, this 2 last registers (that could also be called R6 and R7) are not regular registers, but up/down counters, using 74HC191 ICs. They are also connected similar to the Stack Pointer, so that when Y overflows, X increments automatically, meaning that only 1 instruction is needed:

`INC XY`

This works both for INC and DEC.
