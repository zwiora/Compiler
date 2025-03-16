from sly import Lexer
from compiler_data import CompilerData


class CompilerLexer(Lexer):

    data = CompilerData()

    tokens = {
        PROCEDURE, IS, IN, END, PROGRAM, 
        ASSIGN, SEMICOL, BRACKETRL, BRACKETRR, BRACKETSL, BRACKETSR, COMMA, T,
        IF, THEN, ELSE, ENDIF, 
        WHILE, DO, ENDWHILE, 
        REPEAT, UNTIL, 
        READ, WRITE, 
        PLUS, MINUS, MUL, DIV, MOD, 
        EQ, NEQ, GTH, LTH, GEQ, LEQ, 
        NUM, PIDENTIFIER}

    ignore = " \t"

    @_(r"\#.*\n")
    def ignore_comm(self, t):
        self.data.lines.append([len(self.data.lines)+1, self.index])

    @_(r"\n")
    def ignore_endline(self, t):
        self.data.lines.append([len(self.data.lines)+1, self.index])

    PLUS = r"\+"
    MINUS = r"\-"
    MUL = r"\*"
    DIV = r"\/"
    MOD = r"\%"
    PROCEDURE  = r"PROCEDURE"
    IS = r"IS" 
    IN = r"IN"
    PROGRAM = r"PROGRAM"
    ASSIGN = r"\:\="
    SEMICOL = r"\;"
    BRACKETRL = r"\("
    BRACKETRR = r"\)"
    BRACKETSL = r"\["
    BRACKETSR = r"\]"
    COMMA = r"\,"
    IF = r"IF"
    THEN = r"THEN"
    ELSE = r"ELSE"
    ENDIF = r"ENDIF"
    WHILE = r"WHILE"
    DO = r"DO"
    ENDWHILE = r"ENDWHILE" 
    REPEAT = r"REPEAT"
    UNTIL = r"UNTIL"
    READ = r"READ"
    WRITE = r"WRITE"
    NEQ = r"\!\="
    GEQ = r"\>\="
    LEQ = r"\<\="
    GTH = r"\>"
    LTH = r"\<"
    EQ = r"\="

    END = r"END"
    T = r"T"

    PIDENTIFIER = r"[_a-z]+"

    @_(r"[0-9]+")
    def NUM(self, t):
        t.value = int(t.value)
        return t
    
    def error(self, t):
        self.index += 1

    ### init ###
    def __init__(self, dataStruct):
        self.data = dataStruct
