import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def _colores_tema():
    """Devuelve colores de fondo/texto según el tema activo."""
    try:
        import colores
        c = colores.COLORES
        # Para gráficas, siempre preferimos fondo oscuro para que se vean
        # las líneas de colores. Pero si estás en claro, usamos un gris suave.
        if colores.get_tema() == "claro":
            return {
                "fondo":    "#ffffff",
                "texto":    "#1a1a2e",
                "borde":    "#a0a0b0",
                "eje":      "#6b6b80",
                "barra_ok": "#059669",
                "barra_mid":"#7b2cbf",
                "barra_bad":"#dc2626",
            }
        else:
            return {
                "fondo":    "#16213e",
                "texto":    "#eaeaea",
                "borde":    "#a0a0b0",
                "eje":      "#a0a0b0",
                "barra_ok": "#06d6a0",
                "barra_mid":"#7b2cbf",
                "barra_bad":"#ef476f",
            }
    except Exception:
        # Fallback por si algo falla
        return {
            "fondo":    "#16213e",
            "texto":    "#eaeaea",
            "borde":    "#a0a0b0",
            "eje":      "#a0a0b0",
            "barra_ok": "#06d6a0",
            "barra_mid":"#7b2cbf",
            "barra_bad":"#ef476f",
        }


def calcular_porcentajes(semana: dict) -> list[tuple[str, float]]:
    """Compatibilidad con el código viejo. Devuelve [(nombre, pct), ...]"""
    import habitos as hb
    datos = hb.calcular_porcentajes_habitos(semana)
    return [(n, pct) for n, pct, _, _ in datos]


