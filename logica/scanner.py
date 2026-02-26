def escanear_codigo(texto_cpp):

    lineas = texto_cpp.split('\n')
    codigo_limpio = []
    
    for linea in lineas:
        linea = linea.strip()
        if linea and not linea.startswith("//"):
            codigo_limpio.append(linea)
            
    return codigo_limpio