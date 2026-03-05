class Token:
    def __init__(self, tipo, valor, linea):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea

    def __repr__(self):
        return f"<{self.tipo}: {self.valor}>"


class ScannerManual:
    def __init__(self):
        self.fuente = ""
        self.pos = 0
        self.longitud = 0
        self.linea_actual = 1
        
        self.palabras_reservadas = {
            "auto", "break", "case", "char", "const", "continue", "default",
            "do", "double", "else", "enum", "extern", "float", "for", "goto",
            "if", "int", "long", "register", "return", "short", "signed",
            "sizeof", "static", "struct", "switch", "typedef", "union",
            "unsigned", "void", "volatile", "while", "cout", "cin", "endl",
            "using", "namespace", "std", "main", "printf", "scanf"
        }

    def escanear(self, texto_entrada):
        self.fuente = texto_entrada
        self.longitud = len(texto_entrada)
        self.pos = 0
        self.linea_actual = 1
        tokens = []

        while self.pos < self.longitud:
            char_actual = self.fuente[self.pos]

            if char_actual == '\n':
                self.linea_actual += 1
                self.pos += 1
                continue

            if char_actual in [' ', '\t', '\r']:
                self.pos += 1
                continue

            if char_actual == '/' and self.pos + 1 < self.longitud and self.fuente[self.pos + 1] == '/':
                while self.pos < self.longitud and self.fuente[self.pos] != '\n':
                    self.pos += 1
                continue

            if char_actual == '/' and self.pos + 1 < self.longitud and self.fuente[self.pos + 1] == '*':
                self.pos += 2
                while self.pos + 1 < self.longitud:
                    if self.fuente[self.pos] == '\n':
                        self.linea_actual += 1
                    if self.fuente[self.pos] == '*' and self.fuente[self.pos + 1] == '/':
                        self.pos += 2
                        break
                    self.pos += 1
                continue

            if char_actual == '#':
                lexema = "#"
                self.pos += 1
                while self.pos < self.longitud and self.fuente[self.pos].isalpha():
                    lexema += self.fuente[self.pos]
                    self.pos += 1
                tokens.append(Token("DIRECTIVA", lexema, self.linea_actual))
                continue
            if char_actual == '"':
                lexema = '"'
                self.pos += 1
                while self.pos < self.longitud and self.fuente[self.pos] != '"':
                    lexema += self.fuente[self.pos]
                    self.pos += 1
                if self.pos < self.longitud:
                    lexema += '"'  # Cerrar comillas
                    self.pos += 1
                tokens.append(Token("CADENA_TEXTO", lexema, self.linea_actual))
                continue

            if char_actual.isalpha() or char_actual == '_':
                lexema = ""
                while self.pos < self.longitud and (self.fuente[self.pos].isalnum() or self.fuente[self.pos] == '_'):
                    lexema += self.fuente[self.pos]
                    self.pos += 1
                
                if lexema in self.palabras_reservadas:
                    tokens.append(Token("PALABRA_RESERVADA", lexema, self.linea_actual))
                else:
                    tokens.append(Token("IDENTIFICADOR", lexema, self.linea_actual))
                continue

            if char_actual.isdigit():
                lexema = ""
                es_real = False
                while self.pos < self.longitud and self.fuente[self.pos].isdigit():
                    lexema += self.fuente[self.pos]
                    self.pos += 1
                
                if self.pos < self.longitud and self.fuente[self.pos] == '.':
                    if self.pos + 1 < self.longitud and self.fuente[self.pos + 1].isdigit():
                        es_real = True
                        lexema += '.'
                        self.pos += 1
                        while self.pos < self.longitud and self.fuente[self.pos].isdigit():
                            lexema += self.fuente[self.pos]
                            self.pos += 1
                
                tipo = "NUMERO_REAL" if es_real else "NUMERO_ENTERO"
                tokens.append(Token(tipo, lexema, self.linea_actual))
                continue

            if self.pos + 1 < self.longitud:
                doble_char = char_actual + self.fuente[self.pos + 1]
                if doble_char in ["==", "!=", "<=", ">=", "++", "--", "&&", "||", "<<", ">>", "+=", "-=", "*=", "/="]:
                    tokens.append(Token("OPERADOR", doble_char, self.linea_actual))
                    self.pos += 2
                    continue

            if char_actual in "+-*/=<>!&|%":
                tokens.append(Token("OPERADOR", char_actual, self.linea_actual))
                self.pos += 1
                continue
            
            if char_actual in "(){}[];,":
                tokens.append(Token("PUNTUACION", char_actual, self.linea_actual))
                self.pos += 1
                continue

            tokens.append(Token("ERROR", char_actual, self.linea_actual))
            self.pos += 1

        return tokens



def escanear_codigo(texto_cpp):
    escaner = ScannerManual()
    lista_tokens = escaner.escanear(texto_cpp)
    return lista_tokens