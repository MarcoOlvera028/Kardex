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
def mostrar_estado(parent, ciclo_activo):
    for w in parent.winfo_children():
        w.destroy()

    contenedor = tk.Frame(parent, bg="white")
    contenedor.pack(fill="both", expand=True)

    header = tk.Frame(contenedor, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="ESTADO ACADÉMICO",
        bg="#d0e4f5",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    tree = ttk.Treeview(
        contenedor,
        columns=("clave", "nombre", "especialidad"),
        show="tree headings"
    )

    tree.heading("#0", text="Grupo")
    tree.heading("clave", text="Clave")
    tree.heading("nombre", text="Nombre")
    tree.heading("especialidad", text="Especialidad")

    tree.column("#0", width=160)
    tree.column("clave", width=120)
    tree.column("nombre", width=220)
    tree.column("especialidad", width=200)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    tree.bind("<Double-1>", lambda e: abrir_materia_estado(tree, ciclo_id=ciclo_activo))

    cargar_materias_agrupadas(tree)


def cargar_materias_agrupadas(tree):
    tree.delete(*tree.get_children())

    filas = obtener_todos("""
        SELECT
            g.id,
            g.nombre,
            m.id,
            m.clave,
            m.nombre,
            COALESCE(e.nombre, '')
        FROM Materias m
        LEFT JOIN Grados g ON g.id = m.grupo_id
        LEFT JOIN Especialidades e ON e.id = m.especialidad_id
        ORDER BY g.id, m.nombre
    """)

    grupos = {}

    for fila in filas:
        grado_id = fila[0]
        grado_nombre = fila[1]
        materia_id = fila[2]
        clave = fila[3]
        nombre = fila[4]
        especialidad = fila[5]

        # Crear nodo padre si no existe
        if grado_id not in grupos:
            nodo_grupo = tree.insert(
                "",
                "end",
                iid=f"grupo_{grado_id}",
                text=grado_nombre,
                open=False
            )
            grupos[grado_id] = nodo_grupo

        # Insertar materia como hijo
        tree.insert(
            grupos[grado_id],
            "end",
            iid=f"materia_{materia_id}",
            text="",
            values=(clave, nombre, especialidad)
        )


def abrir_materia_estado(tree, ciclo_id):
    seleccion = tree.selection()
    if not seleccion:
        return

    item_id = seleccion[0]

    if not item_id.startswith("materia_"):
        return

    materia_id = item_id.replace("materia_", "")
    ventana_asignar_alumnos(tree, materia_id, ciclo_id)


def abrir_ventana_detalle_materia(tree, materia_id):
    fila = obtener_todos("""
        SELECT 
            m.clave,
            m.nombre,
            COALESCE(e.nombre, '')
        FROM Materias m
        LEFT JOIN Especialidades e ON e.id = m.especialidad_id
        WHERE m.id = ?
    """, (materia_id,))

    if not fila:
        return

    top = tk.Toplevel()
    top.title("Detalle de Materia")
    top.geometry("400x250")
    top.grab_set()

    tk.Label(top, text=f"Clave: {fila[0][0]}").pack(pady=10)
    tk.Label(top, text=f"Nombre: {fila[0][1]}").pack(pady=10)
    tk.Label(top, text=f"Especialidad: {fila[0][2]}").pack(pady=10)


def ventana_asignar_alumnos(parent, materia_id, ciclo_id):

    top = tk.Toplevel(parent.winfo_toplevel())
    top.title("Asignar alumnos a materia")
    top.geometry("600x520")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    top.resizable(False, False)

    # Centrar ventana
    top.update_idletasks()
    x = (top.winfo_screenwidth() // 2) - (600 // 2)
    y = (top.winfo_screenheight() // 2) - (520 // 2)
    top.geometry(f"600x520+{x}+{y}")

    cont = tk.Frame(top, padx=20, pady=15)
    cont.pack(fill="both", expand=True)

    # =========================
    # OBTENER GRUPO
    # =========================
    grupo_id = obtener_todos("""
        SELECT grupo_id FROM Materias WHERE id = ?
    """, (materia_id,))[0][0]

    grupo_nombre = obtener_todos("""
        SELECT nombre FROM Grados WHERE id = ?
    """, (grupo_id,))[0][0]

    ciclo_id = ciclo_id["id"]

    # =========================
    # ENCABEZADO
    # =========================
    tk.Label(
        cont,
        text=f"Grupo: {grupo_nombre}",
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w")

    # =========================
    # BUSCADOR
    # =========================
    buscador_frame = tk.Frame(cont)
    buscador_frame.pack(fill="x", pady=(10, 5))

    tk.Label(buscador_frame, text="Buscar alumno:").pack(side="left")

    buscar_var = tk.StringVar()
    entry_buscar = tk.Entry(buscador_frame, textvariable=buscar_var)
    entry_buscar.pack(side="left", fill="x", expand=True, padx=5)

    # =========================
    # OBTENER ALUMNOS DEL GRUPO + CICLO
    # =========================
    alumnos = obtener_todos("""
        SELECT e.id, e.nombre
        FROM Estudiantes e
        JOIN DatosEscolares d ON d.estudiante_id = e.id
        WHERE d.grupo LIKE ?
        AND d.ciclo_id = ?
        ORDER BY e.nombre
    """, (grupo_nombre + "%", ciclo_id))

    # =========================
    # OBTENER LOS YA INSCRITOS EN LA MATERIA
    # =========================
    inscritos = obtener_todos("""
        SELECT alumno_id
        FROM EstadoAcademico
        WHERE materia_id = ?
        AND ciclo_id = ?
    """, (materia_id, ciclo_id))

    inscritos_ids = {fila[0] for fila in inscritos}

    # =========================
    # LISTA SCROLL
    # =========================
    lista_frame = tk.Frame(cont)
    lista_frame.pack(fill="both", expand=True, pady=5)

    canvas = tk.Canvas(lista_frame)
    scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=canvas.yview)
    frame_check = tk.Frame(canvas)

    frame_check.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=frame_check, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    checks = {}

    def cargar_lista(filtro=""):
        for widget in frame_check.winfo_children():
            widget.destroy()

        for alumno_id, nombre in alumnos:
            if filtro.lower() in nombre.lower():

                var = tk.BooleanVar()

                # 🔥 MARCAR SI YA ESTÁ INSCRITO
                if alumno_id in inscritos_ids:
                    var.set(True)

                chk = tk.Checkbutton(
                    frame_check,
                    text=nombre,
                    variable=var,
                    anchor="w"
                )
                chk.pack(fill="x", anchor="w")

                checks[alumno_id] = var

    cargar_lista()

    def filtrar(*args):
        cargar_lista(buscar_var.get())

    buscar_var.trace_add("write", filtrar)

    # =========================
    # BOTONES EXTRA
    # =========================
    extras = tk.Frame(cont)
    extras.pack(fill="x", pady=(5, 0))

    def seleccionar_todos():
        for var in checks.values():
            var.set(True)

    def deseleccionar_todos():
        for var in checks.values():
            var.set(False)

    tk.Button(extras, text="Deseleccionar todos", command=deseleccionar_todos).pack(side="left")
    tk.Button(extras, text="Seleccionar todos", command=seleccionar_todos).pack(side="left", padx=5)

    # =========================
    # BOTONES INFERIORES
    # =========================
    botones = tk.Frame(cont)
    botones.pack(fill="x", pady=(10, 0))

    def guardar():
        for alumno_id, var in checks.items():

            if var.get():
                # INSERTAR SI NO EXISTE
                ejecutar_consulta("""
                    INSERT OR IGNORE INTO EstadoAcademico
                    (alumno_id, materia_id, ciclo_id)
                    VALUES (?, ?, ?)
                """, (alumno_id, materia_id, ciclo_id))

            else:
                # ELIMINAR SI EXISTE
                ejecutar_consulta("""
                    DELETE FROM EstadoAcademico
                    WHERE alumno_id = ?
                    AND materia_id = ?
                    AND ciclo_id = ?
                """, (alumno_id, materia_id, ciclo_id))

        top.destroy()

    tk.Button(botones, text="Guardar", width=12, command=guardar).pack(side="right", padx=5)
    tk.Button(botones, text="Cancelar", width=12, command=top.destroy).pack(side="right")

def guardar_asignaciones(materia_id, ciclo_id, checks, ventana):

    # Si ciclo_id es diccionario, extraemos el id real
    if isinstance(ciclo_id, dict):
        ciclo_id = ciclo_id["id"]

    for alumno_id, var in checks.items():

        if var.get():
            try:
                ejecutar_consulta("""
                    INSERT INTO EstadoAcademico (
                        alumno_id,
                        materia_id,
                        ciclo_id
                    )
                    VALUES (?, ?, ?)
                """, (alumno_id, materia_id, ciclo_id))
            except Exception as e:
                print("Error insertando:", e)
                pass

    ventana.destroy()


