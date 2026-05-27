import tkinter as tk
import os
import hashlib
from PIL import Image, ImageTk
from tkinter import ttk, messagebox

from db.conexion import obtener_todos
from ventana_principal import abrir_ventana_principal

from utils.rutas import ruta_recurso


# =====================================================
# HASH PASSWORD
# =====================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def solo_mayusculas(var):
    var.set(var.get().upper())

# =====================================================
# VALIDAR LOGIN
# =====================================================
def validar_login(usuario, password):
    usuario = usuario.upper()
    fila = obtener_todos(
        """
        SELECT id, password, activo
        FROM usuarios
        WHERE usuario=?
        """,
        (usuario,)
    )

    if not fila:
        return None, "Usuario no existe"

    usuario_id, password_db, activo = fila[0]

    if not activo:
        return None, "Usuario inactivo"

    if hash_password(password) != password_db:
        return None, "Contraseña incorrecta"

    return usuario_id, None


# =====================================================
# VENTANA LOGIN
# =====================================================
def abrir_login():
    root = tk.Tk()
    root.title("Inicio de sesión")
    root.geometry("520x260")
    root.resizable(False, False)

    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 260
    y = (root.winfo_screenheight() // 2) - 130
    root.geometry(f"+{x}+{y}")

    # ===============================
    # CONTENEDOR PRINCIPAL
    # ===============================
    cont = tk.Frame(root)
    cont.pack(fill="both", expand=True)

    # ===============================
    # COLUMNA DERECHA (FORMULARIO)
    # ===============================
    frame_form = tk.Frame(cont, padx=20, pady=25)
    frame_form.pack(side="right", fill="both", expand=True)

    tk.Label(frame_form, text="Usuario").pack(anchor="w")

    usuario_var = tk.StringVar()
    usuario_var.trace_add("write", lambda *args: solo_mayusculas(usuario_var))

    entry_usuario = tk.Entry(frame_form, textvariable=usuario_var)
    entry_usuario.pack(fill="x", pady=5)
    entry_usuario.focus()

    tk.Label(
        frame_form,
        text="Contraseña"
    ).pack(anchor="w", pady=(10, 0))

    entry_password = tk.Entry(frame_form, show="*")
    entry_password.pack(fill="x", pady=5)

    def ingresar():
        usuario = entry_usuario.get().strip().upper()
        password = entry_password.get()

        if not usuario or not password:
            messagebox.showwarning(
                "Datos incompletos",
                "Ingrese usuario y contraseña"
            )
            return

        usuario_id, error = validar_login(usuario, password)

        if error:
            messagebox.showerror("Error", error)
            return

        root.destroy()
        abrir_ventana_principal(usuario_id)

    ttk.Button(
        frame_form,
        text="Ingresar",
        command=ingresar
    ).pack(pady=20)

    root.bind("<Return>", lambda e: ingresar())

    # ===============================
    # COLUMNA IZQUIERDA (IMAGEN)
    # ===============================
    frame_img = tk.Frame(cont, padx=20, pady=20)
    frame_img.pack(side="left", fill="y")

    try:
        ruta_img = ruta_recurso("img/icono.png")

        img = Image.open(ruta_img)
        img = img.resize((250, 250), Image.LANCZOS)

        icono_img = ImageTk.PhotoImage(img)

        lbl_img = tk.Label(frame_img, image=icono_img)
        lbl_img.image = icono_img  # mantener referencia
        lbl_img.pack(expand=True)

    except Exception as e:
        print("Error cargando imagen:", e)

    root.mainloop()


# =====================================================
# ENTRY POINT
# =====================================================
if __name__ == "__main__":
    abrir_login()
