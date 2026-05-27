import tkinter as tk
from tkinter import ttk, filedialog
import hashlib

from db.conexion import obtener_todos, ejecutar_consulta


# =====================================================
# UTILIDADES UI
# =====================================================
def centrar_ventana(win, parent):
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()

    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)

    win.geometry(f"{w}x{h}+{x}+{y}")


def show_error(parent, titulo, mensaje):
    root = parent.winfo_toplevel()

    win = tk.Toplevel(root)
    win.title(titulo)
    win.transient(root)
    win.grab_set()
    win.resizable(False, False)

    tk.Label(
        win,
        text=mensaje,
        wraplength=300,
        padx=20,
        pady=20
    ).pack()

    ttk.Button(win, text="Aceptar", command=win.destroy).pack(pady=(0, 15))

    win.update_idletasks()
    centrar_ventana(win, root)
    win.wait_window()


def ask_yes_no(parent, titulo, mensaje):
    root = parent.winfo_toplevel()
    respuesta = {"valor": False}

    win = tk.Toplevel(root)
    win.title(titulo)
    win.transient(root)
    win.grab_set()
    win.resizable(False, False)

    tk.Label(
        win,
        text=mensaje,
        wraplength=300,
        padx=20,
        pady=20
    ).pack()

    frame = tk.Frame(win)
    frame.pack(pady=(0, 15))
    ttk.Button(
        frame,
        text="No",
        command=win.destroy
    ).pack(side="left", padx=10)
    ttk.Button(
        frame,
        text="Sí",
        command=lambda: (respuesta.update(valor=True), win.destroy())
    ).pack(side="left", padx=10)

    

    win.update_idletasks()
    centrar_ventana(win, root)
    win.wait_window()

    return respuesta["valor"]


