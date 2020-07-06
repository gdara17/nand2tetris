import sys
from os.path import splitext, basename

class Translator:
    def __init__(self, filename):
        self.filename = filename
        self.branch_id = 0
        self.base_addrs = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }

    def encode_program_control_cmd(self, command: str, label: str):
        if command == "label":
            return f"({label})"
        elif command == "goto":
            return (f"@{label}\n"
                    f"0;JMP")
        elif command == "if-goto":
            return (f"@SP\n"
                    f"AM=M-1\n"
                    f"D=M\n"
                    f"@{label}\n"
                    f"D;JNE")

    def encode_log_operation(self, operation: str):
        # single arg operations
        if operation == "not":
            return ("@SP\n"
                    "A=M-1\n"
                    "M=!M")
        if operation == "neg":
            return ("@SP\n"
                    "A=M-1\n"
                    "D=0\n"
                    "M=D-M")

        # preamble for two arg operations
        preamble = ("@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    "A=A-1")

        # two arg math operations
        if operation == "add":
            return (f"{preamble}\n"
                    "M=M+D")
        if operation == "sub":
            return (f"{preamble}\n"
                    "M=M-D")
        if operation == "and":
            return (f"{preamble}\n"
                    "M=M&D")
        if operation == "or":
            return (f"{preamble}\n"
                    "M=M|D")
        
        # two arg log operations
        if operation == "eq":
            branch_cond = "JNE"
        if operation == "gt":
            branch_cond = "JLE"
        if operation == "lt":
            branch_cond = "JGE"
        if operation in ("eq", "gt", "lt"):
            self.branch_id += 1
            return (f"{preamble}\n"
                    f"D=M-D\n"
                    f"@FALSE_{self.branch_id}\n"
                    f"D;{branch_cond}\n"
                    f"@SP\n"
                    f"A=M-1\n"
                    f"M=-1\n"
                    f"@CONTINUE_{self.branch_id}\n"
                    f"0;JMP\n"
                    f"(FALSE_{self.branch_id})\n"
                    f"@SP\n"
                    f"A=M-1\n"
                    f"M=0\n"
                    f"(CONTINUE_{self.branch_id})")

    def encode_push(self, segment: str, i: int):
        if segment == "constant":
            return (f"@{i}\n"
                    f"D=A\n"
                    f"@SP\n"
                    f"A=M\n"
                    f"M=D\n"
                    f"@SP\n"
                    f"M=M+1")
        if segment in ("local", "argument", "this", "that"):
            return (f"@{self.base_addrs[segment]}\n"
                    f"D=M\n"
                    f"@{i}\n"
                    f"A=D+A\n"
                    f"D=M\n"
                    f"@SP\n"
                    f"A=M\n"
                    f"M=D\n"
                    f"@SP\n"
                    f"M=M+1")
        if segment == "temp":
            return (f"@{i + 5}\n"
                    f"D=M\n"
                    f"@SP\n"
                    f"A=M\n"
                    f"M=D\n"
                    f"@SP\n"
                    f"M=M+1")
        if segment == "static":
            return (f"@{self.filename}.{i}\n"
                    f"D=M\n"
                    f"@SP\n"
                    f"A=M\n"
                    f"M=D\n"
                    f"@SP\n"
                    f"M=M+1")
        if segment == "pointer":
            return (f"@{'THAT' if i else 'THIS'}\n"
                    f"D=M\n"
                    f"@SP\n"
                    f"A=M\n"
                    f"M=D\n"
                    f"@SP\n"
                    f"M=M+1")
    def encode_pop(self, segment: str, i: int):
        if segment in ("local", "argument", "this", "that"):
            return (f"@{self.base_addrs[segment]}\n"
                    f"D=M\n"
                    f"@{i}\n"
                    f"D=D+A\n"
                    f"@R13\n"
                    f"M=D\n"
                    f"@SP\n"
                    f"AM=M-1\n"
                    f"D=M\n"
                    f"@R13\n"
                    f"A=M\n"
                    f"M=D")
        if segment == "temp":
            return (f"@{i + 5}\n"
                    f"D=A\n"
                    f"@R13\n"
                    f"M=D\n"
                    f"@SP\n"
                    f"AM=M-1\n"
                    f"D=M\n"
                    f"@R13\n"
                    f"A=M\n"
                    f"M=D")
        if segment == "static":
            return (f"@{self.filename}.{i}\n"
                    f"D=A\n"
                    f"@R13\n"
                    f"M=D\n"
                    f"@SP\n"
                    f"AM=M-1\n"
                    f"D=M\n"
                    f"@R13\n"
                    f"A=M\n"
                    f"M=D")
        if segment == "pointer":
            return (f"@{'THAT' if i else 'THIS'}\n"
                    f"D=A\n"
                    f"@R13\n"
                    f"M=D\n"
                    f"@SP\n"
                    f"AM=M-1\n"
                    f"D=M\n"
                    f"@R13\n"
                    f"A=M\n"
                    f"M=D")


    def parse(self, line: str):
        parts = line.split(" ")
        if len(parts) == 1:
            operation = parts[0]
            return self.encode_log_operation(operation)
        elif len(parts) == 2:
            command, label = parts
            return self.encode_program_control_cmd(command, label)
        elif len(parts) == 3:
            keyword = parts[0]
            if keyword == "push":
                operation, segment, i = parts
                return self.encode_push(segment, eval(i))
            if keyword == "pop":
                operation, segment, i = parts
                return self.encode_pop(segment, eval(i))
            

if __name__ == "__main__":
    infilename = sys.argv[1]
    outfilename = infilename.replace(".vm", ".asm")
    translator = Translator(splitext(basename(infilename))[0])
    with open(infilename, "r") as infile:
        with open(outfilename, "w") as outfile:
            for line in infile:
                line = line.split("//")[0].strip()
                if not line or line.startswith("//"):
                    continue
                asm_code = translator.parse(line)
                outfile.write((f"// {line}\n"
                               f"{asm_code}\n"))