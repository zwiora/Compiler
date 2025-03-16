from compiler_lexer import CompilerLexer
from compiler_parser import CompilerParser
from compiler_data import CompilerData

import sys

def main():

    n = len(sys.argv)
    if n != 3:
        print("Wrong number of arguments!")
        return
    
    dataStruct = CompilerData()
    lexer = CompilerLexer(dataStruct=dataStruct)
    parser = CompilerParser(dataStruct=dataStruct)

    with open(sys.argv[1]) as myFile:
        tokens = lexer.tokenize(myFile.read())
        parser.parse(tokens)

    dataStruct.calculateA()
    dataStruct.listToCode()
    dataStruct.calculateLabels()

    saveFile = open(sys.argv[2], "w")
    saveFile.write(dataStruct.code)
    saveFile.close()

if __name__ == "__main__":
    main()
