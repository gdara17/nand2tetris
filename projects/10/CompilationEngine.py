import sys
from JackTokenizer import JackTokenizer, wrap_token_xml

TAB = "\t"


class CompilationEngine:
    def __init__(self, tokens, outfile):
        self.tokens = tokens
        self.current_token = next(self.tokens)
        self.outfile = outfile
        self.tabs = 0

    def compile_class(self):
        self.__open_tag("class")
        self.__eat("class")
        self.__eat()  # class name
        self.__eat("{")

        while self.current_token[1] in ("static", "field"):
            self.compile_class_var_dec()

        while self.current_token[1] in ("constructor", "function", "method"):
            self.compile_subroutine_dec()

        self.__eat("}")
        self.__close_tag("class")

    def compile_class_var_dec(self):
        self.__open_tag("classVarDec")
        self.__eat_mul(("static", "field"))
        self.__eat()  # var type
        self.__eat()  # var name

        while self.current_token[1] != ";":
            self.__eat(",")
            self.__eat()  # var name

        self.__eat(";")
        self.__close_tag("classVarDec")

    def compile_subroutine_dec(self):
        self.__open_tag("subroutineDec")
        self.__eat_mul(("constructor", "function", "method"))
        self.__eat()  # return type
        self.__eat()  # subroutine name
        self.__eat("(")
        self.compile_parameter_list()
        self.__eat(")")
        self.compile_subroutine_body()
        self.__close_tag("subroutineDec")

    def compile_parameter_list(self):
        self.__open_tag("parameterList")

        if self.current_token[1] != ")":
            self.__eat()  # var type
            self.__eat()  # var name

        while self.current_token[1] != ")":
            self.__eat(",")
            self.__eat()  # var type
            self.__eat()  # var name

        self.__close_tag("parameterList")

    def compile_subroutine_body(self):
        self.__open_tag("subroutineBody")
        self.__eat("{")

        while self.current_token[1] == "var":
            self.compile_var_dec()

        self.compile_statements()
        self.__eat("}")
        self.__close_tag("subroutineBody")

    def compile_var_dec(self):
        self.__open_tag("varDec")
        self.__eat("var")
        self.__eat()  # var type
        self.__eat()  # var name

        while self.current_token[1] != ";":
            self.__eat(",")
            self.__eat()  # var name

        self.__eat(";")
        self.__close_tag("varDec")

    def compile_statements(self):
        self.__open_tag("statements")

        token = self.current_token[1]
        while token in self.statements:
            self.statements[token](self)
            token = self.current_token[1]

        self.__close_tag("statements")

    def compile_let(self):
        self.__open_tag("letStatement")
        self.__eat("let")
        self.__eat()  # some identifier

        if self.current_token[1] == "[":
            self.__eat("[")
            self.compile_expression()
            self.__eat("]")

        self.__eat("=")
        self.compile_expression()
        self.__eat(";")
        self.__close_tag("letStatement")

    def compile_if(self):
        self.__open_tag("ifStatement")
        self.__eat("if")
        self.__eat("(")
        self.compile_expression()
        self.__eat(")")
        self.__eat("{")
        self.compile_statements()
        self.__eat("}")

        if self.current_token[1] == "else":
            self.__eat("else")
            self.__eat("{")
            self.compile_statements()
            self.__eat("}")

        self.__close_tag("ifStatement")

    def compile_while(self):
        self.__open_tag("whileStatement")
        self.__eat("while")
        self.__eat("(")
        self.compile_expression()
        self.__eat(")")
        self.__eat("{")
        self.compile_statements()
        self.__eat("}")
        self.__close_tag("whileStatement")

    def compile_do(self):
        self.__open_tag("doStatement")
        self.__eat("do")
        self.__eat()  # some identifier

        if self.current_token[1] == ".":
            self.__eat(".")
            self.__eat()  # some identifier

        self.__eat("(")
        self.compile_expression_list()
        self.__eat(")")
        self.__eat(";")
        self.__close_tag("doStatement")

    def compile_return(self):
        self.__open_tag("returnStatement")
        self.__eat("return")

        if self.current_token[1] != ";":
            self.compile_expression()

        self.__eat(";")
        self.__close_tag("returnStatement")

    statements = {
        "let": compile_let,
        "if": compile_if,
        "while": compile_while,
        "do": compile_do,
        "return": compile_return,
    }

    def compile_expression(self):
        self.__open_tag("expression")
        self.compile_term()

        while self.current_token[1] in "+-*/&|<>=":
            self.__eat()  # operator
            self.compile_term()

        self.__close_tag("expression")

    def compile_term(self):
        self.__open_tag("term")

        token = self.current_token[1]
        if token == "(":
            self.__eat("(")
            self.compile_expression()
            self.__eat(")")
        elif token in "-~":
            self.__eat_mul(("-", "~"))
            self.compile_term()
        else:
            self.__eat()  # constant or varname

            token = self.current_token[1]  # update token
            if token == "[":
                self.__eat("[")
                self.compile_expression()
                self.__eat("]")
            elif token == "(":
                self.__eat("(")
                self.compile_expression_list()
                self.__eat(")")
            elif token == ".":
                self.__eat(".")
                self.__eat()  # subroutine name
                self.__eat("(")
                self.compile_expression_list()
                self.__eat(")")

        self.__close_tag("term")

    def compile_expression_list(self):
        self.__open_tag("expressionList")

        if self.current_token[1] != ")":
            self.compile_expression()

        while self.current_token[1] != ")":
            self.__eat(",")
            self.compile_expression()

        self.__close_tag("expressionList")

    def __open_tag(self, tag: str):
        self.outfile.write(f"{TAB * self.tabs}<{tag}>\n")
        self.tabs += 1

    def __close_tag(self, tag: str):
        self.tabs -= 1
        self.outfile.write(f"{TAB * self.tabs}</{tag}>\n")

    def __eat(self, token: str = None):
        if not token or self.current_token[1] == token:
            self.outfile.write(f"{TAB * self.tabs}{wrap_token_xml(self.current_token)}")
            try:
                self.current_token = next(self.tokens)
            except StopIteration:
                pass
        else:
            raise Exception(
                f"Token poisoned! Expected: {token}, Found: {self.current_token[1]}"
            )

    def __eat_mul(self, tokens: tuple):
        for token in tokens:
            if self.current_token[1] == token:
                self.outfile.write(
                    f"{TAB * self.tabs}{wrap_token_xml(self.current_token)}"
                )
                try:
                    self.current_token = next(self.tokens)
                except StopIteration:
                    pass
                break
        else:
            raise Exception(
                f"Token poisoned! Expected: {token}, Found: {self.current_token[1]}"
            )
