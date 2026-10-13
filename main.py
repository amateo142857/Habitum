import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import date

from auth import registrar_usuario, autenticar
import habitos as hb
import stats as st
import exportar as ex
import colores

import warnings
warnings.filterwarnings("ignore", message="Glyph .* missing from font")
warnings.filterwarnings("ignore", message=".*missing from font.*")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ============================================================
# VARIABLES GLOBALES
# ============================================================
ventana = None
USUARIO_ACTUAL = None
SEMANA_ID = None
COL_IZQ = None
COL_DER = None
ENTRY_USER = None
ENTRY_PASS = None
ENTRY_NUEVO = None
COMBO_SEMANAS = None
COMBO_CATEGORIA_NUEVA = None
SPIN_META_NUEVA = None
MES_OFFSET = 0


# ============================================================
# UTILIDADES
# ============================================================
def maximizar():
    try:
        ventana.state("zoomed")
    except Exception:
        try:
            ventana.attributes("-zoomed", True)
        except Exception:
            ventana.geometry(f"{ventana.winfo_screenwidth()}x{ventana.winfo_screenheight()}+0+0")


def maximizar_ventana(v):
    try:
        v.state("zoomed")
    except Exception:
        try:
            v.attributes("-zoomed", True)
        except Exception:
            v.geometry(f"{ventana.winfo_screenwidth()}x{ventana.winfo_screenheight()}+0+0")


def limpiar():
    for w in ventana.winfo_children():
        w.destroy()


def crear_entry(master, placeholder, width=None):
    return ctk.CTkEntry(
        master, placeholder_text=placeholder,
        fg_color=colores.COLORES["panel"],
        text_color=colores.COLORES["texto"],
        border_color=colores.COLORES["acento"],
        height=40,
        width=width if width else 200
    )


def crear_boton(master, texto, comando, color=None, hover=None, width=None):
    return ctk.CTkButton(
        master, text=texto, command=comando,
        fg_color=color or colores.COLORES["acento"],
        hover_color=hover or colores.COLORES["acento_hover"],
        text_color=colores.COLORES["texto"], height=40,
        font=("Arial", 13, "bold"),
        width=width if width else 140
    )


def crear_combo(master, valores, width=180):
    return ctk.CTkComboBox(
        master, values=valores,
        fg_color=colores.COLORES["panel"],
        border_color=colores.COLORES["acento"],
        button_color=colores.COLORES["acento"],
        button_hover_color=colores.COLORES["acento_hover"],
        text_color=colores.COLORES["texto"], width=width,
        dropdown_fg_color=colores.COLORES["panel"],
        dropdown_text_color=colores.COLORES["texto"],
        dropdown_hover_color=colores.COLORES["acento"]
    )


def crear_spin_meta(master, width=70):
    """Crea un OptionMenu para elegir la meta (1-7)."""
    return ctk.CTkOptionMenu(
        master, values=[str(i) for i in range(1, 8)],
        fg_color=colores.COLORES["panel"],
        button_color=colores.COLORES["acento"],
        button_hover_color=colores.COLORES["acento_hover"],
        text_color=colores.COLORES["texto"],
        dropdown_fg_color=colores.COLORES["panel"],
        dropdown_text_color=colores.COLORES["texto"],
        dropdown_hover_color=colores.COLORES["acento"],
        width=width
    )


# ============================================================
# CAMBIO DE TEMA
# ============================================================
def alternar_tema():
    global USUARIO_ACTUAL
    nuevo = "claro" if colores.get_tema() == "oscuro" else "oscuro"
    colores.set_tema(nuevo)
    ctk.set_appearance_mode(nuevo)
    ventana.configure(fg_color=colores.COLORES["fondo"])

    if USUARIO_ACTUAL:
        mostrar_principal()
    else:
        mostrar_login()


