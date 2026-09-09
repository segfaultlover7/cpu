import sys
import os

# ==============================================================================
# HARDWARE DEFINITIONS & MAPS (ISA SPECIFIC)
# ==============================================================================

REGISTER_MAP = {
    "A": 0, "B": 1, "C": 2, "D": 3,
    "E": 4, "F": 5, "X": 6, "Y": 7
}

JMP_COND_MAP = {
    "JZ": 0, "JNZ": 1, "JC": 2, "JNC": 3,
    "JN": 4, "JNN": 5, "JV": 6, "JMP": 7
}

SYSTEM_OPS = {
    "BRK": 0, "PUSHF": 1, "POPF": 2, "RET": 3,
    "RETI": 4, "SEI": 5, "CLI": 6, "HALT": 7
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
    """Parses immediate values, label addresses, and LOW/HIGH byte modifiers."""
    if val_str.startswith("LOW:"):
        return parse_val(val_str[4:], symbol_table) & 0xFF
    if val_str.startswith("HIGH:"):
        return (parse_val(val_str[5:], symbol_table) >> 8) & 0xFF
    if val_str in symbol_table:
        return symbol_table[val_str]
    if val_str.startswith(("0x", "0X")):
        return int(val_str, 16)
    if val_str.isdigit() or (val_str.startswith('-') and val_str[1:].isdigit()):
        return int(val_str, 10)
    raise ValueError(f"Unknown symbol or invalid value: '{val_str}'")

# ==============================================================================
# PSEUDOINSTRUCTION EXPANDER
# ==============================================================================

def expand_pseudoinstructions(mnemonic, tokens):
    """
    Expands high-level pseudoinstructions into base ISA instructions.
    - CALL label / CALL MAR, label -> MOV MARL + MOV MARH + CALL MAR
    - CALL XY, label               -> MOV X + MOV Y + CALL XY
    """
    if mnemonic in ["CALL", "CALLXY"]:
        if mnemonic == "CALLXY":
            target = tokens[0]
            return [
                ("MOV", ["X", f"LOW:{target}"]),
                ("MOV", ["Y", f"HIGH:{target}"]),
                ("CALL", ["XY"])
            ]
        
        # Syntax: CALL MAR / CALL XY (hardware direct) vs CALL label / CALL MAR label / CALL XY label
        if len(tokens) == 1:
            target = tokens[0]
            if target in ["MAR", "XY"]:
                return [(mnemonic, tokens)]  # Hardware instruction
            else:
                # Default CALL label expands via MAR pointer
                return [
                    ("MOV", ["MARL", f"LOW:{target}"]),
                    ("MOV", ["MARH", f"HIGH:{target}"]),
                    ("CALL", ["MAR"])
                ]
        elif len(tokens) == 2:
            ptr, target = tokens[0], tokens[1]
            if ptr == "MAR":
                return [
                    ("MOV", ["MARL", f"LOW:{target}"]),
                    ("MOV", ["MARH", f"HIGH:{target}"]),
                    ("CALL", ["MAR"])
                ]
            elif ptr == "XY":
                return [
                    ("MOV", ["X", f"LOW:{target}"]),
                    ("MOV", ["Y", f"HIGH:{target}"]),
                    ("CALL", ["XY"])
                ]

    return [(mnemonic, tokens)]

# ==============================================================================
# 16-BIT INSTRUCTION ENCODER
# ==============================================================================

def encode_instruction(mnemonic, tokens, symbol_table):
    """
    Encodes instructions according to the exact ISA table opcodes and subopcodes.
    """
    # --------------------------------------------------------------------------
    # Opcode 0x1F: System & Interrupt Instructions
    # --------------------------------------------------------------------------
    if mnemonic in SYSTEM_OPS:
        return (0x1F << 11) | (SYSTEM_OPS[mnemonic] << 8)

    # --------------------------------------------------------------------------
    # Opcode 0x1E: Stack Pointer & Special Register Instructions
    # --------------------------------------------------------------------------
    if mnemonic == "MOV":
        if tokens[0] == "SP" and tokens[1] == "MAR":
            return (0x1E << 11) | (0x0 << 8)
        elif tokens[0] == "MAR" and tokens[1] == "SP":
            return (0x1E << 11) | (0x1 << 8)
        elif tokens[0] == "SP" and tokens[1] == "XY":
            return (0x1E << 11) | (0x2 << 8)
        elif tokens[0] == "X" and tokens[1] == "SPH":
            return (0x1E << 11) | (0x6 << 8)
        elif tokens[0] == "Y" and tokens[1] == "SPL":
            return (0x1E << 11) | (0x7 << 8)
    elif mnemonic == "INC" and tokens[0] == "SP":
        return (0x1E << 11) | (0x3 << 8)
    elif mnemonic == "DEC" and tokens[0] == "SP":
        return (0x1E << 11) | (0x4 << 8)

    # --------------------------------------------------------------------------
    # Opcode 0x1D: Pointer Operations & Hardware Calls
    # --------------------------------------------------------------------------
    if mnemonic == "INC" and tokens[0] == "XY":
        return (0x1D << 11) | (0x0 << 8)
    if mnemonic == "DEC" and tokens[0] == "XY":
        return (0x1D << 11) | (0x1 << 8)
    if mnemonic == "CALL":
        if tokens[0] == "MAR":
            return (0x1D << 11) | (0x2 << 8)
        elif tokens[0] == "XY":
            return (0x1D << 11) | (0x3 << 8)

    # --------------------------------------------------------------------------
    # Opcode 0x1B / 0x1C: Conditional & Unconditional Jumps
    # --------------------------------------------------------------------------
    if mnemonic in JMP_COND_MAP:
        subop = JMP_COND_MAP[mnemonic]
        target = tokens[0]
        if target == "MAR":
            return (0x1B << 11) | (subop << 8)
        elif target == "XY":
            return (0x1C << 11) | (subop << 8)

    # --------------------------------------------------------------------------
    # Opcode 0x02 / 0x03: MOV MARL / MOV MARH
    # --------------------------------------------------------------------------
    if mnemonic == "MOV" and tokens[0] in ["MARL", "MARH"]:
        bit_8 = 1 if tokens[0] == "MARH" else 0
        src = tokens[1]
        if src in REGISTER_MAP:
            return (0x03 << 11) | (bit_8 << 8) | (REGISTER_MAP[src] << 5)
        else:
            val = parse_val(src, symbol_table)
            return (0x02 << 11) | (bit_8 << 8) | (val & 0xFF)

    # --------------------------------------------------------------------------
    # Opcode 0x00 / 0x01: MOV Register Operations
    # --------------------------------------------------------------------------
    if mnemonic == "MOV" and tokens[0] in REGISTER_MAP:
        r_dest = REGISTER_MAP[tokens[0]]
        src = tokens[1]
        if src in REGISTER_MAP:
            return (0x01 << 11) | (r_dest << 8) | (REGISTER_MAP[src] << 5)
        else:
            val = parse_val(src, symbol_table)
            return (0x00 << 11) | (r_dest << 8) | (val & 0xFF)

    # --------------------------------------------------------------------------
    # Opcode 0x04 / 0x05 / 0x06: LD Register Operations
    # --------------------------------------------------------------------------
    if mnemonic == "LD":
        r_dest = REGISTER_MAP[tokens[0]]
        src = tokens[1]
        if src == "MAR":
            return (0x05 << 11) | (r_dest << 8)
        elif src == "XY":
            return (0x06 << 11) | (r_dest << 8)
        else:
            val = parse_val(src, symbol_table)
            return (0x04 << 11) | (r_dest << 8) | (val & 0xFF)

    # --------------------------------------------------------------------------
    # Opcode 0x07 / 0x08 / 0x09: ST Memory Operations
    # --------------------------------------------------------------------------
    if mnemonic == "ST":
        target = tokens[0]
        r_src = REGISTER_MAP[tokens[1]]
        if target == "MAR":
            return (0x08 << 11) | (r_src << 5)
        elif target == "XY":
            return (0x09 << 11) | (r_src << 5)
        else:
            val = parse_val(target, symbol_table)
            return (0x07 << 11) | (r_src << 8) | (val & 0xFF)

    # --------------------------------------------------------------------------
    # Opcode 0x0A / 0x0B: PUSH & POP Operations
    # --------------------------------------------------------------------------
    if mnemonic == "PUSH":
        return (0x0A << 11) | (REGISTER_MAP[tokens[0]] << 8)
    if mnemonic == "POP":
        return (0x0B << 11) | (REGISTER_MAP[tokens[0]] << 8)

    # --------------------------------------------------------------------------
    # Opcode 0x15 - 0x18: Unary Accumulator Operations
    # --------------------------------------------------------------------------
    if mnemonic == "INC" and tokens[0] == "A": return (0x15 << 11)
    if mnemonic == "DEC" and tokens[0] == "A": return (0x16 << 11)
    if mnemonic == "SHR" and tokens[0] == "A": return (0x17 << 11)
    if mnemonic == "ROR" and tokens[0] == "A": return (0x18 << 11)

    # --------------------------------------------------------------------------
    # Opcode 0x0C - 0x14, 0x19 - 0x1A: ALU Operations
    # --------------------------------------------------------------------------
    alu_map = {
        "ADD": (0x0C, 0x0D),
        "ADC": (0x0E, None),
        "SUB": (0x0F, None),
        "SBC": (0x10, None),
        "AND": (0x11, 0x12),
        "OR":  (0x13, None),
        "XOR": (0x14, None),
        "CP":  (0x19, 0x1A)
    }

    if mnemonic in alu_map:
        reg_op, imm_op = alu_map[mnemonic]
        src = tokens[1]
        if src in REGISTER_MAP:
            return (reg_op << 11) | (REGISTER_MAP[src] << 5)
        elif imm_op is not None:
            val = parse_val(src, symbol_table)
            return (imm_op << 11) | (val & 0xFF)

    raise SyntaxError(f"Unknown instruction or invalid format: {mnemonic} {' '.join(tokens)}")

# ==============================================================================
# TWO-PASS ASSEMBLER ENGINE
# ==============================================================================

def assemble(source_code, default_origin=0xC000):
    lines = source_code.splitlines()
    symbol_table = {}
    parsed_program = []
    current_address = default_origin

    # PASS 1: Build Symbol Table & Expand Pseudoinstructions
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
            
            expanded_ops = expand_pseudoinstructions(mnemonic, tokens[1:])
            
            for exp_mnemonic, exp_operands in expanded_ops:
                parsed_program.append({
                    "line_num": line_num,
                    "address": current_address,
                    "mnemonic": exp_mnemonic,
                    "operands": exp_operands
                })
                current_address += 1

    # PASS 2: Encode Machine Binary
    binary_words = []
    for item in parsed_program:
        word = encode_instruction(item["mnemonic"], item["operands"], symbol_table)
        binary_words.append((item["address"], word))

    return symbol_table, binary_words

# ==============================================================================
# OUTPUT FORMATTER & CLI EXECUTION
# ==============================================================================

def generate_digital_hex(binary_words):
    header = "v2.0 raw\n"
    lines = [f"{word:04X}" for _, word in binary_words]
    return header + "\n".join(lines)

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
