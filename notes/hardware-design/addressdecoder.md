
!write myself!
## Decoder Schematic Connections

### 1. 74LS139 (Dual 2-to-4 Decoder)

**Half 1: Top-Level 16K Split**

- **1B (Pin 3):** `A15`
    
- **1A (Pin 2):** `A14`
    
- **1G (Pin 1):** `GND`
    
- **1Y3 (Pin 4):** Active-LOW upper 16 KB detect (`0xC000–0xFFFF`). Drives `74LS00` Pins 1 & 2 and `74LS138` Pin 4.
    

**Half 2: Top 1 KB Peripheral Split**

- **2B (Pin 13):** `A9`
    
- **2A (Pin 14):** `A8`
    
- **2G (Pin 15):** `\PERIPHERAL_1KB_CS` (From `74LS138` Pin 7)
    
- **2Y0..2Y2 (Pins 12, 11, 10):** Unused
    
- **2Y3 (Pin 9):** `\MMIO_CS` (`0xFF00–0xFFFF`)
    

### 2. 74LS138 (3-to-8 Decoder — Top 1 KB Isolation)

- **A (Pin 1):** `A11`
    
- **B (Pin 2):** `A12`
    
- **C (Pin 3):** `A13`
    
- **\G2A (Pin 4):** `1Y3` (From `74LS139` Pin 4)
    
- **\G2B (Pin 5):** `GND`
    
- **G1 (Pin 6):** `A10` _(Active-HIGH enable; isolates 0xFC00–0xFFFF from 0xF800)_
    
- **Y7 (Pin 7):** `\PERIPHERAL_1KB_CS` (`0xFC00–0xFFFF`)
    

### 3. 74LS00 (Quad NAND Gate)

- **Gate 1 (RAM Select Inverter):**
    
    - **Input Pins 1 & 2:** Connected together to `74LS139 1Y3` (Pin 4)
        
    - **Output Pin 3:** `\RAM_CS` (`0x0000–0xBFFF`)
        
- **Gate 2 (ROM Select):**
    
    - **Input Pin 4:** `\RAM_CS` (From Pin 3)
        
    - **Input Pin 5:** `\PERIPHERAL_1KB_CS` (From `74LS138` Pin 7)
        
    - **Output Pin 6:** `\ROM_CS` (`0xC000–0xFBFF`)
        
- **Gate 3 (Peripheral Inverter):**
    
    - **Input Pins 9 & 10:** Connected together to `\PERIPHERAL_1KB_CS` (From `74LS138` Pin 7)
        
    - **Output Pin 8:** `PERIPHERAL_HIGH`
        
- **Gate 4 (Framebuffer Select):**
    
    - **Input Pin 12:** `PERIPHERAL_HIGH` (From Pin 8)
        
    - **Input Pin 13:** `\MMIO_CS` (From `74LS139` Pin 9)
        
    - **Output Pin 11:** `\FB_CS` (`0xFC00–0xFEFF`)
        

## Signal Logic Equations

- $\text{\RAM\_CS} = \text{NOT}(A_{15} \cdot A_{14})$
    
- $\text{\PERIPHERAL\_1KB\_CS} = A_{15} \cdot A_{14} \cdot A_{13} \cdot A_{12} \cdot A_{11} \cdot A_{10}$
    
- $\text{\ROM\_CS} = \text{NAND}(\text{\RAM\_CS}, \text{\PERIPHERAL\_1KB\_CS})$
    
- $\text{\MMIO\_CS} = \text{\PERIPHERAL\_1KB\_CS} \text{ AND } (A_9 \cdot A_8)$
    
- $\text{\FB\_CS} = \text{NAND}(\text{NOT}(\text{\PERIPHERAL\_1KB\_CS}), \text{\MMIO\_CS})$
    

## Hardware Verification Steps

1. **RAM Verification:** Assert address `0x0000` through `0xBFFF`. Verify `\RAM_CS` drops to LOW (0V) while `\ROM_CS`, `\FB_CS`, and `\MMIO_CS` remain HIGH (5V).
    
2. **ROM Verification:** Assert address `0xC000` through `0xFBFF`. Verify `\ROM_CS` drops to LOW (0V).
    
3. **Boundary Verification:** Assert address `0xF800`. Verify `\FB_CS` remains HIGH (5V) and drops to LOW (0V) only when incrementing to `0xFC00`.
    
4. **MMIO Verification:** Assert address `0xFF00` through `0xFFFF`. Verify `\MMIO_CS` drops to LOW (0V) while `\FB_CS` returns to HIGH (5V).