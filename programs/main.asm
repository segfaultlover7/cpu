; cpu test, start at 0xC000
; start SP at 0x3FFF
.main:
  SEI
  MOV X, 0x3F
  MOV Y, 0xFF
  CLI
  MOV SP, XY
  MOV MARL, 0x09
  MOV MARH, 0xC0
  CALL MAR
  MOV X, 0x10
  MOV Y, 0x10

  MOV A, 0x20
  ADD A, 0x10
  MOV B, A
  RET


