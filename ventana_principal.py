import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db.conexion import obtener_todos
from db.configuracion import guardar_ultimo_ciclo, obtener_ultimo_ciclo, guardar_ultima_escuela, obtener_ultima_escuela

from alumnado.alumnos import mostrar_alumnos, mostrar_reinscripciones
from alumnado.admisiones import mostrar_inscripcion

from academico.materias import mostrar_materias
from academico.especialidades import mostrar_especialidades
from academico.estado_academico import mostrar_estado
from academico.calificaciones import mostrar_calificaciones
from academico.extraordinarios import mostrar_extraordinarios
from academico.equivalencia import mostrar_equivalencia
from academico.reportes import mostrar_reportes_academico

from admin.escuela import mostrar_escuela
from admin.ciclos import mostrar_ciclos
from admin.grupos import mostrar_grupos


# =====================================================
# OBTENER CICLO GUARDADO
# =====================================================
def obtener_ciclo_inicial():
    ultimo_id = obtener_ultimo_ciclo()
    if ultimo_id:
        fila = obtener_todos(
            "SELECT id, ciclo FROM ciclos WHERE id=?",
            (ultimo_id,)
        )
        if fila:
            return {"id": fila[0][0], "nombre": fila[0][1]}
    return {"id": None, "nombre": "No seleccionado"}

def obtener_escuela_inicial():
    ultimo_id = obtener_ultima_escuela()
    if ultimo_id:
        fila = obtener_todos(
            "SELECT id, nombre FROM Escuela WHERE id=?",
            (ultimo_id,)
        )
        if fila:
            return {"id": fila[0][0], "nombre": fila[0][1]}

    # fallback: primera escuela
    fila = obtener_todos(
        "SELECT id, nombre FROM Escuela ORDER BY id LIMIT 1"
    )
    if fila:
        return {"id": fila[0][0], "nombre": fila[0][1]}

    return {"id": None, "nombre": "No seleccionada"}

def es_supervisor(usuario_id):
    r = obtener_todos(
        """
        SELECT 1
        FROM usuarios_roles ur
        JOIN roles r ON r.id = ur.rol_id
        WHERE ur.usuario_id=? AND r.nombre='Supervisor'
        """,
        (usuario_id,)
    )
    return bool(r)

def tiene_permiso(usuario_id, modulo, permiso):
    if es_supervisor(usuario_id):
        return True

    r = obtener_todos(
        """
        SELECT 1
        FROM usuarios_permisos
        WHERE usuario_id=? AND modulo=? AND permiso=?
        """,
        (usuario_id, modulo, permiso)
    )
    return bool(r)



