# vistas/alumnos.py
import tkinter as tk
from tkinter import ttk
from db.conexion import obtener_conexion, obtener_todos
from tkinter import ttk, messagebox
from alumnado.datepicker import DatePicker

# =====================================================
# MOSTRAR INSCRIPCIONES
# =====================================================
def mostrar_equivalencia(contenido, ciclo_activo):
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
        text="EQUIVALENCIA",
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

    columnas = ("id", "nombre", "apellido_paterno", "apellido_materno",
                "grupo", "especialidad")

    tabla = ttk.Treeview(
        table_frame,
        columns=columnas,
        show="headings"
    )

    # Encabezados
    tabla.heading("id", text="Matrícula")
    tabla.heading("nombre", text="Nombre")
    tabla.heading("apellido_paterno", text="Apellido Paterno")
    tabla.heading("apellido_materno", text="Apellido Materno")
    tabla.heading("grupo", text="Grupo")
    tabla.heading("especialidad", text="Especialidad")

    # Tamaños iniciales
    tabla.column("id", width=100, anchor="center")
    tabla.column("nombre", width=160)
    tabla.column("apellido_paterno", width=140)
    tabla.column("apellido_materno", width=140)
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
                    E.nombre,
                    E.apellido_paterno,
                    E.apellido_materno,
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
                ORDER BY E.id
            """, (ciclo_activo["id"], like, like, like))
        else:
            cur.execute("""
                SELECT E.matricula,
                    E.nombre,
                    E.apellido_paterno,
                    E.apellido_materno,
                    D.grupo,
                    D.especialidad,
                    E.id
                FROM Estudiantes E
                INNER JOIN DatosEscolares D
                        ON D.estudiante_id = E.id
                    AND D.ciclo_id = ?
                ORDER BY E.id
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

    tabla.bind("<Double-1>", lambda e: abrir_asignar_calificacion(tabla, ciclo_activo))

    # Cargar datos iniciales
    cargar("")



def abrir_asignar_calificacion(tabla, ciclo_activo):

    sel = tabla.focus()
    if not sel:
        return

    vals = tabla.item(sel, "values")

    alumno_id = vals[6]

    ventana_asignar_calificacion(tabla, alumno_id, ciclo_activo["id"])



