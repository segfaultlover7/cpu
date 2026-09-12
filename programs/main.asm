ORG 0xC000

MOV MARL, 0xFF
MOV MARH, 0x01

MOV SP, MAR

MOV X, 0xBF
MOV Y, 0x00

RESET_ENTRY:
    SEI
MAIN_LOOP:
    JMP MAIN_LOOP

KEYBOARD_ISR:
    LD A, XY
    RETI

; Vector space automatically splits targets into two zero-extended byte words
ORG 0xFFF0
    DW RESET_ENTRY
    DW 0x0000
    DW KEYBOARD_ISR

