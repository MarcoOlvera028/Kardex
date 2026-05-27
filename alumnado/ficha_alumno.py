# vistas/ficha_alumno.py
import tkinter as tk
from tkinter import ttk, messagebox
from db.conexion import obtener_conexion, obtener_todos
from .datepicker import DatePicker
import re

# ================================
# LISTA GLOBAL DE CALLBACKS
# ================================
callbacks_nacionalidad = []

# Helpers
def safe(v):
    return "" if v is None else str(v)

def validar_curp(curp: str) -> bool:
    if not curp:
        return True
    curp = curp.strip().upper()
    patron = r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$'
    return bool(re.match(patron, curp))

def validar_telefono_raw(tel: str) -> bool:
    if not tel:
        return True
    digits = re.sub(r'\D', '', tel)
    return len(digits) == 10

def cargar_nacionalidades():
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT nombre FROM Nacionalidades ORDER BY nombre ASC")
    lista = [row[0] for row in cur.fetchall()]
    conn.close()
    return lista

def agregar_nacionalidad(callback_actualizar):
    win = tk.Toplevel()
    win.title("Agregar nacionalidad")
    win.geometry("340x150")
    win.resizable(False, False)
    win.grab_set()
    centrar_ventana2(win)

    tk.Label(win, text="Nueva nacionalidad:", font=("Segoe UI", 11)).pack(pady=10)
    entry = tk.Entry(win, width=28)
    entry.pack()

    def guardar():
        nombre = entry.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío.")
            return

        conn = obtener_conexion()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO Nacionalidades(nombre) VALUES (?)", (nombre,))
            conn.commit()
        except:
            messagebox.showerror("Error", "Esa nacionalidad ya existe.")
            conn.close()
            return
        conn.close()

        win.destroy()

        # Actualizar el combo donde se presionó "+"
        callback_actualizar()

        # Actualizar TODOS los combos de nacionalidad registrados
        for cb in callbacks_nacionalidad:
            cb()

    tk.Button(win, text="Guardar", width=12, command=guardar).pack(pady=12)

class ComboConAgregar(tk.Frame):
    def __init__(self, master, width=26, **kwargs):
        super().__init__(master, bg="white")

        self.cmb = ttk.Combobox(self, width=width, state="readonly")
        self.cmb.pack(side="left")

        self.btn = tk.Button(self, text="+", width=2, command=self.agregar, bg="white")
        self.btn.pack(side="left", padx=4)

        self.actualizar_lista(mantener_valor=False)

        # Registrar callback global
        callbacks_nacionalidad.append(self.actualizar_lista)

    def actualizar_lista(self, mantener_valor=True):
        lista = cargar_nacionalidades()
        valor_actual = self.cmb.get() if mantener_valor else ""

        self.cmb["values"] = lista

        if valor_actual in lista:
            self.cmb.set(valor_actual)
        else:
            self.cmb.set("")   # IMPORTANTE: dejar vacío

    def agregar(self):
        agregar_nacionalidad(self.actualizar_lista)

    def get(self):
        return self.cmb.get()

    def set(self, valor):
        self.cmb.set(valor if valor else "")

def cargar_estados():
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM Estados ORDER BY nombre")
    lista = cur.fetchall()   # (id, nombre)
    conn.close()
    return lista

def cargar_municipios(estado_id):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM Municipios WHERE estado_id=? ORDER BY nombre", (estado_id,))
    lista = cur.fetchall()
    conn.close()
    return lista