def ventana_asignar_calificacion(parent, alumno_id, ciclo_id):

    top = tk.Toplevel(parent.winfo_toplevel())
    top.title("Asignar calificaciones")
    top.geometry("650x500")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    top.resizable(False, False)

    # =========================
    # CENTRAR VENTANA
    # =========================
    top.update_idletasks()

    width = 650
    height = 500

    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)

    top.geometry(f"{width}x{height}+{x}+{y}")

    cont = tk.Frame(top, padx=20, pady=20)
    cont.pack(fill="both", expand=True)

    datos = obtener_todos("""
        SELECT 
            E.nombre,
            E.apellido_paterno,
            E.apellido_materno,
            D.estudiante_id,
            D.grupo,
            D.especialidad
        FROM Estudiantes E
        JOIN DatosEscolares D
            ON D.estudiante_id = E.id
        WHERE E.id = ?
        AND D.ciclo_id = ?
    """, (alumno_id, ciclo_id))

    if datos:
        nombre, ap, am, matricula, grupo, especialidad = datos[0]
        nombre_completo = f"{nombre} {ap} {am}"
    else:
        nombre_completo = ""
        matricula = ""
        grupo = ""
        especialidad = ""

    # =========================
    # HEADER ALUMNO
    # =========================

    header = tk.Frame(cont, bg="#d0e4f5", padx=10, pady=10)
    header.pack(fill="x", pady=(0, 15))

    tk.Label(
        header,
        text=f"Nombre alumno: {nombre_completo}",
        font=("Segoe UI", 13, "bold"),
        bg="#d0e4f5"
    ).pack(anchor="w")

    info_frame = tk.Frame(header, bg="#d0e4f5")
    info_frame.pack(fill="x", pady=(4,0))

    tk.Label(
        info_frame,
        text=f"id: {matricula}",
        font=("Segoe UI", 10),
        bg="#d0e4f5"
    ).pack(side="left")

    tk.Label(
        info_frame,
        text=f"Grupo: {grupo}",
        font=("Segoe UI", 10),
        bg="#d0e4f5"
    ).pack(side="left", padx=20)

    tk.Label(
        info_frame,
        text=f"Especialidad: {especialidad}",
        font=("Segoe UI", 10),
        bg="#d0e4f5"
    ).pack(side="left")

    # =========================
    # FRAME MATERIAS
    # =========================
    materias_frame = tk.Frame(cont)
    materias_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(materias_frame)
    scrollbar = ttk.Scrollbar(materias_frame, orient="vertical", command=canvas.yview)

    frame = tk.Frame(canvas)

    frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    window_id = canvas.create_window((0, 0), window=frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    def ajustar_ancho(event):
        canvas.itemconfig(window_id, width=event.width)

    canvas.bind("<Configure>", ajustar_ancho)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def activar_scroll(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def desactivar_scroll(event):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", activar_scroll)
    canvas.bind("<Leave>", desactivar_scroll)
    entradas = {}

    # =========================
    # OBTENER MATERIAS DEL ALUMNO
    # =========================
    materias = obtener_todos("""
        SELECT 
            ea.id,
            m.nombre,
            ea.final,
            ea.fecha
        FROM EstadoAcademico ea
        JOIN Materias m ON m.id = ea.materia_id
        WHERE ea.alumno_id = ?
        AND ea.ciclo_id = ?
        ORDER BY m.nombre
    """, (alumno_id, ciclo_id))

    # =========================
    # VALIDACION CALIFICACION
    # =========================
    def validar_decimal(P):

        if P == "":
            return True

        try:
            if float(P) <= 10 and P.count(".") <= 1:
                return True
        except:
            pass

        return False

    vcmd = (top.register(validar_decimal), "%P")

    # =========================
    # BLOQUES POR MATERIA
    # =========================
    for ea_id, nombre, final, fecha in materias:

        bloque = tk.Frame(
            frame,
            bg="white",
            bd=1,
            relief="solid",
            padx=10,
            pady=10
        )
        bloque.pack(fill="x", pady=5)

        tk.Label(
            bloque,
            text=nombre,
            font=("Segoe UI", 11, "bold"),
            bg="white"
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        cal_var = tk.StringVar(value="" if final is None else str(final))

        tk.Label(
            bloque,
            text="Calificación",
            bg="white"
        ).grid(row=1, column=0, sticky="w")

        entry_cal = tk.Entry(
            bloque,
            width=10,
            textvariable=cal_var,
            validate="key",
            validatecommand=vcmd
        )
        entry_cal.grid(row=1, column=1, padx=5)

        tk.Label(
            bloque,
            text="Fecha",
            bg="white"
        ).grid(row=1, column=2)

        fecha_picker = DatePicker(
            bloque,
            initial=fecha
        )
        fecha_picker.grid(row=1, column=3, padx=5)

        entradas[ea_id] = (cal_var, fecha_picker)

    # =========================
    # BOTONES ABAJO
    # =========================
    btn_frame = tk.Frame(top)
    btn_frame.pack(side="bottom", fill="x", pady=15)

    def guardar():

        conn = obtener_conexion()
        cur = conn.cursor()

        for ea_id, vars_tuple in entradas.items():

            cal_var, fecha_picker = vars_tuple

            calificacion = cal_var.get()
            fecha = fecha_picker.get_text()

            cur.execute("""
                UPDATE EstadoAcademico
                SET 
                    parcial1 = NULL,
                    parcial2 = NULL,
                    parcial3 = NULL,
                    fecha = NULL,
                    final = ?,
                    fecha_equivalencia = ?
                WHERE id = ?
            """, (
                float(calificacion) if calificacion else None,
                fecha,
                ea_id
            ))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Calificaciones guardadas")
        top.destroy()

    ttk.Button(
        btn_frame,
        text="Guardar",
        width=14,
        command=guardar
    ).pack(side="right", padx=10)

    ttk.Button(
        btn_frame,
        text="Cancelar",
        width=14,
        command=top.destroy
    ).pack(side="right")







