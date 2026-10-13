"""
Módulo de exportación: PDF semanal e imagen vertical para redes.
"""
import io
from pathlib import Path
from datetime import date

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader

import habitos as hb

EXPORT_DIR = Path("exportados")
EXPORT_DIR.mkdir(exist_ok=True)


# ============================================================
# HELPERS DE COLORES
# ============================================================
def _hex_a_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _cargar_fuente(tamaño: int, bold: bool = False):
    """Intenta cargar una fuente decente del sistema. Si falla, usa la default."""
    candidatas = [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # Otras comunes
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        # Windows
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
    ]
    for ruta in candidatas:
        try:
            return ImageFont.truetype(ruta, tamaño)
        except Exception:
            continue
    return ImageFont.load_default()


# ============================================================
# IMAGEN VERTICAL PARA REDES (1080x1920)
# ============================================================
def crear_imagen_redes(usuario: str, semana_id: str,
                        paleta: dict,
                        incluir_app: bool = True) -> Path:
    """
    Crea una imagen vertical 1080x1920 (formato historia Instagram/WhatsApp).
    Devuelve la ruta del archivo PNG generado.
    """
    ancho, alto = 1080, 1920

    # Colores
    fondo = _hex_a_rgb(paleta.get("fondo", "#1a1a2e"))
    acento = _hex_a_rgb(paleta.get("acento", "#7b2cbf"))
    acento_hover = _hex_a_rgb(paleta.get("acento_hover", "#9d4edd"))
    exito = _hex_a_rgb(paleta.get("exito", "#06d6a0"))
    texto = _hex_a_rgb(paleta.get("texto", "#eaeaea"))
    texto_suave = _hex_a_rgb(paleta.get("texto_suave", "#a0a0b0"))
    panel = _hex_a_rgb(paleta.get("panel", "#16213e"))

    # Crear imagen con degradado simple (arriba más oscuro, abajo más claro)
    img = Image.new("RGB", (ancho, alto), fondo)
    draw = ImageDraw.Draw(img)

    # Degradado vertical sutil
    for y in range(alto):
        factor = y / alto
        r = int(fondo[0] * (1 - factor) + acento[0] * factor * 0.35)
        g = int(fondo[1] * (1 - factor) + acento[1] * factor * 0.35)
        b = int(fondo[2] * (1 - factor) + acento[2] * factor * 0.35)
        draw.line([(0, y), (ancho, y)], fill=(r, g, b))

    # Datos de la semana
    semana = hb.obtener_semana(usuario, semana_id)
    habitos = semana["habitos"]

    total_cumplidos = 0
    total_meta = 0
    for h in habitos:
        total_cumplidos += sum(h["checks"])
        total_meta += hb._meta_de(h)

    pct_total = min(100, (total_cumplidos / total_meta) * 100) if total_meta else 0

    # Rachas
    rachas = hb.calcular_rachas_todos(usuario, semana_id)
    mejor_racha_nombre = None
    mejor_racha_valor = 0
    for nombre, d in rachas.items():
        if d["maxima_global"] > mejor_racha_valor:
            mejor_racha_valor = d["maxima_global"]
            mejor_racha_nombre = nombre

    # Top 3 hábitos por %
    porcentajes = hb.calcular_porcentajes_habitos(semana)[:3]

    # Fuentes
    f_titulo = _cargar_fuente(72, bold=True)
    f_sub = _cargar_fuente(36, bold=False)
    f_gigante = _cargar_fuente(220, bold=True)
    f_medio = _cargar_fuente(52, bold=True)
    f_item = _cargar_fuente(40, bold=True)
    f_item_pct = _cargar_fuente(48, bold=True)
    f_pie = _cargar_fuente(30, bold=False)

    # ---------- TÍTULO ----------
    y = 120
    draw.text((ancho/2, y), "COMPENDIO DE HÁBITOS",
              font=f_sub, fill=texto_suave, anchor="mm")

    y += 90
    draw.text((ancho/2, y), f"Semana {semana_id}",
              font=f_titulo, fill=texto, anchor="mm")

    y += 100
    # Línea decorativa
    draw.line([(ancho/2 - 150, y), (ancho/2 + 150, y)], fill=acento_hover, width=4)

    y += 120
    # ---------- % GIGANTE ----------
    color_pct = exito if pct_total >= 70 else (acento_hover if pct_total >= 40 else (239, 71, 111))
    draw.text((ancho/2, y), f"{pct_total:.0f}%",
              font=f_gigante, fill=color_pct, anchor="mm")

    y += 160
    draw.text((ancho/2, y), "de cumplimiento semanal",
              font=f_sub, fill=texto_suave, anchor="mm")

    y += 90
    draw.text((ancho/2, y), f"{total_cumplidos} / {total_meta} checks",
              font=f_sub, fill=texto, anchor="mm")

    # ---------- TOP 3 HÁBITOS ----------
    y += 160
    draw.text((ancho/2, y), "🏆 TOP HÁBITOS",
              font=f_medio, fill=acento_hover, anchor="mm")

    y += 80
    medallas = ["🥇", "🥈", "🥉"]
    for i, (nombre, pct, cumpl, meta) in enumerate(porcentajes):
        # Card
        card_x0 = 80
        card_x1 = ancho - 80
        card_y0 = y
        card_y1 = y + 110
        draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1],
                                radius=20, fill=panel)

        # Nombre con medalla
        emoji = medallas[i] if i < 3 else "•"
        try:
            draw.text((card_x0 + 40, (card_y0 + card_y1) / 2),
                      f"{emoji} {nombre}",
                      font=f_item, fill=texto, anchor="lm")
        except Exception:
            draw.text((card_x0 + 40, (card_y0 + card_y1) / 2),
                      f"#{i+1} {nombre}",
                      font=f_item, fill=texto, anchor="lm")

        # Porcentaje a la derecha
        color_i = exito if pct >= 70 else (acento_hover if pct >= 40 else (239, 71, 111))
        draw.text((card_x1 - 40, (card_y0 + card_y1) / 2),
                  f"{pct:.0f}%",
                  font=f_item_pct, fill=color_i, anchor="rm")

        # Barra de progreso mini dentro del card
        barra_y = card_y1 - 18
        barra_x0 = card_x0 + 40
        barra_x1 = card_x1 - 40
        draw.rounded_rectangle([barra_x0, barra_y, barra_x1, barra_y + 8],
                                radius=4, fill=(40, 40, 60))
        barra_relleno = barra_x0 + int((barra_x1 - barra_x0) * (pct / 100))
        draw.rounded_rectangle([barra_x0, barra_y, barra_relleno, barra_y + 8],
                                radius=4, fill=color_i)

        y = card_y1 + 20

    # ---------- MEJOR RACHA ----------
    if mejor_racha_nombre:
        y += 30
        draw.text((ancho/2, y), "🔥 MEJOR RACHA",
                  font=f_medio, fill=acento_hover, anchor="mm")

        y += 80
        card_x0 = 80
        card_x1 = ancho - 80
        card_y0 = y
        card_y1 = y + 120
        draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1],
                                radius=20, fill=panel)

        draw.text((card_x0 + 40, (card_y0 + card_y1) / 2),
                  f"🔥 {mejor_racha_nombre}",
                  font=f_item, fill=texto, anchor="lm")

        draw.text((card_x1 - 40, (card_y0 + card_y1) / 2),
                  f"{mejor_racha_valor} días",
                  font=f_item_pct, fill=exito, anchor="rm")

    # ---------- PIE ----------
    if incluir_app:
        pie_y = alto - 100
        draw.text((ancho/2, pie_y),
                  f"@ {usuario} • Compedio de Hábitos",
                  font=f_pie, fill=texto_suave, anchor="mm")

    # Guardar
    archivo = EXPORT_DIR / f"redes_{usuario}_{semana_id}.png"
    img.save(archivo, "PNG")
    return archivo


