; cpu test, start at 0xC000

.main:
  MOV A, 0x55
  MOV B, A
  MOV MARL, B
