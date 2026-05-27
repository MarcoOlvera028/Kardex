import tkinter as tk
from tkinter import ttk
import hashlib

from db.conexion import obtener_todos, ejecutar_consulta


# =====================================================
# UTILIDAD HASH PASSWORD
# =====================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


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
def mostrar_especialidades(parent, ciclo_activo):
    for w in parent.winfo_children():
        w.destroy()

    contenedor = tk.Frame(parent, bg="white")
    contenedor.pack(fill="both", expand=True)

    header = tk.Frame(contenedor, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="ESPECIALIDADES",
        bg="#d0e4f5",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    toolbar = tk.Frame(contenedor, bg="white")
    toolbar.pack(fill="x", padx=20, pady=5)

    tree = ttk.Treeview(
        contenedor,
        columns=("nombre",),
        show="headings",
        height=12
    )

    tree.heading("nombre", text="Nombre de la Especialidad")
    tree.column("nombre", width=400)

    tree.pack(fill="both", expand=True, padx=20, pady=10)
    tree.bind("<Double-1>", lambda e: modificar_especialidad(parent, tree))

    ttk.Button(
        toolbar,
        text="Agregar",
        command=lambda: ventana_especialidad(parent, tree)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Modificar",
        command=lambda: modificar_especialidad(parent, tree)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Borrar",
        command=lambda: borrar_especialidad(parent, tree)
    ).pack(side="left", padx=5)

    cargar_especialidades(tree)


# =====================================================
# CARGAR materiaS
# =====================================================
def cargar_especialidades(tree):
    tree.delete(*tree.get_children())

    filas = obtener_todos("""
        SELECT id, nombre
        FROM Especialidades
        ORDER BY nombre
    """)

    for f in filas:
        tree.insert("", "end", iid=f[0], values=(f[1],))


# =====================================================
# VENTANA AGREGAR / MODIFICAR
# =====================================================
def ventana_especialidad(parent, tree, datos=None):
    top = tk.Toplevel(parent)
    top.title("Modificar Especialidad" if datos else "Agregar Especialidad")
    top.geometry("350x200")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    top.resizable(False, False)

    cont = tk.Frame(top, padx=20, pady=20)
    cont.pack(fill="both", expand=True)

    nombre_var = tk.StringVar()

    tk.Label(cont, text="Nombre de la especialidad:").pack(anchor="w")
    entry_nombre = tk.Entry(cont, textvariable=nombre_var)
    entry_nombre.pack(fill="x", pady=10)

    if datos:
        nombre_var.set(datos["nombre"])

    def guardar():
        nombre = nombre_var.get().strip()

        if not nombre:
            show_error(top, "Error", "El nombre es obligatorio.")
            return

        # Validar duplicado
        existe = obtener_todos(
            "SELECT id FROM Especialidades WHERE nombre=? AND id != ?",
            (nombre, datos["id"] if datos else 0)
        )

        if existe:
            show_error(top, "Error", "Ya existe una especialidad con ese nombre.")
            return

        if datos:
            ejecutar_consulta(
                "UPDATE Especialidades SET nombre=? WHERE id=?",
                (nombre, datos["id"])
            )
        else:
            ejecutar_consulta(
                "INSERT INTO Especialidades (nombre) VALUES (?)",
                (nombre,)
            )

        cargar_especialidades(tree)
        top.destroy()

    btn_frame = tk.Frame(cont)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Guardar", command=guardar).pack(side="right", padx=5)
    ttk.Button(btn_frame, text="Cancelar", command=top.destroy).pack(side="right")

    top.update_idletasks()
    centrar_ventana(top, parent)

    top.bind("<Return>", lambda e: guardar())
    top.bind("<Escape>", lambda e: top.destroy())


# =====================================================
# MODIFICAR
# =====================================================
def modificar_especialidad(parent, tree):
    seleccion = tree.selection()

    if not seleccion:
        show_error(parent, "Aviso", "Seleccione una especialidad.")
        return

    especialidad_id = seleccion[0]

    fila = obtener_todos(
        "SELECT id, nombre FROM Especialidades WHERE id=?",
        (especialidad_id,)
    )

    if not fila:
        show_error(parent, "Error", "No se encontró la especialidad.")
        return

    datos = {
        "id": fila[0][0],
        "nombre": fila[0][1]
    }

    ventana_especialidad(parent, tree, datos)


# =====================================================
# BORRAR
# =====================================================
def borrar_especialidad(parent, tree):
    seleccion = tree.selection()

    if not seleccion:
        show_error(parent, "Aviso", "Seleccione una especialidad.")
        return

    especialidad_id = seleccion[0]
    nombre = tree.item(especialidad_id, "values")[0]

    # Validar si está en uso
    en_uso = obtener_todos(
        "SELECT id FROM Materias WHERE especialidad_id=?",
        (especialidad_id,)
    )

    if en_uso:
        show_error(
            parent,
            "No permitido",
            "No se puede eliminar porque está asignada a una o más materias."
        )
        return

    confirmar = ask_yes_no(
        parent,
        "Confirmar eliminación",
        f"¿Desea eliminar la especialidad '{nombre}'?"
    )

    if not confirmar:
        return

    ejecutar_consulta(
        "DELETE FROM Especialidades WHERE id=?",
        (especialidad_id,)
    )

    cargar_especialidades(tree)




