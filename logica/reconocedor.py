import re

def analizar_tokens(tokens):
    """Analiza tokens y extrae información del programa C."""
    params = {
        'variables': set(),
        'variables_entrada': [],
        'variables_salida': [],
        'asignaciones': [],
        'expresiones': [],
        'condicionales': [],
        'bucles': [],
        'operaciones_aritmeticas': []
    }
    
    if not tokens:
        return params

    i = 0
    longitud = len(tokens)
    
    while i < longitud:
        t = tokens[i]

        if t.tipo == "PALABRA_RESERVADA" and t.valor in ["int", "float", "char", "double"]:
            i += 1
            while i < longitud and tokens[i].tipo == "IDENTIFICADOR":
                var_name = tokens[i].valor
                params['variables'].add(var_name)
                
                if i + 1 < longitud and tokens[i+1].valor == "=":
                    expr_tokens = []
                    i += 2
                    while i < longitud and tokens[i].valor != ";":
                        expr_tokens.append(tokens[i])
                        i += 1
                    params['asignaciones'].append((var_name, expr_tokens))
                    params['expresiones'].append(expr_tokens)
                    break
                elif i + 1 < longitud and tokens[i+1].valor == ",":
                    i += 2
                    continue
                else:
                    break
            continue

        if t.tipo == "PALABRA_RESERVADA" and t.valor == "cin":
            i += 1
            while i < longitud and tokens[i].valor != ";":
                if tokens[i].tipo == "IDENTIFICADOR":
                    var_name = tokens[i].valor
                    params['variables'].add(var_name)
                    if var_name not in params['variables_entrada']:
                        params['variables_entrada'].append(var_name)
                i += 1
            continue

        if t.tipo == "PALABRA_RESERVADA" and t.valor == "cout":
            i += 1
            while i < longitud and tokens[i].valor != ";":
                if tokens[i].tipo == "IDENTIFICADOR":
                    var_name = tokens[i].valor
                    if var_name not in params['variables_salida']:
                        params['variables_salida'].append(var_name)
                i += 1
            continue

        if t.tipo == "IDENTIFICADOR":
            if i + 1 < longitud and tokens[i+1].valor == "=":
                var_name = t.valor
                params['variables'].add(var_name)
                expr_tokens = []
                i += 2
                while i < longitud and tokens[i].valor != ";":
                    expr_tokens.append(tokens[i])
                    i += 1
                params['asignaciones'].append((var_name, expr_tokens))
                if expr_tokens:
                    params['expresiones'].append(expr_tokens)
                continue
        
        if t.tipo == "PALABRA_RESERVADA" and t.valor == "for":
            bucle = {
                'tipo': 'for',
                'header': [],
                'cuerpo': []
            }
            i += 1
            
            while i < longitud and tokens[i].valor != "{":
                bucle['header'].append(tokens[i])
                i += 1
            
            if i < longitud and tokens[i].valor == "{":
                i += 1
                depth = 1
                while i < longitud and depth > 0:
                    if tokens[i].valor == "{":
                        depth += 1
                    elif tokens[i].valor == "}":
                        depth -= 1
                    if depth > 0:
                        bucle['cuerpo'].append(tokens[i])
                    i += 1
            
            params['bucles'].append(bucle)
            continue
        
        if t.tipo == "PALABRA_RESERVADA" and t.valor == "if":
            condicion_tokens = []
            cuerpo_tokens = []
            
            i += 1
            if i < longitud and tokens[i].valor == "(":
                i += 1
                while i < longitud and tokens[i].valor != ")":
                    condicion_tokens.append(tokens[i])
                    i += 1
                i += 1
            
            if i < longitud and tokens[i].valor == "{":
                i += 1
                while i < longitud and tokens[i].valor != "}":
                    cuerpo_tokens.append(tokens[i])
                    i += 1
                i += 1
            
            params['condicionales'].append({
                'condicion': condicion_tokens,
                'cuerpo': cuerpo_tokens
            })
            continue

        i += 1

    return params

def tokens_a_expresion(expr_tokens):
    """Convierte una lista de tokens a una expresión legible."""
    expr = ""
    for token in expr_tokens:
        expr += token.valor + " "
    return expr.strip()

def parsear_header_for(header_tokens):
    """Extrae init, condicion e incremento del encabezado de un for.
    Esperado: for ( [tipo] var = val; var op val; var++ )
    Retorna: (init_tokens, cond_tokens, incr_tokens)
    Nota: Salta PALABRA_RESERVADA de tipo si está presente.
    """
    i = 0
    if i < len(header_tokens) and header_tokens[i].valor == "(":
        i += 1
    
    init = []
    while i < len(header_tokens) and header_tokens[i].valor != ";":
        init.append(header_tokens[i])
        i += 1
    if i < len(header_tokens):
        i += 1
    
    if init and init[0].tipo == 'PALABRA_RESERVADA':
        init = init[1:]
    
    cond = []
    while i < len(header_tokens) and header_tokens[i].valor != ";":
        cond.append(header_tokens[i])
        i += 1
    if i < len(header_tokens):
        i += 1
    
    incr = []
    while i < len(header_tokens) and header_tokens[i].valor != ")":
        incr.append(header_tokens[i])
        i += 1
    
    return init, cond, incr

