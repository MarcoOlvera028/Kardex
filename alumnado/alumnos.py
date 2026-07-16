# vistas/alumnos.py
import tkinter as tk
from tkinter import ttk
from db.conexion import obtener_conexion, obtener_todos
from .ficha_alumno import mostrar_ficha_alumno
from tkinter import ttk, messagebox

# =====================================================
# MOSTRAR INSCRIPCIONES
# =====================================================
def mostrar_alumnos(contenido, ciclo_activo):
    # Validar ciclo activo
    if not ciclo_activo["id"]:
        messagebox.showwarning(
            "Ciclo no seleccionado",
            "Debe seleccionar un ciclo escolar para ver alumnos."
        )
        return
    """Renderiza la vista de lista de alumnos dentro del frame 'contenido'."""
    
    # limpiar vista previa
    for w in contenido.winfo_children():
        w.destroy()

    # --- TÍTULO ALUMNOS ---
    
    header = tk.Frame(contenido, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="ALUMNOS",
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

    columnas = ("id", "apellido_paterno", "apellido_materno", "nombre", 
                "grupo", "especialidad")

    tabla = ttk.Treeview(
        table_frame,
        columns=columnas,
        show="headings"
    )

    # Encabezados
    tabla.heading("id", text="Matrícula")
    tabla.heading("apellido_paterno", text="Apellido Paterno")
    tabla.heading("apellido_materno", text="Apellido Materno")
    tabla.heading("nombre", text="Nombre")
    tabla.heading("grupo", text="Grupo")
    tabla.heading("especialidad", text="Especialidad")

    # Tamaños iniciales
    tabla.column("id", width=100, anchor="center")
    tabla.column("apellido_paterno", width=140)
    tabla.column("apellido_materno", width=140)
    tabla.column("nombre", width=160)
    tabla.column("grupo", width=100)
    tabla.column("especialidad", width=120)

    # SCROLLBARS VERTICAL + HORIZONTAL
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tabla.xview)
    tabla.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tabla.pack(side="left", fill="both", expand=True)

    # FUNCIÓN: AJUSTAR ANCHO DE COLUMNA (como Excel)
    def ajustar_ancho_columnas():
        font = ("Segoe UI", 10)

        for col in columnas:
            max_width = tk.font.Font(font=font).measure(col) + 20  # ancho del encabezado

            for row in tabla.get_children():
                texto = str(tabla.set(row, col))
                width = tk.font.Font(font=font).measure(texto) + 20
                if width > max_width:
                    max_width = width

            tabla.column(col, width=max_width)

    # FUNCIÓN: CARGAR DATOS
    def cargar(filtro=""):
        conn = obtener_conexion()
        cur = conn.cursor()
        tabla.delete(*tabla.get_children())

        if filtro.strip():
            like = f"%{filtro}%"
            cur.execute("""
                SELECT E.matricula,
                    E.apellido_paterno,
                    E.apellido_materno,
                    E.nombre,
                    D.grupo,
                    D.especialidad,
                    E.id
                FROM Estudiantes E
                INNER JOIN DatosEscolares D
                        ON D.estudiante_id = E.id
                    AND D.ciclo_id = ?
                WHERE E.nombre LIKE ?
                OR E.apellido_paterno LIKE ?
                OR E.apellido_materno LIKE ?
                ORDER BY E.apellido_paterno
            """, (ciclo_activo["id"], like, like, like))
        else:
            cur.execute("""
                SELECT E.matricula,
                    E.apellido_paterno,
                    E.apellido_materno,
                    E.nombre,
                    D.grupo,
                    D.especialidad,
                    E.id
                FROM Estudiantes E
                INNER JOIN DatosEscolares D
                        ON D.estudiante_id = E.id
                    AND D.ciclo_id = ?
                ORDER BY E.apellido_paterno
            """, (ciclo_activo["id"],))


        filas = cur.fetchall()
        conn.close()

        # Insertar filas con valores NULL convertidos a ""
        for row in filas:
            tabla.insert("", "end", values=[v if v is not None else "" for v in row])

        ajustar_ancho_columnas()

    # EVENTOS DE BÚSQUEDA
    btn_buscar.config(command=lambda: cargar(entry_buscar.get()))
    entry_buscar.bind("<Return>", lambda e: cargar(entry_buscar.get()))
    btn_limpiar.config(command=lambda: (entry_buscar.delete(0, tk.END), cargar("")))

    # EVENTO: DOBLE CLIC / SELECCIÓN
    def on_select(event):
        sel = tabla.focus()
        if not sel:
            return
        vals = tabla.item(sel, "values")
        if not vals:
            return
        id = vals[6]
        mostrar_ficha_alumno(id, contenido, ciclo_activo)

    tabla.bind("<<TreeviewSelect>>", on_select)

    # Cargar datos iniciales
    cargar("")



