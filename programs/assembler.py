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
    "JC": 0, "JNC": 1, "JZ": 2, "JNZ": 3,
    "JN": 4, "JNN": 5, "JV": 6, "JNV": 7
}

SYSTEM_OPS = {
    "BRK": 0, "RET": 1, "RTI": 2, "RETI": 2,
    "SEI": 3, "CLI": 4, "PUSHF": 5, "POPF": 6,
    "HALT": 7
}

DIRECTIVES_ORG  = [".ORG", "ORG"]
DIRECTIVES_WORD = [".DW", "DW", ".WORD", "WORD", ".VEC", "VEC", ".VECTOR", "VECTOR"]
DIRECTIVES_BYTE = [".DB", "DB", ".BYTE", "BYTE"]

# ==============================================================================
# TOKENIZER & PARSER HELPERS
# ==============================================================================

def clean_and_tokenize(raw_line):
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
    if mnemonic == "CALLXY":
        target = tokens[0]
        return [
            ("MOV", ["X", f"LOW:{target}"]),
            ("MOV", ["Y", f"HIGH:{target}"]),
            ("CALL", ["XY"])
        ]

    # Direct CALL label -> Word 1: CALL MEM_HIGH, Word 2: CALL MEM_LOW
    if mnemonic == "CALL":
        if len(tokens) == 1:
            target = tokens[0]
            if target in ["MAR", "XY"]:
                return [(mnemonic, tokens)]
            else:
                return [
                    ("CALL", [f"HIGH:{target}"]),
                    ("CALL", [f"LOW:{target}"])
                ]

    # Direct JMP label -> Word 1: JMP MEM_HIGH, Word 2: JMP MEM_LOW
    if mnemonic == "JMP":
        if len(tokens) == 1:
            target = tokens[0]
            if target in ["MAR", "XY"]:
                return [(mnemonic, tokens)]
            else:
                return [
                    ("JMP", [f"HIGH:{target}"]),
                    ("JMP", [f"LOW:{target}"])
                ]

    # Direct JCC label -> Word 1: JCC MEM_HIGH, Word 2: JCC MEM_LOW
    if mnemonic in JMP_COND_MAP:
        if len(tokens) == 1:
            target = tokens[0]
            if target in ["MAR", "XY"]:
                return [(mnemonic, tokens)]
            else:
                return [
                    (mnemonic, [f"HIGH:{target}"]),
                    (mnemonic, [f"LOW:{target}"])
                ]

    return [(mnemonic, tokens)]

# ==============================================================================
# 16-BIT INSTRUCTION ENCODER
# ==============================================================================