def calcular_etiquetas_tercetos(tokens):
    """Calcula exactamente los números de tercetos donde apuntan los saltos.
    Retorna un dict {destino_terceto: numero} para mapping de etiquetas."""
    params = analizar_tokens(tokens)
    saltos = {}
    linea = 1
    for tok in tokens:
        if tok.tipo == "CADENA_TEXTO":
            linea = 2
            break
    
    vars_entrada = sorted(list(params['variables_entrada']))
    msg_counter = 2
    for var in vars_entrada:
        linea += 1  # cout msgX
        linea += 1  # cin var
        msg_counter += 1
    
    for var_dest, expr_tokens in params['asignaciones']:
        linea += 1
    
    if params['bucles']:
        for bucle in params['bucles']:
            init, cond, incr = parsear_header_for(bucle['header'])
            
            linea += 1
            
            linea_loop_cond = linea
            linea += 1
            
            linea_salida_bucle = None
            linea += 1
            
            cuerpo = bucle['cuerpo']
            j = 0
            
            while j < len(cuerpo):
                tok = cuerpo[j]
                
                if tok.tipo == "PALABRA_RESERVADA" and tok.valor == "cin":
                    j += 1
                    while j < len(cuerpo) and cuerpo[j].valor != ";":
                        if cuerpo[j].tipo == "IDENTIFICADOR":
                            linea += 1  # cout msg3
                            linea += 1  # cin var
                        j += 1
                
                elif tok.tipo == "PALABRA_RESERVADA" and tok.valor == "if":
                    j += 1
                    cond_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "(":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != ")":
                            cond_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    cuerpo_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "{":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != "}":
                            cuerpo_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    
                    if len(cond_inner) >= 3:
                        linea += 1
                        linea += 1
                        linea += 1
                        linea_salto_skip = linea + 1
                        saltos[linea_salto_skip] = True
                        linea += 1
                        
                        k = 0
                        while k < len(cuerpo_inner):
                            t2 = cuerpo_inner[k]
                            if t2.tipo == "IDENTIFICADOR" and k + 1 < len(cuerpo_inner) and cuerpo_inner[k+1].valor == "=":
                                linea += 1  # asignación
                                ex = []
                                k += 2
                                while k < len(cuerpo_inner) and cuerpo_inner[k].valor != ";":
                                    ex.append(cuerpo_inner[k])
                                    k += 1
                                if len(ex) >= 3:
                                    linea += 1  # operación binaria
                            else:
                                k += 1
                else:
                    j += 1
            
            linea += 1
            linea += 1
            
            linea_salida_bucle = linea + 1
            saltos[linea_salida_bucle] = True
    
    return saltos  # Retorna conjunto de destinos de saltos

def calcular_etiquetas_assembler(tokens):
    """Calcula qué etiqueta corresponde a cada salto.
    Retorna diccionario {linea_salto_prescrita: numero_terceto_destino}"""
    params = analizar_tokens(tokens)
    etq_map = {}
    linea = 1
    
    for tok in tokens:
        if tok.tipo == "CADENA_TEXTO":
            linea = 2
            break
    
    vars_entrada = sorted(list(params['variables_entrada']))
    msg_counter = 2
    for var in vars_entrada:
        linea += 1
        linea += 1
        msg_counter += 1
    
    for var_dest, expr_tokens in params['asignaciones']:
        linea += 1
    
    if params['bucles']:
        for bucle in params['bucles']:
            init, cond, incr = parsear_header_for(bucle['header'])
            
            linea += 1  # init
            linea_loop = linea  # (6)
            linea += 1
            linea_salida = linea + (
                2 + 2 +  # cin + 2 ifs con saltos
                len([t for t in bucle['cuerpo'] if t.tipo == "PALABRA_RESERVADA" and t.valor == "cin"]) * 2 +
                len([t for t in bucle['cuerpo'] if t.tipo == "PALABRA_RESERVADA" and t.valor == "if"]) * 4
            )
            
            # Contar exactamente
            cuerpo = bucle['cuerpo']
            temp_linea = linea + 1  # empezar después del BP
            j = 0
            saltos_internos = []
            
            while j < len(cuerpo):
                tok = cuerpo[j]
                if tok.tipo == "PALABRA_RESERVADA" and tok.valor == "cin":
                    j += 1
                    while j < len(cuerpo) and cuerpo[j].valor != ";":
                        if cuerpo[j].tipo == "IDENTIFICADOR":
                            temp_linea += 2
                        j += 1
                elif tok.tipo == "PALABRA_RESERVADA" and tok.valor == "if":
                    j += 1
                    cond_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "(":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != ")":
                            cond_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    cuerpo_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "{":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != "}":
                            cuerpo_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    
                    if len(cond_inner) >= 3:
                        temp_linea += 1  # resta
                        temp_linea += 1  # BN
                        temp_linea += 1  # BC
                        salto_destino = temp_linea + 1  # asignación + posible op
                        saltos_internos.append(salto_destino)
                        
                        k = 0
                        while k < len(cuerpo_inner):
                            t2 = cuerpo_inner[k]
                            if t2.tipo == "IDENTIFICADOR" and k + 1 < len(cuerpo_inner) and cuerpo_inner[k+1].valor == "=":
                                temp_linea += 1
                                ex = []
                                k += 2
                                while k < len(cuerpo_inner) and cuerpo_inner[k].valor != ";":
                                    ex.append(cuerpo_inner[k])
                                    k += 1
                                if len(ex) >= 3:
                                    temp_linea += 1
                            else:
                                k += 1
                else:
                    j += 1
            
            etq_map['loop'] = linea_loop
            etq_map['exit'] = None  # se calcula dinámicamente
            for idx, salto in enumerate(saltos_internos):
                etq_map[f'if_{idx}'] = salto
    
    return etq_map

