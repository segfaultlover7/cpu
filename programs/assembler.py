import sys
import os

# ==============================================================================
# HARDWARE DEFINITIONS & MAPS
# ==============================================================================

REGISTER_MAP = {
    "A": 0, "B": 1, "C": 2, "D": 3,
    "E": 4, "F": 5, "X": 6, "Y": 7
}

JMP_COND_MAP = {
    "JMP": 0, "JZ": 1, "JNZ": 2, "JC": 3,
    "JNC": 4, "JN": 5, "JV": 6, "JB": 7
}

# ==============================================================================
# TOKENIZER & PARSER HELPERS
# ==============================================================================

def clean_and_tokenize(raw_line):
    """Strips comments, extracts labels, and normalizes tokens."""
    line = raw_line.split(';')[0].strip()
    if not line:
        return None, []
    
    label = None
    if ':' in line:
        parts = line.split(':', 1)
        label = parts[0].strip()
        line = parts[1].strip()

    if not line:
        return label, []

    tokens = [t.strip() for t in line.replace(',', ' ').split() if t.strip()]
    return label, tokens

def parse_val(val_str, symbol_table):
    """Parses immediate numbers or label addresses."""
    if val_str in symbol_table:
        return symbol_table[val_str]
    if val_str.startswith(("0x", "0X")):
        return int(val_str, 16)
    if val_str.isdigit():
        return int(val_str, 10)
    raise ValueError(f"Unknown symbol or invalid value: '{val_str}'")

# ==============================================================================
# 16-BIT INSTRUCTION ENCODER
# ==============================================================================

def encode_instruction(mnemonic, tokens, symbol_table):
    """
    Bit Layout:
    [15:11] base_opcode (5 bits)
    [10:8]  r_dest / subopcode / jmp_cond / selector bit at Bit 8 (3 bits)
    [7:5]   r_src (3 bits)
    [7:0]   immediate / low byte address (8 bits)
    """
    
    # --------------------------------------------------------------------------
    # SPECIAL SELECTOR INSTRUCTIONS (MARL/MARH, INC/DEC XY, CALL/JCC targets)
    # --------------------------------------------------------------------------

    # 1. MOV MARL, REG (Bit 8 = 0) vs MOV MARH, REG (Bit 8 = 1)
    if mnemonic == "MOV" and tokens[0] in ["MARL", "MARH"]:
        r_src = REGISTER_MAP[tokens[1]]
        bit_8 = 1 if tokens[0] == "MARH" else 0
        return (0x03 << 11) | (bit_8 << 8) | (r_src << 5)

    # 2. INC XY (Bit 8 = 0) vs DEC XY (Bit 8 = 1)
    if mnemonic in ["INC", "DEC"] and tokens[0] == "XY":
        bit_8 = 1 if mnemonic == "DEC" else 0
        return (0x17 << 11) | (bit_8 << 8)

    # 3. CALL MAR (subop = 0) vs CALL XY (subop = 1) vs CALL .label
    if mnemonic == "CALL":
        target = tokens[0]
        if target == "XY":
            return (0x1E << 11) | (1 << 8)
        elif target == "MAR":
            return (0x1E << 11) | (0 << 8)
        else:
            val = parse_val(target, symbol_table)
            return (0x1E << 11) | (0 << 8) | (val & 0xFF)

    # 4. JCC MAR (Opcode 0x1D) vs JCC XY (Opcode 0x18) vs JCC .label
    if mnemonic in JMP_COND_MAP:
        cond_code = JMP_COND_MAP[mnemonic]
        target = tokens[0]
        if target == "XY":
            return (0x18 << 11) | (cond_code << 8)
        elif target == "MAR":
            return (0x1D << 11) | (cond_code << 8)
        else:
            val = parse_val(target, symbol_table)
            return (0x1D << 11) | (cond_code << 8) | (val & 0xFF)

    # --------------------------------------------------------------------------
    # STANDARD INSTRUCTION DISPATCH
    # --------------------------------------------------------------------------

    # Zero-Operand Ops
    if mnemonic == "NOP":   return (0x1F << 11) | (0 << 8)
    if mnemonic == "HALT":  return (0x1F << 11) | (1 << 8)
    if mnemonic == "ZREG":  return (0x1F << 11) | (2 << 8)

    # Moves
    if mnemonic == "MOV":
        r_dest = tokens[0]
        src = tokens[1]
        if r_dest == "MAR":
            val = parse_val(src, symbol_table)
            return (0x02 << 11) | (val & 0xFF)
        elif src in REGISTER_MAP:
            return (0x01 << 11) | (REGISTER_MAP[r_dest] << 8) | (REGISTER_MAP[src] << 5)
        else:
            val = parse_val(src, symbol_table)
            return (0x00 << 11) | (REGISTER_MAP[r_dest] << 8) | (val & 0xFF)

    # Memory Loads
    if mnemonic == "LD":
        r_dest = REGISTER_MAP[tokens[0]]
        src = tokens[1]
        if src == "MAR":   return (0x05 << 11) | (r_dest << 8)
        elif src == "XY":  return (0x06 << 11) | (r_dest << 8)
        else:
            val = parse_val(src, symbol_table)
            return (0x04 << 11) | (r_dest << 8) | (val & 0xFF)

    # Memory Stores
    if mnemonic == "ST":
        target = tokens[0]
        r_src = REGISTER_MAP[tokens[1]]
        if target == "MAR":   return (0x08 << 11) | (r_src << 5)
        elif target == "XY":  return (0x09 << 11) | (r_src << 5)
        else:
            val = parse_val(target, symbol_table)
            return (0x07 << 11) | (r_src << 5) | (val & 0xFF)

    # Stack Operations
    if mnemonic == "PUSH":  return (0x0A << 11) | (REGISTER_MAP[tokens[0]] << 8)
    if mnemonic == "POP":   return (0x0B << 11) | (REGISTER_MAP[tokens[0]] << 8)

    # Unary Operations
    if mnemonic == "INC":  return (0x15 << 11) | (REGISTER_MAP[tokens[0]] << 8)
    if mnemonic == "DEC":  return (0x16 << 11) | (REGISTER_MAP[tokens[0]] << 8)
    if mnemonic == "ROR":  return (0x19 << 11) | (REGISTER_MAP[tokens[0]] << 8)
    if mnemonic == "SHR":  return (0x1A << 11) | (REGISTER_MAP[tokens[0]] << 8)

    # ALU Operations (REG vs IMM)
    alu_opcodes = {
        "ADD": (0x0C, 0x0D), "ADC": (0x0E, None), "SUB": (0x0F, None),
        "SBC": (0x10, None), "AND": (0x11, 0x12), "OR":  (0x13, None),
        "XOR": (0x14, None), "CP":  (0x1C, 0x1B)
    }

    if mnemonic in alu_opcodes:
        reg_op, imm_op = alu_opcodes[mnemonic]
        r_dest = REGISTER_MAP[tokens[0]]
        src = tokens[1]
        if src in REGISTER_MAP:
            return (reg_op << 11) | (r_dest << 8) | (REGISTER_MAP[src] << 5)
        elif imm_op is not None:
            val = parse_val(src, symbol_table)
            return (imm_op << 11) | (r_dest << 8) | (val & 0xFF)
        else:
            raise SyntaxError(f"Instruction '{mnemonic}' does not support immediate values.")

    raise SyntaxError(f"Unknown instruction: {mnemonic} {' '.join(tokens)}")