def encode_instruction(mnemonic, tokens, symbol_table):
    if mnemonic in SYSTEM_OPS:
        return (0x1F << 11) | (SYSTEM_OPS[mnemonic] << 8)

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

    # Base Opcode 29 (0x1D): Register Indirect Pointer Operations
    if mnemonic == "INC" and tokens[0] == "XY":
        return (0x1D << 11) | (0x0 << 8)
    if mnemonic == "DEC" and tokens[0] == "XY":
        return (0x1D << 11) | (0x1 << 8)
    if mnemonic == "INC" and tokens[0] == "MAR":
        return (0x1D << 11) | (0x2 << 8)
    if mnemonic == "DEC" and tokens[0] == "MAR":
        return (0x1D << 11) | (0x3 << 8)
    if mnemonic == "CALL":
        if tokens[0] == "XY":
            return (0x1D << 11) | (0x4 << 8)
        elif tokens[0] == "MAR":
            return (0x1D << 11) | (0x5 << 8)
    if mnemonic == "JMP":
        if tokens[0] == "XY":
            return (0x1D << 11) | (0x6 << 8)
        elif tokens[0] == "MAR":
            return (0x1D << 11) | (0x7 << 8)

    # Base Opcode 27 (0x1B): Conditional Direct Jumps (8 Sub-opcodes)
    if mnemonic in JMP_COND_MAP:
        subop = JMP_COND_MAP[mnemonic]
        val = parse_val(tokens[0], symbol_table)
        return (0x1B << 11) | (subop << 8) | (val & 0xFF)

    # Base Opcode 28 (0x1C): Direct JMP (Subop 0) and Direct CALL (Subop 1)
    if mnemonic == "JMP":
        val = parse_val(tokens[0], symbol_table)
        return (0x1C << 11) | (0x0 << 8) | (val & 0xFF)

    if mnemonic == "CALL":
        val = parse_val(tokens[0], symbol_table)
        return (0x1C << 11) | (0x1 << 8) | (val & 0xFF)

    if mnemonic == "MOV" and tokens[0] in ["MARL", "MARH"]:
        bit_8 = 1 if tokens[0] == "MARH" else 0
        src = tokens[1]
        if src in REGISTER_MAP:
            return (0x03 << 11) | (bit_8 << 8) | (REGISTER_MAP[src] << 5)
        else:
            val = parse_val(src, symbol_table)
            return (0x02 << 11) | (bit_8 << 8) | (val & 0xFF)

    if mnemonic == "MOV" and tokens[0] in REGISTER_MAP:
        r_dest = REGISTER_MAP[tokens[0]]
        src = tokens[1]
        if src in REGISTER_MAP:
            return (0x01 << 11) | (r_dest << 8) | (REGISTER_MAP[src] << 5)
        else:
            val = parse_val(src, symbol_table)
            return (0x00 << 11) | (r_dest << 8) | (val & 0xFF)

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

    if mnemonic == "PUSH":
        return (0x0A << 11) | (REGISTER_MAP[tokens[0]] << 8)
    if mnemonic == "POP":
        return (0x0B << 11) | (REGISTER_MAP[tokens[0]] << 8)

    if mnemonic == "INC" and tokens[0] == "A": return (0x15 << 11)
    if mnemonic == "DEC" and tokens[0] == "A": return (0x16 << 11)
    if mnemonic == "SHR" and tokens[0] == "A": return (0x17 << 11)
    if mnemonic == "ROR" and tokens[0] == "A": return (0x18 << 11)

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

    # PASS 1: Build Symbol Table & Word Allocations
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
            
            if mnemonic in DIRECTIVES_ORG:
                current_address = parse_val(tokens[1], symbol_table)
                continue
            
            if mnemonic in DIRECTIVES_WORD:
                for token in tokens[1:]:
                    parsed_program.append({
                        "line_num": line_num,
                        "address": current_address,
                        "type": "WORD_LOW",
                        "val_str": token
                    })
                    parsed_program.append({
                        "line_num": line_num,
                        "address": current_address + 1,
                        "type": "WORD_HIGH",
                        "val_str": token
                    })
                    current_address += 2
                continue

            if mnemonic in DIRECTIVES_BYTE:
                for token in tokens[1:]:
                    parsed_program.append({
                        "line_num": line_num,
                        "address": current_address,
                        "type": "DB",
                        "val_str": token
                    })
                    current_address += 1
                continue
            
            expanded_ops = expand_pseudoinstructions(mnemonic, tokens[1:])
            for exp_mnemonic, exp_operands in expanded_ops:
                parsed_program.append({
                    "line_num": line_num,
                    "address": current_address,
                    "type": "INST",
                    "mnemonic": exp_mnemonic,
                    "operands": exp_operands
                })
                current_address += 1

    # PASS 2: Encode Machine Words
    binary_words = []
    for item in parsed_program:
        itype = item["type"]
        if itype == "WORD_LOW":
            word = parse_val(item["val_str"], symbol_table) & 0xFF
        elif itype == "WORD_HIGH":
            word = (parse_val(item["val_str"], symbol_table) >> 8) & 0xFF
        elif itype == "DB":
            word = parse_val(item["val_str"], symbol_table) & 0xFF
        else:
            word = encode_instruction(item["mnemonic"], item["operands"], symbol_table)

        binary_words.append((item["address"], word))

    return symbol_table, binary_words

# ==============================================================================
# OUTPUT FORMATTER (16-BIT RAW HEX FOR DIGITAL)
# ==============================================================================

def generate_digital_hex(binary_words, rom_size=0x4000):
    header = "v2.0 raw\n"
    rom_array = [0x0000] * rom_size

    for addr, word in binary_words:
        if 0xC000 <= addr <= 0xFFFF:
            offset = addr - 0xC000
        elif 0 <= addr < rom_size:
            offset = addr
        else:
            raise ValueError(f"Address 0x{addr:04X} out of bounds!")

        rom_array[offset] = word

    lines = [f"{w:04X}" for w in rom_array]
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

    symbols, word_data = assemble(asm_code)

    print(f"--- Assembling {asm_filepath} ---")
    print("\n[Symbol Table]")
    for sym, addr in symbols.items():
        if not sym.startswith('.'):
            print(f"  {sym:<12} -> 0x{addr:04X}")

    print("\n[Assembled Output]")
    for addr, word in word_data:
        print(f"  0x{addr:04X}: 0x{word:04X}")

    hex_output = generate_digital_hex(word_data)
    output_filepath = os.path.splitext(asm_filepath)[0] + ".hex"
    with open(output_filepath, 'w') as f:
        f.write(hex_output)
        
    print(f"\nSuccessfully generated '{output_filepath}'")