def centrar_ventana2(win, master=None):
    win.update_idletasks()

    if master is None:
        master = win.master

    w = win.winfo_width()
    h = win.winfo_height()
    x = master.winfo_rootx() + (master.winfo_width()//2 - w//2)
    y = master.winfo_rooty() + (master.winfo_height()//2 - h//2)

    win.geometry(f"{w}x{h}+{x}+{y}")

def agregar_estado(callback):
    win = tk.Toplevel()
    win.title("Agregar estado")
    win.geometry("340x150")
    win.resizable(False, False)
    win.grab_set()
    centrar_ventana2(win)

    tk.Label(win, text="Nuevo estado:", font=("Segoe UI", 11)).pack(pady=10)
    entry = tk.Entry(win, width=28)
    entry.pack()

    def guardar():
        nombre = entry.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío.")
            return

        conn = obtener_conexion()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO Estados(nombre) VALUES (?)", (nombre,))
            conn.commit()
        except:
            messagebox.showerror("Error", "Ese estado ya existe.")
            conn.close()
            return

        conn.close()
        win.destroy()
        callback()  # refrescar combo

    tk.Button(win, text="Guardar", width=12, command=guardar).pack(pady=12)

def agregar_municipio(estado_nombre, callback):
    win = tk.Toplevel()
    win.title("Agregar municipio")
    win.geometry("340x150")
    win.resizable(False, False)
    win.grab_set()
    centrar_ventana2(win)

    tk.Label(win, text="Nuevo municipio:", font=("Segoe UI", 11)).pack(pady=10)
    entry = tk.Entry(win, width=28)
    entry.pack()

    def guardar():
        nombre = entry.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío.")
            return

        conn = obtener_conexion()
        cur = conn.cursor()

        # obtener id del estado
        cur.execute("SELECT id FROM Estados WHERE nombre=?", (estado_nombre,))
        row = cur.fetchone()
        if not row:
            messagebox.showerror("Error", "Selecciona un estado válido.")
            conn.close()
            return

        estado_id = row[0]

        cur.execute("""
            INSERT INTO Municipios(nombre, estado_id)
            VALUES (?, ?)
        """, (nombre, estado_id))

        conn.commit()
        conn.close()

        win.destroy()
        callback()  # refrescar municipios

    tk.Button(win, text="Guardar", width=12, command=guardar).pack(pady=12)

class EstadoMunicipioPicker(tk.Frame):
    def __init__(self, master, width=26, **kwargs):
        super().__init__(master, **kwargs)

        # Estado
        tk.Label(self, text="Estado:", bg="white").grid(row=0, column=0, sticky="e")
        self.cmb_estado = ttk.Combobox(self, width=width, state="readonly")
        self.cmb_estado.grid(row=0, column=1, sticky="w")
        tk.Button(self, text="+", width=2,
                  command=self.add_estado).grid(row=0, column=2, padx=4)

        # Municipio
        tk.Label(self, text="Municipio:", bg="white").grid(row=1, column=0, sticky="e")
        self.cmb_municipio = ttk.Combobox(self, width=width, state="readonly")
        self.cmb_municipio.grid(row=1, column=1, sticky="w")
        tk.Button(self, text="+", width=2,
                  command=self.add_municipio).grid(row=1, column=2, padx=4)

        # Inicializar
        self.actualizar_estados()

        self.cmb_estado.bind("<<ComboboxSelected>>", self.actualizar_municipios)

    # -------------------------
    #        ESTADOS
    # -------------------------
    def actualizar_estados(self):
        estados = cargar_estados()      # lista [(id,nombre),...]
        self.estados = estados
        self.cmb_estado["values"] = [e[1] for e in estados]
        if estados:
            self.cmb_estado.current(0)
            self.actualizar_municipios()

    def add_estado(self):
        agregar_estado(self.actualizar_estados)

    # -------------------------
    #        MUNICIPIOS
    # -------------------------
    def actualizar_municipios(self, event=None):
        if not self.cmb_estado.get():
            return

        estado_id = next(e[0] for e in self.estados if e[1] == self.cmb_estado.get())
        municipios = cargar_municipios(estado_id)

        self.municipios = municipios
        self.cmb_municipio["values"] = [m[1] for m in municipios]
        if municipios:
            self.cmb_municipio.current(0)
        else:
            self.cmb_municipio.set("")

    def add_municipio(self):
        if not self.cmb_estado.get():
            messagebox.showerror("Error", "Selecciona un estado primero.")
            return

        estado_id = next(e[0] for e in self.estados if e[1] == self.cmb_estado.get())
        agregar_municipio(estado_id, self.actualizar_municipios)

    # --------- Obtener valores ----------
    def get_estado(self):
        return self.cmb_estado.get()

    def get_municipio(self):
        return self.cmb_municipio.get()

def cargar_grupos():
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT g.nombre || '/' || gr.grupo
        FROM grupos gr
        JOIN grados g ON g.id = gr.grado_id
        ORDER BY g.orden, gr.grupo
    """)
    lista = [row[0] for row in cur.fetchall()]
    conn.close()
    return lista

def cargar_especialidades():
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT nombre
        FROM Especialidades
        ORDER BY nombre
    """)
    lista = [row[0] for row in cur.fetchall()]
    conn.close()
    return lista

def asignar_materias_automaticamente(cur, alumno_id, ciclo_id, grupo_nombre, especialidad_nombre):

    # Extraer solo el grado
    grado_nombre = grupo_nombre.split("/")[0].strip()

    # Obtener ID real del grupo
    cur.execute("""
        SELECT id FROM Grados WHERE nombre = ?
    """, (grado_nombre,))
    row = cur.fetchone()

    # Obtener ID real de la especialidad
    cur.execute("""
        SELECT id FROM Especialidades WHERE nombre = ?
    """, (especialidad_nombre,))
    row2 = cur.fetchone()

    if not row:
        return
    
    if not row:
        return

    grupo_id = row[0]
    especialidad_id = row2[0] if row2 else None

    cur.execute("""
        DELETE FROM EstadoAcademico
        WHERE alumno_id = ?
        AND ciclo_id = ?
    """, (alumno_id, ciclo_id))

    # ==========================================
    # Obtener materias:
    # - Del grupo
    # - Tronco común (especialidad_id IS NULL)
    # - O de la especialidad seleccionada
    # ==========================================
    cur.execute("""
        SELECT id FROM Materias
        WHERE grupo_id = ?
        AND (
                especialidad_id IS NULL
                OR especialidad_id = ?
            )
    """, (grupo_id, especialidad_id))


    materias = cur.fetchall()

    for materia in materias:
        materia_id = materia[0]

        cur.execute("""
            INSERT OR IGNORE INTO EstadoAcademico (
                alumno_id,
                materia_id,
                ciclo_id
            )
            VALUES (?, ?, ?)
        """, (alumno_id, materia_id, ciclo_id))




def mostrar_ficha_alumno(id_alumno, contenido, ciclo_activo, modo="normal"):
    import tkinter as tk
    from tkinter import ttk, messagebox
    from db.conexion import obtener_conexion
    from .datepicker import DatePicker
    import re

    def safe(v):
        return "" if v is None else str(v)

    def validar_curp(curp: str) -> bool:
        if not curp:
            return True
        curp = curp.strip().upper()
        patron = r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$'
        return bool(re.match(patron, curp))

    def validar_telefono_raw(tel: str) -> bool:
        if not tel:
            return True
        digits = re.sub(r'\D', '', tel)
        return len(digits) == 10

    # ---------- limpiar pantalla ----------
    for w in contenido.winfo_children():
        w.destroy()

    # ---------- leer BD (valores actuales como fallback) ----------
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("SELECT matricula, nombre, apellido_paterno, apellido_materno FROM Estudiantes WHERE id=?", (id_alumno,))
    alumno = cur.fetchone() or (id_alumno, "", "", "")

    cur.execute("SELECT grupo, especialidad FROM DatosEscolares WHERE estudiante_id=? AND ciclo_id=?", (id_alumno, ciclo_activo["id"]))
    escolares = cur.fetchone()

    cur.execute("""SELECT genero, fecha_nacimiento, correo, curp FROM DatosGenerales WHERE estudiante_id=?""", (id_alumno,))
    generales = cur.fetchone()

    cur.execute("""SELECT nombre, celular FROM DatosFamiliares WHERE estudiante_id=?""", (id_alumno,))
    familiares = cur.fetchone()

    cur.execute("""SELECT calle, numero, estado, municipio, cp, telefono, colonia
                   FROM DatosDireccion WHERE estudiante_id=?""", (id_alumno,))
    direccion = cur.fetchone()

    conn.close()

    # ---------- header ----------
    header = tk.Frame(contenido, bg="#d0e4f5", height=60)
    header.pack(fill="x")
    tk.Label(header, text="Ficha del Alumno", bg="#d0e4f5", font=("Segoe UI", 16, "bold")).pack(pady=12)

    # ---------- body ----------
    body = tk.Frame(contenido, bg="white")
    body.pack(fill="both", expand=True, padx=20, pady=16)

    label_opts = {"bg": "white", "font": ("Segoe UI", 11)}
    entry_opts = {"bd":1, "relief":"solid"}

    # Datos visibles
    tk.Label(body, text="Matrícula:", **label_opts).grid(row=0, column=0, sticky="e", padx=6, pady=8)
    txt_id = tk.Entry(body, width=12, **entry_opts)
    txt_id.insert(0, safe(alumno[0]))
    txt_id.grid(row=0, column=1, sticky="w", padx=6, pady=8)

    tk.Label(body, text="Nombre:", **label_opts).grid(row=0, column=2, sticky="e", padx=6, pady=8)
    txt_nombre = tk.Entry(body, width=32, **entry_opts)
    txt_nombre.insert(0, safe(alumno[1]))
    txt_nombre.grid(row=0, column=3, sticky="w", padx=6, pady=8)

    tk.Label(body, text="Apellido Paterno:", **label_opts).grid(row=1, column=0, sticky="e", padx=6, pady=8)
    txt_paterno = tk.Entry(body, width=32, **entry_opts)
    txt_paterno.insert(0, safe(alumno[2]))
    txt_paterno.grid(row=1, column=1, sticky="w", padx=6, pady=8)

    tk.Label(body, text="Apellido Materno:", **label_opts).grid(row=1, column=2, sticky="e", padx=6, pady=8)
    txt_materno = tk.Entry(body, width=32, **entry_opts)
    txt_materno.insert(0, safe(alumno[3]))
    txt_materno.grid(row=1, column=3, sticky="w", padx=6, pady=8)

    # separador
    tk.Frame(body, height=2, bg="#e0e0e0").grid(row=2, column=0, columnspan=4, sticky="we", pady=12)

    # ---------- pestañas: crear contenedor y paneles persistentes ----------
    tab_bar = tk.Frame(body, bg="white")
    tab_bar.grid(row=3, column=0, columnspan=4, sticky="we", pady=(0,8))

    panels_container = tk.Frame(body, bg="white")
    panels_container.grid(row=4, column=0, columnspan=4, sticky="nsew")
    body.grid_rowconfigure(4, weight=1)
    body.grid_columnconfigure(3, weight=1)

    COLOR_SELEC = "#ffffff"
    COLOR_NORMAL = "#ececec"

    tab_buttons = {}
    panels = {}   # paneles persistentes
    built = {}    # flags de construcción

    # Helper para obtener valor seguro desde tu BD-original
    def bd_safe_get(tuple_obj, idx):
        try:
            return tuple_obj[idx] if tuple_obj and tuple_obj[idx] is not None else None
        except Exception:
            return None

    # ---------- funciones que crean (una sola vez) los contenidos de cada pestaña ----------
    # -----------------------------
    #     ESCOLARES
    # -----------------------------
    def build_escolares():
        if built.get("Escolares"):
            return

        f = tk.Frame(panels_container, bg="white")
        panels["Escolares"] = f

        # ==========================
        # GRUPO
        # ==========================
        tk.Label(f, text="Grupo:", bg="white", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="e", pady=8, padx=8)
        cb_grupo = ttk.Combobox(f, values=cargar_grupos(), state="readonly", width=26)
        if bd_safe_get(escolares,0):
            cb_grupo.set(safe(bd_safe_get(escolares,0)))
        cb_grupo.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        # ==========================
        # ESPECIALIDAD (OCULTA)
        # ==========================
        tk.Label(f, text="Especialidad:", bg="white", font=("Segoe UI", 11))
        lbl_especialidad = f.grid_slaves(row=1, column=0)[0] if f.grid_slaves(row=1, column=0) else None

        lbl_especialidad = tk.Label(f, text="Especialidad:", bg="white", font=("Segoe UI", 11))

        cb_especialidad = ttk.Combobox(f, values=[], state="readonly", width=26)

        # ==========================
        # LÓGICA MOSTRAR / OCULTAR
        # ==========================
        def actualizar_especialidad(event=None):
            grupo = cb_grupo.get()

            if grupo.startswith(("Quinto/", "Sexto/")):
                # cargar desde BD
                especialidades = cargar_especialidades()
                cb_especialidad["values"] = especialidades

                lbl_especialidad.grid(row=1, column=0, sticky="e", pady=8, padx=8)
                cb_especialidad.grid(row=1, column=1, padx=8, pady=8, sticky="w")

                # valor guardado (si existe)
                if bd_safe_get(escolares, 1):
                    cb_especialidad.set(safe(bd_safe_get(escolares, 1)))
            else:
                lbl_especialidad.grid_remove()
                cb_especialidad.grid_remove()
                cb_especialidad.set("")

        cb_grupo.bind("<<ComboboxSelected>>", actualizar_especialidad)

        # Forzar validación inicial (por si ya hay grupo cargado)
        actualizar_especialidad()

        f.cb_grupo = cb_grupo
        f.cb_especialidad = cb_especialidad

        # ---------- Guardado ----------
        built["Escolares"] = True

    # -----------------------------
    #     GENERALES
    # -----------------------------
    def build_generales():
        if built.get("Generales"):
            return
        f = tk.Frame(panels_container, bg="white")
        panels["Generales"] = f

        tk.Label(f, text="Género:", bg="white", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="e", pady=8, padx=8)
        genero_cmb = ttk.Combobox(f, values=["masculino","femenino"], state="readonly", width=20)
        if bd_safe_get(generales,0):
            genero_cmb.set(safe(bd_safe_get(generales,0)))
        genero_cmb.grid(row=0, column=1, padx=8, pady=8, sticky= "w")

        tk.Label(f, text="Fecha de nacimiento:", bg="white", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="e", pady=8, padx=8)
        initial_fn = bd_safe_get(generales,1)
        dp_fecha_nac = DatePicker(f, initial=initial_fn)
        dp_fecha_nac.grid(row=1, column=1, padx=8, pady=8, sticky="w")

        tk.Label(f, text="Correo:", bg="white", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="e", pady=8, padx=8)
        entry_correo = tk.Entry(f, width=28, **entry_opts)
        entry_correo.insert(0, safe(bd_safe_get(generales,2)))
        entry_correo.grid(row=2, column=1, padx=8, pady=8, sticky="w")

        tk.Label(f, text="CURP:", bg="white", font=("Segoe UI", 11)).grid(row=3, column=0, sticky="e", pady=8, padx=8)
        entry_curp = tk.Entry(f, width=28, **entry_opts)
        entry_curp.insert(0, safe(bd_safe_get(generales,3)))
        entry_curp.grid(row=3, column=1, padx=8, pady=8, sticky="w")

        f.genero_cmb = genero_cmb
        f.dp_fecha_nac = dp_fecha_nac
        f.entry_correo = entry_correo
        f.entry_curp = entry_curp

        built["Generales"] = True

    # -----------------------------
    #    FAMILIARES
    # -----------------------------
    def build_familiares():
        if built.get("Familiares"):
            return
        f = tk.Frame(panels_container, bg="white")
        panels["Familiares"] = f

        tk.Label(f, text="Nombre:", bg="white", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="e", pady=8, padx=8)
        entry_fam_nombre = tk.Entry(f, width=28, bd=1, relief="solid")
        entry_fam_nombre.insert(0, safe(bd_safe_get(familiares,0)))
        entry_fam_nombre.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        tk.Label(f, text="Celular:", bg="white", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="e", pady=8, padx=8)
        entry_fam_cel = tk.Entry(f, width=20, bd=1, relief="solid")
        entry_fam_cel.insert(0, safe(bd_safe_get(familiares,1)))
        entry_fam_cel.grid(row=1, column=1, padx=8, pady=8, sticky="w")

        f.entry_fam_nombre = entry_fam_nombre
        f.entry_fam_cel = entry_fam_cel

        built["Familiares"] = True

    # -----------------------------
    #     DIRECCION
    # -----------------------------
    def build_direccion():
        if built.get("Dirección"):
            return

        f = tk.Frame(panels_container, bg="white")
        panels["Dirección"] = f

        # ----------- CAMPOS TEXTO ----------------
        tk.Label(f, text="Calle:", bg="white", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="e", pady=8, padx=8)
        entry_calle = tk.Entry(f, width=34, bd=1, relief="solid")
        entry_calle.insert(0, safe(bd_safe_get(direccion, 0)))
        entry_calle.grid(row=0, column=1, sticky="w", pady=8)

        tk.Label(f, text="Número:", bg="white", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="e", pady=8, padx=8)
        entry_numero = tk.Entry(f, width=34, bd=1, relief="solid")
        entry_numero.insert(0, safe(bd_safe_get(direccion, 1)))
        entry_numero.grid(row=1, column=1, sticky="w", pady=8)

        # ---------------------- ESTADO ----------------------
        tk.Label(f, text="Estado:", bg="white", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="e", pady=6, padx=6)

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM Estados ORDER BY nombre")
        estados = cur.fetchall()
        conn.close()

        nombres_estados = [e[1] for e in estados]

        cb_estado = ttk.Combobox(f, values=nombres_estados, state="readonly", width=32)
        estado_actual = safe(bd_safe_get(direccion, 2))
        if estado_actual:
            cb_estado.set(estado_actual)
        cb_estado.grid(row=2, column=1, sticky="w", pady=6)

        # botón +
        btn_estado_plus = tk.Button(
            f, text="+", width=3,
            command=lambda: agregar_estado(lambda: recargar_estados())
        )
        btn_estado_plus.grid(row=2, column=2, sticky="w", padx=4)

        # -------------------- MUNICIPIO ---------------------
        tk.Label(f, text="Municipio:", bg="white", font=("Segoe UI", 11)).grid(row=3, column=0, sticky="e", pady=8, padx=8)

        cb_municipio = ttk.Combobox(f, values=[], state="readonly", width=32)
        cb_municipio.grid(row=3, column=1, sticky="w", pady=8)

        # botón +
        btn_mun_plus = tk.Button(
            f, text="+", width=3,
            command=lambda: agregar_municipio(cb_estado.get(), lambda: actualizar_municipios())
        )
        btn_mun_plus.grid(row=3, column=2, sticky="w", padx=4)

        # -------------- Funciones para refrescar combos -------------

        def recargar_estados():
            """Vuelve a cargar lista de estados en el combobox"""
            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("SELECT nombre FROM Estados ORDER BY nombre")
            lista = [row[0] for row in cur.fetchall()]
            conn.close()

            cb_estado["values"] = lista
            if lista:
                cb_estado.set(lista[-1])  # selecciona el último agregado

            actualizar_municipios()

        def actualizar_municipios(event=None):
            """Carga municipios basados en el estado seleccionado"""
            estado_sel = cb_estado.get()
            if not estado_sel:
                cb_municipio["values"] = []
                return

            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("""
                SELECT m.nombre 
                FROM Municipios m 
                JOIN Estados e ON e.id = m.estado_id
                WHERE e.nombre = ?
                ORDER BY m.nombre
            """, (estado_sel,))
            municipios = [r[0] for r in cur.fetchall()]
            conn.close()

            cb_municipio["values"] = municipios
            if municipios:
                cb_municipio.set(municipios[0])

        cb_estado.bind("<<ComboboxSelected>>", actualizar_municipios)

        # Cargar municipio guardado del alumno
        municipio_actual = safe(bd_safe_get(direccion, 3))
        if estado_actual:
            actualizar_municipios()
            if municipio_actual:
                cb_municipio.set(municipio_actual)

        # ----------------- RESTO CAMPOS ---------------------
        tk.Label(f, text="C.P:", bg="white", font=("Segoe UI", 11)).grid(row=4, column=0, sticky="e", pady=8, padx=8)
        entry_cp = tk.Entry(f, width=34, bd=1, relief="solid")
        entry_cp.insert(0, safe(bd_safe_get(direccion, 4)))
        entry_cp.grid(row=4, column=1, sticky="w", pady=8)

        tk.Label(f, text="Teléfono:", bg="white", font=("Segoe UI", 11)).grid(row=5, column=0, sticky="e", pady=8, padx=8)
        entry_telefono_dir = tk.Entry(f, width=34, bd=1, relief="solid")
        entry_telefono_dir.insert(0, safe(bd_safe_get(direccion, 5)))
        entry_telefono_dir.grid(row=5, column=1, sticky="w", pady=8)

        tk.Label(f, text="Colonia:", bg="white", font=("Segoe UI", 11)).grid(row=6, column=0, sticky="e", pady=8, padx=8)
        entry_colonia = tk.Entry(f, width=34, bd=1, relief="solid")
        entry_colonia.insert(0, safe(bd_safe_get(direccion, 6)))
        entry_colonia.grid(row=6, column=1, sticky="w", pady=8)

        # Guardar referencias
        f.entry_calle = entry_calle
        f.entry_numero = entry_numero
        f.cb_estado = cb_estado
        f.cb_municipio = cb_municipio
        f.entry_cp = entry_cp
        f.entry_telefono_dir = entry_telefono_dir
        f.entry_colonia = entry_colonia

        built["Dirección"] = True


    # ---------- construcción de pestañas (labels) ----------
    def select_tab(name):
        # pintar visual
        for n, w in tab_buttons.items():
            w.config(bg=COLOR_NORMAL, bd=1, relief="solid")
        tab_buttons[name].config(bg=COLOR_SELEC, bd=2, relief="solid")

        # asegurar que el panel existe y mostrar solo ese
        # construir si no construido
        if name == "Escolares":
            build_escolares()
        elif name == "Generales":
            build_generales()
        elif name == "Familiares":
            build_familiares()
        else:
            build_direccion()

        # hide all panels then show selected
        for n, panel in panels.items():
            panel.pack_forget()
        panels[name].pack(fill="both", expand=True, padx=8, pady=8)
        # conservar referencia a panel activo
        panels_container.current_panel = panels[name]

    for name in ["Escolares", "Generales", "Familiares", "Dirección"]:
        lbl = tk.Label(
            tab_bar,
            text=name,
            bg=COLOR_NORMAL,
            padx=16,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            bd=1,                 # grosor del borde
            relief="solid",       # estilo del borde
            highlightthickness=0
        )
        lbl.pack(side="left", padx=4, pady=4)
        lbl.bind("<Button-1>", lambda e, n=name: select_tab(n))
        tab_buttons[name] = lbl

    # ---------- acciones inferiores ----------
    actions = tk.Frame(contenido, bg="white")
    actions.pack(fill="x", pady=12)

    def guardar():
        # validar nombre/apellidos
        matricula = txt_id.get()
        nombre = txt_nombre.get().strip()
        ap = txt_paterno.get().strip()
        am = txt_materno.get().strip()
        if not nombre or not ap:
            messagebox.showerror("Error", "Nombre y Apellido Paterno son obligatorios.")
            return

        def leer(widget):
            """Lee cualquier widget: Entry, Combobox, StringVar, ComboConAgregar."""
            if widget is None:
                return ""

            # Casos especiales
            if hasattr(widget, "get_text"):
                return widget.get_text().strip()

            if hasattr(widget, "get"):
                try:
                    return widget.get().strip()
                except:
                    pass

            # ComboConAgregar tiene widget.cmb
            if hasattr(widget, "cmb"):
                try:
                    return widget.cmb.get().strip()
                except:
                    pass

            return ""

        
        # --- DEFAULTS desde BD (fallebacks) ---
        cb_grupo_val     = bd_safe_get(escolares,0) or ""
        cb_especialidad_val    = bd_safe_get(escolares,1) or ""

        genero_val       = bd_safe_get(generales,0) or ""
        fecha_nac_val    = bd_safe_get(generales,1)
        correo_val       = bd_safe_get(generales,2) or ""
        curp_val         = bd_safe_get(generales,3) or ""

        fam_nombre_val = bd_safe_get(familiares,0) or ""
        fam_cel_val    = bd_safe_get(familiares,5) or ""

        calle_val       = bd_safe_get(direccion,0) or ""
        numero_val      = bd_safe_get(direccion,1) or ""
        estado_val      = bd_safe_get(direccion,2) or ""
        municipio_val   = bd_safe_get(direccion,3) or ""
        cp_val          = bd_safe_get(direccion,4) or ""
        tel_dir_val     = bd_safe_get(direccion,5) or ""
        colonia_val     = bd_safe_get(direccion,6) or ""

        # --- Sobrescribir con valores actuales de los widgets (si existen) ---
        # para cada panel construido, tomar sus widgets/atributos
        for name, panel in panels.items():
            if not built.get(name):
                continue
            # ESCOLARES
            if name == "Escolares":
                if hasattr(panel, "cb_grupo"):
                    g = panel.cb_grupo.get()
                    cb_grupo_val = g if g else cb_grupo_val
                if cb_grupo_val.startswith(("Quinto/", "Sexto/")):
                    if hasattr(panel, "cb_especialidad"):
                        v = panel.cb_especialidad.get()
                        cb_especialidad_val = v if v else cb_especialidad_val
                else:
                    cb_especialidad_val = None

            # GENERALES
            if name == "Generales":
                if hasattr(panel, "genero_cmb"):
                    genero_val = panel.genero_cmb.get()
                if hasattr(panel, "dp_fecha_nac"):
                    v = panel.dp_fecha_nac.get_text()
                    fecha_nac_val = v if v else fecha_nac_val
                if hasattr(panel, "entry_correo"):
                    correo_val = panel.entry_correo.get().strip()
                if hasattr(panel, "entry_curp"):
                    curp_val = panel.entry_curp.get().strip()
            # FAMILIARES
            if name == "Familiares":
                if hasattr(panel, "entry_fam_nombre"):
                    fam_nombre_val = panel.entry_fam_nombre.get().strip()
                if hasattr(panel, "entry_fam_cel"):
                    fam_cel_val = panel.entry_fam_cel.get().strip()
            # DIRECCIÓN
            if name == "Dirección":
                if hasattr(panel, "entry_calle"):
                    calle_val = panel.entry_calle.get().strip()
                if hasattr(panel, "entry_numero"):
                    numero_val = panel.entry_numero.get().strip()
                if hasattr(panel, "cb_estado"):
                    estado_val = leer(panel.cb_estado)
                if hasattr(panel, "cb_municipio"):
                    municipio_val = leer(panel.cb_municipio)
                if hasattr(panel, "entry_cp"):
                    cp_val = panel.entry_cp.get().strip()
                if hasattr(panel, "entry_telefono_dir"):
                    tel_dir_val = panel.entry_telefono_dir.get().strip()
                if hasattr(panel, "entry_colonia"):
                    colonia_val = panel.entry_colonia.get().strip()

        if not fecha_nac_val:
            messagebox.showerror("Error", "La fecha de nacimiento es obligatoria.")
            select_tab("Generales")
            return
        
        if not genero_val:
            messagebox.showerror("Error", "El genero es obligatoria.")
            select_tab("Generales")
            return

        # --- GUARDAR / UPSERT TODOS LOS DATOS ---
        conn = obtener_conexion()
        cur = conn.cursor()


        # =====================================================
        # REINSCRIPCIÓN
        # =====================================================
        if modo == "reinscripcion":
            # Validar que no exista ya en este ciclo
            cur.execute("""
                SELECT 1
                FROM DatosEscolares
                WHERE estudiante_id=? AND ciclo_id=?
            """, (id_alumno, ciclo_activo["id"]))

            if cur.fetchone():
                messagebox.showerror(
                    "Error",
                    "El alumno ya está inscrito en este ciclo."
                )
                return

            # Insertar nuevo registro escolar
            cur.execute("""
                INSERT INTO DatosEscolares (
                    estudiante_id,
                    ciclo_id,
                    grupo,
                    especialidad
                )
                VALUES (?, ?, ?, ?)
            """, (
                id_alumno,
                ciclo_activo["id"],
                cb_grupo_val,
                cb_especialidad_val
            ))

            # NUEVO
            asignar_materias_automaticamente(
                cur,
                id_alumno,
                ciclo_activo["id"],
                cb_grupo_val,
                cb_especialidad_val
            )

            conn.commit()

            messagebox.showinfo(
                "Éxito",
                "Reinscripción realizada correctamente."
            )
            return

        # =====================================================
        # INSCRIPCIÓN / EDICIÓN NORMAL
        # =====================================================
        # Estudiantes
        cur.execute("""
            UPDATE Estudiantes
            SET matricula=?, nombre=?, apellido_paterno=?, apellido_materno=?
            WHERE id=?
        """, (matricula, nombre, ap, am, id_alumno))

        # DatosEscolares
        cur.execute("""
            SELECT COUNT(*)
            FROM DatosEscolares
            WHERE estudiante_id=? AND ciclo_id=?
        """, (id_alumno, ciclo_activo["id"]))

        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO DatosEscolares (
                    estudiante_id,
                    ciclo_id,
                    grupo,
                    especialidad
                )
                VALUES (?, ?, ?, ?)
            """, (
                id_alumno,
                ciclo_activo["id"],
                cb_grupo_val,
                cb_especialidad_val
            ))
        else:
            cur.execute("""
                UPDATE DatosEscolares
                SET grupo=?, especialidad=?
                WHERE estudiante_id=? AND ciclo_id=?
            """, (
                cb_grupo_val,
                cb_especialidad_val,
                id_alumno,
                ciclo_activo["id"]
            ))

        # DatosGenerales
        cur.execute("""
            INSERT INTO DatosGenerales (
                estudiante_id, genero, fecha_nacimiento, correo, curp
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(estudiante_id) DO UPDATE SET
                genero=excluded.genero,
                fecha_nacimiento=excluded.fecha_nacimiento,
                correo=excluded.correo,
                curp=excluded.curp
        """, (
            id_alumno, genero_val, fecha_nac_val, correo_val, curp_val
        ))

        # DatosFamiliares
        cur.execute("""
            INSERT INTO DatosFamiliares (
                estudiante_id, nombre, celular
            )
            VALUES (?, ?, ?)
            ON CONFLICT(estudiante_id) DO UPDATE SET
                nombre=excluded.nombre,
                celular=excluded.celular
        """, (
            id_alumno, fam_nombre_val, fam_cel_val
        ))

        # DatosDireccion
        cur.execute("""
            INSERT INTO DatosDireccion (
                estudiante_id, calle, numero, estado,
                municipio, cp, telefono, colonia
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(estudiante_id) DO UPDATE SET
                calle=excluded.calle,
                numero=excluded.numero,
                estado=excluded.estado,
                municipio=excluded.municipio,
                cp=excluded.cp,
                telefono=excluded.telefono,
                colonia=excluded.colonia
        """, (
            id_alumno, calle_val, numero_val, estado_val,
            municipio_val, cp_val, tel_dir_val, colonia_val
        ))

        # Asignar materias automáticamente
        asignar_materias_automaticamente(
            cur,
            id_alumno,
            ciclo_activo["id"],
            cb_grupo_val,
            cb_especialidad_val
        )

        conn.commit()
        messagebox.showinfo("Éxito", "Datos guardados correctamente.")

    def salir(ciclo_activo):
        if modo == "reinscripcion":
            from .alumnos import mostrar_reinscripciones
            mostrar_reinscripciones(contenido, ciclo_activo)
        else:
            from .alumnos import mostrar_alumnos
            mostrar_alumnos(contenido, ciclo_activo)


    def eliminar_estudiante():
        matricula = txt_id.get()

        if not id_alumno:
            messagebox.showwarning("Aviso", "No hay estudiante seleccionado.")
            return

        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Desea eliminar el estudiante con matrícula {matricula}?\n\n"
            "⚠ Esta acción eliminará TODOS los datos relacionados y no se puede deshacer."
        )

        if not confirmacion:
            return

        try:
            conn = obtener_conexion()
            cur = conn.cursor()

            # Eliminar primero tablas relacionadas
            cur.execute("DELETE FROM DatosDireccion WHERE estudiante_id=?", (id_alumno,))
            cur.execute("DELETE FROM DatosFamiliares WHERE estudiante_id=?", (id_alumno,))
            cur.execute("DELETE FROM DatosGenerales WHERE estudiante_id=?", (id_alumno,))
            cur.execute("DELETE FROM DatosEscolares WHERE estudiante_id=?", (id_alumno,))
            
            # Finalmente eliminar estudiante
            cur.execute("DELETE FROM Estudiantes WHERE id=?", (id_alumno,))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Estudiante eliminado correctamente.")

            salir(ciclo_activo)

        except Exception as e:
            conn.rollback()
            conn.close()
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

    # botonos inferiores
    btn_guardar = tk.Button(actions, text="Guardar", bg="#4caf50", fg="white", padx=16, pady=6, command=guardar)
    btn_guardar.pack(side="right", padx=8)
    btn_salir = tk.Button(actions, text="Salir", bg="#f44336", fg="white", padx=16, pady=6, command=lambda: salir(ciclo_activo)) 
    btn_salir.pack(side="right")

    btn_eliminar = tk.Button(
        actions,
        text="Eliminar estudiante",
        bg="#9e9e9e",
        fg="white",
        padx=16,
        pady=6,
        command=lambda: eliminar_estudiante()
    )
    btn_eliminar.pack(side="left", padx=8)

    # por defecto activar Escolares
    select_tab("Escolares")
    # pintar visual inicial
    for n, lbl in tab_buttons.items():
        lbl.config(bg=COLOR_NORMAL)
    tab_buttons["Escolares"].config(bg=COLOR_SELEC, relief="raised")
