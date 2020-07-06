import sys
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from os.path import isdir
from os import listdir

if __name__ == "__main__":
    path = sys.argv[1]
    if isdir(path):
        infilenames = [
            path + "/" + file for file in listdir(path) if file.endswith(".jack")
        ]
    else:
        infilenames = [path]

    outfilenames = [
        infilename.replace(".jack", "Out.xml") for infilename in infilenames
    ]

    for infilename, outfilename in zip(infilenames, outfilenames):
        with open(infilename, "r") as infile:
            tokenizer = JackTokenizer(infile)
            with open(outfilename, "w") as outfile:
                engine = CompilationEngine(tokenizer.tokens(), outfile)
                engine.compile_class()
        print(infilename, outfilename)