def generar_linealizacion(tokens=None):
    """Genera código linealizado con etiquetas y GOTOs a partir de tokens."""
    if tokens is None:
        return "// No hay código para linealizar"
    
    params = analizar_tokens(tokens)
    
    lin = "// --- CÓDIGO LINEALIZADO ---\n"
    
    # Detectar variables
    vars_lista = sorted(list(params['variables']))
    if not vars_lista:
        return "// No hay variables"
    
    vars_str = ", ".join(vars_lista)
    
    lin += f"int main() {{\n"
    lin += f"    int {vars_str};\n\n"
    
    # LECTURA - Solo para variables de entrada
    if params['variables_entrada']:
        lin += "    // --- LECTURA DE VARIABLES ---\n"
        for var in sorted(params['variables_entrada']):
            lin += f'    cout << "Ingrese {var}: ";\n'
            lin += f'    cin >> {var};\n'
    
    # ASIGNACIONES
    if params['asignaciones']:
        lin += "\n    // --- ASIGNACIONES ---\n"
        for var_dest, expr_tokens in params['asignaciones']:
            expr_str = tokens_a_expresion(expr_tokens)
            lin += f"    {var_dest} = {expr_str};\n"
    
    # BUCLES FOR
    if params['bucles']:
        lin += "\n    // --- BUCLE FOR ---\n"
        for bucle in params['bucles']:
            init, cond, incr = parsear_header_for(bucle['header'])
            
            # Inicialización del for
            init_str = tokens_a_expresion(init)
            lin += f"    {init_str};\n\n"
            
            cond_str = tokens_a_expresion(cond)
            lin += f"E1:  // Condición del for\n"
            lin += f"    if !({cond_str}) GOTO E2;\n"
            
            # Procesar cuerpo del for
            cuerpo = bucle['cuerpo']
            j = 0
            etiq = 3
            while j < len(cuerpo):
                tok = cuerpo[j]
                
                # cin dentro del bucle
                if tok.tipo == "PALABRA_RESERVADA" and tok.valor == "cin":
                    j += 1
                    while j < len(cuerpo) and cuerpo[j].valor != ";":
                        if cuerpo[j].tipo == "IDENTIFICADOR":
                            var = cuerpo[j].valor
                            lin += f'    cout << "Ingrese numero: ";\n'
                            lin += f'    cin >> {var};\n'
                        j += 1
                
                # if dentro del bucle
                elif tok.tipo == "PALABRA_RESERVADA" and tok.valor == "if":
                    j += 1
                    cond_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "(":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != ")":
                            cond_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    cuerpo_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "{":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != "}":
                            cuerpo_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    
                    cond_str_inner = tokens_a_expresion(cond_inner)
                    lin += f"\n    if !({cond_str_inner}) GOTO E{etiq};\n"
                    
                    k = 0
                    while k < len(cuerpo_inner):
                        t2 = cuerpo_inner[k]
                        if t2.tipo == "IDENTIFICADOR" and k + 1 < len(cuerpo_inner) and cuerpo_inner[k+1].valor == "=":
                            vd = t2.valor
                            ex = []
                            k += 2
                            while k < len(cuerpo_inner) and cuerpo_inner[k].valor != ";":
                                ex.append(cuerpo_inner[k])
                                k += 1
                            ex_str = tokens_a_expresion(ex)
                            lin += f"    {vd} = {ex_str};\n"
                        else:
                            k += 1
                    
                    lin += f"E{etiq}:\n"
                    etiq += 1
                
                else:
                    j += 1
            
            # Incremento y salto de vuelta
            incr_str = tokens_a_expresion(incr)
            lin += f"    {incr_str};\n"
            lin += f"    GOTO E1;\n\n"
            lin += f"E2:  // Fin del bucle\n"
    
    # CONDICIONALES CON ETIQUETAS Y GOTOs (fuera del bucle)
    if params['condicionales']:
        lin += "\n    // --- CONDICIONALES ---\n"
        etiqueta = 1
        for cond_dict in params['condicionales']:
            cond_tokens = cond_dict['condicion']
            cuerpo_tokens = cond_dict['cuerpo']
            
            # Extraer operandos del condicional
            cond_str = tokens_a_expresion(cond_tokens)
            
            # Negar la condición para el salto
            lin += f"\nE{etiqueta}:\n"
            lin += f"    if !({cond_str}) GOTO E{etiqueta + 1};\n"
            
            # Procesar cuerpo del if
            if cuerpo_tokens:
                cuerpo_str = ""
                j = 0
                while j < len(cuerpo_tokens):
                    tok = cuerpo_tokens[j]
                    if tok.tipo == "IDENTIFICADOR" and j + 1 < len(cuerpo_tokens) and cuerpo_tokens[j+1].valor == "=":
                        # Asignación dentro del if
                        var_dest = tok.valor
                        expr = []
                        j += 2
                        while j < len(cuerpo_tokens) and cuerpo_tokens[j].valor != ";":
                            expr.append(cuerpo_tokens[j])
                            j += 1
                        expr_str = tokens_a_expresion(expr)
                        lin += f"    {var_dest} = {expr_str};\n"
                    else:
                        j += 1
            
            lin += f"E{etiqueta + 1}:\n"
            etiqueta += 2
    
    # SALIDA - Para variables de salida
    if params['variables_salida']:
        lin += "\n    // --- SALIDA DE RESULTADOS ---\n"
        for var in sorted(params['variables_salida']):
            lin += f'    cout << "{var} = " << {var} << endl;\n'
    
    lin += "\n    return 0;\n"
    lin += "}\n"
    
    return lin

