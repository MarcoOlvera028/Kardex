import tkinter as tk
import tempfile
import os
import sys
import subprocess

from tkinter import ttk, messagebox
from datetime import date

from db.conexion import obtener_todos
from db.reportes_sql import construir_consulta

from alumnado.datepicker import DatePicker

from tkinter import filedialog
from utils.pdf_reportes import construir_pdf_en_memoria
from utils.pdf_boleta import generar_pdf_boleta, generar_pdf_kardex, generar_pdf_reprobados, generar_excel_boleta_materia, generar_excel_plantilla


def mostrar_reportes_academico(parent, ciclo_activo):

    for w in parent.winfo_children():
        w.destroy()

    contenedor = tk.Frame(parent, bg="white")
    contenedor.pack(fill="both", expand=True)

    # =========================
    # HEADER
    # =========================
    header = tk.Frame(contenedor, bg="#d0e4f5", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text=f"Reportes – Ciclo {ciclo_activo['nombre']}",
        bg="#d0e4f5",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    # =========================
    # NOTEBOOK
    # =========================
    notebook = ttk.Notebook(contenedor)
    notebook.pack(fill="both", expand=True, padx=15, pady=15)

    # =========================
    # DATOS BD
    # =========================

    alumnos = obtener_todos("""
        SELECT 
            E.id,
            E.nombre || ' ' || E.apellido_paterno || ' ' || E.apellido_materno
        FROM Estudiantes E
        JOIN DatosEscolares D
            ON D.estudiante_id = E.id
        WHERE D.ciclo_id = ?
        ORDER BY E.nombre
    """, (ciclo_activo["id"],))

    alumnos_dict = {a[1]: a[0] for a in alumnos}

    grupos = obtener_todos("""
        SELECT DISTINCT grupo
        FROM DatosEscolares
        WHERE ciclo_id = ?
        ORDER BY grupo
    """, (ciclo_activo["id"],))

    grupos_lista = [g[0] for g in grupos]

    # =========================
    # PESTAÑA BOLETA
    # =========================

    tab_boleta = tk.Frame(notebook, bg="white")
    notebook.add(tab_boleta, text="Boleta del alumno")


    frame_filtros = tk.Frame(tab_boleta, bg="white")
    frame_filtros.pack(fill="x", padx=20, pady=20)

    tk.Label(
        frame_filtros,
        text="Alumno:",
        bg="white",
        font=("Segoe UI", 11)
    ).pack(side="left", padx=(0,10))

    combo_alumno = ttk.Combobox(
        frame_filtros,
        values=list(alumnos_dict.keys()),
        width=50
    )

    combo_alumno.pack(side="left")


    def filtrar_alumnos(event):

        texto = combo_alumno.get().lower()

        filtrados = [
            nombre for nombre in alumnos_dict.keys()
            if texto in nombre.lower()
        ]

        combo_alumno["values"] = filtrados


    combo_alumno.bind("<KeyRelease>", filtrar_alumnos)


    # Frame inferior fijo para el botón
    frame_btn = tk.Frame(tab_boleta, bg="white")
    frame_btn.pack(side="bottom", fill="x", pady=10)

    btn_generar = tk.Button(
        frame_btn,
        text="Generar",
        bg="#2e86c1",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=12,
        command=lambda: generar_boleta()
    )

    btn_generar.pack(anchor="e", padx=20, pady=10)

    def generar_boleta():

        alumno_nombre = combo_alumno.get()

        if alumno_nombre not in alumnos_dict:
            messagebox.showwarning("Aviso", "Seleccione un alumno válido")
            return

        alumno_id = alumnos_dict[alumno_nombre]

        datos = obtener_todos("""
            SELECT
                M.nombre,
                EA.parcial1,
                EA.parcial2,
                EA.parcial3,
                EA.final,
                EA.fecha,
                EA.fecha_equivalencia,
                C.ciclo
            FROM EstadoAcademico EA
            JOIN Materias M
                ON M.id = EA.materia_id
            JOIN Ciclos C
                ON C.id = EA.ciclo_id
            WHERE EA.alumno_id = ? AND EA.ciclo_id = ?
        """, (alumno_id, ciclo_activo["id"]))


        filas = []

        for m, p1, p2, p3, final, fecha, fecha_eq, ciclo in datos:

            if fecha:
                tipo = "EO"
                periodo = fecha

            elif fecha_eq:
                tipo = "E"
                periodo = fecha_eq

            else:
                tipo = "O"
                periodo = ciclo

            filas.append([
                m,
                p1,
                p2,
                p3,
                final,
                tipo,
                periodo
            ])


        datos_escolares = obtener_todos("""
            SELECT grupo, especialidad
            FROM DatosEscolares
            WHERE estudiante_id = ?
        """, (alumno_id,))

        grupo = ""
        especialidad = ""

        if datos_escolares:
            grupo = datos_escolares[0][0]
            especialidad = datos_escolares[0][1] or ""

        grado = grupo.split("/")[0] if grupo else ""

        if grado not in ("Quinto", "Sexto"):
            especialidad = ""

        dato_matricula = obtener_todos("""
            SELECT matricula
            FROM Estudiantes
            WHERE id = ?
        """, (alumno_id,))

        matricula = ""

        if dato_matricula:
            matricula = dato_matricula

        pdf_bytes = generar_pdf_boleta(
            alumno_nombre,
            matricula,
            grupo,
            especialidad,
            filas
        )

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(pdf_bytes)
        tmp.close()

        if sys.platform == "win32":
            os.startfile(tmp.name)
        else:
            import subprocess
            subprocess.Popen(["xdg-open", tmp.name])

    # =========================
    # PESTAÑA KARDEX
    # =========================

    tab_kardex = tk.Frame(notebook, bg="white")
    notebook.add(tab_kardex, text="Kardex del alumno")


    # obtener TODOS los alumnos
    alumnos_kardex = obtener_todos("""
        SELECT
            id,
            nombre || ' ' || apellido_paterno || ' ' || apellido_materno
        FROM Estudiantes
        ORDER BY nombre
    """)

    alumnos_kardex_dict = {a[1]: a[0] for a in alumnos_kardex}


    frame_kardex = tk.Frame(tab_kardex, bg="white")
    frame_kardex.pack(fill="x", padx=20, pady=20)

    tk.Label(
        frame_kardex,
        text="Alumno:",
        bg="white",
        font=("Segoe UI",11)
    ).pack(side="left", padx=(0,10))

    combo_kardex = ttk.Combobox(
        frame_kardex,
        values=list(alumnos_kardex_dict.keys()),
        width=50
    )

    combo_kardex.pack(side="left")


    def filtrar_kardex(event):

        texto = combo_kardex.get().lower()

        filtrados = [
            nombre for nombre in alumnos_kardex_dict.keys()
            if texto in nombre.lower()
        ]

        combo_kardex["values"] = filtrados


    combo_kardex.bind("<KeyRelease>", filtrar_kardex)


    frame_btn_kardex = tk.Frame(tab_kardex, bg="white")
    frame_btn_kardex.pack(side="bottom", fill="x", pady=10)

    btn_generar_kardex = tk.Button(
        frame_btn_kardex,
        text="Generar",
        bg="#2e86c1",
        fg="white",
        font=("Segoe UI",11,"bold"),
        width=12,
        command=lambda: generar_kardex()
    )

    btn_generar_kardex.pack(anchor="e", padx=20, pady=10)


    def generar_kardex():

        escuela = obtener_todos("""
            SELECT nombre, rfc, direccion
            FROM Escuela
            LIMIT 1
        """)[0]

        escuela = {
            "nombre": escuela[0],
            "rfc": escuela[1],
            "direccion": escuela[2]
        }

        alumno_nombre = combo_kardex.get()

        if alumno_nombre not in alumnos_kardex_dict:
            messagebox.showwarning("Aviso","Seleccione un alumno válido")
            return

        alumno_id = alumnos_kardex_dict[alumno_nombre]

        datos = obtener_todos("""
            SELECT
                D.grupo,
                D.especialidad,
                M.clave,
                M.nombre,
                EA.final,
                EA.fecha,
                EA.fecha_equivalencia,
                C.ciclo
            FROM EstadoAcademico EA
            JOIN Materias M
                ON M.id = EA.materia_id
            JOIN Ciclos C
                ON C.id = EA.ciclo_id
            JOIN DatosEscolares D
                ON D.estudiante_id = EA.alumno_id
                AND D.ciclo_id = EA.ciclo_id
            WHERE EA.alumno_id = ?
        """,(alumno_id,))


        orden_grados = {
            "Primero":1,
            "Segundo":2,
            "Tercero":3,
            "Cuarto":4,
            "Quinto":5,
            "Sexto":6
        }


        datos_por_grupo = {}

        suma_general = 0
        count_general = 0


        for grupo, especialidad, clave, materia, final, fecha, fecha_eq, ciclo in datos:

            if fecha:
                tipo = "EO"
                periodo = fecha
            elif fecha_eq:
                tipo = "E"
                periodo = fecha_eq
            else:
                tipo = "O"
                periodo = ciclo


            if grupo not in datos_por_grupo:
                datos_por_grupo[grupo] = {
                    "filas": [],
                    "finales": [],
                    "especialidad": especialidad
                }


            datos_por_grupo[grupo]["filas"].append([
                clave,
                materia,
                final,
                tipo,
                periodo
            ])


            if final:
                datos_por_grupo[grupo]["finales"].append(final)
                suma_general += final
                count_general += 1


        for grupo in datos_por_grupo:

            finales = datos_por_grupo[grupo]["finales"]

            promedio = sum(finales)/len(finales) if finales else 0

            datos_por_grupo[grupo]["promedio"] = promedio


        datos_ordenados = dict(
            sorted(
                datos_por_grupo.items(),
                key=lambda x: orden_grados.get(x[0].split("/")[0],99)
            )
        )


        promedio_general = suma_general/count_general if count_general else 0


        pdf_bytes = generar_pdf_kardex(
            alumno_nombre,
            escuela,
            datos_ordenados,
            promedio_general
        )


        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(pdf_bytes)
        tmp.close()

        if sys.platform == "win32":
            os.startfile(tmp.name)
        else:
            subprocess.Popen(["xdg-open", tmp.name])




    # =========================
    # PESTAÑA REPROBADOS
    # =========================

    tab_reprobados = tk.Frame(notebook, bg="white")
    notebook.add(tab_reprobados, text="Alumnos reprobados")

    frame_filtros_rep = tk.Frame(tab_reprobados, bg="white")
    frame_filtros_rep.pack(fill="x", padx=20, pady=20)


    # =========================
    # COMBO GRADO
    # =========================

    tk.Label(
        frame_filtros_rep,
        text="Grado:",
        bg="white",
        font=("Segoe UI",11)
    ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

    grados = obtener_todos("""
        SELECT id, nombre
        FROM Grados
        ORDER BY orden
    """)

    grados_dict = {g[1]: g[0] for g in grados}

    lista_grados = ["Todos los grados"] + list(grados_dict.keys())

    combo_grado = ttk.Combobox(
        frame_filtros_rep,
        values=lista_grados,
        width=25,
        state="readonly"
    )

    combo_grado.grid(row=0, column=1, padx=10, pady=5)


    # =========================
    # COMBO GRUPO
    # =========================

    tk.Label(
        frame_filtros_rep,
        text="Grupo:",
        bg="white",
        font=("Segoe UI",11)
    ).grid(row=0, column=2, padx=5, pady=5, sticky="w")

    combo_grupo = ttk.Combobox(
        frame_filtros_rep,
        width=25,
        state="readonly"
    )

    combo_grupo.grid(row=0, column=3, padx=10, pady=5)


    # =========================
    # CARGAR GRUPOS SEGÚN GRADO
    # =========================

    def cargar_grupos(event):

        grado_nombre = combo_grado.get()

        # Caso: Todos los grados
        if grado_nombre == "Todos los grados":

            combo_grupo["values"] = ["Todos los grupos"]
            combo_grupo.set("Todos los grupos")
            return

        if grado_nombre not in grados_dict:
            return

        grado_id = grados_dict[grado_nombre]

        grupos = obtener_todos("""
            SELECT grupo
            FROM Grupos
            WHERE grado_id = ?
            ORDER BY grupo
        """,(grado_id,))

        lista_grupos = ["Todos los grupos"] + [g[0] for g in grupos]

        combo_grupo["values"] = lista_grupos


    combo_grado.bind("<<ComboboxSelected>>", cargar_grupos)


    # =========================
    # BOTÓN GENERAR
    # =========================

    frame_btn_rep = tk.Frame(tab_reprobados, bg="white")
    frame_btn_rep.pack(side="bottom", fill="x", pady=10)


    btn_generar_rep = tk.Button(
        frame_btn_rep,
        text="Generar",
        bg="#2e86c1",
        fg="white",
        font=("Segoe UI",11,"bold"),
        width=12,
        command=lambda: generar_reprobados()
    )

    btn_generar_rep.pack(anchor="e", padx=20, pady=10)


    # =========================
    # FUNCIÓN
    # =========================

    def generar_reprobados():

        grado = combo_grado.get()
        grupo = combo_grupo.get()

        if not grado:
            messagebox.showwarning(
                "Aviso",
                "Seleccione grado y grupo"
            )
            return

        # =========================
        # DATOS ESCUELA
        # =========================

        escuela = obtener_todos("""
            SELECT nombre, rfc, direccion
            FROM Escuela
            LIMIT 1
        """)[0]

        escuela = {
            "nombre": escuela[0],
            "rfc": escuela[1],
            "direccion": escuela[2]
        }

        # =========================
        # CONSULTA REPROBADOS
        # =========================

        if grado == "Todos los grados":
            grupo_completo = None
        elif grupo == "Todos los grupos":
            grupo_completo = f"{grado}/%"
        else:
            grupo_completo = f"{grado}/{grupo}"

        if grado == "Todos los grados":
            datos = obtener_todos("""
                SELECT
                    E.apellido_paterno || ' ' || E.apellido_materno || ' ' || E.nombre,
                    M.nombre,
                    EA.final
                FROM EstadoAcademico EA
                JOIN Estudiantes E
                    ON E.id = EA.alumno_id
                JOIN Materias M
                    ON M.id = EA.materia_id
                JOIN DatosEscolares D
                    ON D.estudiante_id = E.id
                    AND D.ciclo_id = EA.ciclo_id
                WHERE EA.final < 6
                ORDER BY E.apellido_paterno
            """)

        elif grupo == "Todos los grupos":
            datos = obtener_todos("""
                SELECT
                    E.apellido_paterno || ' ' || E.apellido_materno || ' ' || E.nombre,
                    M.nombre,
                    EA.final
                FROM EstadoAcademico EA
                JOIN Estudiantes E
                    ON E.id = EA.alumno_id
                JOIN Materias M
                    ON M.id = EA.materia_id
                JOIN DatosEscolares D
                    ON D.estudiante_id = E.id
                    AND D.ciclo_id = EA.ciclo_id
                WHERE D.grupo LIKE ?
                AND EA.final < 6
                ORDER BY E.apellido_paterno
            """,(grupo_completo,))

        else:

            datos = obtener_todos("""
                SELECT
                    E.apellido_paterno || ' ' || E.apellido_materno || ' ' || E.nombre,
                    M.nombre,
                    EA.final
                FROM EstadoAcademico EA
                JOIN Estudiantes E
                    ON E.id = EA.alumno_id
                JOIN Materias M
                    ON M.id = EA.materia_id
                JOIN DatosEscolares D
                    ON D.estudiante_id = E.id
                    AND D.ciclo_id = EA.ciclo_id
                WHERE D.grupo = ?
                AND EA.final < 6
                ORDER BY E.apellido_paterno
            """,(grupo_completo,))


        filas = []

        for i, (alumno, materia, final) in enumerate(datos, start=1):

            filas.append([
                i,
                alumno,
                materia,
                final
            ])

        pdf_bytes = generar_pdf_reprobados(
            escuela,
            grado,
            grupo,
            filas
        )

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(pdf_bytes)
        tmp.close()

        if sys.platform == "win32":
            os.startfile(tmp.name)
        else:
            subprocess.Popen(["xdg-open", tmp.name])



    # =========================
    # PESTAÑA BOLETA POR MATERIA
    # =========================

    tab_boleta_mat = tk.Frame(notebook, bg="white")
    notebook.add(tab_boleta_mat, text="Boleta por materia")

    frame_filtros_mat = tk.Frame(tab_boleta_mat, bg="white")
    frame_filtros_mat.pack(fill="x", padx=20, pady=20)

    tk.Label(frame_filtros_mat, text="Tipo:", bg="white").grid(row=0, column=0, padx=5, pady=5)

    combo_tipo = ttk.Combobox(
        frame_filtros_mat,
        values=["Ordinario", "Extraordinario"],
        state="readonly",
        width=20
    )
    combo_tipo.set("Ordinario")
    combo_tipo.grid(row=0, column=1, padx=10)

    tk.Label(frame_filtros_mat, text="Grado:", bg="white").grid(row=1, column=0, padx=5, pady=5)

    grados = obtener_todos("""
        SELECT id, nombre
        FROM Grados
        ORDER BY orden
    """)

    grados_dict_mat = {g[1]: g[0] for g in grados}

    combo_grado_mat = ttk.Combobox(
        frame_filtros_mat,
        values=list(grados_dict_mat.keys()),
        state="readonly",
        width=25
    )
    combo_grado_mat.grid(row=1, column=1, padx=10)

    tk.Label(frame_filtros_mat, text="Grupo:", bg="white").grid(row=1, column=2, padx=5)

    combo_grupo_mat = ttk.Combobox(
        frame_filtros_mat,
        state="readonly",
        width=25
    )
    combo_grupo_mat.grid(row=1, column=3, padx=10)


    tk.Label(frame_filtros_mat, text="Materia:", bg="white").grid(row=2, column=0, padx=5)

    combo_materia_mat = ttk.Combobox(
        frame_filtros_mat,
        state="readonly",
        width=50
    )
    combo_materia_mat.grid(row=2, column=1, columnspan=3, padx=10, pady=10)


    def cargar_grupos_mat(event):
        grado = combo_grado_mat.get()

        if grado not in grados_dict_mat:
            return

        grado_id = grados_dict_mat[grado]

        grupos = obtener_todos("""
            SELECT grupo
            FROM Grupos
            WHERE grado_id = ?
            ORDER BY grupo
        """, (grado_id,))

        combo_grupo_mat["values"] = [g[0] for g in grupos]

    combo_grado_mat.bind("<<ComboboxSelected>>", cargar_grupos_mat)


    def cargar_materias_mat(event):
        grado = combo_grado_mat.get()
        grupo = combo_grupo_mat.get()

        if grado not in grados_dict_mat or not grupo:
            return

        grado_id = grados_dict_mat[grado]

        if grado in ("Quinto", "Sexto"):

            mapa = {"501":1, "502":2, "503":3}
            esp_id = mapa.get(grupo)

            materias = obtener_todos("""
                SELECT nombre
                FROM Materias
                WHERE grupo_id = ?
                AND especialidad_id = ?
                ORDER BY nombre
            """, (grado_id, esp_id))

        else:

            materias = obtener_todos("""
                SELECT nombre
                FROM Materias
                WHERE grupo_id = ?
                ORDER BY nombre
            """, (grado_id,))

        combo_materia_mat["values"] = [m[0] for m in materias]

    combo_grupo_mat.bind("<<ComboboxSelected>>", cargar_materias_mat)


    frame_btn_mat = tk.Frame(tab_boleta_mat, bg="white")
    frame_btn_mat.pack(side="bottom", fill="x", pady=10)

    btn_plantilla = tk.Button(
        frame_btn_mat,
        text="Descargar plantilla",
        bg="#7dcea0",
        fg="white",
        width=18,
        command=lambda: descargar_plantilla()
    )
    btn_plantilla.pack(side="left", padx=20)

    btn_generar_mat = tk.Button(
        frame_btn_mat,
        text="Generar",
        bg="#2e86c1",
        fg="white",
        width=12,
        command=lambda: generar_boleta_materia()
    )
    btn_generar_mat.pack(side="right", padx=20)


    def descargar_plantilla():
        tipo = combo_tipo.get()
        grado = combo_grado_mat.get()
        grupo = combo_grupo_mat.get()
        materia = combo_materia_mat.get()

        if not (grado and grupo and materia):
            messagebox.showwarning("Aviso", "Complete todos los campos")
            return

        grupo_completo = f"{grado}/{grupo}"

        # =========================
        # DATOS ESCUELA
        # =========================

        escuela = obtener_todos("""
            SELECT nombre, rfc, direccion
            FROM Escuela
            LIMIT 1
        """)[0]

        escuela = {
            "nombre": escuela[0],
            "rfc": escuela[1],
            "direccion": escuela[2]
        }

        # =========================
        # ALUMNOS DEL GRUPO
        # =========================

        alumnos = obtener_todos("""
            SELECT 
            E.matricula,
            E.apellido_paterno || ' ' || E.apellido_materno || ' ' || E.nombre,
            FROM Estudiantes E
            JOIN DatosEscolares D
                ON D.estudiante_id = E.id
            WHERE D.grupo = ?
            ORDER BY E.apellido_paterno
        """,(grupo_completo,))

        lista_alumnos = alumnos

        # =========================
        # GENERAR EXCEL
        # =========================

        excel_bytes = generar_excel_plantilla(
            escuela,
            grupo_completo,
            materia,
            lista_alumnos,
            ciclo_activo["nombre"]
        )

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        tmp.write(excel_bytes)
        tmp.close()

        if sys.platform == "win32":
            os.startfile(tmp.name)
        else:
            subprocess.Popen(["xdg-open", tmp.name])


    def generar_boleta_materia():
        tipo = combo_tipo.get()
        grado = combo_grado_mat.get()
        grupo = combo_grupo_mat.get()
        materia = combo_materia_mat.get()

        if not (grado and grupo and materia):
            messagebox.showwarning("Aviso", "Complete todos los campos")
            return

        grupo_completo = f"{grado}/{grupo}"

        # =========================
        # DATOS ESCUELA
        # =========================

        escuela = obtener_todos("""
            SELECT nombre, rfc, direccion
            FROM Escuela
            LIMIT 1
        """)[0]

        escuela = {
            "nombre": escuela[0],
            "rfc": escuela[1],
            "direccion": escuela[2]
        }

        # =========================
        # ALUMNOS DEL GRUPO
        # =========================

        datos = obtener_todos("""
            SELECT
                E.matricula,
                E.nombre || ' ' || E.apellido_paterno || ' ' || E.apellido_materno,
                EA.parcial1,
                EA.parcial2,
                EA.parcial3,
                EA.final,
                EA.fecha
            FROM EstadoAcademico EA
            JOIN Estudiantes E
                ON E.id = EA.alumno_id
            JOIN DatosEscolares D
                ON D.estudiante_id = E.id
                AND D.ciclo_id = EA.ciclo_id
            JOIN Materias M
                ON M.id = EA.materia_id
            WHERE D.grupo = ?
            AND M.nombre = ?
            ORDER BY E.apellido_paterno
        """, (grupo_completo, materia))

        filas_excel = []

        for matricula, alumno, p1, p2, p3, final, fecha in datos:

            # Extraordinario
            if tipo == "Extraordinario" and not fecha:
                continue

            # Ordinario
            if tipo == "Ordinario" and fecha:
                continue

            filas_excel.append([
                matricula,
                alumno,
                p1,
                p2,
                p3,
                final
            ])

        # =========================
        # GENERAR EXCEL
        # =========================

        excel_bytes = generar_excel_boleta_materia(
            escuela,
            grupo_completo,
            materia,
            filas_excel,
            ciclo_activo["nombre"]
        )

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        tmp.write(excel_bytes)
        tmp.close()

        if sys.platform == "win32":
            os.startfile(tmp.name)
        else:
            subprocess.Popen(["xdg-open", tmp.name])