# ============================================================
# PDF SEMANAL
# ============================================================
def crear_pdf_semanal(usuario: str, semana_id: str, paleta: dict) -> Path:
    """
    Crea un PDF A4 con el resumen semanal.
    Devuelve la ruta del archivo generado.
    """
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure

    semana = hb.obtener_semana(usuario, semana_id)

    archivo = EXPORT_DIR / f"resumen_{usuario}_{semana_id}.pdf"
    c = pdf_canvas.Canvas(str(archivo), pagesize=A4)
    ancho_pag, alto_pag = A4

    # Colores
    fondo = HexColor(paleta.get("fondo", "#1a1a2e"))
    panel = HexColor(paleta.get("panel", "#16213e"))
    acento = HexColor(paleta.get("acento", "#7b2cbf"))
    acento_hover = HexColor(paleta.get("acento_hover", "#9d4edd"))
    exito = HexColor(paleta.get("exito", "#06d6a0"))
    texto = HexColor(paleta.get("texto", "#eaeaea"))
    texto_suave = HexColor(paleta.get("texto_suave", "#a0a0b0"))

    # ---------- FONDO ----------
    c.setFillColor(fondo)
    c.rect(0, 0, ancho_pag, alto_pag, fill=1, stroke=0)

    # ---------- CABECERA ----------
    c.setFillColor(texto)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(2*cm, alto_pag - 2.5*cm, "Compendio de Hábitos")

    c.setFillColor(texto_suave)
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, alto_pag - 3.4*cm, f"Usuario: {usuario}")

    c.setFillColor(acento_hover)
    c.setFont("Helvetica-Bold", 18)
    c.drawRightString(ancho_pag - 2*cm, alto_pag - 2.5*cm, f"Semana {semana_id}")

    # ---------- RESUMEN ----------
    habitos = semana["habitos"]
    total_cumplidos = sum(sum(h["checks"]) for h in habitos)
    total_meta = sum(hb._meta_de(h) for h in habitos)
    pct_total = min(100, (total_cumplidos / total_meta) * 100) if total_meta else 0

    # Card resumen
    y_top = alto_pag - 5*cm
    c.setFillColor(panel)
    c.roundRect(2*cm, y_top - 3*cm, ancho_pag - 4*cm, 3*cm,
                radius=12, fill=1, stroke=0)

    c.setFillColor(texto_suave)
    c.setFont("Helvetica", 11)
    c.drawString(3*cm, y_top - 1*cm, "Cumplimiento total")

    color_pct = exito if pct_total >= 70 else (acento_hover if pct_total >= 40 else HexColor("#ef476f"))
    c.setFillColor(color_pct)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(3*cm, y_top - 2.4*cm, f"{pct_total:.0f}%")

    c.setFillColor(texto)
    c.setFont("Helvetica", 14)
    c.drawRightString(ancho_pag - 3*cm, y_top - 1.7*cm,
                       f"{total_cumplidos} / {total_meta} checks")

    # ---------- GRÁFICA DE BARRAS ----------
    try:
        datos = hb.calcular_porcentajes_habitos(semana)
        if datos:
            fig = Figure(figsize=(7, 3), dpi=100, facecolor=paleta.get("fondo", "#1a1a2e"))
            ax = fig.add_subplot(111)
            ax.set_facecolor(paleta.get("fondo", "#1a1a2e"))

            nombres = [d[0][:15] for d in datos]
            valores = [d[1] for d in datos]
            colores_bar = [
                paleta.get("exito", "#06d6a0") if v >= 70
                else paleta.get("acento", "#7b2cbf") if v >= 40
                else "#ef476f"
                for v in valores
            ]
            ax.bar(nombres, valores, color=colores_bar)
            ax.set_ylim(0, 110)
            ax.set_title("Cumplimiento por hábito", color=paleta.get("texto", "#eaeaea"))
            ax.tick_params(colors=paleta.get("texto", "#eaeaea"), labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(paleta.get("texto_suave", "#a0a0b0"))
            ax.set_ylabel("% vs meta", color=paleta.get("texto", "#eaeaea"))
            import matplotlib.pyplot as plt
            plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
            fig.tight_layout()

            # Renderizar figura a imagen en memoria
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=100, facecolor=fig.get_facecolor())
            buf.seek(0)

            # Insertar en el PDF
            y_img = y_top - 3*cm - 1*cm
            c.drawImage(ImageReader(buf), 2*cm, y_img - 8*cm,
                        width=ancho_pag - 4*cm, height=8*cm)
    except Exception as e:
        print(f"[pdf] Error gráfica barras: {e}")

    # ---------- GRÁFICA DE CATEGORÍAS ----------
    try:
        resumen_cat = hb.calcular_por_categoria(semana)
        if resumen_cat:
            fig = Figure(figsize=(5, 3), dpi=100, facecolor=paleta.get("fondo", "#1a1a2e"))
            ax = fig.add_subplot(111)
            ax.set_facecolor(paleta.get("fondo", "#1a1a2e"))

            etiquetas = []
            valores = []
            colores_pie = []
            for cat, (_, _, pct) in resumen_cat.items():
                info = hb.CATEGORIAS.get(cat, hb.CATEGORIAS["Otros"])
                etiquetas.append(cat)
                valores.append(pct)
                colores_pie.append(info["color"])

            ax.pie(valores, labels=etiquetas, colors=colores_pie,
                   autopct="%1.0f%%", startangle=90,
                   textprops={"color": paleta.get("texto", "#eaeaea"), "fontsize": 9})
            ax.set_title("Distribución por categoría", color=paleta.get("texto", "#eaeaea"))
            fig.tight_layout()

            buf2 = io.BytesIO()
            fig.savefig(buf2, format="png", dpi=100, facecolor=fig.get_facecolor())
            buf2.seek(0)

            y_img2 = y_top - 3*cm - 1*cm - 8*cm - 0.5*cm
            c.drawImage(ImageReader(buf2), 2*cm, y_img2 - 7*cm,
                        width=ancho_pag - 4*cm, height=7*cm)
    except Exception as e:
        print(f"[pdf] Error gráfica pastel: {e}")

    # ---------- TOP HÁBITOS (TEXTO) ----------
    y_tabla = 4*cm
    c.setFillColor(acento_hover)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y_tabla + 1.5*cm, "Top hábitos")

    c.setFillColor(texto)
    c.setFont("Helvetica", 11)

    top = hb.calcular_porcentajes_habitos(semana)
    for i, (nombre, pct, cumpl, meta) in enumerate(top[:5]):
        medalla = ["🥇", "🥈", "🥉", "•", "•"][i]
        y_item = y_tabla + 0.9*cm - i*0.5*cm
        c.drawString(2*cm, y_item, f"#{i+1}  {nombre}")
        c.drawRightString(ancho_pag - 2*cm, y_item, f"{cumpl}/{meta}  ({pct:.0f}%)")

    # ---------- PIE ----------
    c.setFillColor(texto_suave)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(ancho_pag/2, 1.5*cm,
                         f"Generado el {date.today().strftime('%d/%m/%Y')}")

    c.showPage()
    c.save()
    return archivo