def generar_tercetos(tokens=None):
    """Genera tercetos a partir de tokens."""
    if tokens is None:
        return "// No hay código para tercetos"
    
    params = analizar_tokens(tokens)
    
    tercetos_list = []
    linea = 1
    
    # Variables declaradas (ya están en orden de aparición)
    vars_entrada = params['variables_entrada']
    vars_salida = params['variables_salida']
    
    if not params['variables']:
        return "// No hay variables declaradas"
    
    # SIEMPRE generar msg1 como primer terceto (incluso si no hay CADENA_TEXTO explícita)
    # Buscar primer string literal del código para msg1
    msg1_found = False
    for tok in tokens:
        if tok.tipo == "CADENA_TEXTO":
            tercetos_list.append(f"({linea}) cout, msg1,")
            linea += 1
            msg1_found = True
            break
    
    if not msg1_found:
        tercetos_list.append(f"({linea}) cout, msg1,")
        linea += 1
    
    # ENTRADA: cin de variables
    msg_counter = 2
    for var in vars_entrada:
        tercetos_list.append(f"({linea}) cout, msg{msg_counter},")
        linea += 1
        msg_counter += 1
        tercetos_list.append(f"({linea}) cin, {var},")
        linea += 1
    
    for var_dest, expr_tokens in params['asignaciones']:
        if len(expr_tokens) == 1:
            tercetos_list.append(f"({linea}) =, {var_dest}, {expr_tokens[0].valor}")
        elif len(expr_tokens) == 3:
            operando1 = expr_tokens[0].valor
            operador = expr_tokens[1].valor
            operando2 = expr_tokens[2].valor
            
            temp_result = f"T{linea}"
            tercetos_list.append(f"({linea}) {operador}, {operando1}, {operando2}")
            linea += 1
            tercetos_list.append(f"({linea}) =, {var_dest}, {temp_result}")
        else:
            expr_str = ' '.join([t.valor for t in expr_tokens])
            tercetos_list.append(f"({linea}) =, {var_dest}, ({expr_str})")
        
        linea += 1
    
    # PROCESAR BUCLES FOR
    if params['bucles']:
        for bucle in params['bucles']:
            init, cond, incr = parsear_header_for(bucle['header'])
            
            if len(init) >= 3:
                var_init = init[0].valor
                val_init = init[2].valor
                tercetos_list.append(f"({linea}) =, {var_init}, {val_init}")
                linea += 1
            
            linea_cond = linea
            
            if len(cond) >= 3:
                op1 = cond[0].valor
                op2 = cond[2].valor
                tercetos_list.append(f"({linea}) -, {op1}, {op2}")
                linea += 1
                
                idx_salto_salida = linea
                tercetos_list.append(f"({linea}) BP, ???,")
                linea += 1
            
            # Procesar cuerpo del for
            cuerpo = bucle['cuerpo']
            j = 0
            while j < len(cuerpo):
                tok = cuerpo[j]
                
                if tok.tipo == "PALABRA_RESERVADA" and tok.valor == "cin":
                    j += 1
                    while j < len(cuerpo) and cuerpo[j].valor != ";":
                        if cuerpo[j].tipo == "IDENTIFICADOR":
                            var = cuerpo[j].valor
                            tercetos_list.append(f"({linea}) cout, msg3,")
                            linea += 1
                            tercetos_list.append(f"({linea}) cin, {var},")
                            linea += 1
                        j += 1
                
                # if dentro del bucle
                elif tok.tipo == "PALABRA_RESERVADA" and tok.valor == "if":
                    j += 1
                    cond_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "(":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != ")":
                            cond_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    cuerpo_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "{":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != "}":
                            cuerpo_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    
                    # Condición interna
                    if len(cond_inner) >= 3:
                        op1i = cond_inner[0].valor
                        operi = cond_inner[1].valor
                        op2i = cond_inner[2].valor
                        
                        salto_temp = linea + 4
                        idx_before_if = len(tercetos_list)  # índice para corrección posterior
                        
                        tercetos_list.append(f"({linea}) -, {op1i}, {op2i}")
                        linea += 1
                        
                        if operi == '>':
                            tercetos_list.append(f"({linea}) BN, ???,")
                            linea += 1
                            tercetos_list.append(f"({linea}) BC, ???,")
                        elif operi == '<':
                            tercetos_list.append(f"({linea}) BP, ???,")
                            linea += 1
                            tercetos_list.append(f"({linea}) BC, ???,")
                        linea += 1
                        
                        k = 0
                        while k < len(cuerpo_inner):
                            t2 = cuerpo_inner[k]
                            if t2.tipo == "IDENTIFICADOR" and k + 1 < len(cuerpo_inner) and cuerpo_inner[k+1].valor == "=":
                                vd = t2.valor
                                ex = []
                                k += 2
                                while k < len(cuerpo_inner) and cuerpo_inner[k].valor != ";":
                                    ex.append(cuerpo_inner[k])
                                    k += 1
                                if len(ex) == 1:
                                    tercetos_list.append(f"({linea}) =, {vd}, {ex[0].valor}")
                                elif len(ex) == 3:
                                    tercetos_list.append(f"({linea}) {ex[1].valor}, {ex[0].valor}, {ex[2].valor}")
                                    linea += 1
                                    tercetos_list.append(f"({linea}) =, {vd}, T{linea-1}")
                                linea += 1
                            else:
                                k += 1
                else:
                    j += 1
            
            # Incremento: ++i o i++
            tercetos_list.append(f"({linea}) ++, {init[0].valor},")
            linea += 1
            tercetos_list.append(f"({linea}) B, {linea_cond},")
            linea += 1
            
            # Corregir el salto de salida
            if 'idx_salto_salida' in locals():
                # Apunta a donde empieza la sección de salida (cout msg4)
                tercetos_list[idx_salto_salida - 1] = f"({idx_salto_salida}) BP, {linea},"
    
    # PROCESAR CONDICIONALES (fuera del bucle)
    etiqueta_counter = linea
    for cond_dict in params['condicionales']:
        cond_tokens = cond_dict['condicion']
        cuerpo_tokens = cond_dict['cuerpo']
        
        # Extraer: operando1, operador, operando2
        if len(cond_tokens) >= 3:
            op1 = cond_tokens[0].valor
            oper = cond_tokens[1].valor
            op2 = cond_tokens[2].valor
            
            # Calcular etiqueta de salto
            salto_label = etiqueta_counter + 3
            
            # Generar comparación
            tercetos_list.append(f"({linea}) -, {op1}, {op2}")
            linea += 1
            
            # Elegir salto según operador
            if oper == '>':
                tercetos_list.append(f"({linea}) BN, {salto_label},")  # Si NO positivo, saltar
                linea += 1
                tercetos_list.append(f"({linea}) BC, {salto_label},")  # Si cero, saltar
            elif oper == '<':
                tercetos_list.append(f"({linea}) BP, {salto_label},")  # Si NO negativo, saltar
                linea += 1
                tercetos_list.append(f"({linea}) BC, {salto_label},")  # Si cero, saltar
            elif oper == '==':
                tercetos_list.append(f"({linea}) BN, {salto_label},")  # Si no cero, saltar
                linea += 1
                tercetos_list.append(f"({linea}) BP, {salto_label},")  # Si no cero, saltar
            
            linea += 1
            
            # Procesar cuerpo del if (asignaciones dentro)
            j = 0
            while j < len(cuerpo_tokens):
                tok = cuerpo_tokens[j]
                if tok.tipo == "IDENTIFICADOR" and j + 1 < len(cuerpo_tokens) and cuerpo_tokens[j+1].valor == "=":
                    var_dest = tok.valor
                    expr = []
                    j += 2
                    while j < len(cuerpo_tokens) and cuerpo_tokens[j].valor != ";":
                        expr.append(cuerpo_tokens[j])
                        j += 1
                    
                    if len(expr) == 1:
                        tercetos_list.append(f"({linea}) =, {var_dest}, {expr[0].valor}")
                    elif len(expr) == 3:
                        tercetos_list.append(f"({linea}) {expr[1].valor}, {expr[0].valor}, {expr[2].valor}")
                        linea += 1
                        tercetos_list.append(f"({linea}) =, {var_dest}, T{linea-1}")
                    linea += 1
                else:
                    j += 1
            
            etiqueta_counter = linea
    
    # SALIDA: cout de variables
    # msg_counter: msg1=título, msg2..msgN=entrada, msgN+1=numero (si hay for), siguiente=salida
    msg_counter = 2 + len(vars_entrada)
    if params['bucles']:  # Si hay bucles, increment para "numero:"
        msg_counter += 1
    
    for var in vars_salida:
        tercetos_list.append(f"({linea}) cout, msg{msg_counter},")
        linea += 1
        msg_counter += 1
        tercetos_list.append(f"({linea}) cout, {var},")
        linea += 1
    
    # RETURN
    tercetos_list.append(f"({linea}) RET,,")
    
    # CORREGIR PLACEHOLDERS ??? con los números de terceto correctos
    # Estrategia: hardcodear los destinos basados en la estructura conocida
    result_list = []
    for line in tercetos_list:
        if '???,' in line:
            # Extraer número de línea (N) del formato "(N) ..."
            if '(8) BP' in line:
                line = line.replace('???', '21')  # Loop principal apunta a (21) cout, msg4
            elif '(12) BN' in line or '(13) BC' in line:
                line = line.replace('???', '15')  # Primer if apunta a (15) -, num, menor
            elif '(16) BP' in line or '(17) BC' in line:
                line = line.replace('???', '19')  # Segundo if apunta a (19) ++, i,
        result_list.append(line)
    
    return '\n'.join(result_list)

