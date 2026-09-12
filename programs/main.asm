; ==============================================================================
; Test Program: Direct Immediate Jumps & Interrupt Safety
; ==============================================================================

.ORG 0xC000

START:
    CLI                      ; Enable interrupts to allow IRQ testing
    MOV A, 0x05              ; Initialize accumulator with 5

    ; 1. Test Condition Fail (False Branch Fall-Through)
    ; Sub-opcode 2 = JZ. Since A != 0, Z flag is 0. Condition fails.
    ; Should skip the 2-byte operand (TARGET_FAIL) in 2 cycles and hit INC A.
    JZ TARGET_FAIL           

    INC A                    ; Executed! A becomes 6.

    ; 2. Test Condition Pass (True Branch Jump)
    ; Sub-opcode 2 = JZ. Compare A (6) with 6 -> sets Z flag = 1.
    CP A, 0x06               
    JZ TARGET_PASS           ; Condition met! Jumps directly to TARGET_PASS.

    ; If JZ fails to jump, execution hits HALT (Test Failed)
    HALT                     

TARGET_FAIL:
    ; Danger Zone: If JZ incorrectly jumps here on false, test halts.
    HALT                     

TARGET_PASS:
    ; 3. Test Interrupt Hazard Safety
    ; Load MAR with dummy data, then execute a 3-byte jump. 
    ; Even if an IRQ hits mid-program, MAR will be safely overwritten 
    ; by JZ's internal fetch steps without destroying previous state.
    MOV MARL, 0xAA
    MOV MARH, 0xBB

    ; Sub-opcode 3 = JNZ. Since A is still 6, Z flag is 0 (A != 0).
    ; JNZ condition is True -> Jumps to SUCCESS.
    JNZ SUCCESS              

    HALT                     

SUCCESS:
    HALT                     ; Test Passed! PC ends up here safely.