# ============================================================
# LOGIN / REGISTRO
# ============================================================
def mostrar_login():
    global ENTRY_USER, ENTRY_PASS
    limpiar()

    frame = ctk.CTkFrame(ventana, fg_color=colores.COLORES["panel"], corner_radius=20)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(frame, text="🔐 Compendio de Hábitos",
                 font=("Arial", 22, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(padx=40, pady=(30, 20))

    ENTRY_USER = crear_entry(frame, "Usuario")
    ENTRY_USER.pack(padx=40, pady=8, fill="x")

    ENTRY_PASS = crear_entry(frame, "Contraseña")
    ENTRY_PASS.configure(show="*")
    ENTRY_PASS.pack(padx=40, pady=8, fill="x")

    crear_boton(frame, "Iniciar sesión", login).pack(padx=40, pady=(20, 8), fill="x")
    crear_boton(frame, "Registrarse", registrar,
                color=colores.COLORES["exito"], hover="#05b88a").pack(padx=40, pady=(0, 15), fill="x")

    icono = "☀️" if colores.get_tema() == "oscuro" else "🌙"
    crear_boton(frame, f"{icono} Cambiar tema", alternar_tema,
                width=200).pack(padx=40, pady=(0, 25))

    ENTRY_PASS.bind("<Return>", lambda e: login())


def login():
    global USUARIO_ACTUAL, SEMANA_ID
    u = ENTRY_USER.get()
    p = ENTRY_PASS.get()
    if autenticar(u, p):
        USUARIO_ACTUAL = u.lower().strip()
        SEMANA_ID = hb.semana_actual_id()

        try:
            import logros as lg
            nuevos = lg.comprobar_logros(USUARIO_ACTUAL)
            if nuevos:
                mensaje = "🏅 ¡Has desbloqueado logros!\n\n"
                for nid in nuevos:
                    info = lg.LOGROS.get(nid, {})
                    mensaje += f"{info.get('icono', '🏅')} {info.get('nombre', nid)}\n"
                messagebox.showinfo("¡Nuevos logros!", mensaje)
        except Exception as e:
            print(f"[logros] Error: {e}")

        mostrar_principal()
    else:
        messagebox.showerror("Error", "Credenciales incorrectas")


def registrar():
    u = ENTRY_USER.get()
    p = ENTRY_PASS.get()
    ok, msg = registrar_usuario(u, p)
    if ok:
        messagebox.showinfo("Éxito", msg)
    else:
        messagebox.showerror("Error", msg)


# ============================================================
# PANTALLA PRINCIPAL
# ============================================================
def mostrar_principal():
    global COL_IZQ, COL_DER, COMBO_SEMANAS
    limpiar()

    # HEADER
    header = ctk.CTkFrame(ventana, fg_color=colores.COLORES["panel"], height=60, corner_radius=0)
    header.pack(fill="x")

    crear_boton(header, "Cerrar sesión", mostrar_login,
                color=colores.COLORES["error"], hover="#c73a5d",
                width=140).pack(side="right", padx=(10, 20), pady=10)

    ctk.CTkLabel(header, text=f"👤 {USUARIO_ACTUAL}",
                 font=("Arial", 14, "bold"),
                 text_color=colores.COLORES["texto"]).pack(side="right", padx=(0, 10), pady=15)

    icono = "☀️" if colores.get_tema() == "oscuro" else "🌙"
    crear_boton(header, icono, alternar_tema,
                width=50).pack(side="right", padx=(0, 10), pady=10)

    ctk.CTkLabel(header, text="📘 Compendio de Hábitos",
                 font=("Arial", 15, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(side="left", padx=20, pady=15)

    # SELECTOR DE SEMANA (sin los botones de vistas nuevas)
    selector = ctk.CTkFrame(ventana, fg_color=colores.COLORES["fondo"])
    selector.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(selector, text="Semana:", text_color=colores.COLORES["texto"],
                 font=("Arial", 13, "bold")).pack(side="left", padx=(0, 10))

    COMBO_SEMANAS = crear_combo(selector,
                                hb.listar_semanas(USUARIO_ACTUAL) or [SEMANA_ID],
                                width=200)
    COMBO_SEMANAS.configure(command=cambiar_semana)
    COMBO_SEMANAS.set(SEMANA_ID)
    COMBO_SEMANAS.pack(side="left")

    crear_boton(selector, "➕ Nueva semana", crear_nueva_semana,
                width=150).pack(side="left", padx=10)

    crear_boton(selector, "📋 Copiar anterior", copiar_anterior,
                color=colores.COLORES["exito"], hover="#05b88a",
                width=160).pack(side="left", padx=5)

    crear_boton(selector, "🗑 Eliminar semana", borrar_semana_actual,
                color=colores.COLORES["error"], hover="#c73a5d",
                width=160).pack(side="left", padx=5)

    # CONTENEDOR PRINCIPAL (dos columnas)
    contenedor = ctk.CTkFrame(ventana, fg_color=colores.COLORES["fondo"])
    contenedor.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # COLUMNA IZQUIERDA — scrollable
    col_izq_wrap = ctk.CTkFrame(contenedor, fg_color="transparent")
    col_izq_wrap.pack(side="left", fill="both", expand=True)

    COL_IZQ = ctk.CTkScrollableFrame(
        col_izq_wrap,
        fg_color=colores.COLORES["fondo"],
        scrollbar_button_color=colores.COLORES["acento"],
        scrollbar_button_hover_color=colores.COLORES["acento_hover"]
    )
    COL_IZQ.pack(fill="both", expand=True)

    # COLUMNA DERECHA — wrapper para fijar ancho
    col_der_wrap = ctk.CTkFrame(contenedor, fg_color="transparent", width=310)
    col_der_wrap.pack(side="right", fill="y", padx=(15, 0))
    col_der_wrap.pack_propagate(False)

    COL_DER = ctk.CTkScrollableFrame(
        col_der_wrap,
        fg_color=colores.COLORES["panel"],
        corner_radius=15,
        scrollbar_button_color=colores.COLORES["acento"],
        scrollbar_button_hover_color=colores.COLORES["acento_hover"]
    )
    COL_DER.pack(fill="both", expand=True)

    render_tabla()
    render_panel_derecho()


def cambiar_semana(valor):
    global SEMANA_ID
    SEMANA_ID = valor
    render_tabla()
    render_panel_derecho()


# ============================================================
# NUEVA SEMANA / COPIAR / ELIMINAR
# ============================================================
def crear_nueva_semana():
    dialog = ctk.CTkToplevel(ventana)
    dialog.title("Nueva semana")
    dialog.geometry("420x260")
    dialog.configure(fg_color=colores.COLORES["fondo"])
    dialog.grab_set()

    ctk.CTkLabel(dialog, text="ID semana (ej: 2025-W05)",
                 text_color=colores.COLORES["texto"],
                 font=("Arial", 12)).pack(pady=(20, 5))
    entry = crear_entry(dialog, "YYYY-Wnn")
    entry.pack(padx=30, fill="x")

    var_copiar = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(
        dialog, text="Copiar hábitos de la semana anterior",
        variable=var_copiar,
        fg_color=colores.COLORES["exito"], hover_color="#05b88a",
        text_color=colores.COLORES["texto"],
        font=("Arial", 12)
    ).pack(pady=15)

    def accion_crear():
        global SEMANA_ID
        sid = entry.get().strip().upper()
        try:
            int(sid.split("-W")[0]); int(sid.split("-W")[1])
        except Exception:
            messagebox.showerror("Error", "Formato inválido. Usa YYYY-Wnn")
            return

        hb.obtener_semana(USUARIO_ACTUAL, sid)

        if var_copiar.get():
            ok, msg, n = hb.copiar_habitos_semana_anterior(USUARIO_ACTUAL, sid)
            if ok:
                messagebox.showinfo("Copiado", msg)
            elif "no hay" not in msg.lower():
                messagebox.showinfo("Info", msg)

        SEMANA_ID = sid
        dialog.destroy()
        mostrar_principal()

    crear_boton(dialog, "Crear", accion_crear).pack(pady=10)


def copiar_anterior():
    ok, msg, n = hb.copiar_habitos_semana_anterior(USUARIO_ACTUAL, SEMANA_ID)
    if ok:
        messagebox.showinfo("Listo", msg)
        render_tabla()
        render_panel_derecho()
    else:
        messagebox.showwarning("Aviso", msg)


def borrar_semana_actual():
    global SEMANA_ID
    if not SEMANA_ID:
        return
    confirmar = messagebox.askyesno(
        "Eliminar semana",
        f"¿Seguro que quieres eliminar la semana {SEMANA_ID}?\n"
        "Se borrarán TODOS los hábitos y checks de esa semana."
    )
    if not confirmar:
        return

    eliminada = hb.eliminar_semana(USUARIO_ACTUAL, SEMANA_ID)
    if not eliminada:
        messagebox.showwarning("Aviso", "Esa semana no existía.")
        return

    SEMANA_ID = hb.semana_actual_id()
    hb.obtener_semana(USUARIO_ACTUAL, SEMANA_ID)
    mostrar_principal()


# ============================================================
# PANEL DERECHO
# ============================================================
def render_panel_derecho():
    for w in COL_DER.winfo_children():
        w.destroy()

    ctk.CTkLabel(COL_DER, text="📊 Resumen",
                 font=("Arial", 15, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(pady=(20, 5))

    ctk.CTkLabel(COL_DER, text="Cumplimiento por categoría",
                 font=("Arial", 11),
                 text_color=colores.COLORES["texto_suave"]).pack(pady=(0, 15))

    semana = hb.obtener_semana(USUARIO_ACTUAL, SEMANA_ID)
    resumen = hb.calcular_por_categoria(semana)

    if resumen:
        for cat, (cumplidos, total, pct) in sorted(resumen.items(),
                                                   key=lambda x: x[1][2], reverse=True):
            info = hb.CATEGORIAS.get(cat, hb.CATEGORIAS["Otros"])

            card = ctk.CTkFrame(COL_DER, fg_color=colores.COLORES["fondo"], corner_radius=10)
            card.pack(fill="x", padx=15, pady=5)

            fila = ctk.CTkFrame(card, fg_color="transparent")
            fila.pack(fill="x", padx=10, pady=(8, 3))

            ctk.CTkLabel(fila, text=f"{info['icono']} {cat}",
                         text_color=info["color"],
                         font=("Arial", 12, "bold")).pack(side="left")

            ctk.CTkLabel(fila, text=f"{pct:.0f}%",
                         text_color=info["color"],
                         font=("Arial", 12, "bold")).pack(side="right")

            barra = ctk.CTkProgressBar(card, height=8,
                                       progress_color=info["color"],
                                       fg_color=colores.COLORES["panel_alt"])
            barra.pack(fill="x", padx=10, pady=(0, 10))
            barra.set(pct / 100)

    # RACHAS ACTIVAS
    ctk.CTkLabel(COL_DER, text="🔥 Rachas activas",
                 font=("Arial", 13, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(pady=(20, 5))

    rachas = hb.calcular_rachas_todos(USUARIO_ACTUAL, SEMANA_ID)
    rachas_activas = sorted(
        [(n, d) for n, d in rachas.items() if d["actual"] > 0],
        key=lambda x: x[1]["actual"], reverse=True
    )

    if not rachas_activas:
        ctk.CTkLabel(COL_DER, text="Sin rachas aún",
                     text_color=colores.COLORES["texto_suave"],
                     font=("Arial", 11)).pack(pady=5)
    else:
        for nombre, d in rachas_activas[:5]:
            fila = ctk.CTkFrame(COL_DER, fg_color="transparent")
            fila.pack(fill="x", padx=15, pady=2)

            color = colores.COLORES["exito"] if d["actual"] >= 5 else (
                colores.COLORES["acento_hover"] if d["actual"] >= 2
                else colores.COLORES["texto_suave"])

            ctk.CTkLabel(fila, text=f"🔥 {nombre}",
                         text_color=colores.COLORES["texto"],
                         font=("Arial", 11),
                         anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=f"{d['actual']}",
                         text_color=color,
                         font=("Arial", 12, "bold")).pack(side="right")

    # BOTONES DE GRÁFICAS
    ctk.CTkLabel(COL_DER, text="📈 Análisis",
                 font=("Arial", 13, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(pady=(20, 5))

    crear_boton(COL_DER, "🍩 Ver pastel", mostrar_grafica_categorias,
                width=200).pack(pady=5)

    crear_boton(COL_DER, "📈 Tendencia global",
                mostrar_tendencia_global,
                color=colores.COLORES["acento"],
                width=200).pack(pady=5)

    crear_boton(COL_DER, "📈 Tendencia por hábito",
                mostrar_tendencia_por_habito,
                color=colores.COLORES["acento"],
                width=200).pack(pady=(5, 20))


# ============================================================
# TABLA DE HÁBITOS
# ============================================================
def render_tabla():
    global ENTRY_NUEVO, COMBO_CATEGORIA_NUEVA, SPIN_META_NUEVA
    for w in COL_IZQ.winfo_children():
        w.destroy()

    semana = hb.obtener_semana(USUARIO_ACTUAL, SEMANA_ID)
    fechas = hb.fechas_semana(SEMANA_ID)
    rachas = hb.calcular_rachas_todos(USUARIO_ACTUAL, SEMANA_ID)

    ctk.CTkLabel(COL_IZQ,
                 text=f"📅 Semana {SEMANA_ID}",
                 font=("Arial", 18, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(pady=(5, 10))

    tabla = ctk.CTkFrame(COL_IZQ, fg_color=colores.COLORES["panel"], corner_radius=15)
    tabla.pack(fill="both", expand=True, padx=5, pady=5)

    # Cabecera
    ctk.CTkLabel(tabla, text="Hábito", width=180, anchor="w",
                 font=("Arial", 12, "bold"),
                 text_color=colores.COLORES["acento_hover"]).grid(row=0, column=0, padx=10, pady=10, sticky="w")

    ctk.CTkLabel(tabla, text="Categoría", width=110,
                 font=("Arial", 12, "bold"),
                 text_color=colores.COLORES["acento_hover"]).grid(row=0, column=1, padx=5)

    for i, (dia, fecha) in enumerate(zip(hb.DIAS, fechas)):
        ctk.CTkLabel(tabla, text=f"{dia[:3]}\n{fecha}",
                     font=("Arial", 11, "bold"),
                     text_color=colores.COLORES["texto"]).grid(row=0, column=i+2, padx=5, pady=10)

    ctk.CTkLabel(tabla, text="Progreso", width=80,
                 font=("Arial", 12, "bold"),
                 text_color=colores.COLORES["acento_hover"]).grid(row=0, column=9, padx=5)

    ctk.CTkLabel(tabla, text="🔥 Racha", width=100,
                 font=("Arial", 12, "bold"),
                 text_color=colores.COLORES["acento_hover"]).grid(row=0, column=10, padx=5)

    ctk.CTkLabel(tabla, text="Acciones", width=100,
                 font=("Arial", 12, "bold"),
                 text_color=colores.COLORES["acento_hover"]).grid(row=0, column=11, padx=5)

    # Filas
    for r, habito in enumerate(semana["habitos"], start=1):
        cat = habito.get("categoria", "Otros")
        info = hb.CATEGORIAS.get(cat, hb.CATEGORIAS["Otros"])

        ctk.CTkLabel(tabla, text=habito["nombre"], width=180, anchor="w",
                     text_color=colores.COLORES["texto"],
                     font=("Arial", 12)).grid(row=r, column=0, padx=10, pady=6, sticky="w")

        ctk.CTkLabel(tabla, text=f"{info['icono']} {cat}", width=110,
                     text_color=info["color"],
                     font=("Arial", 11, "bold")).grid(row=r, column=1, padx=5)

        for c, check in enumerate(habito["checks"]):
            var = ctk.BooleanVar(value=check)
            cb = ctk.CTkCheckBox(
                tabla, text="", variable=var, width=30,
                fg_color=colores.COLORES["exito"], hover_color="#05b88a",
                border_color=colores.COLORES["acento"],
                command=lambda h=habito["nombre"], i=c: on_check(h, i)
            )
            if check:
                cb.select()
            cb.grid(row=r, column=c+2, padx=5, pady=6)

        meta = hb._meta_de(habito)
        cumplidos = sum(habito["checks"])
        pct = min(100, (cumplidos / meta) * 100)

        color_pct = colores.COLORES["exito"] if pct >= 70 else (
            colores.COLORES["acento_hover"] if pct >= 40 else colores.COLORES["error"])

        ctk.CTkLabel(tabla, text=f"{cumplidos}/{meta}\n{pct:.0f}%",
                     width=80,
                     text_color=color_pct,
                     font=("Arial", 12, "bold")).grid(row=r, column=9, padx=5)

        datos_racha = rachas.get(habito["nombre"], {"actual": 0, "maxima_global": 0})
        racha_act = datos_racha["actual"]
        racha_max = datos_racha["maxima_global"]

        if racha_act >= 5:
            texto_racha = f"🔥 {racha_act}"
            color_racha = colores.COLORES["exito"]
        elif racha_act >= 2:
            texto_racha = f"🔥 {racha_act}"
            color_racha = colores.COLORES["acento_hover"]
        elif racha_act == 1:
            texto_racha = "🔥 1"
            color_racha = colores.COLORES["texto_suave"]
        else:
            texto_racha = "—"
            color_racha = colores.COLORES["texto_suave"]

        contenedor_racha = ctk.CTkFrame(tabla, fg_color="transparent")
        contenedor_racha.grid(row=r, column=10, padx=5)

        ctk.CTkLabel(contenedor_racha, text=texto_racha,
                     text_color=color_racha,
                     font=("Arial", 13, "bold")).pack()
        ctk.CTkLabel(contenedor_racha, text=f"máx {racha_max}",
                     text_color=colores.COLORES["texto_suave"],
                     font=("Arial", 9)).pack()

        acciones = ctk.CTkFrame(tabla, fg_color="transparent")
        acciones.grid(row=r, column=11, padx=5)

        ctk.CTkButton(acciones, text="✏", width=32, height=28,
                      fg_color=colores.COLORES["acento"],
                      hover_color=colores.COLORES["acento_hover"],
                      command=lambda h=habito: abrir_editor_habito(h)
                      ).pack(side="left", padx=2)

        ctk.CTkButton(acciones, text="✖", width=32, height=28,
                      fg_color=colores.COLORES["error"], hover_color="#c73a5d",
                      command=lambda n=habito["nombre"]: borrar_habito(n)
                      ).pack(side="left", padx=2)

    # Fila para agregar
    fila_add = len(semana["habitos"]) + 1

    ENTRY_NUEVO = crear_entry(tabla, "Nuevo hábito...", width=180)
    ENTRY_NUEVO.grid(row=fila_add, column=0, padx=10, pady=15, sticky="w")
    ENTRY_NUEVO.bind("<Return>", lambda e: agregar_habito())

    COMBO_CATEGORIA_NUEVA = crear_combo(tabla, list(hb.CATEGORIAS.keys()), width=130)
    COMBO_CATEGORIA_NUEVA.set("Salud")
    COMBO_CATEGORIA_NUEVA.grid(row=fila_add, column=1, padx=5, pady=15)

    ctk.CTkLabel(tabla, text="Meta:",
                 text_color=colores.COLORES["texto"],
                 font=("Arial", 11, "bold")).grid(row=fila_add, column=2, padx=(5, 2), pady=15)

    SPIN_META_NUEVA = crear_spin_meta(tabla, width=60)
    SPIN_META_NUEVA.set("7")
    SPIN_META_NUEVA.grid(row=fila_add, column=3, padx=(0, 5), pady=15)

    crear_boton(tabla, "➕ Agregar", agregar_habito,
                color=colores.COLORES["exito"], hover="#05b88a",
                width=120).grid(row=fila_add, column=4, columnspan=2, padx=5, pady=15, sticky="w")

    crear_boton(tabla, "📊 Gráfica hábitos", mostrar_grafica,
                width=160).grid(row=fila_add, column=6, columnspan=3, padx=5, pady=15)

    # ---------- NUEVA SECCIÓN: VISTAS ----------
    # Sección debajo de la tabla con los botones de vistas
    separador = ctk.CTkFrame(COL_IZQ, fg_color=colores.COLORES["acento"], height=2)
    separador.pack(fill="x", padx=20, pady=(25, 10))

    ctk.CTkLabel(COL_IZQ,
                 text="🧭 Explorar",
                 font=("Arial", 15, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(pady=(5, 5))

    ctk.CTkLabel(COL_IZQ,
                 text="Vistas alternativas de tus hábitos",
                 font=("Arial", 11),
                 text_color=colores.COLORES["texto_suave"]).pack(pady=(0, 15))

    # Contenedor horizontal para los 3 botones
    fila_vistas = ctk.CTkFrame(COL_IZQ, fg_color="transparent")
    fila_vistas.pack(fill="x", padx=20, pady=(0, 25))

    crear_boton(fila_vistas, "📅 Hoy",
                mostrar_vista_hoy,
                color=colores.COLORES["acento_hover"],
                width=180).pack(side="left", padx=10, pady=5)

    crear_boton(fila_vistas, "📆 Calendario",
                lambda: mostrar_calendario(0),
                color=colores.COLORES["acento_hover"],
                width=180).pack(side="left", padx=10, pady=5)

    crear_boton(fila_vistas, "🏅 Logros",
                mostrar_logros,
                color=colores.COLORES["acento_hover"],
    )
        # ---------- NUEVA SECCIÓN: COMPARTIR ----------
    separador2 = ctk.CTkFrame(COL_IZQ, fg_color=colores.COLORES["exito"], height=2)
    separador2.pack(fill="x", padx=20, pady=(25, 10))

    ctk.CTkLabel(COL_IZQ,
                 text="📤 Compartir",
                 font=("Arial", 15, "bold"),
                 text_color=colores.COLORES["exito"]).pack(pady=(5, 5))

    ctk.CTkLabel(COL_IZQ,
                 text="Exporta tu resumen o crea una imagen para redes",
                 font=("Arial", 11),
                 text_color=colores.COLORES["texto_suave"]).pack(pady=(0, 15))

    fila_compartir = ctk.CTkFrame(COL_IZQ, fg_color="transparent")
    fila_compartir.pack(fill="x", padx=20, pady=(0, 25))

    crear_boton(fila_compartir, "📄 Exportar PDF",
                exportar_pdf_semana,
                color=colores.COLORES["exito"], hover="#05b88a",
                width=200).pack(side="left", padx=10, pady=5)

    crear_boton(fila_compartir, "📱 Imagen para redes",
                exportar_imagen_redes,
                color=colores.COLORES["acento_hover"],
                width=220).pack(side="left", padx=10, pady=5)
                
    


# ============================================================
# EDITAR HÁBITO
# ============================================================
def abrir_editor_habito(habito):
    dialog = ctk.CTkToplevel(ventana)
    dialog.title("Editar hábito")
    dialog.geometry("420x460")
    dialog.configure(fg_color=colores.COLORES["fondo"])
    dialog.grab_set()

    ctk.CTkLabel(dialog, text="✏ Editar hábito",
                 font=("Arial", 16, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(pady=(20, 15))

    ctk.CTkLabel(dialog, text="Nombre:",
                 text_color=colores.COLORES["texto"],
                 font=("Arial", 12)).pack(anchor="w", padx=30)

    entry_nombre = crear_entry(dialog, "Nombre")
    entry_nombre.insert(0, habito["nombre"])
    entry_nombre.pack(padx=30, pady=(3, 12), fill="x")

    ctk.CTkLabel(dialog, text="Categoría:",
                 text_color=colores.COLORES["texto"],
                 font=("Arial", 12)).pack(anchor="w", padx=30)

    combo_cat = crear_combo(dialog, list(hb.CATEGORIAS.keys()), width=200)
    combo_cat.set(habito.get("categoria", "Otros"))
    combo_cat.pack(padx=30, pady=(3, 12), anchor="w")

    ctk.CTkLabel(dialog, text="Meta semanal (días):",
                 text_color=colores.COLORES["texto"],
                 font=("Arial", 12)).pack(anchor="w", padx=30)

    spin_meta = crear_spin_meta(dialog, width=200)
    spin_meta.set(str(habito.get("meta", 7)))
    spin_meta.pack(padx=30, pady=(3, 15), anchor="w")

    def guardar():
        nuevo_nombre = entry_nombre.get().strip()
        nueva_cat = combo_cat.get()
        nueva_meta = int(spin_meta.get())

        if not nuevo_nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return

        ok, msg = hb.editar_habito(
            USUARIO_ACTUAL, SEMANA_ID,
            habito["nombre"], nuevo_nombre, nueva_cat, nueva_meta
        )
        if ok:
            dialog.destroy()
            render_tabla()
            render_panel_derecho()
        else:
            messagebox.showerror("Error", msg)

    crear_boton(dialog, "Guardar cambios", guardar,
                color=colores.COLORES["exito"], hover="#05b88a",
                width=180).pack(pady=10)


# ============================================================
# GRÁFICAS
# ============================================================
def abrir_ventana_grafica(titulo, figura):
    v = ctk.CTkToplevel(ventana)
    v.title(titulo)
    v.configure(fg_color=colores.COLORES["fondo"])
    v.after(0, lambda: maximizar_ventana(v))

    canvas = FigureCanvasTkAgg(figura, master=v)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
    return v


def mostrar_grafica():
    semana = hb.obtener_semana(USUARIO_ACTUAL, SEMANA_ID)
    fig = st.crear_figura_barras(semana)
    v = abrir_ventana_grafica(f"Estadísticas - {SEMANA_ID}", fig)

    datos = st.calcular_porcentajes(semana)
    if datos:
        mejor = datos[0]
        peor = datos[-1]
        resumen = ctk.CTkFrame(v, fg_color=colores.COLORES["panel"], corner_radius=10)
        resumen.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(resumen, text=f"🏆 Mejor: {mejor[0]} ({mejor[1]:.0f}%)",
                     text_color=colores.COLORES["exito"],
                     font=("Arial", 13, "bold")).pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(resumen, text=f"⚠️ A mejorar: {peor[0]} ({peor[1]:.0f}%)",
                     text_color=colores.COLORES["error"],
                     font=("Arial", 13, "bold")).pack(side="right", padx=20, pady=10)


def mostrar_grafica_categorias():
    semana = hb.obtener_semana(USUARIO_ACTUAL, SEMANA_ID)
    fig = st.crear_figura_categorias(semana)
    abrir_ventana_grafica(f"Distribución - {SEMANA_ID}", fig)


def mostrar_tendencia_global():
    fig = st.crear_figura_tendencia_global(USUARIO_ACTUAL)
    abrir_ventana_grafica("📈 Tendencia global", fig)


def mostrar_tendencia_por_habito():
    fig = st.crear_figura_tendencia_por_habito(USUARIO_ACTUAL)
    abrir_ventana_grafica("📈 Tendencia por hábito", fig)


# ============================================================
# VISTA "HOY"
# ============================================================
def mostrar_vista_hoy():
    for w in ventana.winfo_children():
        w.destroy()

    hoy = date.today()
    dia_idx = hoy.weekday()
    nombre_dia = hb.DIAS[dia_idx]
    fecha_str = hoy.strftime("%d/%m/%Y")

    header = ctk.CTkFrame(ventana, fg_color=colores.COLORES["panel"], height=60)
    header.pack(fill="x")

    crear_boton(header, "← Volver", mostrar_principal,
                width=120).pack(side="left", padx=20, pady=10)

    ctk.CTkLabel(header, text="📅 Hoy",
                 font=("Arial", 18, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(side="left", padx=10)

    semana_actual = hb.semana_actual_id()
    semana = hb.obtener_semana(USUARIO_ACTUAL, semana_actual)

    centro = ctk.CTkFrame(ventana, fg_color=colores.COLORES["fondo"])
    centro.pack(fill="both", expand=True, padx=40, pady=20)

    ctk.CTkLabel(centro, text=nombre_dia,
                 font=("Arial", 32, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(pady=(10, 0))

    ctk.CTkLabel(centro, text=fecha_str,
                 font=("Arial", 16),
                 text_color=colores.COLORES["texto_suave"]).pack(pady=(0, 20))

    if semana["habitos"]:
        cumplidos = sum(1 for h in semana["habitos"] if h["checks"][dia_idx])
        total = len(semana["habitos"])
        pct = (cumplidos / total) * 100 if total else 0
    else:
        cumplidos = 0
        total = 0
        pct = 0

    color_pct = colores.COLORES["exito"] if pct >= 70 else (
        colores.COLORES["acento_hover"] if pct >= 40 else colores.COLORES["error"])

    ctk.CTkLabel(centro, text=f"{cumplidos} / {total}",
                 font=("Arial", 48, "bold"),
                 text_color=color_pct).pack()

    barra = ctk.CTkProgressBar(centro, width=400, height=14,
                                progress_color=color_pct,
                                fg_color=colores.COLORES["panel_alt"])
    barra.pack(pady=10)
    barra.set(pct / 100)

    ctk.CTkLabel(centro, text=f"{pct:.0f}% del día",
                 font=("Arial", 14),
                 text_color=colores.COLORES["texto_suave"]).pack(pady=(0, 20))

    if not semana["habitos"]:
        ctk.CTkLabel(centro, text="No tienes hábitos esta semana.\nAñádelos desde la vista principal.",
                     font=("Arial", 14),
                     text_color=colores.COLORES["texto_suave"]).pack(pady=40)
        return

    contenedor_habitos = ctk.CTkScrollableFrame(centro,
                                                 fg_color="transparent",
                                                 scrollbar_button_color=colores.COLORES["acento"])
    contenedor_habitos.pack(fill="both", expand=True, padx=20, pady=10)

    for h in semana["habitos"]:
        marcado = h["checks"][dia_idx]
        info = hb.CATEGORIAS.get(h.get("categoria", "Otros"), hb.CATEGORIAS["Otros"])

        card = ctk.CTkFrame(contenedor_habitos,
                            fg_color=colores.COLORES["panel"],
                            corner_radius=15)
        card.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(card, text=info["icono"],
                     font=("Arial", 28)).pack(side="left", padx=(20, 10), pady=15)

        ctk.CTkLabel(card, text=h["nombre"],
                     font=("Arial", 18, "bold"),
                     text_color=colores.COLORES["texto"],
                     anchor="w").pack(side="left", fill="x", expand=True, pady=15)

        if marcado:
            texto_btn = "✓ Hecho"
            color_btn = colores.COLORES["exito"]
            hover_btn = "#05b88a"
        else:
            texto_btn = "Marcar"
            color_btn = colores.COLORES["acento"]
            hover_btn = colores.COLORES["acento_hover"]

        ctk.CTkButton(card, text=texto_btn,
                      width=140, height=45,
                      font=("Arial", 14, "bold"),
                      fg_color=color_btn, hover_color=hover_btn,
                      command=lambda n=h["nombre"], i=dia_idx: on_check_hoy(n, i)
                      ).pack(side="right", padx=20, pady=10)


def on_check_hoy(nombre, dia_idx):
    hb.toggle_check(USUARIO_ACTUAL, hb.semana_actual_id(), nombre, dia_idx)
    mostrar_vista_hoy()


# ============================================================
# CALENDARIO MENSUAL
# ============================================================
def mostrar_calendario(mes_offset=0):
    import calendar

    global MES_OFFSET
    MES_OFFSET = mes_offset

    for w in ventana.winfo_children():
        w.destroy()

    hoy = date.today()

    año = hoy.year
    mes = hoy.month + mes_offset
    while mes < 1:
        mes += 12
        año -= 1
    while mes > 12:
        mes -= 12
        año += 1

    primer_dia = date(año, mes, 1)
    dias_en_mes = calendar.monthrange(año, mes)[1]

    nombre_mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][mes - 1]

    header = ctk.CTkFrame(ventana, fg_color=colores.COLORES["panel"], height=60)
    header.pack(fill="x")

    crear_boton(header, "← Volver", mostrar_principal,
                width=120).pack(side="left", padx=20, pady=10)

    ctk.CTkLabel(header, text=f"📆 {nombre_mes} {año}",
                 font=("Arial", 18, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(side="left", padx=10)

    centro = ctk.CTkFrame(ventana, fg_color=colores.COLORES["fondo"])
    centro.pack(fill="both", expand=True, padx=40, pady=20)

    nav = ctk.CTkFrame(centro, fg_color="transparent")
    nav.pack(fill="x", pady=10)

    crear_boton(nav, "◀ Mes anterior",
                lambda: mostrar_calendario(mes_offset - 1),
                width=160).pack(side="left", padx=5)

    crear_boton(nav, "Mes actual",
                lambda: mostrar_calendario(0),
                color=colores.COLORES["acento_hover"],
                width=140).pack(side="left", padx=5)

    crear_boton(nav, "Mes siguiente ▶",
                lambda: mostrar_calendario(mes_offset + 1),
                width=160).pack(side="left", padx=5)

    cab = ctk.CTkFrame(centro, fg_color="transparent")
    cab.pack(fill="x", pady=(20, 5))

    for i, d in enumerate(["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]):
        cab.grid_columnconfigure(i, weight=1)
        ctk.CTkLabel(cab, text=d,
                     font=("Arial", 13, "bold"),
                     text_color=colores.COLORES["acento_hover"]).grid(row=0, column=i, padx=5)

    grid = ctk.CTkFrame(centro, fg_color="transparent")
    grid.pack(fill="both", expand=True, pady=5)

    for i in range(7):
        grid.grid_columnconfigure(i, weight=1)

    dia_semana_inicio = primer_dia.weekday()

    data = hb._cargar(USUARIO_ACTUAL)
    semanas = data["semanas"]

    fila = 0
    col = dia_semana_inicio

    for dia in range(1, dias_en_mes + 1):
        fecha = date(año, mes, dia)

        año_iso, semana_iso, _ = fecha.isocalendar()
        sid = f"{año_iso}-W{semana_iso:02d}"
        dia_semana = fecha.weekday()

        pct_dia = None
        if sid in semanas:
            total_c = 0
            total_m = 0
            for h in semanas[sid]["habitos"]:
                if h["checks"][dia_semana]:
                    total_c += 1
                total_m += 1
            if total_m > 0:
                pct_dia = (total_c / total_m) * 100

        if pct_dia is None:
            color_circ = colores.COLORES["panel_alt"]
            color_texto = colores.COLORES["texto_suave"]
        elif pct_dia >= 80:
            color_circ = colores.COLORES["exito"]
            color_texto = "#ffffff"
        elif pct_dia >= 50:
            color_circ = colores.COLORES["acento"]
            color_texto = "#ffffff"
        elif pct_dia > 0:
            color_circ = colores.COLORES["error"]
            color_texto = "#ffffff"
        else:
            color_circ = colores.COLORES["panel_alt"]
            color_texto = colores.COLORES["texto_suave"]

        celda = ctk.CTkFrame(grid, fg_color=color_circ,
                              corner_radius=10,
                              height=80)
        celda.grid(row=fila, column=col, padx=5, pady=5, sticky="nsew")
        celda.grid_propagate(False)

        es_hoy = (fecha == hoy)

        ctk.CTkLabel(celda, text=str(dia),
                     font=("Arial", 16, "bold"),
                     text_color=color_texto).pack(pady=(10, 0))

        if pct_dia is not None:
            ctk.CTkLabel(celda, text=f"{pct_dia:.0f}%",
                         font=("Arial", 11),
                         text_color=color_texto).pack()

        if es_hoy:
            ctk.CTkLabel(celda, text="HOY",
                         font=("Arial", 9, "bold"),
                         text_color="#ffffff").pack(side="bottom", pady=4)

        col += 1
        if col > 6:
            col = 0
            fila += 1

    leyenda = ctk.CTkFrame(centro, fg_color=colores.COLORES["panel"], corner_radius=10)
    leyenda.pack(fill="x", pady=(20, 0))

    items = [
        ("Nada", colores.COLORES["panel_alt"]),
        ("Poco (<50%)", colores.COLORES["error"]),
        ("Medio (50-79%)", colores.COLORES["acento"]),
        ("Excelente (≥80%)", colores.COLORES["exito"]),
    ]

    for texto, color in items:
        item = ctk.CTkFrame(leyenda, fg_color="transparent")
        item.pack(side="left", padx=15, pady=10)

        ctk.CTkFrame(item, fg_color=color, width=20, height=20,
                     corner_radius=5).pack(side="left", padx=5)
        ctk.CTkLabel(item, text=texto,
                     text_color=colores.COLORES["texto"],
                     font=("Arial", 11)).pack(side="left")


# ============================================================
# LOGROS
# ============================================================
def mostrar_logros():
    import logros as lg

    for w in ventana.winfo_children():
        w.destroy()

    header = ctk.CTkFrame(ventana, fg_color=colores.COLORES["panel"], height=60)
    header.pack(fill="x")

    crear_boton(header, "← Volver", mostrar_principal,
                width=120).pack(side="left", padx=20, pady=10)

    ctk.CTkLabel(header, text="🏅 Logros",
                 font=("Arial", 18, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(side="left", padx=10)

    centro = ctk.CTkScrollableFrame(ventana, fg_color=colores.COLORES["fondo"],
                                     scrollbar_button_color=colores.COLORES["acento"])
    centro.pack(fill="both", expand=True, padx=40, pady=20)

    desbloqueados = lg.cargar_logros(USUARIO_ACTUAL)
    total = len(lg.LOGROS)
    conseguidos = len(desbloqueados)

    ctk.CTkLabel(centro,
                 text=f"{conseguidos} / {total} logros desbloqueados",
                 font=("Arial", 20, "bold"),
                 text_color=colores.COLORES["acento_hover"]).pack(pady=(0, 15))

    pct = (conseguidos / total) * 100 if total else 0
    barra = ctk.CTkProgressBar(centro, width=500, height=14,
                                progress_color=colores.COLORES["exito"])
    barra.pack(pady=10)
    barra.set(pct / 100)

    ctk.CTkLabel(centro, text=f"{pct:.0f}% completado",
                 font=("Arial", 12),
                 text_color=colores.COLORES["texto_suave"]).pack(pady=(0, 30))

    grid = ctk.CTkFrame(centro, fg_color="transparent")
    grid.pack(fill="both", expand=True)

    columnas = 3
    for i in range(columnas):
        grid.grid_columnconfigure(i, weight=1)

    for idx, (logro_id, info) in enumerate(lg.LOGROS.items()):
        fila = idx // columnas
        col = idx % columnas

        desbloqueado = logro_id in desbloqueados
        fecha = desbloqueados.get(logro_id, "")

        card = ctk.CTkFrame(grid,
                            fg_color=colores.COLORES["panel"] if desbloqueado
                                     else colores.COLORES["panel_alt"],
                            corner_radius=15,
                            border_width=2,
                            border_color=colores.COLORES["exito"] if desbloqueado
                                        else colores.COLORES["borde"])
        card.grid(row=fila, column=col, padx=10, pady=10, sticky="nsew")

        icono_color = colores.COLORES["texto"] if desbloqueado else colores.COLORES["texto_suave"]
        ctk.CTkLabel(card, text=info["icono"] if desbloqueado else "🔒",
                     font=("Arial", 42),
                     text_color=icono_color).pack(pady=(20, 5))

        ctk.CTkLabel(card, text=info["nombre"],
                     font=("Arial", 15, "bold"),
                     text_color=colores.COLORES["exito"] if desbloqueado
                                else colores.COLORES["texto_suave"]).pack(pady=3)

        ctk.CTkLabel(card, text=info["desc"],
                     font=("Arial", 11),
                     text_color=colores.COLORES["texto_suave"],
                     wraplength=200).pack(pady=5, padx=10)

        if desbloqueado:
            ctk.CTkLabel(card, text=f"✓ {fecha}",
                         font=("Arial", 10, "bold"),
                         text_color=colores.COLORES["exito"]).pack(pady=(5, 15))
        else:
            ctk.CTkLabel(card, text="Bloqueado",
                         font=("Arial", 10),
                         text_color=colores.COLORES["texto_suave"]).pack(pady=(5, 15))


# ============================================================
# ACCIONES SOBRE HÁBITOS
# ============================================================
def on_check(nombre, dia_idx):
    hb.toggle_check(USUARIO_ACTUAL, SEMANA_ID, nombre, dia_idx)
    render_tabla()
    render_panel_derecho()

    try:
        import logros as lg
        nuevos = lg.comprobar_logros(USUARIO_ACTUAL)
        if nuevos:
            mensaje = "🏅 ¡Nuevo logro desbloqueado!\n\n"
            for nid in nuevos:
                info = lg.LOGROS.get(nid, {})
                mensaje += f"{info.get('icono', '🏅')} {info.get('nombre', nid)}\n"
                mensaje += f"   {info.get('desc', '')}\n\n"
            messagebox.showinfo("¡Logro desbloqueado!", mensaje)
    except Exception as e:
        print(f"[logros] Error: {e}")


def agregar_habito():
    nombre = ENTRY_NUEVO.get().strip()
    categoria = COMBO_CATEGORIA_NUEVA.get()
    meta = int(SPIN_META_NUEVA.get())

    if not nombre:
        return

    if hb.agregar_habito(USUARIO_ACTUAL, SEMANA_ID, nombre, categoria, meta):
        render_tabla()
        render_panel_derecho()
    else:
        messagebox.showwarning("Duplicado", "Ese hábito ya existe")


def borrar_habito(nombre):
    if messagebox.askyesno("Confirmar", f"¿Eliminar '{nombre}'?"):
        hb.eliminar_habito(USUARIO_ACTUAL, SEMANA_ID, nombre)
        render_tabla()
        render_panel_derecho()

# ============================================================
# EXPORTAR
# ============================================================
def exportar_pdf_semana():
    """Genera el PDF del resumen semanal."""
    try:
        ruta = ex.crear_pdf_semanal(USUARIO_ACTUAL, SEMANA_ID, colores.COLORES)

        # Preguntar si quiere abrirlo
        abrir = messagebox.askyesno(
            "PDF generado",
            f"✅ Se generó el PDF:\n\n{ruta}\n\n¿Quieres abrirlo ahora?"
        )
        if abrir:
            _abrir_archivo(ruta)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n\n{e}")


def exportar_imagen_redes():
    """Genera una imagen vertical para compartir en redes."""
    try:
        ruta = ex.crear_imagen_redes(USUARIO_ACTUAL, SEMANA_ID, colores.COLORES)

        abrir = messagebox.askyesno(
            "Imagen generada",
            f"✅ Se generó la imagen para redes:\n\n{ruta}\n\n"
            f"Medidas: 1080×1920 (formato historia)\n\n"
            f"¿Quieres abrirla ahora?"
        )
        if abrir:
            _abrir_archivo(ruta)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la imagen:\n\n{e}")


def _abrir_archivo(ruta):
    """Abre un archivo con la app por defecto del sistema."""
    import subprocess
    import sys
    try:
        if sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", str(ruta)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(ruta)])
        elif sys.platform.startswith("win"):
            import os
            os.startfile(str(ruta))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")


# ============================================================
# PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    ventana = ctk.CTk()
    ventana.title("Compendio de Hábitos")
    ventana.configure(fg_color=colores.COLORES["fondo"])
    ventana.after(0, maximizar)

    mostrar_login()
    ventana.mainloop()