# =====================================================
# PANTALLA PRINCIPAL
# =====================================================
def mostrar_escuela(parent):
    for w in parent.winfo_children():
        w.destroy()

    contenedor = tk.Frame(parent, bg="white")
    contenedor.pack(fill="both", expand=True)

    header = tk.Frame(contenedor, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="ADMINISTRACIÓN DE ESCUELAS",
        bg="#d0e4f5",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    toolbar = tk.Frame(contenedor, bg="white")
    toolbar.pack(fill="x", padx=20, pady=5)

    ttk.Button(
        toolbar,
        text="Agregar",
        command=lambda: ventana_escuela(parent, tree)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Modificar",
        command=lambda: modificar_escuela(parent, tree)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Borrar",
        command=lambda: borrar_escuela(parent, tree)
    ).pack(side="left", padx=5)

    tree = ttk.Treeview(
        contenedor,
        columns=("id", "nombre", "RFC", "direccion"),
        show="headings",
        height=12
    )

    tree.heading("id", text="ID")
    tree.heading("nombre", text="Nombre")
    tree.heading("RFC", text="R.F.C")
    tree.heading("direccion", text="Dirección")

    tree.column("id", width=50)
    tree.column("nombre", width=260)
    tree.column("RFC", width=100)
    tree.column("direccion", width=300)

    tree.pack(fill="both", expand=True, padx=20, pady=10)
    tree.bind("<Double-1>", lambda e: modificar_escuela(parent, tree))

    cargar_escuelas(tree)


# =====================================================
# CARGAR ESCUELAS
# =====================================================
def cargar_escuelas(tree):
    tree.delete(*tree.get_children())

    filas = obtener_todos("""
        SELECT id, nombre, RFC, direccion
        FROM Escuela
        ORDER BY nombre
    """)

    for f in filas:
        tree.insert("", "end", iid=f[0], values=f)


# =====================================================
# VENTANA AGREGAR / MODIFICAR
# =====================================================
def ventana_escuela(parent, tree, datos=None):
    top = tk.Toplevel(parent)
    top.title("Escuela")
    top.geometry("290x300")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    top.resizable(False, False)

    top.grid_rowconfigure(0, weight=1)
    top.grid_rowconfigure(1, weight=0)
    top.grid_columnconfigure(0, weight=1)

    cont = tk.Frame(top, padx=15, pady=10)
    cont.grid(row=0, column=0, sticky="nsew")

    buttons = tk.Frame(top)
    buttons.grid(row=1, column=0, sticky="ew", pady=8)


    centrar_ventana(top, parent)

    cont = tk.Frame(top, padx=25, pady=15)
    cont.grid(row=0, column=0, sticky="nsew")
    
    main = tk.Frame(cont)
    main.pack(fill="both", expand=True)


    content_frame = tk.Frame(cont)
    content_frame.pack(fill="both", expand=True)

    buttons_frame = tk.Frame(cont)
    buttons_frame.pack(fill="x", pady=(10, 0))
    form_frame = tk.Frame(main)
    form_frame.pack(anchor="center")

    logo_path = tk.StringVar()


    # =========================
    # NOMBRE, R.F.C. Y DIRECCIÓN
    # =========================
    tk.Label(form_frame, text="Nombre escuela:").pack(anchor="w")

    escuela_var = tk.StringVar()

    entry_escuela = tk.Entry(form_frame, width=30, textvariable=escuela_var)
    entry_escuela.pack(pady=4)



    # R.F.C: 
    tk.Label(form_frame, text="R.F.C:").pack(anchor="w")

    rfc_var = tk.StringVar()

    entry_rfc = tk.Entry(form_frame, width=30, textvariable=rfc_var)
    entry_rfc.pack(pady=(0, 10))

    def rfc_mayusculas(*args):
        valor = rfc_var.get()
        if valor != valor.upper():
            rfc_var.set(valor.upper())

    rfc_var.trace_add("write", rfc_mayusculas)

    
    # DIRECCIÓN:
    tk.Label(form_frame, text="Dirección:").pack(anchor="w")

    direccion_var = tk.StringVar()

    entry_direccion = tk.Entry(form_frame, width=30, textvariable=direccion_var)
    entry_direccion.pack(pady=(0, 10))

    # LOGO
    tk.Label(form_frame, text="Logo:").pack(anchor="w")

    logo_frame = tk.Frame(form_frame)
    logo_frame.pack(fill="x", pady=(0, 10))

    entry_logo = tk.Entry(
        logo_frame,
        textvariable=logo_path,
        state="readonly",
        width=23
    )
    entry_logo.pack(side="left", padx=(0, 5))

    def examinar_logo():
        archivo = filedialog.askopenfilename(
            parent=top,
            title="Seleccionar logo",
            filetypes=[("Imágenes PNG", "*.png")]
        )

        if not archivo:
            return

        if not archivo.lower().endswith(".png"):
            show_error(top, "Error", "Solo se permiten archivos PNG.")
            return

        logo_path.set(archivo)

    ttk.Button(
        logo_frame,
        text="Examinar",
        command=examinar_logo
    ).pack(side="left")
    # =========================
    # CARGAR DATOS
    # =========================
    if datos:
        entry_escuela.insert(0, datos["nombre"])

        entry_rfc.insert(0, datos["RFC"])
        entry_direccion.insert(0, datos["direccion"])
        if datos.get("logo"):
            logo_path.set(datos["logo"])

    # =========================
    # BOTONES
    # =========================
    acciones = tk.Frame(content_frame)
    acciones.pack(pady=20)

    def guardar():
        nombre = entry_escuela.get().strip()
        rfc = entry_rfc.get().strip().upper()
        direccion = entry_direccion.get().strip()
        logo = logo_path.get()

        if logo and not logo.lower().endswith(".png"):
            show_error(top, "Error", "El logo debe ser un archivo PNG.")
            return

        if not nombre or not rfc:
            show_error(top, "Error", "Todos los campos son obligatorios.")
            return

        if datos:
            ejecutar_consulta(
                "UPDATE Escuela SET nombre=?, RFC=?, direccion=?, logo=? WHERE id=?",
                (nombre, rfc, direccion, logo, datos["id"])
            )
        else:
            ejecutar_consulta(
                "INSERT INTO Escuela (nombre, RFC, direccion, logo) VALUES (?, ?, ?, ?)",
                (nombre, rfc, direccion, logo)
            )

        cargar_escuelas(tree)
        top.destroy()


    ttk.Button(buttons, text="Guardar", command=guardar).pack(side="right", padx=15)
    ttk.Button(buttons, text="Cancelar", command=top.destroy).pack(side="right")

    top.bind("<Return>", lambda e: guardar())
    top.bind("<Escape>", lambda e: top.destroy())


# =====================================================
# MODIFICAR
# =====================================================
def modificar_escuela(parent, tree):
    sel = tree.selection()
    if not sel:
        show_error(parent, "Aviso", "Seleccione una escuela.")
        return

    escuela_id = sel[0]

    fila = obtener_todos(
        "SELECT nombre, RFC, direccion FROM Escuela WHERE id=?",
        (escuela_id,)
    )

    if not fila:
        show_error(parent, "Error", "No se encontró la escuela.")
        return

    datos = {
        "id": escuela_id,
        "nombre": fila[0][0],
        "RFC": fila[0][1],
        "direccion": fila[0][2]
    }

    ventana_escuela(parent, tree, datos)

# =====================================================
# BORRAR
# =====================================================
def borrar_escuela(parent, tree):
    sel = tree.selection()
    if not sel:
        show_error(parent, "Aviso", "Seleccione una escuela.")
        return

    escuela_id = sel[0]
    escuela = tree.item(escuela_id, "values")[0]

    if not ask_yes_no(
        parent,
        "Confirmar",
        f"¿Eliminar la escuela:  '{escuela}'?"
    ):
        return

    ejecutar_consulta("DELETE FROM Escuela WHERE id=?", (escuela_id,))
    cargar_escuelas(tree)
