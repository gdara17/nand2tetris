import re
import sys

class Instruction:
    def __init__(self, instruction_type: str, **kwargs):
        self.type = instruction_type.upper()
        
        if instruction_type == "A":
            self.value = kwargs["value"]
        elif instruction_type == "C":
            self.dest = kwargs.get("dest", "null")
            self.comp = kwargs.get("comp")
            self.jump = kwargs.get("jump", "null")
    
    def __str__(self):
        if self.type == "A":
            return f"Type: {self.type}, Value: {self.value}"
        elif self.type == "C":
            return f"Type: {self.type}, Dest: {self.dest}, Comp: {self.comp}, Jump: {self.jump}"
            

class Parser:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.n = 16

    def parse_line(self, line):
        line = line.replace(" ", "")
        a_instruction_pattern = re.compile(r"@\w+")
        c_instruction_pattern = re.compile(r"([\w\s]+=)?[\w\s]+(;[\w\s]+)?")

        if re.match(a_instruction_pattern, line):
            value = line[1:]
            if value.isdecimal():
                return Instruction("A", value=value)
            elif value in self.symbol_table:
                return Instruction("A", value=self.symbol_table[value])
            else:
                self.symbol_table[value] = self.n
                self.n += 1
                return Instruction("A", value=self.symbol_table[value])
        elif re.match(c_instruction_pattern, line):
            parts = re.split("[=;]", line)
            if len(parts) == 3:
                return Instruction("C", dest=parts[0], comp=parts[1], jump=parts[2]) 
            elif len(parts) == 2:
                if "=" in line:
                    return Instruction("C", dest=parts[0], comp=parts[1]) 
                else:
                    return Instruction("C", comp=parts[0], jump=parts[1]) 
        return None


class Encoder:
    dest_table = {
        "null": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111"
    }
    
    jump_table = {
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111" 
    }

    comp_table = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "M": "1110000",
        "!D": "0001101",
        "!A": "0110001",
        "!M": "1110001",
        "-D": "0001111",
        "-A": "0110011",
        "-M": "1110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "M+1": "1110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "M-1": "1110010",
        "D+A": "0000010",
        "D+M": "1000010",
        "D-A": "0010011",
        "D-M": "1010011",
        "A-D": "0000111",
        "M-D": "1000111",
        "D&A": "0000000",
        "D&M": "1000000",
        "D|A": "0010101",
        "D|M": "1010101"
	}

    def __init__(self):
        pass

    def encode_instruction(self, instruction: Instruction):
        if instruction.type == "A":
            return "0" + format(eval(str(instruction.value)), "b").zfill(15)[-15:]
        else:
            return "111" + self.comp_table[instruction.comp] + self.dest_table[instruction.dest] + self.jump_table[instruction.jump]
        
class Preprocessor:

    def get_default_table(self):
        return {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576,
        }
    
    def get_symbol_table_from(self, filename):
        symbol_table = self.get_default_table()
        line_number = 0
        with open(filename, "r") as f:
            for line in f:
                line = line.strip().replace(" ", "").split("//")[0]
                if not line or line.startswith("//"):
                    continue
                elif line.startswith("("):
                    label = line.strip("()")
                    symbol_table[label] = line_number
                    continue
                line_number += 1
        return symbol_table

class Assembler:
    def __init__(self, parser, encoder):
        self.parser = parser
        self.encoder = encoder

    def compile(self, filename):
        infilename = filename
        outfilename = infilename.replace(".asm", ".hack")
        with open(infilename, "r") as infile:
            with open(outfilename, "w") as outfile:
                for line in infile:
                    line = line.strip().replace(" ", "")
                    if not line or line.startswith("//") or line.startswith("("):
                        continue
                    line = line.split("//")[0]
                    instruction = self.parser.parse_line(line)
                    codeline = self.encoder.encode_instruction(instruction)
                    outfile.write(f"{codeline}\n")


if __name__ == "__main__":
    filename = sys.argv[1]

    preprocessor = Preprocessor()
    symbol_table = preprocessor.get_symbol_table_from(filename)
    parser = Parser(symbol_table)
    encoder = Encoder()
    assembler = Assembler(parser, encoder)
    assembler.compile(filename)