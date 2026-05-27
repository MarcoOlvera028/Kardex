from db.conexion import obtener_todos, ejecutar_consulta

def guardar_ultimo_ciclo(ciclo_id):
    ejecutar_consulta(
        """
        INSERT INTO configuracion (clave, valor)
        VALUES ('ultimo_ciclo', ?)
        ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor
        """,
        (str(ciclo_id),)
    )

def obtener_ultimo_ciclo():
    fila = obtener_todos(
        "SELECT valor FROM configuracion WHERE clave='ultimo_ciclo'"
    )
    return int(fila[0][0]) if fila else None

def guardar_ultima_escuela(escuela_id):
    ejecutar_consulta(
        """
        INSERT INTO configuracion (clave, valor)
        VALUES ('ultima_escuela', ?)
        ON CONFLICT(clave)
        DO UPDATE SET valor=excluded.valor
        """,
        (str(escuela_id),)
    )


def obtener_ultima_escuela():
    fila = obtener_todos(
        "SELECT valor FROM configuracion WHERE clave='ultima_escuela'"
    )
    return int(fila[0][0]) if fila else None