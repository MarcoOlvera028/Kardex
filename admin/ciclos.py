import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from db.conexion import obtener_todos, ejecutar_consulta
from alumnado.datepicker import DatePicker


def messagebox_centrado(parent, tipo, titulo, mensaje):
    temp = tk.Toplevel(parent)
    temp.withdraw()
    temp.transient(parent)
    temp.grab_set()

    parent.update_idletasks()

    x = parent.winfo_rootx() + parent.winfo_width() // 2
    y = parent.winfo_rooty() + parent.winfo_height() // 2
    temp.geometry(f"+{x}+{y}")

    if tipo == "error":
        messagebox.showerror(titulo, mensaje, parent=temp)
    elif tipo == "warning":
        messagebox.showwarning(titulo, mensaje, parent=temp)
    elif tipo == "info":
        messagebox.showinfo(titulo, mensaje, parent=temp)
    elif tipo == "askyesno":
        res = messagebox.askyesno(titulo, mensaje, parent=temp)
        temp.destroy()
        return res

    temp.destroy()


# =====================================================
# PANTALLA PRINCIPAL
# =====================================================
def mostrar_ciclos(parent, ciclo_activo):
    for w in parent.winfo_children():
        w.destroy()

    contenedor = tk.Frame(parent, bg="white")
    contenedor.pack(fill="both", expand=True)

    header = tk.Frame(contenedor, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="ADMINISTRACIÓN DE CICLOS",
        bg="#d0e4f5",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    # BOTONES
    toolbar = tk.Frame(contenedor, bg="white")
    toolbar.pack(fill="x", padx=20, pady=5)

    ttk.Button(
        toolbar,
        text="Agregar",
        command=lambda: ventana_ciclo(parent, tree, ciclo_activo=ciclo_activo)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Modificar",
        command=lambda: modificar_ciclo(parent, tree, ciclo_activo=ciclo_activo)
    ).pack(side="left", padx=5)

    ttk.Button(
        toolbar,
        text="Borrar",
        command=lambda: borrar_ciclo(parent, tree)
    ).pack(side="left", padx=5)

    # TABLA
    columnas = ("id", "ciclo", "inicio", "fin", "status")
    tree = ttk.Treeview(contenedor, columns=columnas, show="headings", height=12)

    tree.heading("id", text="ID")
    tree.heading("ciclo", text="Ciclo")
    tree.heading("inicio", text="Inicio")
    tree.heading("fin", text="Fin")
    tree.heading("status", text="Status")

    tree.column("id", width=50, anchor="center")
    tree.column("ciclo", width=240)
    tree.column("inicio", width=100, anchor="center")
    tree.column("fin", width=100, anchor="center")
    tree.column("status", width=120, anchor="center")


    tree.pack(fill="both", expand=True, padx=20, pady=10)
    tree.bind("<Double-1>", lambda e: modificar_ciclo(parent, tree, ciclo_activo))


    cargar_ciclos(tree)

def messagebox_centrado(parent, tipo, titulo, mensaje):
    temp = tk.Toplevel(parent)
    temp.withdraw()
    temp.transient(parent)
    temp.grab_set()

    parent.update_idletasks()

    x = parent.winfo_rootx() + parent.winfo_width() // 2
    y = parent.winfo_rooty() + parent.winfo_height() // 2
    temp.geometry(f"+{x}+{y}")

    if tipo == "error":
        messagebox.showerror(titulo, mensaje, parent=temp)
    elif tipo == "warning":
        messagebox.showwarning(titulo, mensaje, parent=temp)
    elif tipo == "info":
        messagebox.showinfo(titulo, mensaje, parent=temp)
    elif tipo == "askyesno":
        res = messagebox.askyesno(titulo, mensaje, parent=temp)
        temp.destroy()
        return res

    temp.destroy()

# =====================================================
def cargar_ciclos(tree):
    tree.delete(*tree.get_children())

    filas = obtener_todos(
        "SELECT id, ciclo, inicio, fin, status FROM ciclos ORDER BY id ASC"
    )

    for f in filas:
        tree.insert("", "end", values=f)



# =====================================================
# VENTANA AGREGAR / MODIFICAR
# =====================================================
def ventana_ciclo(parent, tree, ciclo_activo, datos=None):
    top = tk.Toplevel(parent)
    top.title("Ciclo escolar")
    top.geometry("280x250")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    top.resizable(False, False)

    centrar_ventana(top, parent)

    cont = tk.Frame(top, padx=25, pady=20)
    cont.pack(fill="both", expand=True)
    cont.columnconfigure(0, weight=0)
    cont.columnconfigure(1, weight=1)


    # ==============================
    # FILA 0 - CICLO
    # ==============================
    tk.Label(cont, text="Ciclo:").grid(row=0, column=0, sticky="w", pady=8)
    entry_ciclo = tk.Entry(cont, width=32)
    entry_ciclo.grid(row=0, column=1, sticky="w", pady=8)

    if datos:
        # ==============================
        # FILA 1 - INICIO
        # ==============================
        tk.Label(cont, text="Inicio:").grid(row=1, column=0, sticky="w", pady=8)
        dp_inicio = DatePicker(cont)
    
        dp_inicio.grid(row=1, column=1, sticky="w", pady=8)

        # ==============================
        # FILA 2 - FIN
        # ==============================
        tk.Label(cont, text="Fin:").grid(row=2, column=0, sticky="w", pady=8)
        dp_fin = DatePicker(cont)
        dp_fin.grid(row=2, column=1, sticky="w", pady=8)
    else:
        # ==============================
        # FILA 1 - INICIO
        # ==============================
        tk.Label(cont, text="Inicio:").grid(row=1, column=0, sticky="w", pady=8)
        dp_inicio = DatePicker(cont, initial=date.today())
    
        dp_inicio.grid(row=1, column=1, sticky="w", pady=8)

        # ==============================
        # FILA 2 - FIN
        # ==============================
        tk.Label(cont, text="Fin:").grid(row=2, column=0, sticky="w", pady=8)
        dp_fin = DatePicker(cont, initial=date.today())
        dp_fin.grid(row=2, column=1, sticky="w", pady=8)

    # ==============================
    # FILA 3 - STATUS
    # ==============================
    tk.Label(cont, text="Status:").grid(row=3, column=0, sticky="w", pady=8)

    status_var = tk.StringVar(value="Desmontado")

    frame_status = tk.Frame(cont)
    frame_status.grid(row=3, column=1, sticky="w", pady=8)

    tk.Radiobutton(
        frame_status,
        text="Montado",
        variable=status_var,
        value="Montado"
    ).pack(side="left", padx=5)

    tk.Radiobutton(
        frame_status,
        text="Desmontado",
        variable=status_var,
        value="Desmontado"
    ).pack(side="left", padx=5)

    # ==============================
    # CARGAR DATOS SI ES MODIFICAR
    # ==============================
    if datos:
        entry_ciclo.insert(0, datos["ciclo"])
        dp_inicio.entry.insert(0, datos["inicio"])
        dp_fin.entry.insert(0, datos["fin"])
        status_var.set(datos["status"])

    # ==============================
    # BOTONES
    # ==============================
    acciones = tk.Frame(cont)
    acciones.grid(row=5, column=0, columnspan=2, pady=20)

    def guardar():
        ciclo = entry_ciclo.get().strip()
        inicio = dp_inicio.get_text()
        fin = dp_fin.get_text()
        status = status_var.get()

        if not ciclo or not inicio or not fin:
            messagebox_centrado(
                top,
                "error",
                "Operación no permitida",
                "Todos los campos son obligatorios."
            )
            return

        if datos:
            # 🚫 NO permitir desmontar el ciclo activo
            if datos["id"] == ciclo_activo["id"] and status == "Desmontado":
                messagebox_centrado(
                    top,
                    "error",
                    "Operación no permitida",
                    "No se puede desmontar un ciclo activo."
                )
                return

            ejecutar_consulta(
                """
                UPDATE ciclos
                SET ciclo=?, inicio=?, fin=?, status=?
                WHERE id=?
                """,
                (ciclo, inicio, fin, status, datos["id"])
            )
        else:
            ejecutar_consulta(
                """
                INSERT INTO ciclos (ciclo, inicio, fin, status)
                VALUES (?, ?, ?, ?)
                """,
                (ciclo, inicio, fin, status)
            )

        cargar_ciclos(tree)
        top.destroy()

    ttk.Button(acciones, text="Guardar", command=guardar).pack(side="right", padx=6)
    ttk.Button(acciones, text="Cancelar", command=top.destroy).pack(side="right")


# =====================================================
def modificar_ciclo(parent, tree, ciclo_activo):
    sel = tree.selection()
    if not sel:
        messagebox_centrado(
            parent,
            "warning",
            "Aviso",
            "Seleccione un ciclo."
        )
        return

    valores = tree.item(sel[0], "values")

    datos = {
        "id": valores[0],
        "ciclo": valores[1],
        "inicio": valores[2],
        "fin": valores[3],
        "status": valores[4]
    }

    ventana_ciclo(parent, tree, ciclo_activo, datos)



# =====================================================
def borrar_ciclo(parent, tree):
    sel = tree.selection()
    if not sel:
        messagebox_centrado(
            parent,
            "warning",
            "Aviso",
            "Seleccione un ciclo."
        )
        return

    valores = tree.item(sel[0], "values")
    ciclo_id = valores[0]
    ciclo_nombre = valores[1]
    status = valores[4]

    if status == "Montado":
        messagebox_centrado(
            parent,
            "error",
            "Acción no permitida",
            "No se puede borrar un ciclo que está Montado."
        )
        return

    if not messagebox_centrado(
        parent,
        "askyesno",
        "Confirmar",
        f"¿Eliminar el ciclo '{ciclo_nombre}'?"
    ):
        return

    ejecutar_consulta("DELETE FROM ciclos WHERE id=?", (ciclo_id,))
    cargar_ciclos(tree)



# =====================================================
def centrar_ventana(win, parent):
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()

    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)

    win.geometry(f"{w}x{h}+{x}+{y}")
