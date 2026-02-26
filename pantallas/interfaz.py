import tkinter as tk
from logica.scanner import escanear_codigo
from logica.reconocedor import generar_tercetos, generar_assembler

def procesar_traduccion(txt_cpp, txt_tercetos, txt_asm):
    # 1. Scanner (Obtenemos el texto)
    codigo_fuente = txt_cpp.get("1.0", tk.END)
    lineas_limpias = escanear_codigo(codigo_fuente)
    
    # 2. Reconocedor (Generamos Tercetos y Assembler)
    tercetos = generar_tercetos()
    assembler = generar_assembler()
    
    # 3. Mostrar en pantalla
    txt_tercetos.delete("1.0", tk.END)
    txt_tercetos.insert("1.0", tercetos)
    
    txt_asm.delete("1.0", tk.END)
    txt_asm.insert("1.0", assembler)

def iniciar_interfaz():
    root = tk.Tk()
    root.title("Traductor: Alto Nivel -> Tercetos -> Assembler (Trabajo 4)")
    root.geometry("1100x600")
    
    # Título superior
    tk.Label(root, text="Proceso de Compilación (Trabajo 4)", font=("Arial", 16, "bold")).pack(pady=10)
    
    # Frame para las 3 columnas
    frame_textos = tk.Frame(root)
    frame_textos.pack(fill=tk.BOTH, expand=True, padx=10)
    
    # --- Columna 1: Alto Nivel (C++) ---
    frame_cpp = tk.Frame(frame_textos)
    frame_cpp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    tk.Label(frame_cpp, text="1. Alto Nivel (C++)", font=("Arial", 12)).pack()
    txt_cpp = tk.Text(frame_cpp, width=30, height=25, bg="#f0f0f0")
    txt_cpp.pack(fill=tk.BOTH, expand=True)
    
    # Código C++ por defecto

    codigo_cpp_default = """#include <iostream>

using namespace std;

int main() {
    int numero_actual;
    int mayor, menor;
    
    cout << "--- Lector de 6 numeros (00-99) ---" << endl;

    cout << "Ingrese el numero 1: ";
    cin >> numero_actual;
    
    mayor = numero_actual;
    menor = numero_actual;

    for (int i = 2; i <= 6; i++) {
        cout << "Ingrese el numero " << i << ": ";
        cin >> numero_actual;

        if (numero_actual > mayor) {
            mayor = numero_actual;
        }
        
        if (numero_actual < menor) {
            menor = numero_actual;
        }
    }

    cout << "\\nResultados:" << endl;
    cout << "El mayor es: " << mayor << endl;
    cout << "El menor es: " << menor << endl;

    return 0;
}"""
    txt_cpp.insert("1.0", codigo_cpp_default)

    # --- Columna 2: Tercetos ---
    frame_tercetos = tk.Frame(frame_textos)
    frame_tercetos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    tk.Label(frame_tercetos, text="2. Linealización (Tercetos)", font=("Arial", 12)).pack()
    txt_tercetos = tk.Text(frame_tercetos, width=30, height=25, bg="#e6f7ff")
    txt_tercetos.pack(fill=tk.BOTH, expand=True)

    # --- Columna 3: Assembler ---
    frame_asm = tk.Frame(frame_textos)
    frame_asm.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    tk.Label(frame_asm, text="3. Assembler 16 bits", font=("Arial", 12)).pack()
    txt_asm = tk.Text(frame_asm, width=40, height=25, bg="#e6ffe6")
    txt_asm.pack(fill=tk.BOTH, expand=True)

    # Botón de acción
    btn_traducir = tk.Button(root, text="Traducir (Ejecutar proceso)", font=("Arial", 12, "bold"), bg="orange",
                             command=lambda: procesar_traduccion(txt_cpp, txt_tercetos, txt_asm))
    btn_traducir.pack(pady=15)

    root.mainloop()