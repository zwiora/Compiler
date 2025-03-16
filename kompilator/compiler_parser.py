from sly import Parser
from compiler_lexer import CompilerLexer
from compiler_data import CompilerData

import math
import sys

result = ""

class CompilerParser(Parser):
    # debugfile = "parser.out"
    tokens = CompilerLexer.tokens

    data = CompilerData()
    
    @_("procedures main")
    def init(self, p):
        self.data.L = [["JUMP", "#*main"]]

        if self.data.isMul:
            # multiplication (b, c, h - return address) return a
            l = [
                ["LABEL", "#mul"],
                ["GET", "b"],
                ["JZERO", "#mul_return"],
                ["GET", "c"],
                ["JZERO", "#mul_return"],   
                ["SUB" ,"b"],
                ["JZERO", "#mul_reverse"],
                ["RST", "a"],
                ["PUT" ,"f"],
                ["GET" ,"c"],
                ["PUT" ,"e"],
                ["GET", "b"],
                ["PUT", "d"],
                ["JUMP", "#mul_while"],
                ["LABEL", "#mul_reverse"],
                ["PUT", "f"],
                ["GET", "b"],
                ["PUT", "e"],
                ["GET", "c"],
                ["PUT", "d"],
                ["LABEL", "#mul_while"],
                ["SHR", "d"],
                ["SHL", "d"],
                ["SUB", "d"],
                ["JZERO", "#mul_skipif"],
                ["GET", "f"],
                ["ADD", "e"],
                ["PUT", "f"],
                ["LABEL", "#mul_skipif"],
                ["SHL", "e"],
                ["SHR", "d"],
                ["GET", "d"],
                ["JPOS", "#mul_while"],
                ["GET", "f"],
                ["LABEL", "#mul_return"],
                ["INC", "h"],
                ["INC", "h"],
                ["JUMPR", "h"]
            ]

            self.data.L.extend(l)

        if self.data.isDiv:
            # division (b, c, h - return address) return a
            l = [
                ["LABEL", "#div"],
                ["GET", "b"],
                ["JZERO", "#div_return"],
                ["GET", "c"],
                ["JZERO", "#div_return"],
                ["PUT", "e"],
                ["DEC", "e"],
                ["RST", "a"],
                ["PUT", "d"],
                ["GET", "b"],
                ["LABEL", "#div_shiftwhile"],
                ["INC", "a"],
                ["SUB", "c"],   
                ["JZERO", "#div_mainwhile"],
                ["ADD", "c"],   
                ["SHL", "c"],   
                ["JUMP", "#div_shiftwhile"],
                ["LABEL", "#div_mainwhile"],
                ["SHR", "c"],   
                ["GET", "c"], 
                ["SUB", "e"],
                ["JZERO", "#div_end"], 
                ["SHL", "d"],   
                ["GET", "b"],   
                ["INC", "a"],   
                ["SUB", "c"],   
                ["JZERO", "#div_mainwhile"],
                ["DEC", "a"],   
                ["PUT", "b"],
                ["INC", "d"],   
                ["JUMP", "#div_mainwhile"],
                ["LABEL", "#div_end"],
                ["GET", "d"],
                ["LABEL", "#div_return"],
                ["INC", "h"],
                ["INC", "h"],
                ["JUMPR", "h"]
            ]

            self.data.L.extend(l)

        if self.data.isMod:
            # modulo (b, c, h - return address) return a
            l = [
                ["LABEL", "#mod"],
                ["GET", "b"],
                ["JZERO", "#mod_return"],
                ["GET", "c"],
                ["JZERO", "#mod_return"],
                ["PUT", "e"],
                ["DEC", "e"],
                ["RST", "a"],
                ["PUT", "d"],
                ["GET", "b"],
                ["LABEL", "#mod_shiftwhile"],
                ["INC", "a"],
                ["SUB", "c"],   
                ["JZERO", "#mod_mainwhile"],
                ["ADD", "c"],   
                ["SHL", "c"],   
                ["JUMP", "#mod_shiftwhile"],
                ["LABEL", "#mod_mainwhile"],
                ["SHR", "c"],
                ["GET", "c"], 
                ["SUB", "e"],
                ["JZERO", "#mod_end"], 
                ["SHL", "d"],   
                ["GET", "b"],   
                ["INC", "a"],   
                ["SUB", "c"],   
                ["JZERO", "#mod_mainwhile"],
                ["DEC", "a"],   
                ["PUT", "b"],
                ["INC", "d"],   
                ["JUMP", "#mod_mainwhile"],
                ["LABEL", "#mod_end"],
                ["GET", "b"],
                ["LABEL", "#mod_return"],
                ["INC", "h"],
                ["INC", "h"],
                ["JUMPR", "h"]
            ]

            self.data.L.extend(l)

        self.data.L.extend(p.procedures)

        self.data.L.extend(p.main)
        return 0
    
    # procedures
    @_("procedures PROCEDURE proc_head IS declarations IN commands END")
    def procedures(self, p):
        self.data.declared = []
        self.data.procedureAddr[p.proc_head[0]] = [len(self.data.A), len(p.proc_head[1])]
        for x in p.proc_head[1]:
            self.data.A[x[0]+"_"+p.proc_head[0]+"!"] = x[1]
        for x in p.declarations:
            self.data.A[x[0]+"_"+p.proc_head[0]] = x[1]

        self.data.A["*return_"+p.proc_head[0]] = ["v", -1]
        
        for x in p.commands:
            if (x[0] == "SET" and type(x[2]) != int) or x[0][-1] == "!" or x[0][-1] == "^":
                varName = x[2].replace("@", "", 1)
                if varName not in self.data.A.keys():
                    x[2] += "_"+p.proc_head[0]
                    varName = x[2].replace("@", "", 1)
                    if varName not in self.data.A.keys():
                        x[2] += "!"
                        varName = x[2].replace("@", "", 1)
                        if varName not in self.data.A.keys():
                            varName = varName.replace("_"+p.proc_head[0]+"!", "", 1)
                            print("Błąd: niezadeklarowana zmienna " + varName)
                            sys.exit(1)

        l = p.procedures
        l.extend([["LABEL", "#"+p.proc_head[0]]])
        l.extend([
            ["INC", "h"],
            ["INC", "h"],
            ["GET", "h"],
            ["SET", "b", "@*return_"+p.proc_head[0]],
            ["STORE", "b"]])
        l.extend(p.commands)
        l.extend([["SET", "b", "@*return_"+p.proc_head[0]],
            ["LOAD", "b"],
            ["JUMPR", "a"]])
        return l
    
    @_("procedures PROCEDURE proc_head IS IN commands END")
    def procedures(self, p):
        self.data.declared = []
        self.data.procedureAddr[p.proc_head[0]] = [len(self.data.A), len(p.proc_head[1])]
        for x in p.proc_head[1]:
            self.data.A[x[0]+"_"+p.proc_head[0]+"!"] = x[1]

        self.data.A["*return_"+p.proc_head[0]] = ["v", -1]

        for x in p.commands:
            if (x[0] == "SET" and type(x[2]) != int) or x[0][-1] == "!" or x[0][-1] == "^":
                varName = x[2].replace("@", "", 1)
                if varName not in self.data.A.keys():
                    x[2] += "_"+p.proc_head[0]
                    varName = x[2].replace("@", "", 1)
                    if varName not in self.data.A.keys():
                        x[2] += "!"
                        varName = x[2].replace("@", "", 1)
                        if varName not in self.data.A.keys():
                            varName = varName.replace("_"+p.proc_head[0]+"!", "", 1)
                            print("Błąd: niezadeklarowana zmienna " + varName)
                            sys.exit(1)

        l = p.procedures
        l.extend([["LABEL", "#"+p.proc_head[0]]])
        l.extend([
            ["INC", "h"],
            ["INC", "h"],
            ["GET", "h"],
            ["SET", "b", "@*return_"+p.proc_head[0]],
            ["STORE", "b"]])
        l.extend(p.commands)
        l.extend([["SET", "b", "@*return_"+p.proc_head[0]],
            ["LOAD", "b"],
            ["JUMPR", "a"]])
        return l
    
    @_("")
    def procedures(self, p):
        return []
    
    # main
    @_("PROGRAM IS declarations IN commands END")
    def main(self, p):
        self.data.declared = []
        for x in p.declarations:
            self.data.A[x[0]+"_*main"] = x[1]

        for x in p.commands:
            if (x[0] == "SET" and type(x[2]) != int and (len(x) < 4 or type(x[3]) != bool)) or x[0][-1] == "!" or x[0][-1] == "^":
                x[2] += "_*main"
                varName = x[2].replace("@", "", 1)
                if varName not in self.data.A.keys():
                    varName = varName.replace("_*main", "", 1)
                    print("Błąd: niezadeklarowana zmienna " + varName)
                    sys.exit(1)

        l = [["LABEL", "*main"]]
        l.extend(p.commands)
        return l
    
    @_("PROGRAM IS IN commands END")
    def main(self, p):
        self.data.declared = []

        for x in p.commands:
            if (x[0] == "SET" and type(x[2]) != int and (len(x) < 4 or type(x[3]) != bool)) or x[0][-1] == "!" or x[0][-1] == "^":
                x[2] += "_*main"
                varName = x[2].replace("@", "", 1)
                if varName not in self.data.A.keys():
                    varName = varName.replace("_*main", "", 1)
                    print("Błąd: niezadeklarowana zmienna " + varName)
                    sys.exit(1)

        l = [["LABEL", "*main"]]
        l.extend(p.commands)
        return l
    
    # commands
    @_("commands command")
    def commands(self, p):
        l = p.commands
        l.extend(p.command)
        return l
    
    @_("command")
    def commands(self, p):
        return p.command
    
    # command
    @_("identifier ASSIGN expression SEMICOL")
    def command(self, p):
        if(len(p.identifier) == 1):
            for x in self.data.declared:
                if x[0] == p.identifier:
                    x[2] = True
                    break

        l = []
        if type(p.identifier) == str:
            l.append(["SET_^", "g", "@"+str(p.identifier)])

            l.append(["SET_!", "a", "@"+str(p.identifier)])
            l.append(["LOAD_!", "a", "@"+p.identifier])
            l.append(["PUT_!", "g", "@"+p.identifier])

            l.extend(p.expression)

            l.append(["STORE", "g"])
        else:
            if type(p.identifier[1]) == int:
                l.append(["SET_^", "g", "@"+p.identifier[0], p.identifier[1]])
                
                l.append(["SET_!", "$"+str(p.index), "@"+p.identifier[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.identifier[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.identifier[0], p.identifier[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.identifier[0]])
                l.append(["PUT_!", "g", "@"+p.identifier[0]])

                l.extend(p.expression)

                l.append(["STORE", "g"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.identifier[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.identifier[1]])
                l.append(["PUT_!", "g", "@"+p.identifier[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.identifier[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.identifier[0]])

                l.append(["SET_^", "g", "@"+p.identifier[0]])

                l.append(["ADD", "g"])
                l.append(["PUT", "g"])
                l.extend(p.expression)
                l.append(["STORE", "g"])
        return l
    
    @_("IF condition THEN commands ELSE commands ENDIF")
    def command(self, p):
        if type(p.condition) == bool:
            if p.condition:
                return p.commands0
            else:
                return p.commands1
        else:
            l = p.condition
            for x in l:
                if x[0] == "JZERO" or x[0] == "JPOS" or x[0] == "JUMP":
                    x[1] += "_" + str(p.index)
            l.append(["LABEL", "#then_" + str(p.index)])
            l.extend(p.commands0)
            l.append(["JUMP", "#end_" + str(p.index)])
            l.append(["LABEL", "#else_" + str(p.index)])
            l.extend(p.commands1)
            l.append(["LABEL", "#end_" + str(p.index)])

            return l
    
    @_("IF condition THEN commands ENDIF")
    def command(self, p):
        if type(p.condition) == bool:
            if p.condition:
                return p.commands
            else:
                return []
        else:
            l = p.condition
            for x in l:
                if x[0] == "JZERO" or x[0] == "JPOS" or x[0] == "JUMP":
                    x[1] += "_" + str(p.index)
            l.append(["LABEL", "#then_" + str(p.index)])
            l.extend(p.commands)
            l.append(["LABEL", "#else_" + str(p.index)])

            return l
    
    @_("WHILE condition DO commands ENDWHILE")
    def command(self, p):

        if type(p.condition) == bool:
            if p.condition:
                l = [["LABEL", "#then_" + str(p.index)]]
                l.extend(p.commands)
                l.append(["JUMP", "#then_" + str(p.index)])
                return l
            else:
                return []
        else:
            l = [["LABEL", "#while_" + str(p.index)]]
            l1 = p.condition
            for x in l1:
                if x[0] == "JZERO" or x[0] == "JPOS" or x[0] == "JUMP":
                    x[1] += "_" + str(p.index)
            l.extend(l1)
            l.append(["LABEL", "#then_" + str(p.index)])
            l.extend(p.commands)
            l.append(["JUMP", "#while_" + str(p.index)])
            l.append(["LABEL", "#else_" + str(p.index)])

            return l
    
    @_("REPEAT commands UNTIL condition SEMICOL")
    def command(self, p):
        l = [["LABEL", "#else_" + str(p.index)]]
        l.extend(p.commands)

        if type(p.condition) == bool:
            if p.condition:
                return p.commands
            else:
                l.append(["JUMP", "#else_" + str(p.index)])
                return l
        else:
            l1 = p.condition
            for x in l1:
                if x[0] == "JZERO" or x[0] == "JPOS" or x[0] == "JUMP":
                    x[1] += "_" + str(p.index)
            l.extend(l1)
            l.append(["LABEL", "#then_" + str(p.index)])

            return l
    
    @_("proc_call SEMICOL")
    def command(self, p):
        return p.proc_call
    
    @_("READ identifier SEMICOL")
    def command(self, p):
        if len(p.identifier) == 1:
            for x in self.data.declared:
                if p.identifier == x[0]:
                    if x[1] == "t":
                        print("Błąd: niewłaściwe użycie tablicy w linii " + str(len(self.data.lines)))
                        sys.exit(1)
                    break

        if(len(p.identifier) == 1):
            for x in self.data.declared:
                if x[0] == p.identifier:
                    x[2] = True
                    break

        l = []
        if type(p.identifier) == str:
            l.append(["SET_^", "$"+str(p.index), "@"+str(p.identifier)])

            l.append(["SET_!", "a", "@"+str(p.identifier)])
            l.append(["LOAD_!", "a", "@"+p.identifier])
            l.append(["PUT_!", "b", "@"+p.identifier])

            l.append(["READ"])
            l.append(["STORE", "$"+str(p.index)])
        else:
            if type(p.identifier[1]) == int:
                l.append(["SET_^", "c", "@"+p.identifier[0], p.identifier[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.identifier[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.identifier[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.identifier[0], p.identifier[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.identifier[0]])
                l.append(["PUT_!", "c", "@"+p.identifier[0]])

                l.append(["READ"])
                l.append(["STORE", "c"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.identifier[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.identifier[1]])
                l.append(["PUT_!", "c", "@"+p.identifier[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.identifier[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.identifier[0]])

                l.append(["SET_^", "c", "@"+p.identifier[0]])

                l.append(["ADD", "c"])
                l.append(["PUT", "c"])
                l.append(["READ"])
                l.append(["STORE", "c"])
        return l
    
    @_("WRITE value SEMICOL")
    def command(self, p):

        l = []
        if type(p.value) == int:
            l.append(["SET", "a", p.value])
        elif type(p.value) == str:
            l.append(["SET", "$"+str(p.index), "@"+p.value])
            l.append(["LOAD", "$"+str(p.index)])
            l.append(["LOAD_!", "a", "@"+p.value])
        else:
            if type(p.value[1]) == int:
                l.append(["SET_^", "a", "@"+p.value[0], p.value[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value[0], p.value[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value[1]])
                l.append(["PUT_!", "c", "@"+p.value[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value[0]])

                l.append(["SET_^", "c", "@"+p.value[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

        l.append(["WRITE"])
        return l
    
    # proc_head
    @_("PIDENTIFIER BRACKETRL args_decl BRACKETRR")
    def proc_head(self, p):   
        types = []
        for i in p.args_decl:
            if len(i[1]) == 2:
                types.append("v")
            else:
                types.append("t")
        
        self.data.proceduresArgs[p.PIDENTIFIER] = types
        return p.PIDENTIFIER, p.args_decl

    # proc_call
    @_("PIDENTIFIER BRACKETRL args BRACKETRR")
    def proc_call(self, p):
            
        if p.PIDENTIFIER not in self.data.proceduresArgs.keys():
            print("Błąd: niezdefiniowana procedura "+ str(p.PIDENTIFIER) +" w linii " + str(len(self.data.lines)+1))
            sys.exit(1)

        if p.PIDENTIFIER not in self.data.procedureAddr.keys():
            print("Błąd: niewłaściwe użycie procedury "+ str(p.PIDENTIFIER) +" w linii " + str(len(self.data.lines)+1))
            sys.exit(1)

        for i in range(0, len(p.args)):
            for x in self.data.declared:
                if p.args[i] == x[0]:
                    if x[1] != self.data.proceduresArgs[p.PIDENTIFIER][i]:
                        print("Błąd: niewłaściwe parametry procedury "+ str(p.PIDENTIFIER) +" w linii " + str(len(self.data.lines)+1))
                        sys.exit(1)
                    break
        
        startIdx = self.data.procedureAddr[p.PIDENTIFIER][0]
        noParams = self.data.procedureAddr[p.PIDENTIFIER][1]

        l = []
        nr = 0
        for i in range(startIdx, startIdx+noParams):
            l.append(["SET", "a", "@"+p.args[nr]])
            l.append(["LOAD_!", "a", "@"+p.args[nr]])
            l.append(["SET", "$"+str(p.index), "@"+list(self.data.A)[i], True])
            l.append(["STORE", "$"+str(p.index)])
            nr+=1
            
        l.extend([["STRK", "h"],
                ["JUMP", "#"+ p.PIDENTIFIER]])
        
        return l
    
    # declarations
    @_("declarations COMMA PIDENTIFIER")
    def declarations(self, p):
        for x in self.data.declared:
            if p.PIDENTIFIER == x[0]:
                print("Błąd: powtórne użycie identyfikatora " + p.PIDENTIFIER + " w linii " + str(len(self.data.lines)))
                sys.exit(1)

        self.data.declared.append([p.PIDENTIFIER, "v", False])
        l = p.declarations
        l.append([p.PIDENTIFIER, ["v", -1]])
        return l
    
    @_("declarations COMMA PIDENTIFIER BRACKETSL NUM BRACKETSR")
    def declarations(self, p):
        for x in self.data.declared:
            if p.PIDENTIFIER == x[0]:
                print("Błąd: powtórne użycie identyfikatora " + p.PIDENTIFIER + " w linii " + str(len(self.data.lines)))
                sys.exit(1)

        self.data.declared.append([p.PIDENTIFIER, "t", False])

        l = p.declarations
        l.append([p.PIDENTIFIER, ["t", -1, p.NUM]])
        return l
    
    @_("PIDENTIFIER")
    def declarations(self, p):
        for x in self.data.declared:
            if p.PIDENTIFIER == x[0]:
                print("Błąd: powtórne użycie identyfikatora " + p.PIDENTIFIER + " w linii " + str(len(self.data.lines)))
                sys.exit(1)

        self.data.declared.append([p.PIDENTIFIER, "v", False])
        l = [[p.PIDENTIFIER, ["v", -1]]]
        return l
    
    @_("PIDENTIFIER BRACKETSL NUM BRACKETSR")
    def declarations(self, p):
        for x in self.data.declared:
            if p.PIDENTIFIER == x[0]:
                print("Błąd: powtórne użycie identyfikatora " + p.PIDENTIFIER + " w linii " + str(len(self.data.lines)))
                sys.exit(1)

        self.data.declared.append([p.PIDENTIFIER, "t", False])

        l = [[p.PIDENTIFIER, ["t", -1, p.NUM]]]
        return l
    
    # args_decl
    @_("args_decl COMMA PIDENTIFIER")
    def args_decl(self, p):
        self.data.declared.append([p.PIDENTIFIER, "v", True])
        l = p.args_decl
        l.append([p.PIDENTIFIER, ["v", -1]])
        return l
    
    @_("args_decl COMMA T PIDENTIFIER")
    def args_decl(self, p):
        self.data.declared.append([p.PIDENTIFIER, "t", True])

        l = p.args_decl
        l.append([p.PIDENTIFIER, ["v", -1, 0]])
        return l    
    
    @_("PIDENTIFIER")
    def args_decl(self, p):
        self.data.declared.append([p.PIDENTIFIER, "v", True])
        return [[p.PIDENTIFIER, ["v", -1]]]
    
    @_("T PIDENTIFIER")
    def args_decl(self, p):
        self.data.declared.append([p.PIDENTIFIER, "t", True])

        return [[p.PIDENTIFIER, ["v", -1, 0]]]
    
    # args
    @_("args COMMA PIDENTIFIER")
    def args(self, p):
        for x in self.data.declared:
            if p.PIDENTIFIER == x[0]:
                x[2] = True
                
        l = p.args
        l.append(p.PIDENTIFIER)
        return l
    
    @_("PIDENTIFIER")
    def args(self, p):
        for x in self.data.declared:
            if p.PIDENTIFIER == x[0]:
                x[2] = True

        return [p.PIDENTIFIER]
    
    # expression
    @_("value")
    def expression(self, p):
        if type(p.value) == int:
            return [["SET", "a", p.value]]
        elif type(p.value) == str:
            return[["SET", "$"+str(p.index), "@"+p.value], ["LOAD", "$"+str(p.index)], ["LOAD_!", "a", "@"+p.value]]
        else:
            l = []
            if type(p.value[1]) == int:
                l.append(["SET_^", "a", "@"+p.value[0], p.value[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value[0], p.value[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value[1]])
                l.append(["PUT_!", "c", "@"+p.value[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value[0]])

                l.append(["SET_^", "c", "@"+p.value[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            return l
    
    @_("value PLUS value")
    def expression(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return [["SET", "a", p.value0 + p.value1]]
        elif type(p.value0) != int and type(p.value1) != int:

            l = []
            if type(p.value0) == str:               
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "d"])

            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l.append(["ADD", "d"])

            return l
        else:
            if type(p.value0) == int:
                valInt = p.value0
                valVar = p.value1
            else:
                valInt = p.value1
                valVar = p.value0

            l = []
            if type(valVar) == str:
               l.append(["SET", "$"+str(p.index), "@"+valVar])
               l.append(["LOAD", "$"+str(p.index)])
               l.append(["LOAD_!", "a", "@"+valVar])
            elif type(valVar[1]) == int:
                l.append(["SET_^", "a", "@"+valVar[0], valVar[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+valVar[0], valVar[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+valVar[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+valVar[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+valVar[1]])
                l.append(["PUT_!", "c", "@"+valVar[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+valVar[0]])

                l.append(["SET_^", "c", "@"+valVar[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l.append(["SET", "$"+str(p.index+1), valInt])
            l.append(["ADD", "$"+str(p.index+1)])
            return l
    
    @_("value MINUS value")
    def expression(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return [["SET", "a", p.value0 - p.value1]]
        elif type(p.value0) != int and type(p.value1) != int:
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "d"])

            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l.append(["SUB", "d"])

            return l
        elif type(p.value0) == int:
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD_!", "a", "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [["PUT", "$"+str(p.index+1)],
                ["SET", "a", p.value0], 
                ["SUB", "$"+str(p.index+1)]]
            l.extend(l1)

            return l
        else:
            l = []
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [["SET", "$"+str(p.index+1), p.value1], 
                ["SUB", "$"+str(p.index+1)]]
            l.extend(l1)
            
            return l
    
    @_("value MUL value")
    def expression(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return [["SET", "a", p.value0 * p.value1]]
        elif type(p.value0) != int and type(p.value1) != int:
            self.data.isMul = True
            l = []
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "c"])

            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "d", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "d", "@"+p.value1[0]])

                l.append(["ADD", "d"])
                l.append(["LOAD", "a"])
                
            l.extend([["PUT", "b"],
                ["STRK", "h"],
                ["JUMP", "#mul"]])
            
            return l
        else:
            self.data.isMul = True
            l = []
            if type(p.value0) == int:
                valInt = p.value0
                valVar = p.value1
            else:
                valInt = p.value1
                valVar = p.value0

            if type(valVar) == str:
                l.append(["SET", "$"+str(p.index), "@"+valVar])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+valVar])
            elif type(valVar[1]) == int:
                l.append(["SET_^", "a", "@"+valVar[0], valVar[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+valVar[0], valVar[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+valVar[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+valVar[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+valVar[1]])
                l.append(["PUT_!", "c", "@"+valVar[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+valVar[0]])

                l.append(["SET_^", "c", "@"+valVar[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                    
            l1 = [["PUT", "c"],
                ["SET", "b", valInt], 
                ["STRK", "h"],
                ["JUMP", "#mul"]]
            
            l.extend(l1)
            return l
    
    @_("value DIV value")
    def expression(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return [["SET", "a", math.floor(p.value0 / p.value1)]]
        elif type(p.value0) != int and type(p.value1) != int:
            self.data.isDiv = True
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "c"])

            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "d", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "d", "@"+p.value0[0]])

                l.append(["ADD", "d"])
                l.append(["LOAD", "a"])

            l.extend([["PUT", "b"],
                ["STRK", "h"],
                ["JUMP", "#div"]])
            
            return l
        elif type(p.value0) == int:
            self.data.isDiv = True
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                    
            l1 = [["PUT", "c"],
                ["SET", "b", p.value0], 
                ["STRK", "h"],
                ["JUMP", "#div"]]
            
            l.extend(l1)
            return l
        
        else:
            self.data.isDiv = True
            l =[]
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                    
            l1 = [["PUT", "b"],
                ["SET", "c", p.value1], 
                ["STRK", "h"],
                ["JUMP", "#div"]]
            
            l.extend(l1)
            return l
        
    @_("value MOD value")
    def expression(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return [["SET", "a", p.value0 % p.value1]]
        elif type(p.value0) != int and type(p.value1) != int:
            self.data.isMod = True
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "c"])

            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "d", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "d", "@"+p.value0[0]])

                l.append(["ADD", "d"])
                l.append(["LOAD", "a"])

            l.extend([["PUT", "b"],
                ["STRK", "h"],
                ["JUMP", "#mod"]])
            
            return l
        elif type(p.value0) == int:
            self.data.isMod = True
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                    
            l1 = [["PUT", "c"],
                ["SET", "b", p.value0], 
                ["STRK", "h"],
                ["JUMP", "#mod"]]
            
            l.extend(l1)
            return l
        
        else:
            self.data.isMod = True
            l =[]
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                    
            l1 = [["PUT", "b"],
                ["SET", "c", p.value1], 
                ["STRK", "h"],
                ["JUMP", "#mod"]]
            
            l.extend(l1)
            return l
    
    # condition
    @_("value EQ value")
    def condition(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return p.value0 == p.value1
        elif type(p.value0) != int and type(p.value1) != int:
            l = []
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "d"])

            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                

            l1 = [["PUT", "$"+str(p.index+1)],
                ["SUB", "$"+str(p.index+1)],
                ["JPOS", "#else"],
                ["GET", "$"+str(p.index+1)],
                ["SUB", "d"],
                ["JPOS", "#else"]]
            
            l.extend(l1)
            return l
        
        else:
            if type(p.value0) == int:
                valInt = p.value0
                valVar = p.value1
            else:
                valInt = p.value1
                valVar = p.value0

            l = []
            if type(valVar) == str:
               l.append(["SET", "$"+str(p.index), "@"+valVar])
               l.append(["LOAD", "$"+str(p.index)])
               l.append(["LOAD_!", "a", "@"+valVar])
            elif type(valVar[1]) == int:
                l.append(["SET_^", "a", "@"+valVar[0], valVar[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+valVar[0], valVar[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+valVar[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+valVar[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+valVar[1]])
                l.append(["PUT_!", "c", "@"+valVar[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+valVar[0]])

                l.append(["SET_^", "c", "@"+valVar[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                    
            l1 = [["PUT", "c"],
                ["SET", "$"+str(p.index+1), valInt], 
                ["SUB", "$"+str(p.index+1)],
                ["JPOS", "#else"],
                ["GET", "$"+str(p.index+1)],
                ["SUB", "c"],
                ["JPOS", "#else"]]
            
            l.extend(l1)
            return l
    
    @_("value NEQ value")
    def condition(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return p.value0 != p.value1
        elif type(p.value0) != int and type(p.value1) != int:
            l = []
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "d"])

            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [["PUT", "$"+str(p.index+1)],
                ["SUB", "$"+str(p.index+1)],
                ["JPOS", "#then"],
                ["GET", "$"+str(p.index+1)],
                ["SUB", "d"],
                ["JZERO", "#else"]]
            
            l.extend(l1)
            
            return l
        else:
            if type(p.value0) == int:
                valInt = p.value0
                valVar = p.value1
            else:
                valInt = p.value1
                valVar = p.value0

            l = []
            if type(valVar) == str:
               l.append(["SET", "$"+str(p.index), "@"+valVar])
               l.append(["LOAD", "$"+str(p.index)])
               l.append(["LOAD_!", "a", "@"+valVar])
            elif type(valVar[1]) == int:
                l.append(["SET_^", "a", "@"+valVar[0], valVar[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+valVar[0], valVar[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+valVar[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+valVar[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+valVar[1]])
                l.append(["PUT_!", "c", "@"+valVar[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+valVar[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+valVar[0]])

                l.append(["SET_^", "c", "@"+valVar[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                    
            l1 = [["PUT", "c"],
                ["SET", "$"+str(p.index+1), valInt], 
                ["SUB", "$"+str(p.index+1)],
                ["JPOS", "#then"],
                ["GET", "$"+str(p.index+1)],
                ["SUB", "c"],
                ["JZERO", "#else"]]
            
            l.extend(l1)
            return l
    
    @_("value GTH value")
    def condition(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return p.value0 > p.value1
        elif type(p.value0) != int and type(p.value1) != int:
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "d"])

            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])


            l1 = [
                ["SUB", "d"],
                ["JZERO", "#else"]]
            
            l.extend(l1)
            
            return l
        elif type(p.value0) == int:
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [["PUT", "$"+str(p.index+1)],
                ["SET", "a", p.value0], 
                ["SUB", "$"+str(p.index+1)],
                ["JZERO", "#else"]]
            
            l.extend(l1)
            return l
        else:
            l =[]
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [["SET", "$"+str(p.index+1), p.value1], 
                ["SUB", "$"+str(p.index+1)],
                ["JZERO", "#else"]]
            
            l.extend(l1)
            return l
                    
    
    @_("value LTH value")
    def condition(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return p.value0 < p.value1
        elif type(p.value0) != int and type(p.value1) != int:
            l = []
            if type(p.value0) == str:               
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "d"])

            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [
                ["SUB", "d"],
                ["JZERO", "#else"]]
            
            l.extend(l1)
            
            return l
        elif type(p.value0) == int:
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD_!", "a", "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [["SET", "$"+str(p.index+1), p.value0], 
                ["SUB", "$"+str(p.index+1)],
                ["JZERO", "#else"]]
            
            l.extend(l1)
            return l
        else:
            l = []
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
            
            l1 = [["PUT", "$"+str(p.index+1)],
                ["SET", "a", p.value1], 
                ["SUB", "$"+str(p.index+1)],
                ["JZERO", "#else"]]
            
            l.extend(l1)
            return l
    
    @_("value GEQ value")
    def condition(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return p.value0 >= p.value1
        elif type(p.value0) != int and type(p.value1) != int:
            l = []
            if type(p.value0) == str:               
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "d"])

            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [
                ["SUB", "d"],
                ["JPOS", "#else"]]
            
            l.extend(l1)
            
            return l
        elif type(p.value0) == int:
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD_!", "a", "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [["SET", "$"+str(p.index+1), p.value0], 
                ["SUB", "$"+str(p.index+1)],
                ["JPOS", "#else"]]
            
            l.extend(l1)
            return l
        else:
            l = []
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
            
            l1 = [["PUT", "$"+str(p.index+1)],
                ["SET", "a", p.value1], 
                ["SUB", "$"+str(p.index+1)],
                ["JPOS", "#else"]]
            
            l.extend(l1)
            return l
    
    @_("value LEQ value")
    def condition(self, p):
        if type(p.value0) == int and type(p.value1) == int:
            return p.value0 <= p.value1
        elif type(p.value0) != int and type(p.value1) != int:
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])
                
            l.append(["PUT", "d"])

            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])


            l1 = [
                ["SUB", "d"],
                ["JPOS", "#else"]]
            
            l.extend(l1)
            
            return l
        elif type(p.value0) == int:
            l = []
            if type(p.value1) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value1])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1])
            elif type(p.value1[1]) == int:
                l.append(["SET_^", "a", "@"+p.value1[0], p.value1[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value1[0], p.value1[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value1[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value1[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value1[1]])
                l.append(["PUT_!", "c", "@"+p.value1[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value1[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value1[0]])

                l.append(["SET_^", "c", "@"+p.value1[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [["PUT", "$"+str(p.index+1)],
                ["SET", "a", p.value0], 
                ["SUB", "$"+str(p.index+1)],
                ["JPOS", "#else"]]
            
            l.extend(l1)
            return l
        else:
            l =[]
            if type(p.value0) == str:
                l.append(["SET", "$"+str(p.index), "@"+p.value0])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0])
            elif type(p.value0[1]) == int:
                l.append(["SET_^", "a", "@"+p.value0[0], p.value0[1]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["SET_!", "$"+str(p.index+1), "@"+p.value0[0], p.value0[1]])
                l.append(["ADD_!", "$"+str(p.index+1), "@"+p.value0[0]])

                l.append(["LOAD", "a"])
            else:
                l.append(["SET", "$"+str(p.index), "@"+p.value0[1]])
                l.append(["LOAD", "$"+str(p.index)])
                l.append(["LOAD_!", "a", "@"+p.value0[1]])
                l.append(["PUT_!", "c", "@"+p.value0[0]])

                l.append(["SET_!", "$"+str(p.index), "@"+p.value0[0]])
                l.append(["LOAD_!", "$"+str(p.index), "@"+p.value0[0]])

                l.append(["SET_^", "c", "@"+p.value0[0]])

                l.append(["ADD", "c"])
                l.append(["LOAD", "a"])

            l1 = [["SET", "$"+str(p.index+1), p.value1], 
                ["SUB", "$"+str(p.index+1)],
                ["JPOS", "#else"]]
            
            l.extend(l1)
            return l
        
    
    # value
    @_("NUM")
    def value(self, p):
        return p.NUM
    
    @_("identifier")
    def value(self, p):

        if len(p.identifier) == 1:

            isDeclared = False
            for x in self.data.declared:
                if p.identifier == x[0]:
                    isDeclared = True
                    if x[1] == "v" and x[2] == False:
                        print("Ostrzeżenie: możliwa niezainicjowana zmienna " + str(p.identifier) + " w linii " + str(len(self.data.lines)+1))
                    elif x[1] == "t":
                        print("Błąd: niewłaściwe użycie tablicy w linii " + str(len(self.data.lines)+1))
                        sys.exit(1)
                    break
            if not isDeclared:
                print("Błąd: niezadeklarowana zmienna " + str(p.identifier) + " w linii " + str(len(self.data.lines)+1))
                sys.exit(1)
        else:
            for x in self.data.declared:
                if p.identifier[1] == x[0]:
                    if x[1] == "v" and x[2] == False:
                        print("Ostrzeżenie: niezainicjowana zmienna " + str(p.identifier[1]) + " w linii " + str(len(self.data.lines)+1))
                    break

        return p.identifier
    
    # identifier
    @_("PIDENTIFIER")
    def identifier(self, p):
        return p.PIDENTIFIER
    
    @_("PIDENTIFIER BRACKETSL NUM BRACKETSR")
    def identifier(self, p):
        return [p.PIDENTIFIER, p.NUM]
    
    @_("PIDENTIFIER BRACKETSL PIDENTIFIER BRACKETSR")
    def identifier(self, p):
        return [p.PIDENTIFIER0, p.PIDENTIFIER1]

    ### error ###   
    def error(self, p):
        print("Błąd składni w linii ", end="")
        for i in self.data.lines:
            if p.index <= i[1]:
                print(i[0])
                sys.exit(1)

        print(len(self.data.lines)+1)
        sys.exit(1)


    ### init ###
    def __init__(self, dataStruct):
        self.data = dataStruct
