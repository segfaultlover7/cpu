; cpu test

.ORG 0xC100

.main:
  MOV A, 0x55
  MOV B, A
  MOV MARL, B
