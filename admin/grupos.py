from db.conexion import obtener_todos
from db.conexion import obtener_todos, ejecutar_consulta
import tkinter as tk
from tkinter import ttk, messagebox

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

    ttk.Button(
        win,
        text="Aceptar",
        command=win.destroy
    ).pack(pady=(0, 15))

    win.update_idletasks()

    w = win.winfo_width()
    h = win.winfo_height()

    x = root.winfo_rootx() + (root.winfo_width() // 2) - (w // 2)
    y = root.winfo_rooty() + (root.winfo_height() // 2) - (h // 2)

    win.geometry(f"{w}x{h}+{x}+{y}")

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

    w = win.winfo_width()
    h = win.winfo_height()

    x = root.winfo_rootx() + (root.winfo_width() // 2) - (w // 2)
    y = root.winfo_rooty() + (root.winfo_height() // 2) - (h // 2)

    win.geometry(f"{w}x{h}+{x}+{y}")

    win.wait_window()
    return respuesta["valor"]


def cargar_grupos(tree):
    tree.delete(*tree.get_children())

    grados = obtener_todos("""
        SELECT id, nombre
        FROM grados
        ORDER BY orden
    """)

    for grado_id, grado_nombre in grados:
        # Nodo padre → GRADO (columna Grado)
        nodo_grado = tree.insert(
            "",
            "end",
            text=grado_nombre,
            open=False
        )

        grupos = obtener_todos("""
            SELECT id, grupo
            FROM grupos
            WHERE grado_id=?
            ORDER BY grupo
        """, (grado_id,))

        for grupo_id, grupo in grupos:
            # Nodo hijo → GRUPO (columna Grupo)
            tree.insert(
                nodo_grado,
                "end",
                values=(grupo,),
                iid=f"grupo_{grupo_id}"
            )


def ventana_grupo(parent, tree, datos=None):
    top = tk.Toplevel(parent)
    top.title("Grupo")
    top.geometry("260x180")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    top.resizable(False, False)

    centrar_ventana(top, parent)

    cont = tk.Frame(top, padx=25, pady=20)
    cont.pack(fill="both", expand=True)

    # =========================
    # GRADO
    # =========================
    tk.Label(cont, text="Grado:").grid(row=0, column=0, sticky="w", pady=8)

    grados = obtener_todos("SELECT id, nombre FROM grados ORDER BY orden")
    grado_map = {g[1]: g[0] for g in grados}

    cb_grado = ttk.Combobox(
        cont,
        values=list(grado_map.keys()),
        state="readonly",
        width=25
    )
    cb_grado.grid(row=0, column=1, sticky="w", pady=8)

    # =========================
    # GRUPO
    # =========================
    tk.Label(cont, text="Grupo:").grid(row=1, column=0, sticky="w", pady=8)
    entry_grupo = tk.Entry(cont, width=28)
    entry_grupo.grid(row=1, column=1, sticky="w", pady=8)
    # =========================
    # CARGAR DATOS
    # =========================
    if datos:
        cb_grado.set(datos["grado"])
        entry_grupo.insert(0, datos["grupo"])

    # =========================
    # BOTONES
    # =========================
    acciones = tk.Frame(cont)
    acciones.grid(row=3, column=0, columnspan=2, pady=20)

    def guardar():
        grado_nombre = cb_grado.get()
        grupo = entry_grupo.get().strip()

        if not grado_nombre or not grupo:
            show_error(
                top,
                "Error",
                "Todos los campos son obligatorios."
            )
            return

        grado_id = grado_map[grado_nombre]

        if datos:
            ejecutar_consulta(
                """
                UPDATE grupos
                SET grado_id=?, grupo=?
                WHERE id=?
                """,
                (grado_id, grupo, datos["id"])
            )
        else:
            ejecutar_consulta(
                """
                INSERT INTO grupos (grado_id, grupo)
                VALUES (?, ?)
                """,
                (grado_id, grupo)
            )

        cargar_grupos(tree)
        top.destroy()

    top.bind("<Return>", lambda e: guardar())
    ttk.Button(acciones, text="Guardar", command=guardar).pack(side="right", padx=6)
    ttk.Button(acciones, text="Cancelar", command=top.destroy).pack(side="right")

def modificar_grupo(parent, tree):
    sel = tree.selection()
    if not sel:
        show_error(parent, "Error", "Seleccione un grupo.")
        return

    item = sel[0]
    parent_item = tree.parent(item)

    # 🚫 No permitir modificar un grado
    if parent_item == "":
        show_error(parent, "Aviso", "Seleccione un grupo, no un grado.")
        return

    grupo_id = int(item.replace("grupo_", ""))
    grupo = tree.item(item, "values")[0]
    grado = tree.item(parent_item, "text")

    datos = {
        "id": grupo_id,
        "grado": grado,
        "grupo": grupo
    }

    ventana_grupo(parent, tree, datos)


def borrar_grupo(parent, tree):
    sel = tree.selection()
    if not sel:
        show_error(parent, "Aviso", "Seleccione un grupo.")
        return

    item = sel[0]
    parent_item = tree.parent(item)

    if parent_item == "":
        show_error(parent, "Aviso", "Seleccione un grupo, no un grado.")
        return

    grupo_id = int(item.replace("grupo_", ""))
    grupo = tree.item(item, "values")[0]
    grado = tree.item(parent_item, "text")

    if not ask_yes_no(
        parent,
        "Confirmar",
        f"¿Eliminar el grupo {grado} / {grupo}?"
    ):
        return

    ejecutar_consulta(
        "DELETE FROM grupos WHERE id=?",
        (grupo_id,)
    )

    cargar_grupos(tree)


def mostrar_grupos(parent):
    for w in parent.winfo_children():
        w.destroy()

    contenedor = tk.Frame(parent, bg="white")
    contenedor.pack(fill="both", expand=True)

    header = tk.Frame(contenedor, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="ADMINISTRACIÓN DE GRUPOS",
        bg="#d0e4f5",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    toolbar = tk.Frame(contenedor, bg="white")
    toolbar.pack(fill="x", padx=20, pady=5)

    ttk.Button(
        toolbar,
        text="Agregar",
        command=lambda: ventana_grupo(parent, tree)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Modificar",
        command=lambda: modificar_grupo(parent, tree)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Borrar",
        command=lambda: borrar_grupo(parent, tree)
    ).pack(side="left", padx=5)

    tree = ttk.Treeview(contenedor, columns=("grupo",), show="tree headings", height=12)

    tree.heading("#0", text="Grado")
    tree.heading("grupo", text="Grupo")

    tree.column("#0", width=100)
    tree.column("grupo", width=120, anchor="center")

    tree.pack(fill="both", expand=True, padx=20, pady=10)
    tree.bind("<Double-1>", lambda e: modificar_grupo(parent, tree))

    cargar_grupos(tree)
