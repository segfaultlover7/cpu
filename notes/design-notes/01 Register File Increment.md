The first change I immediately though of when programming on the first design of the CPU was that 4 general purpose registers was not enough.

Not only the problem was the commodity of using few registers, but this also caused me to constantly be accessing the RAM, which is far slower in terms of cycles than using the GPRs.

This change has a great cost in hardware, since now (almost) the amount of register chips had to be doubled, but the trade-off was worth. 

It's "almost" double the amount, because now instead of having 4 GPRs + the accumulator, the accumulator will be accessed as a GPR (in decodification), so now there are 7 GPRs + Accumulator, making less instructions with enough commodity for programming.