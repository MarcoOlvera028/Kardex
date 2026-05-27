import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from db.conexion import obtener_conexion
from .datepicker import DatePicker
from .ficha_alumno import mostrar_ficha_alumno

import re

def centrar_ventana(win, parent):
    win.update_idletasks()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()

    ww = win.winfo_width()
    wh = win.winfo_height()

    x = px + (pw // 2) - (ww // 2)
    y = py + (ph // 2) - (wh // 2)

    win.geometry(f"+{x}+{y}")


class ComboConAgregar(tk.Frame):
    def __init__(self, master, width=26, **kwargs):
        super().__init__(master, **kwargs, bg="white")

        self.cmb = ttk.Combobox(self, width=width, state="readonly")
        self.cmb.pack(side="left")

        self.btn = tk.Button(self, text="+", width=2, command=self.agregar)
        self.btn.pack(side="left", padx=4)

        self.actualizar_lista()

    def get(self):
        return self.cmb.get()

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

def agregar_estado(callback):
    win = tk.Toplevel()
    win.title("Agregar estado")
    win.geometry("340x150")
    win.resizable(False, False)
    win.grab_set()

    centrar_ventana(win, win.master)

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
            conn.close()
        except:
            messagebox.showerror("Error", "Ese estado ya existe.")
            return

        win.destroy()
        callback()

    tk.Button(win, text="Guardar", width=12, command=guardar).pack(pady=12)

def agregar_municipio(estado_id, callback):
    win = tk.Toplevel()
    win.title("Agregar municipio")
    win.geometry("340x150")
    win.resizable(False, False)
    win.grab_set()

    centrar_ventana(win, win.master)

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
        cur.execute("""
            INSERT INTO Municipios(nombre, estado_id)
            VALUES (?,?)
        """, (nombre, estado_id))
        conn.commit()
        conn.close()

        win.destroy()
        callback()

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


def mostrar_inscripcion(contenido, ciclo_activo):

    # limpiar pantalla
    for w in contenido.winfo_children():
        w.destroy()

    # ---------- HEADER ----------
    header = tk.Frame(contenido, bg="#d0e4f5", height=60)
    header.pack(fill="x")
    tk.Label(header, text="Nueva inscripción", bg="#d0e4f5",
             font=("Segoe UI", 16, "bold")).pack(pady=12)

    # ---------- BODY ----------
    body = tk.Frame(contenido, bg="white")
    body.pack(fill="both", expand=True, padx=20, pady=16)

    label_opts = {"bg":"white", "font":("Segoe UI",11)}
    entry_opts = {"bd":1, "relief":"solid"}

    # ID (no existe aún)
    tk.Label(body, text="Matrícula:", **label_opts).grid(row=0, column=0, sticky="e", padx=6, pady=8)
    txt_id = tk.Entry(body, width=12, **entry_opts)
    txt_id.grid(row=0, column=1, sticky="w", padx=6, pady=8)

    # NOMBRE
    tk.Label(body, text="Nombre:", **label_opts).grid(row=0, column=2, sticky="e", padx=6, pady=8)
    txt_nombre = tk.Entry(body, width=32, **entry_opts)
    txt_nombre.grid(row=0, column=3, sticky="w", padx=6, pady=8)

    tk.Label(body, text="Apellido Paterno:", **label_opts).grid(row=1, column=0, sticky="e", padx=6, pady=8)
    txt_paterno = tk.Entry(body, width=32, **entry_opts)
    txt_paterno.grid(row=1, column=1, sticky="w", padx=6, pady=8)

    tk.Label(body, text="Apellido Materno:", **label_opts).grid(row=1, column=2, sticky="e", padx=6, pady=8)
    txt_materno = tk.Entry(body, width=32, **entry_opts)
    txt_materno.grid(row=1, column=3, sticky="w", padx=6, pady=8)

    # separador
    tk.Frame(body, height=2, bg="#e0e0e0").grid(row=2, column=0, columnspan=4,
                                               sticky="we", pady=12)

    # -----------------------------
    #        SISTEMA DE PESTAÑAS
    # -----------------------------
    tab_bar = tk.Frame(body, bg="white")
    tab_bar.grid(row=3, column=0, columnspan=4, sticky="we", pady=(0,8))

    panels_container = tk.Frame(body, bg="white")
    panels_container.grid(row=4, column=0, columnspan=4, sticky="nsew")
    body.grid_rowconfigure(4, weight=1)
    body.grid_columnconfigure(3, weight=1)

    COLOR_SELEC = "#ffffff"
    COLOR_NORMAL = "#ececec"

    tab_buttons = {}
    panels = {}

    # -----------------------------
    #     ESCOLARES
    # -----------------------------
    def build_escolares():
        if "Escolares" in panels:
            return panels["Escolares"]

        f = tk.Frame(panels_container, bg="white")

        # ==========================
        # GRUPO
        # ==========================
        tk.Label(f, text="Grupo:", bg="white").grid(
            row=0, column=0, sticky="e", pady=8, padx=8
        )

        cb_grupo = ttk.Combobox(
            f,
            values=cargar_grupos(),
            state="readonly",
            width=26
        )
        cb_grupo.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        # ==========================
        # ESPECIALIDAD (OCULTA)
        # ==========================
        lbl_especialidad = tk.Label(f, text="Especialidad:", bg="white")
        cb_especialidad = ttk.Combobox(
            f,
            values=cargar_especialidades(),
            state="readonly",
            width=26
        )

        # No se hace grid aún → queda oculta

        # ==========================
        # EVENTO CAMBIO DE GRUPO
        # ==========================
        def on_grupo_change(event=None):
            grupo = cb_grupo.get()

            if grupo.startswith(("Quinto/", "Sexto/")):
                lbl_especialidad.grid(
                    row=1, column=0, sticky="e", pady=8, padx=8
                )
                cb_especialidad.grid(
                    row=1, column=1, padx=8, pady=8, sticky="w"
                )
            else:
                lbl_especialidad.grid_remove()
                cb_especialidad.grid_remove()
                cb_especialidad.set("")

        cb_grupo.bind("<<ComboboxSelected>>", on_grupo_change)

        # Guardar referencias
        f.cb_grupo = cb_grupo
        f.cb_especialidad = cb_especialidad

        panels["Escolares"] = f
        return f

    # -----------------------------
    #     GENERALES
    # -----------------------------
    def build_generales():
        if "Generales" in panels:
            return panels["Generales"]
        f = tk.Frame(panels_container, bg="white")

        tk.Label(f, text="Género:", bg="white", font=("Segoe UI", 11)).grid(
            row=0, column=0, sticky="e", pady=8, padx=8
        )
        genero_cmb = ttk.Combobox(f, values=["masculino", "femenino"],
                                state="readonly", width=20)
        genero_cmb.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        tk.Label(f, text="Fecha nacimiento:",
                bg="white", font=("Segoe UI", 11)).grid(
            row=1, column=0, sticky="e", pady=8, padx=8
        )
        dp_fn = DatePicker(f, initial=date.today())
        dp_fn.grid(row=1, column=1, padx=8, pady=8, sticky="w")

        # Correo
        tk.Label(f, text="Correo:", bg="white", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="e", pady=8, padx=8)
        entry_correo = tk.Entry(f, width=28, **entry_opts)
        entry_correo.grid(row=2, column=1, padx=8, pady=8, sticky="w")

        # CURP
        tk.Label(f, text="CURP:", bg="white", font=("Segoe UI", 11)).grid(row=3, column=0, sticky="e", pady=8, padx=8)
        entry_curp = tk.Entry(f, width=28, **entry_opts)
        entry_curp.grid(row=3, column=1, padx=8, pady=8, sticky="w")

        f.genero_cmb = genero_cmb
        f.dp_fn = dp_fn
        f.entry_correo = entry_correo 
        f.entry_curp = entry_curp 

        panels["Generales"] = f
        return f

    # -----------------------------
    #    FAMILIARES
    # -----------------------------
    def build_familiares():
        if "Familiares" in panels:
            return panels["Familiares"]
        f = tk.Frame(panels_container, bg="white")

        labels = ["Nombre", "Celular"]

        entries = {}

        for i,lbl in enumerate(labels):
            tk.Label(f, text=lbl+":", bg="white", font=("Segoe UI", 11)).grid(row=i, column=0, sticky="e", pady=8, padx=8)

            e = tk.Entry(f, width=28, **entry_opts)
            e.grid(row=i, column=1, sticky="w", pady=8)
            entries[lbl] = e


        f.entries = entries
        panels["Familiares"] = f
        return f

    # -----------------------------
    #     DIRECCION
    # -----------------------------
    def build_direccion():
        if "Dirección" in panels:
            return panels["Dirección"]

        f = tk.Frame(panels_container, bg="white")

        # ================================
        # CAMPOS BASE
        # ================================
        labels = ["Calle", "Número", "C.P", "Teléfono", "Colonia"]
        entries = {}

        for idx, lbl in enumerate(labels):
            tk.Label(
                f, text=lbl + ":", bg="white",
                font=("Segoe UI", 11)
            ).grid(row=idx, column=0, sticky="e", pady=8, padx=8)

            e = tk.Entry(f, width=34, bd=1, relief="solid")
            e.grid(row=idx, column=1, sticky="w", pady=8)
            entries[lbl] = e

        # ================================
        # Cargar Estados desde BD
        # ================================
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT nombre FROM Estados ORDER BY nombre ASC")
        lista_estados = [row[0] for row in cur.fetchall()]
        conn.close()

        # ================================
        # ESTADO (Combobox + botón +)
        # ================================
        estados = cargar_estados()
        estados_dict = {nombre: id for id, nombre in estados}
        tk.Label(f, text="Estado:", bg="white", font=("Segoe UI", 11)).grid(
            row=5, column=0, sticky="e", pady=8, padx=8
        )

        cb_estado = ttk.Combobox(f, values=lista_estados, state="readonly", width=32)
        cb_estado.grid(row=5, column=1, sticky="w", pady=8)

        # Botón para añadir estados
        btn_estado_plus = tk.Button(
            f, text="+", width=3,
            command=lambda: agregar_estado(cb_estado)
        )
        btn_estado_plus.grid(row=5, column=2, sticky="w", padx=4)


        # ================================
        # MUNICIPIO (Dependiente + botón +)
        # ================================
        tk.Label(
            f,
            text="Municipio:",
            bg="white",
            font=("Segoe UI", 11)
        ).grid(
            row=6, column=0, sticky="e", pady=8, padx=8
        )

        cb_municipio = ttk.Combobox(
            f,
            values=[],
            state="readonly",
            width=32
        )
        cb_municipio.grid(
            row=6, column=1, sticky="w", pady=8
        )

        def abrir_agregar_municipio():
            estado_nombre = cb_estado.get()

            if not estado_nombre:
                messagebox.showwarning("Aviso", "Seleccione un estado primero")
                return

            estado_id = estados_dict[estado_nombre]

            def recargar_municipios():
                municipios = cargar_municipios(estado_id)
                municipios_dict = {nombre: id for id, nombre in municipios}
                cb_municipio["values"] = list(municipios_dict.keys())
                cb_municipio.set("")

            agregar_municipio(estado_id, recargar_municipios)

        btn_municipio_plus = tk.Button(
            f,
            text="+",
            width=3,
            command=abrir_agregar_municipio
        )
        btn_municipio_plus.grid(
            row=6, column=2, sticky="w", padx=4
        )


        # ================================
        # Funciones dinámicas
        # ================================
        def actualizar_municipios(event=None):
            estado_sel = cb_estado.get()
            if not estado_sel:
                return

            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute(
                "SELECT nombre FROM Municipios WHERE estado_id = (SELECT id FROM Estados WHERE nombre=?) ORDER BY nombre ASC",
                (estado_sel,)
            )
            municipios = [row[0] for row in cur.fetchall()]
            conn.close()

            cb_municipio["values"] = municipios
            cb_municipio.set("")

        cb_estado.bind("<<ComboboxSelected>>", actualizar_municipios)

        # ================================
        # Guardar widgets
        # ================================
        entries["Estado"] = cb_estado
        entries["Municipio"] = cb_municipio

        f.entries = entries
        panels["Dirección"] = f
        return f

    # =============================
    # CREAR TODOS LOS PANELES
    # =============================
    build_escolares()
    build_generales()
    build_familiares()
    build_direccion()

    # ocultar todos inicialmente
    for p in panels.values():
        p.pack_forget()
    # --------------------------
    #  ACTIVAR PESTAÑA
    # --------------------------
    def select_tab(name):
        # actualizar estilos
        for n, l in tab_buttons.items():
            l.config(bg=COLOR_NORMAL, bd=1, relief="solid")
        tab_buttons[name].config(bg=COLOR_SELEC, bd=2, relief="solid")

        # ocultar todos
        for pnl in panels.values():
            pnl.pack_forget()

        # mostrar seleccionado
        p = panels[name]
        p.pack(fill="both", expand=True, padx=8, pady=8)
        panels_container.current_panel = p


    # crear labels pestañas
    # Botones de pestañas con borde visible
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


    # por defecto activar la pestaña "Escolares"
    select_tab("Escolares")

    # -----------------------------
    #    BOTON GUARDAR / SALIR
    # -----------------------------
    actions = tk.Frame(contenido, bg="white")
    actions.pack(fill="x", pady=12)

    # -----------------------------
    #     GUARDAR NUEVO ALUMNO
    # -----------------------------
    def guardar():
        conn = obtener_conexion()
        cur = conn.cursor()
        
        # VALIDAR CAMPOS GENERALES OBLIGATORIOS
        if not txt_nombre.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
        if not txt_paterno.get().strip():
            messagebox.showerror("Error", "El apellido paterno es obligatorio.")
            return

        # Recuperar valores ESCOLARES
        es = panels["Escolares"]
        grupo = es.cb_grupo.get().strip() or None
        especialidad = es.cb_especialidad.get().strip() or None

        # GENERALES
        ge = panels["Generales"]
        genero = ge.genero_cmb.get() or None
        fecha_nac = ge.dp_fn.get_text() or None
        correo = ge.entry_correo.get().strip() or None
        curp = ge.entry_curp.get().strip() or None

        if not genero:
            messagebox.showerror("Error", "El género es obligatorio.")
            select_tab("Generales")
            return
        
        if not fecha_nac:
            messagebox.showerror("Error", "La fecha de nacimiento es obligatoria.")
            select_tab("Generales")
            return

        # FAMILIARES
        fam = panels["Familiares"].entries
        f_nombre = fam["Nombre"].get().strip() or None
        f_cel = fam["Celular"].get().strip() or None


        # DIRECCIÓN
        dir = panels["Dirección"].entries
        calle = dir["Calle"].get().strip() or None
        numero = dir["Número"].get().strip() or None
        estado = dir["Estado"].get() or None
        municipio = dir["Municipio"].get() or None
        cp = dir["C.P"].get().strip() or None
        tel_dir = dir["Teléfono"].get().strip() or None
        colonia = dir["Colonia"].get().strip() or None

        # -----------------------------
        #       GUARDAR EN BD
        # -----------------------------
        # Crear alumno
        cur.execute("""
            INSERT INTO Estudiantes(matricula, nombre, apellido_paterno, apellido_materno)
            VALUES (?,?,?,?)
        """,(txt_id.get(), txt_nombre.get().strip(), txt_paterno.get().strip(),
             txt_materno.get().strip()))

        id_nuevo = cur.lastrowid

        # ESCOLARES
        cur.execute("""INSERT INTO DatosEscolares(estudiante_id, ciclo_id, grupo, especialidad)
            VALUES (?,?,?,?)
        """, (id_nuevo, ciclo_activo["id"], grupo, especialidad))


        # GENERALES
        cur.execute("""
            INSERT INTO DatosGenerales(estudiante_id, genero, fecha_nacimiento, correo, curp ) 
            VALUES (?,?,?,?,?) 
        """, (id_nuevo, genero, fecha_nac, correo, curp))


        # FAMILIARES
        cur.execute("""
            INSERT INTO DatosFamiliares(estudiante_id, nombre, celular)
            VALUES (?,?,?)
        """,(id_nuevo, f_nombre, f_cel))

        # DIRECCIÓN
        cur.execute("""
            INSERT INTO DatosDireccion(estudiante_id, calle, numero, estado,
            municipio, cp, telefono, colonia)
            VALUES (?,?,?,?,?,?,?,?)
        """,(id_nuevo, calle, numero, estado, municipio, cp, tel_dir, colonia))



         # -----------------------------------
        # INSERTAR MATERIAS EN ESTADO ACADEMICO
        # -----------------------------------

        # 1️⃣ Obtener ID real del grupo
        cur.execute("""
            SELECT id FROM Grados WHERE nombre = ?
        """, (grupo,))
        grupo_row = cur.fetchone()

        if grupo_row:
            grupo_id = grupo_row[0]

            # 2️⃣ Obtener materias que pertenecen a ese grupo
            cur.execute("""
                SELECT id FROM Materias
                WHERE grupo_id = ?
            """, (grupo_id,))
            materias = cur.fetchall()

            # 3️⃣ Insertar cada materia en EstadoAcademico
            for materia in materias:
                materia_id = materia[0]

                cur.execute("""
                    INSERT INTO EstadoAcademico (
                        alumno_id,
                        materia_id,
                        ciclo_id
                    )
                    VALUES (?, ?, ?)
                """, (
                    id_nuevo,
                    materia_id,
                    ciclo_activo["id"]
                ))
        
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Alumno registrado correctamente.")

        # mostrar ficha del alumno recién creado
        mostrar_ficha_alumno(id_nuevo, contenido, ciclo_activo)

    btn_guardar = tk.Button(actions, text="Guardar", bg="#4caf50",
                             fg="white", padx=16, pady=6, command=guardar)
    btn_guardar.pack(side="right", padx=8)

