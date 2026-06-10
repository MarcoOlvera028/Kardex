# vistas/alumnos.py
import tkinter as tk
from tkinter import ttk
from db.conexion import obtener_conexion, obtener_todos, ejecutar_consulta
from tkinter import ttk, messagebox

# =====================================================
# MOSTRAR INSCRIPCIONES
# =====================================================
def mostrar_calificaciones(contenido, ciclo_activo):
    # Validar ciclo activo
    if not ciclo_activo["id"]:
        messagebox.showwarning(
            "Ciclo no seleccionado",
            "Debe seleccionar un ciclo escolar para ver las materias."
        )
        return
    
    # limpiar vista previa
    for w in contenido.winfo_children():
        w.destroy()

    # --- TÍTULO ALUMNOS ---
    
    header = tk.Frame(contenido, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="ORDINARIO",
        bg="#d0e4f5",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)



    # --- BUSCADOR ---
    top = tk.Frame(contenido, bg="white")
    top.pack(fill="x", padx=20, pady=(20, 0))

    tk.Label(top, text="Buscar:", bg="white").pack(side="left", padx=(0,8))
    entry_buscar = tk.Entry(top, bd=1, relief="solid")
    entry_buscar.pack(side="left", padx=(0,8))

    btn_buscar = tk.Button(top, text="Buscar")
    btn_buscar.pack(side="left")

    btn_limpiar = tk.Button(top, text="Mostrar todos")
    btn_limpiar.pack(side="left", padx=(8,0))

    # --- TABLA ---
    table_frame = tk.Frame(contenido, bg="white")
    table_frame.pack(fill="both", expand=True, padx=20, pady=20)

    columnas = ("info",)

    tabla = ttk.Treeview(
        table_frame,
        columns=columnas,
        show="tree"
    )

    tabla.pack(fill="both", expand=True)

    # SCROLLBARS VERTICAL + HORIZONTAL
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)

    vsb.pack(side="right", fill="y")
    tabla.pack(side="left", fill="both", expand=True)

    # FUNCIÓN: CARGAR DATOS
    def cargar_estructura(filtro=""):
        tabla.delete(*tabla.get_children())

        conn = obtener_conexion()
        cur = conn.cursor()

        # 1️⃣ Obtener grados
        cur.execute("SELECT id, nombre FROM Grados ORDER BY id")
        grados = cur.fetchall()

        for grado_id, grado_nombre in grados:

            grado_node = tabla.insert(
                "",
                "end",
                text=f"{grado_nombre}",
                open=False
            )

            # 2️⃣ Obtener grupos del grado
            cur.execute("""
                SELECT id, grupo
                FROM Grupos
                WHERE grado_id = ?
                ORDER BY grupo
            """, (grado_id,))
            grupos = cur.fetchall()

            if grado_nombre in ("Quinto", "Sexto"):
                cur.execute("""
                    SELECT id, nombre, especialidad_id
                    FROM Materias
                    WHERE grupo_id = ?
                    AND nombre LIKE ?
                    ORDER BY nombre
                """, (grado_id, f"%{filtro}%"))

                materias = cur.fetchall()

            else:
                cur.execute("""
                    SELECT id, nombre, orden
                    FROM Materias
                    WHERE grupo_id = ?
                    AND nombre LIKE ?
                    ORDER BY orden
                """, (grado_id, f"%{filtro}%"))

                materias = [(m[0], m[1], None) for m in cur.fetchall()]



            mapa_especialidad = {
                "501": 1,
                "502": 2,
                "503": 3
            }

            for grupo_id, grupo_nombre in grupos:

                grupo_node = tabla.insert(
                    grado_node,
                    "end",
                    text=f"Grupo {grupo_nombre}",
                    open=False
                )

                # Insertar todas las materias del grado en cada grupo
                for materia_id, materia_nombre, especialidad_id in materias:
                    if grado_nombre in ("Quinto", "Sexto"):

                        esp_grupo = mapa_especialidad.get(grupo_nombre)

                        if especialidad_id != esp_grupo:
                            continue

                    tabla.insert(
                        grupo_node,
                        "end",
                        text=materia_nombre,
                        tags=(f"materia_{materia_id}",)
                    )

        conn.close()


    def on_double_click(event):
        item = tabla.focus()
        if not item:
            return

        tags = tabla.item(item, "tags")

        if not tags:
            return

        tag = tags[0]

        # Si es materia
        if tag.startswith("materia_"):
            materia_id = int(tag.split("_")[1])

            # Obtener grupo padre
            grupo_item = tabla.parent(item)
            grupo_text = tabla.item(grupo_item, "text")

            # Obtener grado padre
            grado_item = tabla.parent(grupo_item)
            grado_text = tabla.item(grado_item, "text")

            ventana_calificaciones_materia(
                tabla,
                materia_id,
                grado_text,
                grupo_text,
                ciclo_activo["id"]
            )

    # EVENTOS DE BÚSQUEDA
    btn_buscar.config(command=lambda: cargar_estructura(entry_buscar.get()))
    entry_buscar.bind("<Return>", lambda e: cargar_estructura(entry_buscar.get()))
    btn_limpiar.config(command=lambda: (entry_buscar.delete(0, tk.END), cargar_estructura()))

    tabla.bind("<Double-1>", on_double_click)

    # Cargar datos iniciales
    cargar_estructura()


