import sys
from JackTokenizer import JackTokenizer, wrap_token_xml
from SymbolTable import SymbolTable

TAB = "\t"


class CompilationEngine:
    def __init__(self, tokens, outfile):
        self.tokens = tokens
        self.symbol_table = SymbolTable()
        self.current_token = next(self.tokens)
        self.outfile = outfile
        self.while_counter = 0
        self.if_counter = 0

    def compile_class(self):
        self.__eat("class")
        self.classname = self.__eat()
        self.__eat("{")

        while self.current_token[1] in ("static", "field"):
            self.compile_class_var_dec()

        while self.current_token[1] in ("constructor", "function", "method"):
            self.compile_subroutine_dec()

        self.__eat("}")

    def compile_class_var_dec(self):
        kind = self.__eat_mul(("static", "field"))
        type = self.__eat()
        name = self.__eat()
        self.symbol_table.define(name, type, kind)

        while self.current_token[1] != ";":
            self.__eat(",")
            name = self.__eat()
            self.symbol_table.define(name, type, kind)

        self.__eat(";")

    def compile_subroutine_dec(self):
        self.symbol_table.start_subroutine()

        kind = self.__eat_mul(("constructor", "function", "method"))
        self.__eat()  # return type
        subroutine_name = self.__eat()  # subroutine name
        self.__eat("(")
        if kind == "method":
            self.symbol_table.define("this", self.classname, "argument")
        self.compile_parameter_list()
        self.__eat(")")
        self.compile_subroutine_body(subroutine_name, kind)

    def compile_parameter_list(self):
        if self.current_token[1] != ")":
            type = self.__eat()
            name = self.__eat()
            self.symbol_table.define(name, type, "argument")

        while self.current_token[1] != ")":
            self.__eat(",")
            type = self.__eat()
            name = self.__eat()
            self.symbol_table.define(name, type, "argument")

    def compile_subroutine_body(self, subroutine_name: str, subroutine_kind: str):
        self.__eat("{")

        while self.current_token[1] == "var":
            self.compile_var_dec()

        self.outfile.write(
            f"function {self.classname}.{subroutine_name} {self.symbol_table.var_count('var')}\n"
        )

        if subroutine_kind == "method":
            self.outfile.write("push argument 0\n")
            self.outfile.write("pop pointer 0\n")
        elif subroutine_kind == "constructor":
            self.outfile.write(
                f"push constant {self.symbol_table.var_count('field')}\n"
            )
            self.outfile.write("call Memory.alloc 1\n")
            self.outfile.write("pop pointer 0\n")

        self.compile_statements()
        self.__eat("}")

    def compile_var_dec(self):
        kind = self.__eat("var")
        type = self.__eat()
        name = self.__eat()
        self.symbol_table.define(name, type, kind)

        while self.current_token[1] != ";":
            self.__eat(",")
            name = self.__eat()
            self.symbol_table.define(name, type, kind)

        self.__eat(";")

    def compile_statements(self):
        token = self.current_token[1]
        while token in self.statements:
            self.statements[token](self)
            token = self.current_token[1]

    def compile_let(self):
        self.__eat("let")
        name = self.__eat()
        kind = self.symbol_table.kind_of(name)
        index = self.symbol_table.index_of(name)

        if self.current_token[1] == "[":
            self.__eat("[")
            self.compile_expression()
            self.__eat("]")
            self.outfile.write(f"push {kind} {index}\n")
            self.outfile.write(f"add\n")
            self.outfile.write(f"pop temp 0\n")
            self.__eat("=")
            self.compile_expression()
            self.__eat(";")
            self.outfile.write(f"push temp 0\n")
            self.outfile.write(f"pop pointer 1\n")
            self.outfile.write(f"pop that 0\n")
        else:
            self.__eat("=")
            self.compile_expression()
            self.__eat(";")
            self.outfile.write(f"pop {kind} {index}\n")

    def compile_if(self):
        if_counter = self.if_counter
        self.if_counter += 1

        self.__eat("if")
        self.__eat("(")
        self.compile_expression()
        self.__eat(")")

        self.outfile.write("not\n")
        self.outfile.write(f"if-goto ELSE_{if_counter}\n")

        self.__eat("{")
        self.compile_statements()
        self.__eat("}")

        self.outfile.write(f"goto CONTINUE_{if_counter}\n")
        self.outfile.write(f"label ELSE_{if_counter}\n")

        if self.current_token[1] == "else":
            self.__eat("else")
            self.__eat("{")
            self.compile_statements()
            self.__eat("}")

        self.outfile.write(f"label CONTINUE_{if_counter}\n")

    def compile_while(self):
        while_counter = self.while_counter
        self.while_counter += 1

        self.outfile.write(f"label WHILE_{while_counter}\n")
        self.__eat("while")
        self.__eat("(")
        self.compile_expression()
        self.__eat(")")
        self.outfile.write("not\n")
        self.outfile.write(f"if-goto WHILE_EXIT_{while_counter}\n")
        self.__eat("{")
        self.compile_statements()
        self.__eat("}")
        self.outfile.write(f"goto WHILE_{while_counter}\n")
        self.outfile.write(f"label WHILE_EXIT_{while_counter}\n")

    def compile_do(self):
        self.__eat("do")
        identifier = self.__eat()  # some identifier
        self.__compile_subroutine_call(identifier)
        self.outfile.write("pop temp 0\n")
        self.__eat(";")

    def compile_return(self):
        self.__eat("return")

        if self.current_token[1] != ";":
            self.compile_expression()
        else:
            self.outfile.write("push constant 0\n")

        self.outfile.write("return\n")
        self.__eat(";")

    statements = {
        "let": compile_let,
        "if": compile_if,
        "while": compile_while,
        "do": compile_do,
        "return": compile_return,
    }

    bin_operators = {
        "+": "add",
        "-": "sub",
        "&": "and",
        "|": "or",
        "<": "lt",
        ">": "gt",
        "=": "eq",
    }

    unary_operators = {"-": "neg", "~": "not"}

    def compile_expression(self):
        self.compile_term()

        while self.current_token[1] in "+-*/&|<>=":
            operator = self.__eat()  # operator
            self.compile_term()

            if operator in "+-&|<>=":
                self.outfile.write(f"{self.bin_operators[operator]}\n")
            elif operator == "*":
                self.outfile.write("call Math.multiply 2\n")
            elif operator == "/":
                self.outfile.write("call Math.divide 2\n")

    def compile_term(self):
        token = self.current_token[1]
        if token == "(":
            self.__eat("(")
            self.compile_expression()
            self.__eat(")")
        elif token in "-~":
            operator = self.__eat_mul(("-", "~"))
            self.compile_term()
            self.outfile.write(f"{self.unary_operators[operator]}\n")
        elif token == "null":
            self.__eat("null")
            self.outfile.write("push constant 0\n")
        elif token == "this":
            self.__eat("this")
            self.outfile.write("push pointer 0\n")
        elif token in ("true", "false"):
            keyword = self.__eat_mul(("true", "false"))
            self.outfile.write("push constant 0\n")
            if keyword == "true":
                self.outfile.write("not\n")
        elif self.current_token[0] == "integerConstant":
            integer = self.__eat()
            self.outfile.write(f"push constant {integer}\n")
        elif self.current_token[0] == "stringConstant":
            string = self.__eat()
            self.outfile.write(f"push constant {len(string)}\n")
            self.outfile.write("call String.new 1\n")
            for ch in string:
                self.outfile.write(f"push constant {ord(ch)}\n")
                self.outfile.write("call String.appendChar 2\n")
        else:
            identifier = self.__eat()

            token = self.current_token[1]  # update token
            if token == "[":
                self.__eat("[")
                self.compile_expression()
                self.__eat("]")

                kind = self.symbol_table.kind_of(identifier)
                index = self.symbol_table.index_of(identifier)
                self.outfile.write(f"push {kind} {index}\n")
                self.outfile.write("add\n")
                self.outfile.write("pop pointer 1\n")
                self.outfile.write("push that 0\n")
            elif token in ".(":
                self.__compile_subroutine_call(identifier)
            else:
                kind = self.symbol_table.kind_of(identifier)
                index = self.symbol_table.index_of(identifier)
                self.outfile.write(f"push {kind} {index}\n")

    def __compile_subroutine_call(self, identifier):
        token = self.current_token[1]
        if token == "(":
            func_to_call = f"{self.classname}.{identifier}"
            num_args = 1
            self.outfile.write("push pointer 0\n")  # this
        elif token == ".":
            self.__eat(".")
            subroutine_name = self.__eat()
            type = self.symbol_table.type_of(identifier)

            if type == None:  # is function of class
                func_to_call = f"{identifier}.{subroutine_name}"
                num_args = 0
            else:  # method called on instance
                kind = self.symbol_table.kind_of(identifier)
                index = self.symbol_table.index_of(identifier)
                self.outfile.write(f"push {kind} {index}\n")
                func_to_call = f"{type}.{subroutine_name}"
                num_args = 1

        self.__eat("(")
        num_args += self.compile_expression_list()
        self.__eat(")")
        self.outfile.write(f"call {func_to_call} {num_args}\n")

    def compile_expression_list(self):
        num_expressions = 0

        if self.current_token[1] != ")":
            self.compile_expression()
            num_expressions += 1

        while self.current_token[1] != ")":
            self.__eat(",")
            self.compile_expression()
            num_expressions += 1

        return num_expressions

    def __eat(self, token: str = None):
        if not token or self.current_token[1] == token:
            ret = self.current_token[1]
            try:
                self.current_token = next(self.tokens)
            except StopIteration:
                pass
            finally:
                return ret
        else:
            raise Exception(
                f"Token poisoned! Expected: {token}, Found: {self.current_token[1]}"
            )

    def __eat_mul(self, tokens: tuple):
        for token in tokens:
            if self.current_token[1] == token:
                ret = self.current_token[1]
                try:
                    self.current_token = next(self.tokens)
                except StopIteration:
                    pass
                finally:
                    return ret
        else:
            raise Exception(
                f"Token poisoned! Expected: {token}, Found: {self.current_token[1]}"
            )
