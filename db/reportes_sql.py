# control_escolar/reportes_sql.py

# ==============================
# COLUMNAS DE ORDEN
# ==============================
COLUMNAS_ORDEN = {
    "matricula": "e.matricula",
    "alfabetico": "e.apellido_paterno, e.apellido_materno, e.nombre",
    "fecha_inscripcion": "de.fecha_inscripcion"
}

# ==============================
# COLUMNAS DE AGRUPACIÓN
# ==============================
COLUMNAS_AGRUPAR = {
    "Sin agrupar": None,
    "Fecha inscripción": "DATE(de.fecha_inscripcion)",
    "Grupo": "de.grupo",
    "Género": "dg.genero",
    "Condición": "de.condicion"
}


# ==============================
# SELECT BASE
# ==============================
def obtener_select_base():
    return """
    SELECT
        e.matricula AS matricula,
        e.nombre,
        e.apellido_paterno,
        e.apellido_materno,
        de.fecha_inscripcion,
        de.grupo,
        dg.genero,
        de.condicion
    """


# ==============================
# FROM BASE
# ==============================
def obtener_from_base():
    return """
    FROM Estudiantes e
    INNER JOIN DatosEscolares de
        ON de.estudiante_id = e.id
    LEFT JOIN DatosGenerales dg
        ON dg.estudiante_id = e.id
    """


# ==============================
# WHERE BASE (ciclo + fecha)
# ==============================
def obtener_where_base(ciclo_id, fecha_tipo, desde, hasta):
    where = ["de.ciclo_id = ?"]
    params = [ciclo_id]

    if fecha_tipo == "rango" and desde and hasta:
        where.append("de.fecha_inscripcion BETWEEN ? AND ?")
        params.extend([desde, hasta])

    return "WHERE " + " AND ".join(where), params


# ==============================
# GROUP BY
# ==============================
def obtener_group_by(agrupar):
    col = COLUMNAS_AGRUPAR.get(agrupar)
    if not col:
        return ""
    return f"GROUP BY {col}"


# ==============================
# ORDER BY
# ==============================
def obtener_order_by(orden):
    col = COLUMNAS_ORDEN.get(orden)
    if not col:
        return ""
    return f"ORDER BY {col}"


# ==============================
# CONSTRUCTOR PRINCIPAL
# ==============================
def construir_consulta(tipo, **kwargs):
    
    if tipo == "boleta_alumno":

        sql = """
            SELECT
                e.matricula,
                e.nombre,
                e.apellido_paterno,
                e.apellido_materno,
                de.grupo,
                de.especialidad,
                m.nombre AS materia,
                ea.parcial1,
                ea.parcial2,
                ea.parcial3,
                ea.final
            FROM EstadoAcademico ea
            JOIN Estudiantes e
                ON e.id = ea.alumno_id
            JOIN DatosEscolares de
                ON de.estudiante_id = e.id
            JOIN Materias m
                ON m.id = ea.materia_id
            WHERE ea.alumno_id = ?
            AND ea.ciclo_id = ?
            ORDER BY m.nombre
        """

        return sql, [kwargs["alumno_id"], kwargs["ciclo_id"]]

    if tipo == "concentrado_calificaciones":

        sql = """
            SELECT
                de.grupo,
                e.matricula,
                e.nombre,
                e.apellido_paterno,
                e.apellido_materno,
                m.nombre AS materia,
                ea.final
            FROM EstadoAcademico ea
            JOIN Estudiantes e
                ON e.id = ea.alumno_id
            JOIN DatosEscolares de
                ON de.estudiante_id = e.id
            JOIN Materias m
                ON m.id = ea.materia_id
            WHERE de.grupo = ?
            AND ea.ciclo_id = ?
            ORDER BY e.apellido_paterno, m.nombre
        """

        return sql, [kwargs["grupo"], kwargs["ciclo_id"]]
    
    if tipo == "alumnos_reprobados":

        sql = """
            SELECT
                de.grupo,
                e.matricula,
                e.nombre,
                e.apellido_paterno,
                e.apellido_materno,
                m.nombre AS materia,
                ea.final
            FROM EstadoAcademico ea
            JOIN Estudiantes e
                ON e.id = ea.alumno_id
            JOIN DatosEscolares de
                ON de.estudiante_id = e.id
            JOIN Materias m
                ON m.id = ea.materia_id
            WHERE ea.final < 7
            AND de.grupo = ?
            AND ea.ciclo_id = ?
            ORDER BY e.apellido_paterno
        """

        return sql, [kwargs["grupo"], kwargs["ciclo_id"]]
    
    if tipo == "kardex_alumno":

        sql = """
            SELECT
                e.matricula,
                e.nombre,
                e.apellido_paterno,
                e.apellido_materno,
                c.nombre AS ciclo,
                m.nombre AS materia,
                ea.final
            FROM EstadoAcademico ea
            JOIN Estudiantes e
                ON e.id = ea.alumno_id
            JOIN Materias m
                ON m.id = ea.materia_id
            JOIN Ciclos c
                ON c.id = ea.ciclo_id
            WHERE ea.alumno_id = ?
            ORDER BY c.id, m.nombre
        """

        return sql, [kwargs["alumno_id"]]

    params = [kwargs["ciclo_id"]]

    select_sql = """
        SELECT
            e.matricula AS matricula,

            TRIM(
                e.nombre || ' ' ||
                e.apellido_paterno || ' ' ||
                e.apellido_materno
            ) AS nombre,

            de.fecha_inscripcion,
            de.grupo,
            dg.genero,
            de.condicion,

            TRIM(
                IFNULL(df.nombre, '') ||
                CASE
                    WHEN df.celular IS NOT NULL AND df.celular != ''
                    THEN ' - ' || df.celular
                    ELSE ''
                END
            ) AS contacto
    """

    from_sql = """
        FROM Estudiantes e
        JOIN DatosEscolares de
            ON de.estudiante_id = e.id
        JOIN DatosGenerales dg
            ON dg.estudiante_id = e.id
        LEFT JOIN DatosFamiliares df
            ON df.estudiante_id = e.id
    """

    where_sql = "WHERE de.ciclo_id = ?"


    sql = f"""
        {select_sql}
        {from_sql}
        {where_sql}
    """

    return sql.strip(), params