def ventana_calificaciones_materia(parent, materia_id, grado, grupo, ciclo_id):

    top = tk.Toplevel(parent.winfo_toplevel())
    top.title("Calificaciones por Materia")
    top.geometry("800x550")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    top.resizable(False, False)

    top.update_idletasks()

    width = 850
    height = 650

    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)

    top.geometry(f"{width}x{height}+{x}+{y}")

    cont = tk.Frame(top, padx=20, pady=20, bg="#f0f0f0")
    cont.pack(fill="both", expand=True)

    # =========================
    # ENCABEZADO SUPERIOR
    # =========================
    header = tk.Frame(cont, bg="#f0f0f0")
    header.pack(fill="x", pady=(0, 15))

    materia_nombre = obtener_todos(
        "SELECT nombre FROM Materias WHERE id = ?",
        (materia_id,)
    )[0][0]

    # Quitar palabra "Grupo"
    grupo_limpio = grupo.replace("Grupo ", "")

    # Obtener nombre del ciclo
    ciclo_nombre = obtener_todos(
        "SELECT ciclo FROM ciclos WHERE id = ?",
        (ciclo_id,)
    )[0][0]

    # Título grande
    tk.Label(
        header,
        text=f"{materia_nombre}",
        font=("Segoe UI", 16, "bold"),
        bg="#f0f0f0"
    ).pack(anchor="w")

    # Subinfo en línea
    info_frame = tk.Frame(header, bg="#f0f0f0")
    info_frame.pack(fill="x", pady=(5, 0))

    tk.Label(
        info_frame,
        text=f"Grado/Grupo: {grado} / {grupo_limpio}",
        font=("Segoe UI", 10),
        bg="#f0f0f0"
    ).pack(side="left")

    tk.Label(
        info_frame,
        text=f"Ciclo: {ciclo_nombre}",
        font=("Segoe UI", 10),
        bg="#f0f0f0"
    ).pack(side="right")

    ttk.Separator(cont, orient="horizontal").pack(fill="x", pady=10)

    grupo_completo = f"{grado}/{grupo_limpio}"
    # =========================
    # OBTENER ALUMNOS DE ESA MATERIA
    # =========================
    alumnos = obtener_todos("""
        SELECT 
            ea.id,
            e.nombre,
            e.apellido_paterno,
            e.apellido_materno,
            ea.parcial1,
            ea.parcial2,
            ea.parcial3,
            ea.final
        FROM EstadoAcademico ea
        JOIN Estudiantes e ON e.id = ea.alumno_id
        JOIN DatosEscolares de ON de.estudiante_id = ea.alumno_id
        WHERE ea.materia_id = ?
        AND ea.ciclo_id = ? AND de.ciclo_id=? AND de.grupo = ?
        ORDER BY e.nombre
    """, (materia_id, ciclo_id, ciclo_id, grupo_completo))


    tabla_container = tk.Frame(cont, bg="white")
    tabla_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(tabla_container, bg="white", highlightthickness=0)
    scrollbar = ttk.Scrollbar(tabla_container, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg="white")

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=frame, anchor="nw")
    def ajustar_ancho(event):
        canvas.itemconfig("all", width=event.width)

    canvas.bind("<Configure>", ajustar_ancho)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _bind_mousewheel(event):
        canvas.bind("<MouseWheel>", _on_mousewheel)

    def _unbind_mousewheel(event):
        canvas.unbind("<MouseWheel>")
    
    canvas.bind("<Enter>", _bind_mousewheel)
    canvas.bind("<Leave>", _unbind_mousewheel)

    frame.bind("<Enter>", _bind_mousewheel)
    frame.bind("<Leave>", _unbind_mousewheel)

    entradas = {}

    # =========================
    # BLOQUES POR ALUMNO
    # =========================
    for ea_id, nombre, ap, am, p1, p2, p3, final in alumnos:

        bloque = tk.Frame(frame, bg="white", bd=1, relief="solid", padx=10, pady=10)
        bloque.pack(fill="x", pady=5)

        nombre_completo = f"{nombre} {ap} {am}"

        tk.Label(bloque, text=nombre_completo, font=("Segoe UI", 11, "bold"), bg="white").grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))

        p1_var = tk.StringVar(value="" if p1 is None else str(p1))
        p2_var = tk.StringVar(value="" if p2 is None else str(p2))
        p3_var = tk.StringVar(value="" if p3 is None else str(p3))
        final_var = tk.StringVar(value="" if final is None else str(final))

        tk.Label(bloque, text="Primer Parcial").grid(row=1, column=0)
        tk.Entry(bloque, width=6, textvariable=p1_var).grid(row=1, column=1)

        tk.Label(bloque, text="Segundo Parcial").grid(row=1, column=2)
        tk.Entry(bloque, width=6, textvariable=p2_var).grid(row=1, column=3)

        tk.Label(bloque, text="Tercer Parcial").grid(row=1, column=4)
        tk.Entry(bloque, width=6, textvariable=p3_var).grid(row=1, column=5)

        tk.Label(bloque, text="Final").grid(row=1, column=6)
        tk.Entry(bloque, width=6, textvariable=final_var).grid(row=1, column=7)

        entradas[ea_id] = (p1_var, p2_var, p3_var, final_var)

    # =========================
    # BOTONES
    # =========================
    btn_frame = tk.Frame(top, bg="white")
    btn_frame.pack(side="bottom", pady=15)

    def guardar():
        for ea_id, vars_tuple in entradas.items():
            p1, p2, p3, final = vars_tuple

            ejecutar_consulta("""
                UPDATE EstadoAcademico
                SET parcial1 = ?,
                    parcial2 = ?,
                    parcial3 = ?,
                    final = ?
                WHERE id = ?
            """, (
                p1.get() or None,
                p2.get() or None,
                p3.get() or None,
                final.get() or None,
                ea_id
            ))

        top.destroy()

    btn_guardar = ttk.Button(btn_frame, text="Guardar", width=15, command=guardar)
    btn_guardar.pack(side="right")

    btn_cancelar = ttk.Button(btn_frame, text="Cancelar", width=15, command=top.destroy)
    btn_cancelar.pack(side="right")
    





