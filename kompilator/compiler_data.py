import math


class CompilerData:
    lines = []
    A = {}
    L = []
    code = ""
    labels = {}
    procedureAddr = {}
    isMul = False
    isDiv = False
    isMod = False
    declared = []
    proceduresArgs = {}

    registers = []

    def printA(self):
        print("Variables with addresses:")
        print(self.A)
        print()

    def printL(self):
        print("Pseudocode:")
        for x in self.L:
            print(x)
        print()

    def printCode(self):
        print("Machine code:")
        print(self.code)

    def calculateA(self):
        i = 0
        for k in self.A:
            self.A[k][1] = i
            if self.A[k][0] == "v":
                i += 1
            elif self.A[k][0] == "t":
                i += self.A[k][2]

    def calculateLabels(self):
        i = 0

        for line in self.code.splitlines():
            if line.split(" ")[0] == "LABEL":
                self.labels[line.split(" ")[1].replace("#", "", 1)] = i
            else:
                i += 1

        new = ""
        for line in self.code.splitlines():
            order = line.split(" ")[0]
            if order == "LABEL":
                pass
            elif order == "JUMP" or order == "JZERO" or order == "JPOS":
                new += order + " " + str(self.labels[line.split(" ")[1].replace("#", "", 1)]) + "\n"
            else:
                new += line + "\n"

        self.code = new

    def putNumberIntoRegister(self, val, r):
        a = "RST "+r+"\n"
        valBin = str(bin(val))
        valBin = valBin.replace("0b", "", 1)
        first = True
        for x in valBin:
            if not first:
                a += "SHL "+r+"\n"
            else:
                first = False

            if x == "1":
                a += "INC "+r+"\n"
        return a

    def listToCode(self):
        for x in self.L:
            if x[0] == 'LABEL':
                self.code += x[0] + " " + x[1] + "\n"
            elif x[0] == 'SET':
                if type(x[2]) != int:
                    varName = x[2].replace("@", "", 1)
                    if len(x) == 4 and type(x[3]) != bool:
                        val = self.A[varName][1] + x[3]
                    else:
                        val = self.A[varName][1]
                else:
                    val = x[2]

                if x[1][0] == '$':
                    self.code += self.putNumberIntoRegister(val, "b")     
                else:
                    self.code += self.putNumberIntoRegister(val, x[1])     

            elif x[0] == 'STORE':
                if x[1][0] == '$':
                    self.code += "STORE b\n"    
                else:
                    self.code += "STORE "+ x[1] +"\n"
            elif x[0] == 'LOAD':
                if x[1][0] == '$':
                    self.code += "LOAD b\n"    
                else:
                    self.code += "LOAD "+ x[1] +"\n"
            elif x[0] == 'INC':
                if x[1][0] == '$':
                    self.code += "INC b\n"    
                else:
                    self.code += "INC "+ x[1] +"\n"
            elif x[0] == 'DEC':
                if x[1][0] == '$':
                    self.code += "DEC b\n"    
                else:
                    self.code += "DEC "+ x[1] +"\n"
            elif x[0] == 'ADD':
                if x[1][0] == '$':
                    self.code += "ADD b\n"    
                else:
                    self.code += "ADD "+ x[1] +"\n"
            elif x[0] == 'SUB':
                if x[1][0] == '$':
                    self.code += "SUB b\n"    
                else:
                    self.code += "SUB "+ x[1] +"\n"
            elif x[0] == 'RST':
                if x[1][0] == '$':
                    self.code += "RST b\n"    
                else:
                    self.code += "RST "+ x[1] +"\n"
            elif x[0] == 'PUT':
                if x[1][0] == '$':
                    self.code += "PUT b\n"    
                else:
                    self.code += "PUT "+ x[1] +"\n"
            elif x[0] == 'GET':
                if x[1][0] == '$':
                    self.code += "GET b\n"    
                else:
                    self.code += "GET "+ x[1] +"\n"
            elif x[0] == 'SHR':
                if x[1][0] == '$':
                    self.code += "SHR b\n"    
                else:
                    self.code += "SHR "+ x[1] +"\n"
            elif x[0] == 'SHL':
                if x[1][0] == '$':
                    self.code += "SHL b\n"    
                else:
                    self.code += "SHL "+ x[1] +"\n"
            elif x[0] == 'STRK':
                if x[1][0] == '$':
                    self.code += "STRK b\n"    
                else:
                    self.code += "STRK "+ x[1] +"\n"
            elif x[0] == 'JUMPR':
                if x[1][0] == '$':
                    self.code += "JUMPR b\n"    
                else:
                    self.code += "JUMPR "+ x[1] +"\n"
            elif x[0] == 'JUMP':
                self.code += "JUMP "+ x[1] +"\n"
            elif x[0] == 'JZERO':
                self.code += "JZERO "+ x[1] +"\n"
            elif x[0] == 'JPOS':
                self.code += "JPOS "+ x[1] +"\n"
            #### zmienne ####
            elif x[0] == 'SET_^':
                if x[2][-1] != '!':
                    if type(x[2]) != int:                    
                        varName = x[2].replace("@", "", 1)
                        if len(x) == 4 and type(x[3]) != bool:
                            val = self.A[varName][1] + x[3]
                        else:
                            val = self.A[varName][1]
                    else:
                        val = x[2]

                    if x[1][0] == '$':
                        self.code += self.putNumberIntoRegister(val, "b")     
                    else:
                        self.code += self.putNumberIntoRegister(val, x[1])     

            #### argumenty ####
            elif x[0] == 'SET_!':
                if x[2][-1] == '!':
                    if len(x) == 3:                    
                        varName = x[2].replace("@", "", 1)
                        if len(x) == 4 and type(x[3]) != bool:
                            val = self.A[varName][1] + x[3]
                        else:
                            val = self.A[varName][1]
                    else:
                        val = x[3]

                    if x[1][0] == '$':
                        self.code += self.putNumberIntoRegister(val, "b")     
                    else:
                        self.code += self.putNumberIntoRegister(val, x[1])     

            elif x[0] == 'LOAD_!':
                if x[2][-1] == '!':
                    if x[1][0] == '$':
                        self.code += "LOAD b\n"    
                    else:
                        self.code += "LOAD "+ x[1] +"\n"

            elif x[0] == 'PUT_!':
                if x[2][-1] == '!':
                    if x[1][0] == '$':
                        self.code += "PUT b\n"    
                    else:
                        self.code += "PUT "+ x[1] +"\n"

            elif x[0] == 'ADD_!':
                if x[2][-1] == '!':
                    if x[1][0] == '$':
                        self.code += "ADD b\n"    
                    else:
                        self.code += "ADD "+ x[1] +"\n"
            else:
                self.code += x[0] + '\n'
        self.code += "HALT\n"
                

