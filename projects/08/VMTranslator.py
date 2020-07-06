import sys
from os.path import splitext, basename, isdir, isfile
from os import listdir

class Translator:
    def __init__(self):
        # self.filename = filename
        self.branch_id = 0
        self.func_id = 0
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

    def encode_push_ptr(self, ptr: str):
        return (f"@{ptr}\n"
                f"D=M\n"
                f"@SP\n"
                f"A=M\n"
                f"M=D\n"
                f"@SP\n"
                f"M=M+1")

    def encode_call(self, func_name: str, nargs: int):
        self.func_id += 1
        ret_label = f"ret.{self.func_id}"
        return (f"{self.encode_push('constant', ret_label)}\n"
                f"{self.encode_push_ptr('LCL')}\n"
                f"{self.encode_push_ptr('ARG')}\n"
                f"{self.encode_push_ptr('THIS')}\n"
                f"{self.encode_push_ptr('THAT')}\n"
                f"@SP\n"
                f"D=M\n"
                f"@{5 + nargs}\n"
                f"D=D-A\n"
                f"@ARG\n"
                f"M=D\n"
                f"@SP\n"
                f"D=M\n"
                f"@LCL\n"
                f"M=D\n"
                f"{self.encode_program_control_cmd('goto', func_name)}\n"
                f"{self.encode_program_control_cmd('label', ret_label)}")

    def encode_function(self, func_name: str, nargs: int):
        nl = "\n"
        return (f"{self.encode_program_control_cmd('label', func_name)}\n"
                f"{(self.encode_push('constant', 0) + nl) * nargs}")

    def __restore_ptr(self, ptr: str):
        if ptr == "THAT":
            i = 1
        elif ptr == "THIS":
            i = 2
        elif ptr == "ARG":
            i = 3
        elif ptr == "LCL":
            i = 4
        else:
            raise ValueError(f"Should not use ptr {ptr} for this function")

        return (f"@LCL\n"
                f"D=M\n"
                f"@{i}\n"
                f"A=D-A\n"
                f"D=M\n"
                f"@{ptr}\n"
                f"M=D")


    def encode_return(self):
        return (f"@LCL\n"
                f"D=M\n"
                f"@endFrame\n"
                f"M=D\n"
                f"@5\n"
                f"A=D-A\n"
                f"D=M\n"
                f"@retAddr\n"
                f"M=D\n"
                f"{self.encode_pop('argument', 0)}\n"
                f"@ARG\n"
                f"D=M+1\n"
                f"@SP\n"
                f"M=D\n"
                f"{self.__restore_ptr('THAT')}\n"
                f"{self.__restore_ptr('THIS')}\n"
                f"{self.__restore_ptr('ARG')}\n"
                f"{self.__restore_ptr('LCL')}\n"
                f"@retAddr\n"
                f"A=M\n"
                f"0;JMP")

    def encode_init(self):
        return (f"// bootstrap code\n"
                f"@256\n"
                f"D=A\n"
                f"@SP\n"
                f"M=D\n"
                f"{self.encode_call('Sys.init', 0)}\n")

    def parse(self, line: str):
        parts = line.split(" ")
        if len(parts) == 1:
            operation = parts[0]
            if operation == "return":
                return self.encode_return()
            else:
                return self.encode_log_operation(operation)
        if len(parts) == 2:
            command, label = parts
            return self.encode_program_control_cmd(command, label)
        if len(parts) == 3:
            keyword = parts[0]
            if keyword == "call":
                _, func_name, nargs = parts
                return self.encode_call(func_name, eval(nargs))
            if keyword == "function":
                _, func_name, nargs = parts
                return self.encode_function(func_name, eval(nargs))
            if keyword == "push":
                operation, segment, i = parts
                return self.encode_push(segment, eval(i))
            if keyword == "pop":
                operation, segment, i = parts
                return self.encode_pop(segment, eval(i))
            


if __name__ == "__main__":
    path = sys.argv[1]
    if isdir(path):
        infiles = [path + "/" + file for file in listdir(path) if file.endswith(".vm")]
        outfilename = path + "/" + basename(path.rstrip("/")) + ".asm"
    else:
        infiles = [path]
        outfilename = path.replace(".vm", ".asm")
        
    translator = Translator()
    with open(outfilename, "w") as outfile:
        if (path + "/" + "Sys.vm") in infiles:
            outfile.write(translator.encode_init())
        for infilename in infiles:
            translator.filename = basename(infilename).replace(".vm", "")
            with open(infilename, "r") as infile:
                for line in infile:
                    line = line.split("//")[0].strip()
                    if not line or line.startswith("//"):
                        continue
                    asm_code = translator.parse(line)
                    outfile.write((f"// {line}\n"
                                f"{asm_code}\n"))