# ==============================================================================
# TWO-PASS ASSEMBLER ENGINE
# ==============================================================================

def assemble(source_code, default_origin=0xC000):
    lines = source_code.splitlines()
    symbol_table = {}
    parsed_program = []
    
    current_address = default_origin

    # --------------------------------------------------------------------------
    # PASS 1: Build Symbol Table & Address Mapping
    # --------------------------------------------------------------------------
    for line_num, raw_line in enumerate(lines, 1):
        label, tokens = clean_and_tokenize(raw_line)
        
        if label:
            clean_label = label.lstrip('.')
            if clean_label in symbol_table:
                raise NameError(f"Line {line_num}: Duplicate label '{label}'")
            symbol_table[clean_label] = current_address
            symbol_table[f".{clean_label}"] = current_address

        if tokens:
            mnemonic = tokens[0].upper()
            
            if mnemonic == ".ORG":
                current_address = parse_val(tokens[1], symbol_table)
                continue
            
            parsed_program.append({
                "line_num": line_num,
                "address": current_address,
                "mnemonic": mnemonic,
                "operands": tokens[1:]
            })
            
            # Word-addressed ROM: increment PC by 1 for each 16-bit word
            current_address += 1

    # --------------------------------------------------------------------------
    # PASS 2: Generate Binary Code Words
    # --------------------------------------------------------------------------
    binary_words = []
    for item in parsed_program:
        word = encode_instruction(item["mnemonic"], item["operands"], symbol_table)
        binary_words.append((item["address"], word))

    return symbol_table, binary_words

# ==============================================================================
# OUTPUT FORMATTER
# ==============================================================================

def generate_digital_hex(binary_words):
    """Outputs Digital v2.0 raw hex with word-based sparse address markers (@ADDR)."""
    header = "v2.0 raw\n"
    lines = []
    last_addr = None

    for addr, word in binary_words:
        # Check for non-sequential address jump (+1 word)
        #if last_addr is None or addr != last_addr + 1:
        #    lines.append(f"@{addr:04X}")
        lines.append(f"{word:04X}")
        last_addr = addr

    return header + "\n".join(lines)

# ==============================================================================
# CLI EXECUTION
# ==============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <file.asm>")
        sys.exit(1)

    asm_filepath = sys.argv[1]
    
    try:
        with open(asm_filepath, 'r') as f:
            asm_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{asm_filepath}' not found.")
        sys.exit(1)

    symbols, code = assemble(asm_code)

    print(f"--- Assembling {asm_filepath} ---")
    print("\n[Symbol Table]")
    for sym, addr in symbols.items():
        if not sym.startswith('.'):
            print(f"  {sym:<12} -> 0x{addr:04X}")

    print("\n[Assembled 16-Bit Word Addressing]")
    for addr, word in code:
        print(f"  0x{addr:04X}: 0x{word:04X}  ({word:016b})")

    hex_output = generate_digital_hex(code)
    
    output_filepath = os.path.splitext(asm_filepath)[0] + ".hex"
    with open(output_filepath, 'w') as f:
        f.write(hex_output)
        
    print(f"\nSuccessfully generated '{output_filepath}'")
