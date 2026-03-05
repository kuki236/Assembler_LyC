def analizar_tokens(tokens):
    params = {
        'iteraciones': 5,
        'tiene_if_mayor': False,
        'tiene_if_menor': False,
        'asignaciones': []
    }
    
    if not tokens:
        return params

    i = 0
    longitud = len(tokens)
    
    while i < longitud:
        t = tokens[i]

        if t.tipo == "PALABRA_RESERVADA" and t.valor == "for":
            while i < longitud and tokens[i].tipo != "NUMERO_ENTERO":
                i += 1
            if i < longitud:
                inicio = int(tokens[i].valor)
                
                i += 1
                while i < longitud and tokens[i].tipo != "NUMERO_ENTERO":
                    i += 1
                if i < longitud:
                    fin = int(tokens[i].valor)
                    params['iteraciones'] = fin - inicio
                    
        elif t.tipo == "PALABRA_RESERVADA" and t.valor == "if":
            condicion = []
            i += 1
            while i < longitud and tokens[i].valor != ")":
                condicion.append(tokens[i].valor)
                i += 1
            
            if ">" in condicion and "mayor" in condicion:
                params['tiene_if_mayor'] = True
            if "<" in condicion and "menor" in condicion:
                params['tiene_if_menor'] = True

        elif t.tipo == "IDENTIFICADOR":
            if i + 1 < longitud and tokens[i+1].valor == "=":
                variable_izq = t.valor
                if i + 2 < longitud:
                    valor_der = tokens[i+2].valor
                    params['asignaciones'].append((variable_izq, valor_der))
                i += 2
                
        i += 1

    return params

def generar_linealizacion(tokens=None):
    params = analizar_tokens(tokens) if tokens else {
        'iteraciones': 5, 'tiene_if_mayor': True, 'tiene_if_menor': True
    }
    
    limite = 1 + params['iteraciones'] 
    
    lin =  "#include <iostream>\n\n"
    lin += "using namespace std;\n\n"
    lin += "int main() {\n"
    lin += "    int numero_actual;\n"
    lin += "    int mayor, menor;\n\n"
    lin += '    cout << "--- Lector de 6 numeros (00-99) ---" << endl;\n\n'
    
    lin += '    cout << "Ingrese el numero 1: ";\n'
    lin += "    cin >> numero_actual;\n\n"
    lin += "    mayor = numero_actual;\n"
    lin += "    menor = numero_actual;\n\n"
    
    lin += "    int i = 2;\n\n"
    
    lin += f"E1: if !(i<={limite}) GOTO E2\n"
    lin += '    cout << "Ingrese el numero " << i << ": ";\n'
    lin += "    cin >> numero_actual;\n\n"
    
    if params['tiene_if_mayor']:
        lin += "    // --- EVALÚA EL MAYOR ---\n"
        lin += "    if !(numero_actual > mayor) GOTO E3\n"
        lin += "    mayor = numero_actual;\n\n"
    
    if params['tiene_if_menor']:
        lin += "E3: // --- EVALÚA EL MENOR ---\n"
        lin += "    if !(numero_actual < menor) GOTO E4\n"
        lin += "    menor = numero_actual;\n\n"
    
    lin += "E4: i++;\n"
    lin += "    GOTO E1\n"
    
    lin += "E2:\n"
    lin += '    cout << "\\nResultados:" << endl;\n'
    lin += '    cout << "El mayor es: " << mayor << endl;\n'
    lin += '    cout << "El menor es: " << menor << endl;\n'
    lin += "    return 0;\n"
    lin += "}\n"
    
    return lin