# =====================================================
# MOSTRAR REINSCRIPCIONES
# =====================================================
def mostrar_reinscripciones(contenido, ciclo_activo):
    
    def obtener_ciclo_anterior(ciclo_activo):
        fila = obtener_todos("""
            SELECT id, ciclo
            FROM ciclos
            WHERE fin < (
                SELECT inicio FROM ciclos WHERE id = ?
            )
            AND status = 'Montado'
            ORDER BY fin DESC
            LIMIT 1
        """, (ciclo_activo,))

        if fila:
            return {"id": fila[0][0], "nombre": fila[0][1]}
        return None
    
    ciclo_origen = obtener_ciclo_anterior(ciclo_activo["id"])

    if not ciclo_origen:
        messagebox.showwarning(
            "Reinscripción no disponible",
            "No existe un ciclo anterior para reinscripción."
        )
        return
    """
    Igual que mostrar_alumnos, pero al seleccionar un alumno abre la ficha en modo 'reinscripcion'.
    """
    # destruir cualquier cosa previa
    for w in contenido.winfo_children():
        w.destroy()

    
    header = tk.Frame(contenido, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="REINSCRIPCIONES",
        bg="#d0e4f5",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)
    

    # marco superior búsqueda (idéntico)
    top = tk.Frame(contenido, bg="white")
    top.pack(fill="x", padx=20, pady=(20, 0))

    tk.Label(top, text="Buscar:", bg="white").pack(side="left", padx=(0,8))
    entry_buscar = tk.Entry(top, bd=1, relief="solid")
    entry_buscar.pack(side="left", padx=(0,8))

    btn_buscar = tk.Button(top, text="Buscar")
    btn_buscar.pack(side="left")

    btn_limpiar = tk.Button(top, text="Mostrar todos")
    btn_limpiar.pack(side="left", padx=(8,0))

    # ===============================
    # COMBOBOX CICLO / TODOS
    # ===============================
    filtro_ciclo_var = tk.StringVar(value="Ciclo anterior")

    cb_filtro_ciclo = ttk.Combobox(
        top,
        textvariable=filtro_ciclo_var,
        state="readonly",
        width=18,
        values=["Ciclo anterior", "Todos los ciclos"]
    )
    cb_filtro_ciclo.pack(side="right")

    # tabla central
    table_frame = tk.Frame(contenido, bg="white")
    table_frame.pack(fill="both", expand=True, padx=20, pady=20)

    columnas = ("id", "apellido_paterno", "apellido_materno", "nombre", "grupo", "especialidad")
    tabla = ttk.Treeview(table_frame, columns=columnas, show="headings")
    tabla.heading("id", text="Matrícula")
    tabla.heading("apellido_paterno", text="Apellido Paterno")
    tabla.heading("apellido_materno", text="Apellido Materno")
    tabla.heading("nombre", text="Nombre")
    tabla.heading("grupo", text="Grupo")
    tabla.heading("especialidad", text="Especialidad")

    # columnas tamaño inicial
    tabla.column("id", width=100, anchor="center")
    tabla.column("apellido_paterno", width=140)
    tabla.column("apellido_materno", width=140)
    tabla.column("nombre", width=160)
    tabla.column("grupo", width=100)
    tabla.column("especialidad", width=120)

    # SCROLLBARS VERTICAL + HORIZONTAL
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tabla.xview)
    tabla.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tabla.pack(side="left", fill="both", expand=True)

    # FUNCIÓN: AJUSTAR ANCHO DE COLUMNA (como Excel)
    def ajustar_ancho_columnas():
        font = ("Segoe UI", 10)

        for col in columnas:
            max_width = tk.font.Font(font=font).measure(col) + 20  # ancho del encabezado

            for row in tabla.get_children():
                texto = str(tabla.set(row, col))
                width = tk.font.Font(font=font).measure(texto) + 20
                if width > max_width:
                    max_width = width

            tabla.column(col, width=max_width)

    def cargar(filtro=""):
        conn = obtener_conexion()
        cur = conn.cursor()
        tabla.delete(*tabla.get_children())

        modo = filtro_ciclo_var.get()

        if modo == "Todos los ciclos":
            # 🔹 MOSTRAR TODOS LOS ALUMNOS
            if filtro.strip():
                like = f"%{filtro}%"
                cur.execute("""
                    SELECT
                        e.matricula,
                        e.apellido_paterno,
                        e.apellido_materno,
                        e.nombre,
                        d.grupo,
                        d.especialidad,
                        e.id
                    FROM Estudiantes e
                    LEFT JOIN DatosEscolares d
                        ON d.estudiante_id = e.id
                    WHERE
                        e.nombre LIKE ?
                        OR e.apellido_paterno LIKE ?
                        OR e.apellido_materno LIKE ?
                    ORDER BY e.apellido_paterno
                """, (like, like, like))
            else:
                cur.execute("""
                    SELECT
                        e.matricula,
                        e.apellido_paterno,
                        e.apellido_materno,
                        e.nombre,
                        d.grupo,
                        d.especialidad,
                        e.id
                    FROM Estudiantes e
                    LEFT JOIN DatosEscolares d
                        ON d.estudiante_id = e.id
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM DatosEscolares d2
                        WHERE d2.estudiante_id = e.id
                        AND d2.ciclo_id = ?
                    )
                    ORDER BY e.apellido_paterno
                """, (
                    ciclo_activo["id"],
                ))

        else:
            # 🔹 SOLO CICLO ORIGEN (COMO YA LO TENÍAS)
            if filtro.strip():
                like = f"%{filtro}%"
                cur.execute("""
                    SELECT
                        e.matricula,
                        e.apellido_paterno,
                        e.apellido_materno,
                        e.nombre,
                        d.grupo,
                        d.especialidad,
                        e.id
                    FROM Estudiantes e
                    INNER JOIN DatosEscolares d
                        ON d.estudiante_id = e.id
                    WHERE d.ciclo_id = ?
                    AND NOT EXISTS (
                        SELECT 1
                        FROM DatosEscolares d2
                        WHERE d2.estudiante_id = e.id
                        AND d2.ciclo_id = ?
                    )
                    AND (
                        e.nombre LIKE ?
                        OR e.apellido_paterno LIKE ?
                        OR e.apellido_materno LIKE ?
                    )
                    ORDER BY e.apellido_paterno
                """, (
                    ciclo_origen["id"],
                    ciclo_activo["id"],
                    like, like, like
                ))
            else:
                cur.execute("""
                    SELECT
                        e.matricula,
                        e.apellido_paterno,
                        e.apellido_materno,
                        e.nombre,
                        d.grupo,
                        d.especialidad,
                        e.id
                    FROM Estudiantes e
                    INNER JOIN DatosEscolares d
                        ON d.estudiante_id = e.id
                    WHERE d.ciclo_id = ?
                    AND NOT EXISTS (
                        SELECT 1
                        FROM DatosEscolares d2
                        WHERE d2.estudiante_id = e.id
                        AND d2.ciclo_id = ?
                    )
                    ORDER BY e.apellido_paterno
                """, (
                    ciclo_origen["id"],
                    ciclo_activo["id"]
                ))

        filas = cur.fetchall()
        conn.close()

        for row in filas:
            tabla.insert("", "end", values=[v if v is not None else "" for v in row])

        ajustar_ancho_columnas()

    # EVENTOS DE BÚSQUEDA
    btn_buscar.config(command=lambda: cargar(entry_buscar.get()))
    entry_buscar.bind("<Return>", lambda e: cargar(entry_buscar.get()))
    btn_limpiar.config(command=lambda: (entry_buscar.delete(0, tk.END), cargar("")))
    filtro_ciclo_var.trace_add("write", lambda *args: cargar(entry_buscar.get()))

    def on_select(event):
        sel = tabla.focus()
        if not sel:
            return
        vals = tabla.item(sel, "values")
        if not vals:
            return
        matricula = vals[6]
        # abrir ficha en modo reinscripcion (aquí está la diferencia)
        from .ficha_alumno import mostrar_ficha_alumno
        mostrar_ficha_alumno(matricula, contenido, ciclo_activo, modo="reinscripcion")

    tabla.bind("<<TreeviewSelect>>", on_select)

    cargar("")
