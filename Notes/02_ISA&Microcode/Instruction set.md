1 mov A, imm
2 mov reg , reg (works with A both ways)
3 mov mar, reg (select l or h with bit 8)
4 ld reg, mar(16)
5 ld reg, XY
6 st mar(16), reg
7 st XY, reg
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
27 jmp imm8
28 jmp mar
29 jcc imm8 (the conditions are decoded looking at the 3 lowest bits of the IRHB)
30 jcc mar
31 call mar
32 SYSCALLS
32.1 nop
32.2 pushf
32.3 popf
32.4 ret
32.5 rti
32.6 cli
32.7 sei
32.8 halt