def generar_tercetos(tokens=None):
    params = analizar_tokens(tokens) if tokens else {
        'iteraciones': 5, 'tiene_if_mayor': True, 'tiene_if_menor': True
    }
    
    tercetos_list = []
    linea = 1
    
    tercetos_list.append(f"({linea}) CALL, lee_num, ")
    linea += 1
    tercetos_list.append(f"({linea}) =, numero_actual, AL")
    linea += 1
    tercetos_list.append(f"({linea}) =, mayor, numero_actual")
    linea += 1
    tercetos_list.append(f"({linea}) =, menor, numero_actual")
    linea += 1
    
    linea_inicio_for = linea
    tercetos_list.append(f"({linea}) =, i, 2")
    linea += 1
    tercetos_list.append(f"({linea}) -, i, {2 + params['iteraciones']}")
    linea += 1
    linea_bifurcacion_salida = linea
    tercetos_list.append(f"({linea}) BP, [salida], ")
    linea += 1
    
    tercetos_list.append(f"({linea}) CALL, lee_num, ")
    linea += 1
    tercetos_list.append(f"({linea}) =, numero_actual, AL")
    linea += 1
    
    if params['tiene_if_mayor']:
        tercetos_list.append(f"({linea}) -, numero_actual, mayor")
        linea += 1
        tercetos_list.append(f"({linea}) BN, [if_mayor_falso], ")
        linea += 1
        tercetos_list.append(f"({linea}) BC, [if_mayor_falso], ")
        linea += 1
        tercetos_list.append(f"({linea}) =, mayor, numero_actual")
        linea += 1
        linea_if_mayor_falso = linea
    
    if params['tiene_if_menor']:
        tercetos_list.append(f"({linea}) -, numero_actual, menor")
        linea += 1
        tercetos_list.append(f"({linea}) BP, [if_menor_falso], ")
        linea += 1
        tercetos_list.append(f"({linea}) BC, [if_menor_falso], ")
        linea += 1
        tercetos_list.append(f"({linea}) =, menor, numero_actual")
        linea += 1
        linea_if_menor_falso = linea
    
    tercetos_list.append(f"({linea}) ++, i, ")
    linea += 1
    tercetos_list.append(f"({linea}) B, {linea_inicio_for}, ")
    linea += 1
    
    linea_salida = linea
    tercetos_list.append(f"({linea}) =, DL, mayor")
    linea += 1
    tercetos_list.append(f"({linea}) CALL, imp_num, ")
    linea += 1
    tercetos_list.append(f"({linea}) =, DL, menor")
    linea += 1
    tercetos_list.append(f"({linea}) CALL, imp_num, ")
    linea += 1
    tercetos_list.append(f"({linea}) RET, , ")
    
    tercetos_str = []
    for terceto in tercetos_list:
        terceto = terceto.replace("[salida]", str(linea_salida))
        if params['tiene_if_mayor']:
            terceto = terceto.replace("[if_mayor_falso]", str(linea_if_mayor_falso))
        if params['tiene_if_menor']:
            terceto = terceto.replace("[if_menor_falso]", str(linea_if_menor_falso))
        tercetos_str.append(terceto)
    
    return '\n'.join(tercetos_str)

def generar_assembler(tokens=None):
    params = analizar_tokens(tokens) if tokens else {
        'iteraciones': 5, 'tiene_if_mayor': True, 'tiene_if_menor': True
    }
    
    iteraciones = params['iteraciones']
    tiene_mayor = params['tiene_if_mayor']
    tiene_menor = params['tiene_if_menor']
    
    asm = f"""org 100h
jmp start

mayor db 0
menor db 0
msg_inicio db "--- Lector de {iteraciones + 1} numeros (00-99) ---", 13, 10, "$"
msg_mayor  db 13, 10, "El mayor es: $"
msg_menor  db 13, 10, "El menor es: $"

start:
    mov dx, offset msg_inicio
    mov ah, 09h
    int 21h

    call lee_num     
    mov mayor, al    
    mov menor, al    

    mov cx, {iteraciones}        

ciclo:
    call lee_num     
    """
    
    if tiene_mayor:
        asm += """
    cmp al, mayor    
    jle no_es_mayor  
    mov mayor, al    
no_es_mayor:
    """
    
    if tiene_menor:
        asm += """
    cmp al, menor    
    jge no_es_menor  
    mov menor, al    
no_es_menor:
    """
    
    asm += f"""
    loop ciclo       

    mov dx, offset msg_mayor
    mov ah, 09h
    int 21h
    mov dl, mayor
    call imp_num     
    
    mov dx, offset msg_menor
    mov ah, 09h
    int 21h
    mov dl, menor
    call imp_num     

ret

proc lee_num  
    push bx   
    push cx
    mov ah,01
    int 21h   
    sub al,'0'
    mov bl,al 
    mov ah,01
    int 21h   
    sub al,'0'
    mov cx,10
F1: add al,bl   
    loop F1     
    pop cx
    pop bx
    ret    
endp    

proc imp_num
    push bx
    mov bl,dl
    mov dl,0
F2: cmp bl,9
    jle E3
    sub bl,10
    inc dl
    jmp F2
E3: add dl,'0'
    mov ah,02
    int 21h
    mov dl,bl
    add dl,'0'
    int 21h
    pop bx    
    ret
endp
"""
    return asm