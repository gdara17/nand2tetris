import re
import sys
from os.path import isdir
from os import listdir


class JackTokenizer:

    KEYWORD_PATTERN = (
        r"(?P<keyword>class|constructor|function|method"
        r"|field|static|var|int|char|boolean"
        r"|void|true|false|null|this|let|do"
        r"|if|else|while|return)"
    )
    SYMBOL_PATTERN = r"(?P<symbol>[\{\}\(\)\[\]\.,;\+\-\*/&\|<>=~])"
    INT_PATTERN = r"(?P<integerConstant>\d+)"
    STRING_PATTERN = r"(?P<stringConstant>\"[^\n\"]*\")"
    IDENTIFIER_PATTERN = r"(?P<identifier>[A-Za-z_]\w*)"
    TOKEN_PATTERN = (
        f"{KEYWORD_PATTERN}|{SYMBOL_PATTERN}"
        f"|{INT_PATTERN}|{STRING_PATTERN}|{IDENTIFIER_PATTERN}"
    )

    TOKEN_RE = re.compile(TOKEN_PATTERN)

    def __init__(self, infile):
        self.source = self.__drop_comments(infile.read())

    def __drop_comments(self, source):
        comment_line_re = re.compile(r"//.*\n")
        comment_segment_re = re.compile(r"/\*.*?\*/", flags=re.S)

        return re.sub(comment_segment_re, "\n", re.sub(comment_line_re, "\n", source))

    def tokens(self):
        return self.__token_generator()

    def __token_generator(self):
        for match in self.TOKEN_RE.finditer(self.source):
            yield next(
                (group, token) for group, token in match.groupdict().items() if token
            )


def wrap_token_xml(token):
    t_type, value = token
    value = value.strip('"')

    if value == "<":
        value = "&lt;"
    elif value == ">":
        value = "&gt;"
    elif value == "&":
        value = "&amp;"

    return f"<{t_type}> {value} </{t_type}>\n"


def wrap_tokens(tokens):
    for token in tokens:
        yield wrap_token_xml(token)


if __name__ == "__main__":
    path = sys.argv[1]
    if isdir(path):
        infilenames = [
            path + "/" + file for file in listdir(path) if file.endswith(".jack")
        ]
    else:
        infilenames = [path]

    outfilenames = [
        infilename.replace(".jack", "TOut.xml") for infilename in infilenames
    ]

    for infilename, outfilename in zip(infilenames, outfilenames):
        with open(infilename, "r") as infile:
            tokenizer = JackTokenizer(infile)
            with open(outfilename, "w") as outfile:
                outfile.write("<tokens>\n")
                outfile.writelines(wrap_tokens(tokenizer.tokens()))
                outfile.write("</tokens>")
