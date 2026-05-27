# vistas/alumnos.py
import tkinter as tk
from tkinter import ttk
from db.conexion import obtener_conexion, obtener_todos
from tkinter import ttk, messagebox
from alumnado.datepicker import DatePicker

# =====================================================
# MOSTRAR INSCRIPCIONES
# =====================================================
def mostrar_extraordinarios(contenido, ciclo_activo):
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
        text="EXTRAORDINARIOS",
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
    top.title("Asignar calificación")
    top.geometry("400x300")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    top.resizable(False, False)

    # centrar
    top.update_idletasks()
    x = (top.winfo_screenwidth() // 2) - 200
    y = (top.winfo_screenheight() // 2) - 160
    top.geometry(f"+{x}+{y}")

    cont = tk.Frame(top, padx=20, pady=20)
    cont.pack(fill="both", expand=True)

    # =========================
    # MATERIAS REPROBADAS
    # =========================

    materias = obtener_todos("""
        SELECT 
            ea.materia_id,
            m.nombre,
            ea.final
        FROM EstadoAcademico ea
        JOIN Materias m ON m.id = ea.materia_id
        WHERE ea.alumno_id = ?
        AND ea.final < 6
        AND ea.final IS NOT NULL
        ORDER BY m.nombre
    """, (alumno_id,))

    materias_dict = {m[1]: m[0] for m in materias}

    tk.Label(cont, text="Materia:").pack(anchor="w")

    cb_materia = ttk.Combobox(
        cont,
        values=list(materias_dict.keys()),
        state="readonly"
    )
    cb_materia.pack(fill="x", pady=5)

    # =========================
    # CALIFICACION
    # =========================

    tk.Label(cont, text="Calificación:").pack(anchor="w", pady=(10,0))

    calificacion_var = tk.StringVar()

    entry_cal = tk.Entry(cont, textvariable=calificacion_var)
    entry_cal.pack(fill="x", pady=5)

    # Validar decimal
    def validar_decimal(P):

        if P == "":
            return True

        try:
            if float(P) <= 10:
                if P.count(".") <= 1:
                    return True
        except:
            pass

        return False

    vcmd = (top.register(validar_decimal), "%P")
    entry_cal.config(validate="key", validatecommand=vcmd)

    # =========================
    # FECHA
    # =========================

    tk.Label(cont, text="Fecha:").pack(anchor="w", pady=(10,0))

    fecha_picker = DatePicker(cont)
    fecha_picker.pack(fill="x", pady=5)

    # =========================
    # BOTONES
    # =========================

    btn_frame = tk.Frame(cont)
    btn_frame.pack(fill="x", pady=20)

    def guardar():

        materia_nombre = cb_materia.get()

        if not materia_nombre:
            messagebox.showwarning("Error", "Seleccione una materia")
            return

        calificacion = calificacion_var.get()

        if not calificacion:
            messagebox.showwarning("Error", "Ingrese una calificación")
            return

        materia_id = materias_dict[materia_nombre]

        fecha = fecha_picker.get_text()

        conn = obtener_conexion()
        cur = conn.cursor()

        cur.execute("""
            UPDATE EstadoAcademico
            SET parcial1 = NULL, parcial2 = NULL, parcial3 = NULL,
                    final = ?, fecha = ?
            WHERE alumno_id = ?
            AND materia_id = ?
        """, (
            float(calificacion),
            fecha,
            alumno_id,
            materia_id
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Calificación asignada")

        top.destroy()

    ttk.Button(
        btn_frame,
        text="Guardar",
        width=12,
        command=guardar
    ).pack(side="right", padx=10)

    ttk.Button(
        btn_frame,
        text="Cancelar",
        width=12,
        command=top.destroy
    ).pack(side="right")