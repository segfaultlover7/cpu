# ALEPH-8 -- CPU Design & Implementation

The Aleph-8 is an 8-bit Von Neumann architecture with a 16-bit address bus built entirely from 74HC ICs.
## Overview

This repository contains the complete design and documentation of the CPU simulation (made in Digital), as well as the code for the assembler and the programmer of the control unit.

My goal with this repository is to have a place to deposit all my documentation in order to, once finished, make my Bachelor's Thesis. I should say though, i'm an electronics engineer, meaning I barely have any background on computer architecture, so this is not some academic or professional project.

- Architecture: Von Neumann accumulator based
- Instruction set: 32 instructions subdecoded to a total of ~50
- Control unit: Microprogrammed on three 16-bit UV erasable EPROMs

## Architecture

(Missing a block diagram, will do once finished)

<img src="../Attachments/cpu.png" alt="ALU Block Diagram" width="900" />

### Main modules

- **Clock** -> Three 555 timers used for manual and automatic clock(on breadboard)
- **ALU** -> 8-bit accumulator-based ALU able to do ADD, ADC, SUB, SBC, AND, OR, XOR, SHR, SHL, ROR, ROL, with immediates and registers.
- **Register File** -> 7 general purpose registers, 2 of which work together as pointers connected to the address bus.
- **Memory** -> 48 KB of RAM and 16 KB of ROM
- **Instruction Register** -> 16-bit register hardwired to the output of the two program ROMs.
- **Program Counter** -> 16-bit PC which addresses the entire 64 KB of memory
- **Micro-Program Counter** -> 4-bit counter which executes each stage of every instruction.
- **Stack Pointer** -> 16-bit SP starting from the end on RAM.
- **Memory Address Register** -> 16-bit up/down counter used for all types of instructions that need accessing the address bus.
- **Control Unit** -> Three 16-bit EPROMs programmed with all of the control bits.
- **Flag Register** -> Register which holds the state of 5 flags.
- **MMIO** -> Module that enables the flow of data from the CPU to the I/O devices.
- **Interrupt Module** -> Module that synchronizes interrupts and tells the CPU when to do perform an interrupt routine.

## STATUS

Currently, I'm documenting each module, and the ones finished are:
- Stack Pointer
- Program Counter
- Memory Address Register

The rest are not done or completed yet.

## Acknowledgments

I want to start by thanking [mattbatwings](https://github.com/mattbatwings), who gave me the inspiration to attempt building my first computer in Minecraft. After that, [Ben Eater](https://github.com/beneater) was the one that showed me how these computers can be brought to life in breadboards.

I also want to mention [Fadil](https://github.com/Fadil-1), from whom I got the idea to use an SPI OLED, and whose CPU showed me that it is possible to build an actual potent computer in breadboards.