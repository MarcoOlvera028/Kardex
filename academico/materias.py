import tkinter as tk
from tkinter import ttk

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
def mostrar_materias(parent, ciclo_activo):
    for w in parent.winfo_children():
        w.destroy()

    contenedor = tk.Frame(parent, bg="white")
    contenedor.pack(fill="both", expand=True)

    header = tk.Frame(contenedor, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="MATERIAS",
        bg="#d0e4f5",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    toolbar = tk.Frame(contenedor, bg="white")
    toolbar.pack(fill="x", padx=20, pady=5)

    ttk.Button(
        toolbar,
        text="Agregar",
        command=lambda: ventana_materia(parent, tree)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Modificar",
        command=lambda: modificar_materia(parent, tree)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Borrar",
        command=lambda: borrar_materia(parent, tree)
    ).pack(side="left", padx=5)

    tree = ttk.Treeview(
        contenedor,
        columns=("clave",),
        show="tree",
        height=12
    )

    tree.heading("#0", text="Materias")

    tree.column("#0", width=400)

    tree.pack(fill="both", expand=True, padx=20, pady=10)
    tree.bind("<Double-1>", lambda e: editar_si_materia(e, parent, tree))

    def editar_si_materia(event, parent, tree):

        item = tree.focus()

        if not item:
            return

        tags = tree.item(item, "tags")

        if "materia" in tags:
            modificar_materia(parent, tree)

    cargar_materias(tree)


# =====================================================
# CARGAR materias
# =====================================================
def cargar_materias(tree):

    tree.delete(*tree.get_children())

    filas = obtener_todos("""
        SELECT
            m.id,
            g.nombre,
            m.clave,
            m.nombre,
            COALESCE(e.nombre,'') AS especialidad
        FROM Materias m
        LEFT JOIN Grados g ON g.id = m.grupo_id
        LEFT JOIN Especialidades e ON e.id = m.especialidad_id
        ORDER BY g.orden, e.nombre, m.nombre
    """)

    grados = {}
    especialidades = {}

    for materia_id, grado, clave, nombre, especialidad in filas:

        # crear nodo grado
        if grado not in grados:

            grado_node = tree.insert(
                "",
                "end",
                text=grado,
                open=False,
                tags=("grado",)
            )

            grados[grado] = grado_node

        else:
            grado_node = grados[grado]

        # nodo especialidad
        if especialidad:

            key = (grado, especialidad)

            if key not in especialidades:

                espec_node = tree.insert(
                    grado_node,
                    "end",
                    text=especialidad,
                    open=False,
                    tags=("especialidad",)
                )

                especialidades[key] = espec_node

            else:
                espec_node = especialidades[key]

            parent = espec_node

        else:
            parent = grado_node

        tree.insert(
            parent,
            "end",
            iid=str(materia_id),
            text=f"{clave} - {nombre}",
            tags=("materia",)
        )


# =====================================================
# VENTANA AGREGAR / MODIFICAR
# =====================================================
def ventana_materia(parent, tree, datos=None):
    top = tk.Toplevel(parent)
    top.title("Modificar Materia" if datos else "Agregar Materia")
    top.geometry("350x330")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    top.resizable(False, False)

    cont = tk.Frame(top, padx=20, pady=20)
    cont.pack(fill="both", expand=True)

    # =========================
    # VARIABLES
    # =========================
    clave_var = tk.StringVar()
    nombre_var = tk.StringVar()
    grado_var = tk.StringVar()
    especialidad_var = tk.StringVar()

    # =========================
    # CLAVE
    # =========================
    tk.Label(cont, text="Clave de la materia:").pack(anchor="w")
    entry_clave = tk.Entry(cont, textvariable=clave_var)
    entry_clave.pack(fill="x", pady=5)

    # =========================
    # NOMBRE
    # =========================
    tk.Label(cont, text="Nombre de la materia:").pack(anchor="w")
    entry_nombre = tk.Entry(cont, textvariable=nombre_var)
    entry_nombre.pack(fill="x", pady=5)

    # Forzar mayúsculas
    def a_mayusculas(*args):
        clave_var.set(clave_var.get().upper())
        nombre_var.set(nombre_var.get().upper())

    clave_var.trace_add("write", a_mayusculas)
    nombre_var.trace_add("write", a_mayusculas)

    # =========================
    # GRADO
    # =========================
    tk.Label(cont, text="Grado:").pack(anchor="w")

    grados = obtener_todos("SELECT id, nombre FROM Grados ORDER BY id")
    grados_dict = {g[1]: g[0] for g in grados}

    cb_grado = ttk.Combobox(
        cont,
        textvariable=grado_var,
        state="readonly",
        values=list(grados_dict.keys())
    )
    cb_grado.pack(fill="x", pady=5)

    # =========================
    # ESPECIALIDAD
    # =========================
    tk.Label(cont, text="Especialidad:").pack(anchor="w")

    especialidades = obtener_todos("SELECT id, nombre FROM Especialidades ORDER BY nombre")
    especialidades_dict = {e[1]: e[0] for e in especialidades}

    opciones_especialidad = ["Ninguna"] + list(especialidades_dict.keys())

    cb_especialidad = ttk.Combobox(
        cont,
        textvariable=especialidad_var,
        state="readonly",
        values=opciones_especialidad
    )
    cb_especialidad.pack(fill="x", pady=5)

    cb_especialidad.set("Ninguna")

    # =========================
    # CARGAR DATOS SI ES MODIFICAR
    # =========================
    if datos:
        clave_var.set(datos["clave"])
        nombre_var.set(datos["nombre"])
        grado_var.set(datos["grado"])
        especialidad_var.set(datos["especialidad"] or "Ninguna")

    # =========================
    # GUARDAR
    # =========================
    def guardar():
        clave = clave_var.get().strip()
        nombre = nombre_var.get().strip()
        grado_nombre = grado_var.get()
        especialidad_nombre = especialidad_var.get()

        if not clave or not nombre or not grado_nombre:
            show_error(top, "Error", "Clave, nombre y grado son obligatorios.")
            return

        grado_id = grados_dict.get(grado_nombre)
        especialidad_id = None

        if especialidad_nombre != "Ninguna":
            especialidad_id = especialidades_dict.get(especialidad_nombre)

        if datos:  # MODIFICAR
            ejecutar_consulta("""
                UPDATE Materias
                    SET clave=?, nombre=?, grupo_id=?, especialidad_id=?
                WHERE id=?
            """, (clave, nombre, grado_id, especialidad_id, datos["id"]))
        else:  # AGREGAR
            ejecutar_consulta("""
                INSERT INTO Materias (clave, nombre, grupo_id, especialidad_id)
                VALUES (?, ?, ?, ?)
            """, (clave, nombre, grado_id, especialidad_id))

        cargar_materias(tree)
        top.destroy()

    # =========================
    # BOTONES
    # =========================
    btn_frame = tk.Frame(cont)
    btn_frame.pack(pady=20)

    ttk.Button(btn_frame, text="Guardar", command=guardar).pack(side="right", padx=5)
    ttk.Button(btn_frame, text="Cancelar", command=top.destroy).pack(side="right")

    # =========================
    # CENTRAR VENTANA
    # =========================
    top.update_idletasks()
    centrar_ventana(top, parent)

    # Atajos
    top.bind("<Return>", lambda e: guardar())
    top.bind("<Escape>", lambda e: top.destroy())


# =====================================================
# MODIFICAR
# =====================================================
def modificar_materia(parent, tree):
    seleccion = tree.selection()

    if not seleccion:
        show_error(parent, "Aviso", "Seleccione una materia.")
        return

    materia_id = seleccion[0]

    fila = obtener_todos("""
        SELECT 
            m.id,
            m.clave,
            m.nombre,
            g.nombre,
            e.nombre
        FROM Materias m
        LEFT JOIN Grados g ON g.id = m.grupo_id
        LEFT JOIN Especialidades e ON e.id = m.especialidad_id
        WHERE m.id = ?
    """, (materia_id,))

    if not fila:
        show_error(parent, "Error", "No se encontró la materia.")
        return

    datos = {
        "id": fila[0][0],
        "clave": fila[0][1],
        "nombre": fila[0][2],
        "grado": fila[0][3],
        "especialidad": fila[0][4]
    }

    ventana_materia(parent, tree, datos)


# =====================================================
# BORRAR
# =====================================================
def borrar_materia(parent, tree):
    seleccion = tree.selection()

    if not seleccion:
        show_error(parent, "Aviso", "Seleccione una materia.")
        return

    materia_id = seleccion[0]
    valores = tree.item(materia_id, "values")

    confirmar = ask_yes_no(
        parent,
        "Confirmar eliminación",
        f"¿Desea eliminar la materia?"
    )

    if not confirmar:
        return

    ejecutar_consulta(
        "DELETE FROM Materias WHERE id=?",
        (materia_id,)
    )

    cargar_materias(tree)



