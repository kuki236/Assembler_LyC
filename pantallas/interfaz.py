import tkinter as tk
from tkinter import ttk, messagebox, font
from logica.scanner import escanear_codigo
from logica.reconocedor import generar_tercetos, generar_assembler, generar_linealizacion

def procesar_traduccion(txt_cpp, txt_lin, txt_tercetos, txt_asm):
    codigo_fuente = txt_cpp.get("1.0", tk.END).strip()
    
    if not codigo_fuente or codigo_fuente.isspace():
        messagebox.showwarning("Advertencia", "Por favor, ingresa código C para compilar")
        return
    
    lineas_limpias = escanear_codigo(codigo_fuente)
    
    linealizacion = generar_linealizacion(lineas_limpias)
    txt_lin.delete("1.0", tk.END)
    txt_lin.insert("1.0", linealizacion)
    
    tercetos = generar_tercetos(lineas_limpias)
    txt_tercetos.delete("1.0", tk.END)
    txt_tercetos.insert("1.0", tercetos)
    
    assembler = generar_assembler(lineas_limpias)
    txt_asm.delete("1.0", tk.END)
    txt_asm.insert("1.0", assembler)
    
    messagebox.showinfo("✓ Éxito", "Compilación completada correctamente")

def abrir_ventana_expandida(titulo, contenido, color_bg):
    """Abre una ventana con un panel expandido"""
    ventana = tk.Toplevel()
    ventana.title(titulo)
    ventana.geometry("1000x700")
    ventana.config(bg=color_bg)
    
    # Header
    header = tk.Frame(ventana, bg="#1e3a5f", height=40)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    label_header = tk.Label(
        header,
        text=f"📄 {titulo}",
        font=("Segoe UI", 12, "bold"),
        bg="#1e3a5f",
        fg="white"
    )
    label_header.pack(anchor=tk.W, padx=12, pady=8)
    
    # Texto
    frame_contenido = tk.Frame(ventana, bg=color_bg)
    frame_contenido.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    txt = tk.Text(
        frame_contenido,
        font=("Courier New", 10),
        bg="white",
        fg="#333",
        relief=tk.SOLID,
        bd=1,
        wrap=tk.WORD
    )
    txt.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(txt, command=txt.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    txt.config(yscrollcommand=scrollbar.set)
    txt.insert("1.0", contenido)
    txt.config(state=tk.DISABLED)

def iniciar_interfaz():
    root = tk.Tk()
    root.title("🔧 Compilador C → Assembler x86")
    root.geometry("1800x1100")
    root.config(bg="#f0f1f3")
    
    # ==================== HEADER ====================
    header = tk.Frame(root, bg="#1e3a5f", height=60)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    title = tk.Label(
        header,
        text="🔧 COMPILADOR C → ASSEMBLER x86",
        font=("Segoe UI", 20, "bold"),
        bg="#1e3a5f",
        fg="white"
    )
    title.pack(pady=10)
    
    # ==================== CONTENIDO PRINCIPAL ====================
    main_container = tk.Frame(root, bg="#f0f1f3")
    main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
    
    # Panel izquierdo: Editor C
    left_panel = tk.Frame(main_container, bg="white", relief=tk.SOLID, bd=1)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # Título de entrada
    entry_header = tk.Frame(left_panel, bg="#f8f9fa", height=35)
    entry_header.pack(fill=tk.X)
    entry_header.pack_propagate(False)
    
    title_entry = tk.Label(
        entry_header,
        text="📝 CÓDIGO C (ENTRADA)",
        font=("Segoe UI", 12, "bold"),
        bg="#f8f9fa",
        fg="#1e3a5f"
    )
    title_entry.pack(anchor=tk.W, padx=12, pady=7)
    
    # Editor C
    txt_cpp = tk.Text(
        left_panel,
        font=("Courier New", 11),
        bg="#fafbfc",
        fg="#000",
        relief=tk.FLAT,
        bd=0,
        wrap=tk.WORD,
        insertbackground="#1e3a5f"
    )
    txt_cpp.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # Scrollbar para código C
    scrollbar_cpp = tk.Scrollbar(txt_cpp, command=txt_cpp.yview)
    scrollbar_cpp.pack(side=tk.RIGHT, fill=tk.Y)
    txt_cpp.config(yscrollcommand=scrollbar_cpp.set)
    
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
    
    # Panel derecho: Salidas
    right_panel = tk.Frame(main_container, bg="white")
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # ==================== SALIDAS CON PANED WINDOW ====================
    paned = tk.PanedWindow(right_panel, orient=tk.VERTICAL, bg="white", relief=tk.FLAT, bd=0)
    paned.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # --- PANEL 1: LINEALIZACIÓN ---
    frame_lin = tk.Frame(paned, bg="white", relief=tk.SOLID, bd=1)
    paned.add(frame_lin, height=280)
    
    header_lin = tk.Frame(frame_lin, bg="#f0f4f8", height=32)
    header_lin.pack(fill=tk.X)
    header_lin.pack_propagate(False)
    
    header_lin_content = tk.Frame(header_lin, bg="#f0f4f8")
    header_lin_content.pack(anchor=tk.W, padx=10, pady=6, fill=tk.X, expand=True)
    
    label_lin = tk.Label(
        header_lin_content,
        text="🔄 LINEALIZACIÓN",
        font=("Segoe UI", 11, "bold"),
        bg="#f0f4f8",
        fg="#1e3a5f"
    )
    label_lin.pack(side=tk.LEFT)
    
    btn_expand_lin = tk.Button(
        header_lin_content,
        text="⛶",
        font=("Segoe UI", 10),
        bg="#f0f4f8",
        fg="#1e3a5f",
        relief=tk.FLAT,
        padx=8,
        pady=2,
        cursor="hand2"
    )
    btn_expand_lin.pack(side=tk.RIGHT, padx=5)
    
    txt_lin = tk.Text(
        frame_lin,
        font=("Courier New", 10),
        bg="#fff9f0",
        fg="#333",
        relief=tk.FLAT,
        bd=0,
        wrap=tk.WORD,
        height=10
    )
    txt_lin.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    scrollbar_lin = tk.Scrollbar(txt_lin, command=txt_lin.yview)
    scrollbar_lin.pack(side=tk.RIGHT, fill=tk.Y)
    txt_lin.config(yscrollcommand=scrollbar_lin.set)
    
    btn_expand_lin.config(command=lambda: abrir_ventana_expandida("LINEALIZACIÓN", txt_lin.get("1.0", tk.END), "#fff9f0"))
    
    # --- PANEL 2: TERCETOS ---
    frame_tercetos = tk.Frame(paned, bg="white", relief=tk.SOLID, bd=1)
    paned.add(frame_tercetos, height=280)
    
    header_tercetos = tk.Frame(frame_tercetos, bg="#f0f8f4", height=32)
    header_tercetos.pack(fill=tk.X)
    header_tercetos.pack_propagate(False)
    
    header_tercetos_content = tk.Frame(header_tercetos, bg="#f0f8f4")
    header_tercetos_content.pack(anchor=tk.W, padx=10, pady=6, fill=tk.X, expand=True)
    
    label_tercetos = tk.Label(
        header_tercetos_content,
        text="⚙️  TERCETOS",
        font=("Segoe UI", 11, "bold"),
        bg="#f0f8f4",
        fg="#1e3a5f"
    )
    label_tercetos.pack(side=tk.LEFT)
    
    btn_expand_tercetos = tk.Button(
        header_tercetos_content,
        text="⛶",
        font=("Segoe UI", 10),
        bg="#f0f8f4",
        fg="#1e3a5f",
        relief=tk.FLAT,
        padx=8,
        pady=2,
        cursor="hand2"
    )
    btn_expand_tercetos.pack(side=tk.RIGHT, padx=5)
    
    txt_tercetos = tk.Text(
        frame_tercetos,
        font=("Courier New", 10),
        bg="#f0fff9",
        fg="#333",
        relief=tk.FLAT,
        bd=0,
        wrap=tk.WORD,
        height=10
    )
    txt_tercetos.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    scrollbar_tercetos = tk.Scrollbar(txt_tercetos, command=txt_tercetos.yview)
    scrollbar_tercetos.pack(side=tk.RIGHT, fill=tk.Y)
    txt_tercetos.config(yscrollcommand=scrollbar_tercetos.set)
    
    btn_expand_tercetos.config(command=lambda: abrir_ventana_expandida("TERCETOS", txt_tercetos.get("1.0", tk.END), "#f0fff9"))
    
    # --- PANEL 3: ASSEMBLER ---
    frame_asm = tk.Frame(paned, bg="white", relief=tk.SOLID, bd=1)
    paned.add(frame_asm, height=380)
    
    header_asm = tk.Frame(frame_asm, bg="#f8f0f8", height=32)
    header_asm.pack(fill=tk.X)
    header_asm.pack_propagate(False)
    
    header_asm_content = tk.Frame(header_asm, bg="#f8f0f8")
    header_asm_content.pack(anchor=tk.W, padx=10, pady=6, fill=tk.X, expand=True)
    
    label_asm = tk.Label(
        header_asm_content,
        text="🔧 ENSAMBLADOR x86 (Compatible EMU8086)",
        font=("Segoe UI", 11, "bold"),
        bg="#f8f0f8",
        fg="#1e3a5f"
    )
    label_asm.pack(side=tk.LEFT)
    
    btn_expand_asm = tk.Button(
        header_asm_content,
        text="⛶",
        font=("Segoe UI", 10),
        bg="#f8f0f8",
        fg="#1e3a5f",
        relief=tk.FLAT,
        padx=8,
        pady=2,
        cursor="hand2"
    )
    btn_expand_asm.pack(side=tk.RIGHT, padx=5)
    
    txt_asm = tk.Text(
        frame_asm,
        font=("Courier New", 10),
        bg="#fff0f0",
        fg="#333",
        relief=tk.FLAT,
        bd=0,
        wrap=tk.WORD,
        height=14
    )
    txt_asm.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    scrollbar_asm = tk.Scrollbar(txt_asm, command=txt_asm.yview)
    scrollbar_asm.pack(side=tk.RIGHT, fill=tk.Y)
    txt_asm.config(yscrollcommand=scrollbar_asm.set)
    
    btn_expand_asm.config(command=lambda: abrir_ventana_expandida("ENSAMBLADOR x86", txt_asm.get("1.0", tk.END), "#fff0f0"))
    
    # ==================== FOOTER CON BOTONES ====================
    footer = tk.Frame(root, bg="#2c3e50", height=90)
    footer.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)
    footer.pack_propagate(False)
    
    button_frame = tk.Frame(footer, bg="#2c3e50")
    button_frame.pack(expand=True)
    
    btn_compilar = tk.Button(
        button_frame,
        text="▶  COMPILAR",
        font=("Segoe UI", 13, "bold"),
        bg="#27ae60",
        fg="white",
        padx=40,
        pady=15,
        relief=tk.RAISED,
        bd=2,
        cursor="hand2",
        command=lambda: procesar_traduccion(txt_cpp, txt_lin, txt_tercetos, txt_asm)
    )
    btn_compilar.pack(side=tk.LEFT, padx=20)
    
    btn_limpiar = tk.Button(
        button_frame,
        text="🗑️  LIMPIAR",
        font=("Segoe UI", 13, "bold"),
        bg="#e74c3c",
        fg="white",
        padx=40,
        pady=15,
        relief=tk.RAISED,
        bd=2,
        cursor="hand2",
        command=lambda: (txt_cpp.delete("1.0", tk.END), txt_cpp.insert("1.0", codigo_cpp_default),
                         txt_lin.delete("1.0", tk.END), txt_tercetos.delete("1.0", tk.END), 
                         txt_asm.delete("1.0", tk.END))
    )
    btn_limpiar.pack(side=tk.LEFT, padx=20)
    
    root.mainloop()
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    title = tk.Label(
        header,
        text="🔧 COMPILADOR C → ASSEMBLER x86",
        font=("Segoe UI", 20, "bold"),
        bg="#1e3a5f",
        fg="white"
    )
    title.pack(pady=10)
    
    # Crear variable para almacenar panel expandido
    expanded_panel = {}
    
    # Función para expandir/contraer paneles
    def toggle_expand_panel(panel_name, paned_ref, panel_frame, txt_widget):
        """Expande un panel a pantalla completa o lo restaura"""
        if expanded_panel.get('current') == panel_name:
            # Contraer
            paned_ref.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            panel_frame.pack_forget()
            expanded_panel['current'] = None
        else:
            # Expandir
            paned_ref.pack_forget()
            if expanded_panel.get('current'):
                expanded_panel['panels'][expanded_panel['current']].pack_forget()
            
            panel_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            expanded_panel['current'] = panel_name
    
    expanded_panel['panels'] = {}
    
    # ==================== CONTENIDO PRINCIPAL ====================
    main_container = tk.Frame(root, bg="#f0f1f3")
    main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
    
    # Panel izquierdo: Editor C
    left_panel = tk.Frame(main_container, bg="white", relief=tk.SOLID, bd=1)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # Título de entrada
    entry_header = tk.Frame(left_panel, bg="#f8f9fa", height=35)
    entry_header.pack(fill=tk.X)
    entry_header.pack_propagate(False)
    
    title_entry = tk.Label(
        entry_header,
        text="📝 CÓDIGO C (ENTRADA)",
        font=("Segoe UI", 12, "bold"),
        bg="#f8f9fa",
        fg="#1e3a5f"
    )
    title_entry.pack(anchor=tk.W, padx=12, pady=7)
    
    # Editor C
    txt_cpp = tk.Text(
        left_panel,
        font=("Courier New", 11),
        bg="#fafbfc",
        fg="#000",
        relief=tk.FLAT,
        bd=0,
        wrap=tk.WORD,
        insertbackground="#1e3a5f"
    )
    txt_cpp.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # Scrollbar para código C
    scrollbar_cpp = tk.Scrollbar(txt_cpp, command=txt_cpp.yview)
    scrollbar_cpp.pack(side=tk.RIGHT, fill=tk.Y)
    txt_cpp.config(yscrollcommand=scrollbar_cpp.set)
    
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
    
    # Panel derecho: Salidas
    right_panel = tk.Frame(main_container, bg="white")
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # ==================== SALIDAS CON PANED WINDOW ====================
    paned = tk.PanedWindow(right_panel, orient=tk.VERTICAL, bg="white", relief=tk.FLAT, bd=0)
    paned.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # --- PANEL 1: LINEALIZACIÓN ---
    frame_lin = tk.Frame(paned, bg="white", relief=tk.SOLID, bd=1)
    paned.add(frame_lin, height=280)
    
    header_lin = tk.Frame(frame_lin, bg="#f0f4f8", height=32)
    header_lin.pack(fill=tk.X)
    header_lin.pack_propagate(False)
    
    header_lin_content = tk.Frame(header_lin, bg="#f0f4f8")
    header_lin_content.pack(anchor=tk.W, padx=10, pady=6, fill=tk.X, expand=True)
    
    label_lin = tk.Label(
        header_lin_content,
        text="🔄 LINEALIZACIÓN",
        font=("Segoe UI", 11, "bold"),
        bg="#f0f4f8",
        fg="#1e3a5f"
    )
    label_lin.pack(side=tk.LEFT)
    
    btn_expand_lin = tk.Button(
        header_lin_content,
        text="⛶",
        font=("Segoe UI", 10),
        bg="#f0f4f8",
        fg="#1e3a5f",
        relief=tk.FLAT,
        padx=8,
        pady=2,
        cursor="hand2"
    )
    btn_expand_lin.pack(side=tk.RIGHT, padx=5)
    
    txt_lin = tk.Text(
        frame_lin,
        font=("Courier New", 10),
        bg="#fff9f0",
        fg="#333",
        relief=tk.FLAT,
        bd=0,
        wrap=tk.WORD,
        height=10
    )
    txt_lin.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    scrollbar_lin = tk.Scrollbar(txt_lin, command=txt_lin.yview)
    scrollbar_lin.pack(side=tk.RIGHT, fill=tk.Y)
    txt_lin.config(yscrollcommand=scrollbar_lin.set)
    
    # Crear frame expandible para lineal
    expanded_lin = tk.Frame(root, bg="#fff9f0")
    txt_lin_expanded = tk.Text(
        expanded_lin,
        font=("Courier New", 10),
        bg="#fff9f0",
        fg="#333",
        relief=tk.FLAT,
        bd=0,
        wrap=tk.WORD
    )
    txt_lin_expanded.pack(fill=tk.BOTH, expand=True)
    scrollbar_lin_exp = tk.Scrollbar(txt_lin_expanded, command=txt_lin_expanded.yview)
    scrollbar_lin_exp.pack(side=tk.RIGHT, fill=tk.Y)
    txt_lin_expanded.config(yscrollcommand=scrollbar_lin_exp.set)
    
    expanded_panel['panels']['lineal'] = expanded_lin
    btn_expand_lin.config(command=lambda: (toggle_expand_panel('lineal', right_panel, expanded_lin, txt_lin), 
                                            txt_lin_expanded.delete("1.0", tk.END) or txt_lin_expanded.insert("1.0", txt_lin.get("1.0", tk.END))))
    
    # --- PANEL 2: TERCETOS ---
    frame_tercetos = tk.Frame(paned, bg="white", relief=tk.SOLID, bd=1)
    paned.add(frame_tercetos, height=280)
    
    header_tercetos = tk.Frame(frame_tercetos, bg="#f0f8f4", height=32)
    header_tercetos.pack(fill=tk.X)
    header_tercetos.pack_propagate(False)
    
    header_tercetos_content = tk.Frame(header_tercetos, bg="#f0f8f4")
    header_tercetos_content.pack(anchor=tk.W, padx=10, pady=6, fill=tk.X, expand=True)
    
    label_tercetos = tk.Label(
        header_tercetos_content,
        text="⚙️  TERCETOS",
        font=("Segoe UI", 11, "bold"),
        bg="#f0f8f4",
        fg="#1e3a5f"
    )
    label_tercetos.pack(side=tk.LEFT)
    
    btn_expand_tercetos = tk.Button(
        header_tercetos_content,
        text="⛶",
        font=("Segoe UI", 10),
        bg="#f0f8f4",
        fg="#1e3a5f",
        relief=tk.FLAT,
        padx=8,
        pady=2,
        cursor="hand2"
    )
    btn_expand_tercetos.pack(side=tk.RIGHT, padx=5)
    
    txt_tercetos = tk.Text(
        frame_tercetos,
        font=("Courier New", 10),
        bg="#f0fff9",
        fg="#333",
        relief=tk.FLAT,
        bd=0,
        wrap=tk.WORD,
        height=10
    )
    txt_tercetos.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    scrollbar_tercetos = tk.Scrollbar(txt_tercetos, command=txt_tercetos.yview)
    scrollbar_tercetos.pack(side=tk.RIGHT, fill=tk.Y)
    txt_tercetos.config(yscrollcommand=scrollbar_tercetos.set)
    
    expanded_panel['panels']['tercetos'] = {'frame': frame_tercetos, 'parent': main_container}
    btn_expand_tercetos.config(command=lambda: toggle_expand_panel('tercetos', main_container, frame_tercetos, "TERCETOS", txt_tercetos))
    
    # --- PANEL 3: ASSEMBLER ---
    frame_asm = tk.Frame(paned, bg="white", relief=tk.SOLID, bd=1)
    paned.add(frame_asm, height=380)
    
    header_asm = tk.Frame(frame_asm, bg="#f8f0f8", height=32)
    header_asm.pack(fill=tk.X)
    header_asm.pack_propagate(False)
    
    header_asm_content = tk.Frame(header_asm, bg="#f8f0f8")
    header_asm_content.pack(anchor=tk.W, padx=10, pady=6, fill=tk.X, expand=True)
    
    label_asm = tk.Label(
        header_asm_content,
        text="🔧 ENSAMBLADOR x86 (Compatible EMU8086)",
        font=("Segoe UI", 11, "bold"),
        bg="#f8f0f8",
        fg="#1e3a5f"
    )
    label_asm.pack(side=tk.LEFT)
    
    btn_expand_asm = tk.Button(
        header_asm_content,
        text="⛶",
        font=("Segoe UI", 10),
        bg="#f8f0f8",
        fg="#1e3a5f",
        relief=tk.FLAT,
        padx=8,
        pady=2,
        cursor="hand2"
    )
    btn_expand_asm.pack(side=tk.RIGHT, padx=5)
    
    txt_asm = tk.Text(
        frame_asm,
        font=("Courier New", 10),
        bg="#fff0f0",
        fg="#333",
        relief=tk.FLAT,
        bd=0,
        wrap=tk.WORD,
        height=14
    )
    txt_asm.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    scrollbar_asm = tk.Scrollbar(txt_asm, command=txt_asm.yview)
    scrollbar_asm.pack(side=tk.RIGHT, fill=tk.Y)
    txt_asm.config(yscrollcommand=scrollbar_asm.set)
    
    expanded_panel['panels']['asm'] = {'frame': frame_asm, 'parent': main_container}
    btn_expand_asm.config(command=lambda: toggle_expand_panel('asm', main_container, frame_asm, "ENSAMBLADOR", txt_asm))
    
    # ==================== FOOTER CON BOTONES ====================
    footer = tk.Frame(root, bg="#2c3e50", height=90)
    footer.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)
    footer.pack_propagate(False)
    
    button_frame = tk.Frame(footer, bg="#2c3e50")
    button_frame.pack(expand=True)
    
    btn_compilar = tk.Button(
        button_frame,
        text="▶  COMPILAR",
        font=("Segoe UI", 13, "bold"),
        bg="#27ae60",
        fg="white",
        padx=40,
        pady=15,
        relief=tk.RAISED,
        bd=2,
        cursor="hand2",
        command=lambda: procesar_traduccion(txt_cpp, txt_lin, txt_tercetos, txt_asm)
    )
    btn_compilar.pack(side=tk.LEFT, padx=20)
    
    btn_limpiar = tk.Button(
        button_frame,
        text="🗑️  LIMPIAR",
        font=("Segoe UI", 13, "bold"),
        bg="#e74c3c",
        fg="white",
        padx=40,
        pady=15,
        relief=tk.RAISED,
        bd=2,
        cursor="hand2",
        command=lambda: (txt_cpp.delete("1.0", tk.END), txt_cpp.insert("1.0", codigo_cpp_default),
                         txt_lin.delete("1.0", tk.END), txt_tercetos.delete("1.0", tk.END), 
                         txt_asm.delete("1.0", tk.END))
    )
    btn_limpiar.pack(side=tk.LEFT, padx=20)
    
    root.mainloop()