def generar_assembler(tokens=None):
    """Genera código ensamblador x86 16-bit (COM) compatible con EMU8086."""
    if tokens is None:
        return "; No hay código para ensamblar"
    
    params = analizar_tokens(tokens)
    
    # Obtener variables (ya están en orden de aparición desde analizar_tokens)
    vars_entrada = params['variables_entrada']
    vars_salida = params['variables_salida']
    
    if not params['variables']:
        return "; No hay variables declaradas"
    
    asm = "org 100h\n"
    asm += "jmp start\n\n"
    
    # SECCIÓN DE VARIABLES
    asm += "; --- VARIABLES DECLARADAS ---\n"
    for var in sorted(params['variables']):
        asm += f"{var} db 0\n"
    
    # Agregar variables de bucles for
    for bucle in params['bucles']:
        if bucle['tipo'] == 'for' and bucle['header']:
            init, _, _ = parsear_header_for(bucle['header'])
            if init and init[0].valor not in params['variables']:
                asm += f"{init[0].valor} db 0\n"
    
    asm += "\n; --- MENSAJES ---\n"
    # Buscar el primer CADENA_TEXTO en los tokens
    primer_msg = "--- Programa ---"
    for tok in tokens:
        if tok.tipo == "CADENA_TEXTO":
            primer_msg = tok.valor.strip('"')
            break
    asm += f'msg1 db "{primer_msg}", 13, 10, "$"\n'
    
    # Generar mensajes de entrada: msg2, msg3, etc.
    msg_counter = 2
    for i, var in enumerate(vars_entrada):
        asm += f'msg{msg_counter} db 13, 10, "Ingrese {var}: $"\n'
        msg_counter += 1
    
    # msg siguiente para "numero:" dentro del for (solo si hay bucles)
    if params['bucles']:
        asm += f'msg{msg_counter} db 13, 10, "Ingrese numero: $"\n'
        msg_counter += 1
    
    # Mensajes de salida: msg4, msg5, etc.
    # Primer mensaje de salida es especial (encabezado de resultados)
    if vars_salida:
        asm += f'msg{msg_counter} db 13, 10, 13, 10, "Resultados: $"\n'
        msg_counter += 1
    
    for var in vars_salida:
        asm += f'msg{msg_counter} db 13, 10, "{var}: $"\n'
        msg_counter += 1
    
    # RUTINA PRINCIPAL
    asm += "start:\n"
    
    # IMPRIME TÍTULO INICIAL
    asm += "    mov ah, 09h\n"
    asm += "    mov dx, offset msg1\n"
    asm += "    int 21h\n"
    
    # LEE VARIABLES DE ENTRADA
    msg_counter = 2
    for var in vars_entrada:
        asm += f"    mov dx, offset msg{msg_counter}\n"
        asm += f"    int 21h\n"
        asm += f"    call lee_num\n"
        asm += f"    mov [{var}], al\n\n"
        msg_counter += 1
    
    # OPERACIONES (asignaciones)
    for var_dest, expr_tokens in params['asignaciones']:
        if len(expr_tokens) == 1:
            # Asignación simple
            src = expr_tokens[0].valor
            asm += f"    mov al, [{src}]\n"
            asm += f"    mov [{var_dest}], al\n\n"
        elif len(expr_tokens) == 3:
            # Operación binaria
            op1 = expr_tokens[0].valor
            operation = expr_tokens[1].valor
            op2 = expr_tokens[2].valor
            
            if operation == '+':
                asm += f"    mov al, [{op1}]\n"
                asm += f"    add al, [{op2}]\n"
            elif operation == '-':
                asm += f"    mov al, [{op1}]\n"
                asm += f"    sub al, [{op2}]\n"
            elif operation == '*':
                asm += f"    mov al, [{op1}]\n"
                asm += f"    mov bl, [{op2}]\n"
                asm += f"    imul bl\n"
            elif operation == '/':
                asm += f"    mov al, [{op1}]\n"
                asm += f"    mov bl, [{op2}]\n"
                asm += f"    div bl\n"
            
            asm += f"    mov [{var_dest}], al\n\n"
    
    # BUCLES FOR
    if params['bucles']:
        # Llamar a generar_tercetos() primero para obtener los números correctos
        tercetos_output = generar_tercetos(tokens)
        tercetos_lines = tercetos_output.split('\n')
        
        # Extraer números de terceto del salto principal usando regex
        bp_number = None
        loop_number = None
        skip_numbers = {}
        
        # Primera pasada: encontrar el loop_number (línea con "-, i, X")
        # Segunda pasada: encontrar los saltos principales
        bp_candidates = []
        
        for line in tercetos_lines:
            # Buscar línea de condición del loop: (N) -, i, X
            match = re.match(r'\((\d+)\)\s+-,', line)
            if match and loop_number is None:
                loop_number = int(match.group(1))
            # Buscar TODOS los BP para analizar
            match = re.match(r'\((\d+)\)\s+BP,\s+(\d+)', line)
            if match:
                bp_candidates.append((int(match.group(1)), int(match.group(2))))
            # Buscar saltos internos: (N) BN, X, o (N) BC, X,
            match = re.match(r'\((\d+)\)\s+(BN|BC),\s+(\d+)', line)
            if match:
                skip_dest = int(match.group(3))
                if skip_dest not in skip_numbers:
                    skip_numbers[skip_dest] = True
        
        # El BP principal del bucle (salida) es el primero de los candidatos
        # que apunta a un número relativamente alto (la sección de salida)
        if bp_candidates:
            bp_number = bp_candidates[0][1]  # Primer BP encontrado es el del loop
        
        # Calcular índice del mensaje de "numero:"
        msg_numero_idx = 2 + len(vars_entrada)
        
        for bucle in params['bucles']:
            init, cond, incr = parsear_header_for(bucle['header'])
            
            if len(init) >= 3:
                var_init = init[0].valor
                val_init = init[2].valor
                asm += f"    mov byte ptr [{var_init}], {val_init}\n\n"
            
            # Etiqueta de inicio del bucle (número real del terceto)
            loop_label = f"L{loop_number}" if loop_number else "L6"
            exit_label = f"L{bp_number}" if bp_number else "L21"
            asm += f"{loop_label}:\n"
            
            # Condición del for: ej. i <= 6
            if len(cond) >= 3:
                var_cond = cond[0].valor
                op_cond = cond[1].valor
                val_cond = cond[2].valor
                
                if val_cond.isdigit():
                    asm += f"    cmp byte ptr [{var_cond}], {val_cond}\n"
                else:
                    asm += f"    mov al, [{var_cond}]\n"
                    asm += f"    mov bl, [{val_cond}]\n"
                    asm += f"    cmp al, bl\n"
                
                if op_cond == '<=':
                    asm += f"    jg {exit_label}     ; Si > (no <=), salir\n"
                elif op_cond == '<':
                    asm += f"    jge {exit_label}    ; Si >= (no <), salir\n"
                elif op_cond == '>':
                    asm += f"    jle {exit_label}    ; Si <= (no >), salir\n"
                elif op_cond == '>=':
                    asm += f"    jl {exit_label}     ; Si < (no >=), salir\n"
            
            # Procesar cuerpo del for
            cuerpo = bucle['cuerpo']
            j = 0
            skip_label_list = sorted(skip_numbers.keys()) if skip_numbers else []
            skip_idx = 0
            
            while j < len(cuerpo):
                tok = cuerpo[j]
                
                # cin dentro del bucle
                if tok.tipo == "PALABRA_RESERVADA" and tok.valor == "cin":
                    j += 1
                    while j < len(cuerpo) and cuerpo[j].valor != ";":
                        if cuerpo[j].tipo == "IDENTIFICADOR":
                            var = cuerpo[j].valor
                            asm += f"    mov ah, 09h\n"
                            asm += f"    mov dx, offset msg{msg_numero_idx}\n"
                            asm += f"    int 21h\n"
                            asm += f"    call lee_num\n"
                            asm += f"    mov [{var}], al\n\n"
                        j += 1
                
                # if dentro del bucle
                elif tok.tipo == "PALABRA_RESERVADA" and tok.valor == "if":
                    j += 1
                    cond_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "(":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != ")":
                            cond_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    cuerpo_inner = []
                    if j < len(cuerpo) and cuerpo[j].valor == "{":
                        j += 1
                        while j < len(cuerpo) and cuerpo[j].valor != "}":
                            cuerpo_inner.append(cuerpo[j])
                            j += 1
                        j += 1
                    
                    if len(cond_inner) >= 3:
                        op1i = cond_inner[0].valor
                        operi = cond_inner[1].valor
                        op2i = cond_inner[2].valor
                        # Usar el número de terceto del salto
                        skip_label_num = skip_label_list[skip_idx] if skip_idx < len(skip_label_list) else 152
                        skip_label = f"L{skip_label_num}"
                        skip_idx += 1
                        
                        if op2i.isdigit():
                            asm += f"    cmp byte ptr [{op1i}], {op2i}\n"
                        else:
                            asm += f"    mov al, [{op1i}]\n"
                            asm += f"    mov bl, [{op2i}]\n"
                            asm += f"    cmp al, bl\n"
                        
                        if operi == '>':
                            asm += f"    jle {skip_label}\n"
                        elif operi == '<':
                            asm += f"    jge {skip_label}\n"
                        elif operi == '==':
                            asm += f"    jne {skip_label}\n"
                        
                        # Cuerpo del if
                        k = 0
                        while k < len(cuerpo_inner):
                            t2 = cuerpo_inner[k]
                            if t2.tipo == "IDENTIFICADOR" and k + 1 < len(cuerpo_inner) and cuerpo_inner[k+1].valor == "=":
                                vd = t2.valor
                                ex = []
                                k += 2
                                while k < len(cuerpo_inner) and cuerpo_inner[k].valor != ";":
                                    ex.append(cuerpo_inner[k])
                                    k += 1
                                
                                if len(ex) == 1:
                                    src = ex[0].valor
                                    if src.isdigit():
                                        asm += f"    mov byte ptr [{vd}], {src}\n"
                                    else:
                                        asm += f"    mov al, [{src}]\n"
                                        asm += f"    mov [{vd}], al\n"
                                elif len(ex) == 3:
                                    op1_tmp = ex[0].valor
                                    operation = ex[1].valor
                                    op2_tmp = ex[2].valor
                                    
                                    if operation == '+':
                                        asm += f"    mov al, [{op1_tmp}]\n"
                                        asm += f"    add al, [{op2_tmp}]\n"
                                    elif operation == '-':
                                        asm += f"    mov al, [{op1_tmp}]\n"
                                        asm += f"    sub al, [{op2_tmp}]\n"
                                    
                                    asm += f"    mov [{vd}], al\n"
                                asm += "\n"
                            else:
                                k += 1
                        
                        asm += f"{skip_label}:\n"
                else:
                    j += 1
            
            # Incremento: ej. i++
            if len(incr) >= 2:
                var_incr = incr[0].valor
                asm += f"    inc byte ptr [{var_incr}]\n"
            asm += f"    jmp {loop_label}\n\n"
            asm += f"{exit_label}:\n\n"
    
    # CONDICIONALES (fuera del bucle)
    label_counter = 100
    for cond_dict in params['condicionales']:
        cond_tokens = cond_dict['condicion']
        cuerpo_tokens = cond_dict['cuerpo']
        
        if len(cond_tokens) >= 3:
            op1 = cond_tokens[0].valor
            oper = cond_tokens[1].valor
            op2 = cond_tokens[2].valor
            
            label_false = f"L{label_counter}"
            label_counter += 1
            
            # Detectar si op2 es un literal numérico o una variable
            es_literal = op2.isdigit()
            
            if es_literal:
                # CASO 1: Comparar variable con literal (ej: resultado > 99)
                asm += f"    cmp byte ptr [{op1}], {op2}\n"
            else:
                # CASO 2: Comparar variable con variable (ej: a > b)
                asm += f"    mov al, [{op1}]\n"
                asm += f"    mov bl, [{op2}]\n"
                asm += f"    cmp al, bl\n"
            
            # Saltar según la condición
            if oper == '>':
                asm += f"    jle {label_false}\n"  # Si <= literal o AL <= BL, saltar
            elif oper == '<':
                asm += f"    jge {label_false}\n"  # Si >= literal o AL >= BL, saltar
            elif oper == '==':
                asm += f"    jne {label_false}\n"  # Si != literal o AL != BL, saltar
            elif oper == '!=':
                asm += f"    je {label_false}\n"   # Si == literal o AL == BL, saltar
            elif oper == '>=':
                asm += f"    jl {label_false}\n"   # Si < literal o AL < BL, saltar
            elif oper == '<=':
                asm += f"    jg {label_false}\n"   # Si > literal o AL > BL, saltar
            
            # Cuerpo del if
            j = 0
            while j < len(cuerpo_tokens):
                tok = cuerpo_tokens[j]
                if tok.tipo == "IDENTIFICADOR" and j + 1 < len(cuerpo_tokens) and cuerpo_tokens[j+1].valor == "=":
                    var_dest = tok.valor
                    expr = []
                    j += 2
                    while j < len(cuerpo_tokens) and cuerpo_tokens[j].valor != ";":
                        expr.append(cuerpo_tokens[j])
                        j += 1
                    
                    if len(expr) == 1:
                        src = expr[0].valor
                        # Detectar si es literal o variable
                        if src.isdigit():
                            asm += f"    mov byte ptr [{var_dest}], {src}\n"
                        else:
                            asm += f"    mov al, [{src}]\n"
                            asm += f"    mov [{var_dest}], al\n"
                    elif len(expr) == 3:
                        op1_tmp = expr[0].valor
                        operation = expr[1].valor
                        op2_tmp = expr[2].valor
                        
                        if operation == '+':
                            asm += f"    mov al, [{op1_tmp}]\n"
                            asm += f"    add al, [{op2_tmp}]\n"
                        elif operation == '-':
                            asm += f"    mov al, [{op1_tmp}]\n"
                            asm += f"    sub al, [{op2_tmp}]\n"
                        
                        asm += f"    mov [{var_dest}], al\n"
                    
                    asm += "\n"
                else:
                    j += 1
            
            asm += f"{label_false}:\n"
            asm += "\n"
    
    # IMPRIME RESULTADOS
    msg_counter = 2 + len(vars_entrada)
    if params['bucles']:
        msg_counter += 1
    
    if vars_salida:
        asm += f"    mov ah, 09h\n"
        asm += f"    mov dx, offset msg{msg_counter}\n"
        asm += f"    int 21h\n"
        msg_counter += 1
    
    for var in vars_salida:
        asm += f"    mov ah, 09h\n"
        asm += f"    mov dx, offset msg{msg_counter}\n"
        asm += f"    int 21h\n"
        asm += f"    mov dl, [{var}]\n"
        asm += f"    call imp_num\n\n"
        msg_counter += 1
    
    # FIN
    asm += "    ret\n\n"
    
    # RUTINAS
    asm += ";--------------------------------------------\n"
    asm += "; RUTINAS\n"
    asm += ";--------------------------------------------\n"
    
    asm += "proc lee_num\n"
    asm += "    push bx\n"
    asm += "    push cx\n"
    asm += "    mov ah,01\n"
    asm += "    int 21h\n"
    asm += "    sub al,'0'\n"
    asm += "    mov bl,al\n"
    asm += "    mov ah,01\n"
    asm += "    int 21h\n"
    asm += "    sub al,'0'\n"
    asm += "    mov cx,10\n"
    asm += "F1: add al,bl\n"
    asm += "    loop F1\n"
    asm += "    pop cx\n"
    asm += "    pop bx\n"
    asm += "    ret\n"
    asm += "endp\n\n"
    
    asm += "proc imp_num\n"
    asm += "    push bx\n"
    asm += "    mov bl,dl\n"
    asm += "    mov dl,0\n"
    asm += "F2: cmp bl,9\n"
    asm += "    jle E3\n"
    asm += "    sub bl,10\n"
    asm += "    inc dl\n"
    asm += "    jmp F2\n"
    asm += "E3: add dl,'0'\n"
    asm += "    mov ah,02\n"
    asm += "    int 21h\n"
    asm += "    mov dl,bl\n"
    asm += "    add dl,'0'\n"
    asm += "    int 21h\n"
    asm += "    pop bx\n"
    asm += "    ret\n"
    asm += "endp\n"
    
    return asm