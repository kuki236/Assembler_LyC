def analizar_codigo_cpp(codigo_limpio):
    """
    Analiza el código C++ limpio y extrae parámetros clave para generar tercetos.
    Retorna un diccionario con los parámetros encontrados.
    """
    params = {
        'iteraciones': 5,
        'variables_entrada': [],
        'variables_comparacion': [],
        'tiene_if_mayor': False,
        'tiene_if_menor': False,
    }
    
    codigo_str = ' '.join(codigo_limpio)
    
    import re
    for_match = re.search(r'for\s*\(\s*int\s+\w+\s*=\s*(\d+)\s*;\s*\w+\s*<=\s*(\d+)\s*;\s*\w+\+\+\s*\)', codigo_str)
    if for_match:
        inicio = int(for_match.group(1))
        fin = int(for_match.group(2))
        params['iteraciones'] = fin - inicio
    
    if 'numero_actual' in codigo_str and 'mayor' in codigo_str and '>' in codigo_str:
        params['tiene_if_mayor'] = True
    
    if 'numero_actual' in codigo_str and 'menor' in codigo_str and '<' in codigo_str:
        params['tiene_if_menor'] = True
    
    return params


def generar_tercetos(codigo_limpio=None):
    """
    Genera los tercetos dinámicamente basándose en el análisis del código.
    Si no se proporciona código, usa tercetos por defecto.
    """
    if codigo_limpio:
        params = analizar_codigo_cpp(codigo_limpio)
    else:
        params = {
            'iteraciones': 5,
            'tiene_if_mayor': True,
            'tiene_if_menor': True,
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
        linea_salto_if_mayor = linea
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
        linea_salto_if_menor = linea
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
    for i, terceto in enumerate(tercetos_list):
        terceto = terceto.replace("[salida]", str(linea_salida))
        if params['tiene_if_mayor']:
            terceto = terceto.replace("[if_mayor_falso]", str(linea_if_mayor_falso))
        if params['tiene_if_menor']:
            terceto = terceto.replace("[if_menor_falso]", str(linea_if_menor_falso))
        tercetos_str.append(terceto)
    
    return '\n'.join(tercetos_str)

def generar_assembler(codigo_limpio=None):
    """Genera el código Assembler de 16 bits dinámicamente basado en el análisis del código."""
    
    if codigo_limpio:
        params = analizar_codigo_cpp(codigo_limpio)
    else:
        params = {
            'iteraciones': 5,
            'tiene_if_mayor': True,
            'tiene_if_menor': True,
        }
    
    iteraciones = params['iteraciones']
    tiene_mayor = params['tiene_if_mayor']
    tiene_menor = params['tiene_if_menor']
    
    asm = f"""org 100h
jmp start

; --- Variables ---
mayor db 0
menor db 0
msg_inicio db "--- Lector de {iteraciones + 1} numeros (00-99) ---", 13, 10, "$"
msg_mayor  db 13, 10, "El mayor es: $"
msg_menor  db 13, 10, "El menor es: $"

start:
    ; Imprimir mensaje inicial
    mov dx, offset msg_inicio
    mov ah, 09h
    int 21h

    ; 1. LEER EL PRIMER NUMERO (Inicializa mayor y menor)
    call lee_num     
    mov mayor, al    
    mov menor, al    

    ; 2. CICLO PARA LOS {iteraciones} NUMEROS RESTANTES
    mov cx, {iteraciones}        

ciclo:
    call lee_num     ; Lee el siguiente numero en AL
    """
    
    # Agregar IF mayor dinámicamente
    if tiene_mayor:
        asm += """
    ; --- Evaluar Mayor ---
    cmp al, mayor    
    jle no_es_mayor  
    mov mayor, al    
no_es_mayor:
    """
    
    if tiene_menor:
        asm += """
    ; --- Evaluar Menor ---
    cmp al, menor    
    jge no_es_menor  
    mov menor, al    
no_es_menor:
    """
    
    asm += f"""
    loop ciclo       ; Resta 1 a CX, salta a 'ciclo' si no es 0

    ; 3. IMPRIMIR RESULTADOS
    ; Imprimir texto mayor
    mov dx, offset msg_mayor
    mov ah, 09h
    int 21h
    ; Imprimir numero mayor
    mov dl, mayor
    call imp_num     
    
    ; Imprimir texto menor
    mov dx, offset msg_menor
    mov ah, 09h
    int 21h
    ; Imprimir numero menor
    mov dl, menor
    call imp_num     

ret

;--------------------------------------------
; Rutinas del profesor
;--------------------------------------------
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