def crear_figura_barras(semana: dict) -> Figure:
    import habitos as hb

    datos = hb.calcular_porcentajes_habitos(semana)  # (nombre, pct, cumplidos, meta)
    t = _colores_tema()

    fig = Figure(figsize=(6, 4), dpi=100, facecolor=t["fondo"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(t["fondo"])

    if not datos:
        ax.text(0.5, 0.5, "Sin hábitos", ha="center", va="center",
                color=t["texto"], fontsize=14)
        ax.axis("off")
        return fig

    nombres = [d[0] for d in datos]
    valores = [d[1] for d in datos]

    colores = [t["barra_ok"] if v >= 70 else t["barra_mid"] if v >= 40 else t["barra_bad"]
               for v in valores]

    bars = ax.bar(nombres, valores, color=colores, edgecolor=t["texto"], linewidth=0.5)

    for bar, (nombre, pct, cumplidos, meta) in zip(bars, datos):
        ax.text(bar.get_x() + bar.get_width() / 2, pct + 2,
                f"{cumplidos}/{meta}",
                ha="center", color=t["texto"], fontsize=9, fontweight="bold")

    ax.set_ylim(0, 110)
    ax.set_ylabel("% respecto a la meta", color=t["texto"])
    ax.set_title("Cumplimiento semanal (vs meta)", color=t["texto"])
    ax.tick_params(colors=t["texto"])
    for spine in ax.spines.values():
        spine.set_color(t["borde"])

    fig.tight_layout()
    return fig


def crear_figura_categorias(semana: dict) -> Figure:
    import habitos as hb

    resumen = hb.calcular_por_categoria(semana)
    t = _colores_tema()

    fig = Figure(figsize=(6, 4), dpi=100, facecolor=t["fondo"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(t["fondo"])

    if not resumen:
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                color=t["texto"], fontsize=14)
        ax.axis("off")
        return fig

    etiquetas = []
    valores = []
    colores = []

    for cat, (_, _, pct) in resumen.items():
        info = hb.CATEGORIAS.get(cat, hb.CATEGORIAS["Otros"])
        etiquetas.append(cat)
        valores.append(pct)
        colores.append(info["color"])

    wedges, texts, autotexts = ax.pie(
        valores, labels=etiquetas, colors=colores,
        autopct="%1.0f%%", startangle=90,
        textprops={"color": t["texto"], "fontsize": 10}
    )
    for t2 in autotexts:
        t2.set_color("#1a1a2e")
        t2.set_fontweight("bold")

    ax.set_title("Distribución por categoría", color=t["texto"], pad=15)

    fig.tight_layout()
    return fig

# ---------- GRÁFICAS DE TENDENCIA ----------
def _recolectar_historico(usuario: str) -> list[tuple[str, float]]:
    """
    Devuelve lista ordenada cronológicamente de (semana_id, % total de esa semana).
    El % total = promedio de cumplimiento de todos los hábitos, respetando metas.
    """
    import habitos as hb

    data = hb._cargar(usuario)
    semanas = data["semanas"]

    resultado = []
    for sid in sorted(semanas.keys()):
        habitos = semanas[sid]["habitos"]
        if not habitos:
            continue

        total_cumplidos = 0
        total_meta = 0
        for h in habitos:
            total_cumplidos += sum(h["checks"])
            total_meta += hb._meta_de(h)

        if total_meta == 0:
            continue

        pct = min(100, (total_cumplidos / total_meta) * 100)
        resultado.append((sid, pct))

    return resultado


def _recolectar_historico_por_habito(usuario: str) -> dict:
    """
    Devuelve {nombre_habito: [(semana_id, pct), ...]}
    Solo incluye semanas donde el hábito existía.
    """
    import habitos as hb

    data = hb._cargar(usuario)
    semanas = data["semanas"]

    historico = {}
    for sid in sorted(semanas.keys()):
        for h in semanas[sid]["habitos"]:
            meta = hb._meta_de(h)
            cumplidos = sum(h["checks"])
            pct = min(100, (cumplidos / meta) * 100) if meta else 0
            historico.setdefault(h["nombre"], []).append((sid, pct))

    return historico


def crear_figura_tendencia_global(usuario: str) -> Figure:
    """Línea del % total por semana."""
    from colores import COLORES, get_tema

    datos = _recolectar_historico(usuario)
    t = _colores_tema()

    fig = Figure(figsize=(9, 4.5), dpi=100, facecolor=t["fondo"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(t["fondo"])

    if len(datos) < 2:
        ax.text(0.5, 0.5, "Necesitas al menos 2 semanas con datos",
                ha="center", va="center",
                color=t["texto"], fontsize=14)
        ax.axis("off")
        return fig

    semanas = [d[0] for d in datos]
    valores = [d[1] for d in datos]

    # Línea principal
    ax.plot(semanas, valores, marker="o", markersize=8,
            color=COLORES["acento_hover"], linewidth=2.5,
            markerfacecolor=COLORES["exito"],
            markeredgecolor=COLORES["acento_hover"],
            markeredgewidth=2)

    # Área bajo la línea (efecto bonito)
    ax.fill_between(range(len(semanas)), valores,
                    alpha=0.15, color=COLORES["acento_hover"])

    # Etiquetas de valor encima de cada punto
    for i, v in enumerate(valores):
        ax.text(i, v + 4, f"{v:.0f}%", ha="center",
                color=t["texto"], fontsize=10, fontweight="bold")

    # Línea horizontal de referencia al 70%
    ax.axhline(y=70, color=COLORES["exito"], linestyle="--",
               alpha=0.4, linewidth=1)
    ax.text(len(semanas) - 1, 72, "meta 70%",
            color=COLORES["exito"], fontsize=9, alpha=0.8, ha="right")

    ax.set_ylim(0, 110)
    ax.set_ylabel("% cumplimiento total", color=t["texto"])
    ax.set_title("📈 Tendencia global entre semanas",
                 color=t["texto"], fontsize=14, fontweight="bold", pad=15)
    ax.tick_params(colors=t["texto"])
    for spine in ax.spines.values():
        spine.set_color(t["borde"])

    # Rotar labels si son muchas semanas
    if len(semanas) > 8:
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    fig.tight_layout()
    return fig


def crear_figura_tendencia_por_habito(usuario: str) -> Figure:
    """Una línea por hábito, mostrando su evolución en el tiempo."""
    from colores import COLORES

    historico = _recolectar_historico_por_habito(usuario)
    t = _colores_tema()

    fig = Figure(figsize=(10, 5), dpi=100, facecolor=t["fondo"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(t["fondo"])

    if len(historico) == 0:
        ax.text(0.5, 0.5, "Sin datos aún",
                ha="center", va="center",
                color=t["texto"], fontsize=14)
        ax.axis("off")
        return fig

    # Paleta de colores para las líneas (ciclo si hay más hábitos que colores)
    paleta = [
        "#06d6a0", "#7b2cbf", "#4361ee", "#f72585",
        "#ffb703", "#ef476f", "#118ab2", "#8338ec",
        "#fb5607", "#3a86ff", "#ffbe0b", "#8ac926"
    ]

    # Todas las semanas únicas ordenadas
    todas_las_semanas = sorted({s for datos in historico.values() for s, _ in datos})

    for i, (nombre, datos) in enumerate(historico.items()):
        color = paleta[i % len(paleta)]

        # Mapear semana → % (None si no existía esa semana)
        mapa = dict(datos)
        valores = [mapa.get(s) for s in todas_las_semanas]

        # Filtrar None para que la línea no se rompa feo
        xs = [j for j, v in enumerate(valores) if v is not None]
        ys = [v for v in valores if v is not None]

        ax.plot(xs, ys, marker="o", markersize=6,
                linewidth=2, color=color, label=nombre,
                markerfacecolor=color,
                markeredgecolor=t["texto"],
                markeredgewidth=1)

    ax.set_xticks(range(len(todas_las_semanas)))
    ax.set_xticklabels(todas_las_semanas)

    ax.set_ylim(0, 110)
    ax.set_ylabel("% respecto a la meta", color=t["texto"])
    ax.set_title("📈 Tendencia por hábito",
                 color=t["texto"], fontsize=14, fontweight="bold", pad=15)
    ax.tick_params(colors=t["texto"])
    for spine in ax.spines.values():
        spine.set_color(t["borde"])

    # Leyenda fuera del área de la gráfica
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5),
              fontsize=10, framealpha=0.9,
              facecolor=t["fondo"], edgecolor=t["borde"],
              labelcolor=t["texto"])

    if len(todas_las_semanas) > 8:
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # Línea de referencia 70%
    ax.axhline(y=70, color=COLORES["exito"], linestyle="--",
               alpha=0.3, linewidth=1)

    fig.tight_layout()
    return fig