# =====================================================
# VENTANA PRINCIPAL
# =====================================================
def abrir_ventana_principal(usuario_id):
    ventana = tk.Tk()
    ventana.title("Control Escolar")
    ancho = 1000
    alto = 650

    ventana.update_idletasks()

    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    ventana.configure(bg="#f0f0f0")

    fila_usuario = obtener_todos(
        "SELECT usuario FROM usuarios WHERE id=?",
        (usuario_id,)
    )

    usuario = fila_usuario[0][0] if fila_usuario else "Desconocido"

    # =================================================
    # FRAME PRINCIPAL
    # =================================================
    principal_frame = tk.Frame(ventana, bg="#f0f0f0")
    principal_frame.pack(side="top", fill="both", expand=True)

    # Menú lateral
    menu_frame = tk.Frame(principal_frame, width=240, bg="#2c3e50")
    menu_frame.pack(side="left", fill="y")

    # Área de contenido
    contenido = tk.Frame(principal_frame, bg="white")
    contenido.pack(side="right", fill="both", expand=True)

    # =================================================
    # CICLO ACTIVO Y ESCUELA ACTIVA
    # =================================================
    ciclo_activo = obtener_ciclo_inicial()

    escuela_activa = obtener_escuela_inicial()

    # =================================================
    # STATUS BAR
    # =================================================
    status = tk.Frame(ventana, bg="#dcdcdc", height=25)
    status.pack(side="bottom", fill="x")

    fecha = datetime.now().strftime("%d-%m-%Y")

    lbl_fecha = tk.Label(
        status,
        bg="#dcdcdc",
        font=("Segoe UI", 10),
        text=f"Fecha: {fecha}"
    )
    lbl_fecha.pack(side="left", padx=(10, 5))

    lbl_sep1 = tk.Label(status, text=" | ", bg="#dcdcdc")
    lbl_sep1.pack(side="left")

    lbl_usuario = tk.Label(
        status,
        bg="#dcdcdc",
        font=("Segoe UI", 10),
        text=f"Usuario: {usuario}"
    )
    lbl_usuario.pack(side="left", padx=5)

    lbl_sep2 = tk.Label(status, text=" | ", bg="#dcdcdc")
    lbl_sep2.pack(side="left")

    lbl_ciclo = tk.Label(
        status,
        bg="#dcdcdc",
        font=("Segoe UI", 10),
        cursor="hand2"
    )
    lbl_ciclo.pack(side="left", padx=5)

    lbl_sep3 = tk.Label(status, text=" | ", bg="#dcdcdc")
    lbl_sep3.pack(side="left")

    lbl_escuela = tk.Label(
        status,
        bg="#dcdcdc",
        font=("Segoe UI", 10),
        cursor="hand2"
    )
    lbl_escuela.pack(side="left", padx=5)


    def actualizar_status_bar(ciclo_dict):
        lbl_ciclo.config(
            text=f"Ciclo seleccionado: {ciclo_dict['nombre']}"
        )
        lbl_escuela.config(
            text=f"Escuela: {escuela_activa['nombre']}"
        )
    
    actualizar_status_bar(ciclo_activo)

    # =================================================
    # FUNCIÓN TEXTO SIMPLE
    # =================================================
    def mostrar_texto(texto):
        for widget in contenido.winfo_children():
            widget.destroy()
        lbl = tk.Label(contenido, text=texto, font=("Segoe UI", 18), bg="white")
        lbl.pack(pady=30)

    # =================================================
    # SELECTOR DE CICLOS
    # =================================================
    def abrir_selector_ciclos():
        top = tk.Toplevel(ventana)
        top.title("Seleccionar ciclo escolar")
        top.resizable(False, False)

        ancho, alto = 650, 320
        x = ventana.winfo_rootx() + (ventana.winfo_width() // 2) - (ancho // 2)
        y = ventana.winfo_rooty() + (ventana.winfo_height() // 2) - (alto // 2)
        top.geometry(f"{ancho}x{alto}+{x}+{y}")

        top.transient(ventana)
        top.grab_set()
        top.focus_force()

        tree = ttk.Treeview(
            top,
            columns=("id", "ciclo", "inicio", "fin", "status"),
            show="headings"
        )

        tree.heading("id", text="ID")
        tree.heading("ciclo", text="Ciclo")
        tree.heading("inicio", text="Inicio")
        tree.heading("fin", text="Fin")
        tree.heading("status", text="Status")

        tree.column("id", width=50, anchor="center")
        tree.column("ciclo", width=200)
        tree.column("inicio", width=100, anchor="center")
        tree.column("fin", width=100, anchor="center")
        tree.column("status", width=120, anchor="center")

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        filas = obtener_todos(
            "SELECT id, ciclo, inicio, fin, status FROM ciclos WHERE status = 'Montado' ORDER BY inicio ASC"
        )

        for fila in filas:
            item = tree.insert("", "end", values=fila)
            if fila[4] == "Desmontado":
                tree.item(item, tags=("desmontado",))

        tree.tag_configure("desmontado", foreground="#888888")

        def seleccionar(event):
            sel = tree.selection()
            if not sel:
                return

            valores = tree.item(sel[0], "values")
            ciclo_id = valores[0]
            ciclo_nombre = valores[1]
            status = valores[4]

            if status == "Desmontado":
                messagebox.showwarning(
                    "Ciclo no disponible",
                    "Este ciclo está desmontado y no puede ser seleccionado."
                )
                return

            guardar_ultimo_ciclo(ciclo_id)

            ciclo_activo["id"] = ciclo_id
            ciclo_activo["nombre"] = ciclo_nombre

            for w in contenido.winfo_children():
                w.destroy()

            mostrar_texto("Ciclo cambiado correctamente")

            actualizar_status_bar(ciclo_activo)
            top.destroy()

        tree.bind("<Double-1>", seleccionar)

    def abrir_selector_escuela():
        top = tk.Toplevel(ventana)
        top.title("Seleccionar escuela")
        top.resizable(False, False)

        ancho, alto = 600, 300
        x = ventana.winfo_rootx() + (ventana.winfo_width() // 2) - (ancho // 2)
        y = ventana.winfo_rooty() + (ventana.winfo_height() // 2) - (alto // 2)
        top.geometry(f"{ancho}x{alto}+{x}+{y}")

        top.transient(ventana)
        top.grab_set()
        top.focus_force()

        tree = ttk.Treeview(
            top,
            columns=("id", "nombre", "RFC", "direccion"),
            show="headings"
        )

        tree.heading("id", text="ID")
        tree.heading("nombre", text="Escuela")
        tree.heading("RFC", text="RFC")
        tree.heading("direccion", text="Dirección")

        tree.column("id", width=50, anchor="center")
        tree.column("nombre", width=220)
        tree.column("RFC", width=100)
        tree.column("direccion", width=300)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        filas = obtener_todos(
            "SELECT id, nombre, RFC, direccion FROM Escuela ORDER BY nombre"
        )

        for fila in filas:
            tree.insert("", "end", values=fila)

        def seleccionar(event):
            sel = tree.selection()
            if not sel:
                return

            valores = tree.item(sel[0], "values")
            escuela_activa["id"] = valores[0]
            escuela_activa["nombre"] = valores[1]

            guardar_ultima_escuela(valores[0])

            actualizar_status_bar(ciclo_activo)

            for w in contenido.winfo_children():
                w.destroy()

            mostrar_texto("Escuela seleccionada correctamente")
            top.destroy()

        tree.bind("<Double-1>", seleccionar)


    lbl_ciclo.bind("<Double-Button-1>", lambda e: abrir_selector_ciclos())
    lbl_escuela.bind("<Double-Button-1>", lambda e: abrir_selector_escuela())
    # =================================================
    # ESTILOS
    # =================================================
    estilo = ttk.Style()
    estilo.configure("TButton", font=("Segoe UI", 11), padding=6)
    estilo.configure("TMenubutton", font=("Segoe UI", 11), padding=6)

    def crear_menuboton(texto, parent):
        wrapper = tk.Frame(parent, bg="#2c3e50")
        wrapper.pack(pady=10)

        btn = ttk.Menubutton(
            wrapper,
            text=texto,
            width=18,
            cursor="hand2"
        )
        btn.pack()

        menu = tk.Menu(btn, tearoff=0)
        btn["menu"] = menu

        return btn, menu

    # =================================================
    # MENÚ ALUMNADO
    # =================================================
    mb_control, menu_control = crear_menuboton("Alumnado", menu_frame)

    # ----- Admisiones -----
    admisiones_menu = tk.Menu(menu_control, tearoff=0)

    if tiene_permiso(usuario_id, "Alumnado", "Altas"):
        admisiones_menu.add_command(
            label="Altas",
            command=lambda: mostrar_inscripcion(contenido, ciclo_activo)
        )

    if tiene_permiso(usuario_id, "Alumnado", "Reinscripciones"):
        admisiones_menu.add_command(
            label="Reinscripciones",
            command=lambda: mostrar_reinscripciones(contenido, ciclo_activo)
        )

    if admisiones_menu.index("end") is not None:
        menu_control.add_cascade(label="Admisiones", menu=admisiones_menu)

    # ----- Otros -----
    if tiene_permiso(usuario_id, "Alumnado", "Alumnos"):
        menu_control.add_command(
            label="Alumnos",
            command=lambda: mostrar_alumnos(contenido, ciclo_activo)
        )

    # =================================================
    # MENÚ ACADÉMICO
    # =================================================
    mb_academico, menu_academico = crear_menuboton("Académico", menu_frame)

    academico_menu = tk.Menu(menu_academico, tearoff=0)

    if tiene_permiso(usuario_id, "Academico", "Materias"):
        menu_academico.add_command(
            label="Materias",
            command=lambda: mostrar_materias(contenido, ciclo_activo)
        )
    
    if tiene_permiso(usuario_id, "Academico", "Especialidades"):
        menu_academico.add_command(
            label="Especialidades",
            command=lambda: mostrar_especialidades(contenido, ciclo_activo)
        )

    if tiene_permiso(usuario_id, "Academico", "Estado"):
        menu_academico.add_command(
            label="Estado Académico",
            command=lambda: mostrar_estado(contenido, ciclo_activo)
        )
    
    
    if tiene_permiso(usuario_id, "Academico", "Ordinario"):
        academico_menu.add_command(
            label="Ordinario",
            command=lambda: mostrar_calificaciones(contenido, ciclo_activo)
        )
    
    if tiene_permiso(usuario_id, "Academico", "Extraordinarios y más"):
        academico_menu.add_command(
            label="Extraordinarios",
            command=lambda: mostrar_extraordinarios(contenido, ciclo_activo)
        )
    
    if tiene_permiso(usuario_id, "Academico", "Equivalencia"):
        academico_menu.add_command(
            label="Equivalencia",
            command=lambda: mostrar_equivalencia(contenido, ciclo_activo)
        )
    
    if academico_menu.index("end") is not None:
        menu_academico.add_cascade(label="Calificaciones", menu=academico_menu)
    
    if tiene_permiso(usuario_id, "Academico", "Reportes"):
        menu_academico.add_command(
            label="Reportes",
            command=lambda: mostrar_reportes_academico(contenido, ciclo_activo)
        )
    

    
    # =================================================
    # MENÚ ADMIN
    # =================================================
    mb_admin, menu_admin = crear_menuboton("Admin", menu_frame)

    colegio_menu = tk.Menu(menu_admin, tearoff=0)


    if tiene_permiso(usuario_id, "Admin", "Escuela"):
        colegio_menu.add_command(
            label="Escuela",
            command=lambda: mostrar_escuela(contenido)
        )

    if tiene_permiso(usuario_id, "Admin", "Ciclos"):
        colegio_menu.add_command(
            label="Ciclos",
            command=lambda: mostrar_ciclos(contenido, ciclo_activo)
        )

    if tiene_permiso(usuario_id, "Admin", "Grupos"):
        colegio_menu.add_command(
            label="Grupos",
            command=lambda: mostrar_grupos(contenido)
        )

    if colegio_menu.index("end") is not None:
        menu_admin.add_cascade(label="Colegio", menu=colegio_menu)

    # if tiene_permiso(usuario_id, "Admin", "Usuarios"):
    #     menu_admin.add_command(
    #         label="Usuarios",
    #         command=lambda: mostrar_usuarios(contenido)
    #     )

    
    
    def confirmar_salida():
        top = tk.Toplevel(ventana)
        top.title("Salir del sistema")
        top.resizable(False, False)

        ancho, alto = 380, 240
        x = ventana.winfo_rootx() + (ventana.winfo_width() // 2) - (ancho // 2)
        y = ventana.winfo_rooty() + (ventana.winfo_height() // 2) - (alto // 2)
        top.geometry(f"{ancho}x{alto}+{x}+{y}")

        top.transient(ventana)
        top.grab_set()
        top.focus_force()

        cont = tk.Frame(top, padx=25, pady=20)
        cont.pack(fill="both", expand=True)

        tk.Label(
            cont,
            text="¿Qué desea hacer?",
            font=("Segoe UI", 13, "bold")
        ).pack(pady=(0, 15))

        opcion_var = tk.StringVar(value="salir")

        tk.Radiobutton(
            cont,
            text="Cambiar de usuario",
            variable=opcion_var,
            value="usuario"
        ).pack(anchor="w", pady=5)

        tk.Radiobutton(
            cont,
            text="Salir del sistema",
            variable=opcion_var,
            value="salir"
        ).pack(anchor="w", pady=5)

        botones = tk.Frame(cont)
        botones.pack(fill="x", pady=20)

        def aceptar():
            opcion = opcion_var.get()

            top.destroy()
            ventana.destroy()

            if opcion == "usuario":
                from main import abrir_login
                abrir_login()
            else:
                # Cierra completamente la aplicación
                return

        ttk.Button(
            botones,
            text="Aceptar",
            command=aceptar
        ).pack(side="right", padx=5)

        ttk.Button(
            botones,
            text="Cancelar",
            command=top.destroy
        ).pack(side="right")
    
    # =================================================
    # SALIR
    # =================================================
    btn_salir = ttk.Button(menu_frame, text="Salir", command=lambda: confirmar_salida())
    btn_salir.pack(side="bottom", pady=20)

    mostrar_texto("Bienvenido al Sistema de Control Escolar")

    ventana.mainloop()



