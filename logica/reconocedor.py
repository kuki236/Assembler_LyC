def generar_tercetos():
    """Genera los tercetos usando la notación estricta del profesor (BP, BN, BC, B)."""
    # Explicación de las Equivalencias Estructurales aplicadas:
    # - Para el 'for (i=2; i<=6; i++)', hacemos i - 6. Si es BP (Positivo, i>6), salimos del ciclo.
    # - Para 'if (num > mayor)', hacemos num - mayor. Si es BN (Negativo) o BC (Cero), no es mayor, saltamos.
    # - Para 'if (num < menor)', hacemos num - menor. Si es BP (Positivo) o BC (Cero), no es menor, saltamos.
    
    tercetos = (
        "(1) CALL, lee_num, \n"
        "(2) =, numero_actual, AL\n"
        "(3) =, mayor, numero_actual\n"
        "(4) =, menor, numero_actual\n"
        "(5) =, i, 2\n"
        "(6) -, i, 6\n"              # Evaluamos la condición del FOR (i <= 6)
        "(7) BP, 20, \n"             # Si i - 6 es Positivo (i > 6), bifurcamos al final (línea 20)
        "(8) CALL, lee_num, \n"
        "(9) =, numero_actual, AL\n"
        "(10) -, numero_actual, mayor\n" # Evaluamos if (numero_actual > mayor)
        "(11) BN, 14, \n"            # Si es Negativo, saltamos la asignación
        "(12) BC, 14, \n"            # Si es Cero (iguales), saltamos la asignación
        "(13) =, mayor, numero_actual\n"
        "(14) -, numero_actual, menor\n" # Evaluamos if (numero_actual < menor)
        "(15) BP, 18, \n"            # Si es Positivo, saltamos la asignación
        "(16) BC, 18, \n"            # Si es Cero (iguales), saltamos la asignación
        "(17) =, menor, numero_actual\n"
        "(18) ++, i, \n"             # Incrementamos el contador del FOR
        "(19) B, 6, \n"              # Bifurcación Incondicional al inicio del ciclo (línea 6)
        "(20) =, DL, mayor\n"
        "(21) CALL, imp_num, \n"
        "(22) =, DL, menor\n"
        "(23) CALL, imp_num, \n"
        "(24) RET, , \n"
    )
    return tercetos

def generar_assembler():
    """Genera el código Assembler de 16 bits reflejando el código C++ exacto."""
    # NOTA: En el código Assembler final SÍ se usan CMP, JLE y JGE, 
    # ya que es la traducción final del hardware real de los tercetos BP, BN y BC.
    
    asm = """org 100h
jmp start

; --- Variables ---
mayor db 0
menor db 0
msg_inicio db "--- Lector de 6 numeros (00-99) ---", 13, 10, "$"
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

    ; 2. CICLO PARA LOS 5 NUMEROS RESTANTES
    mov cx, 5        

ciclo:
    call lee_num     ; Lee el siguiente numero en AL
    
    ; --- Evaluar Mayor ---
    cmp al, mayor    
    jle no_es_mayor  
    mov mayor, al    
no_es_mayor:

    ; --- Evaluar Menor ---
    cmp al, menor    
    jge no_es_menor  
    mov menor, al    
no_es_menor:

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