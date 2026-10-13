TEMAS = {
    "oscuro": {
        "fondo":        "#1a1a2e",
        "panel":        "#16213e",
        "panel_alt":    "#0f1729",
        "acento":       "#7b2cbf",
        "acento_hover": "#9d4edd",
        "exito":        "#06d6a0",
        "error":        "#ef476f",
        "texto":        "#eaeaea",
        "texto_suave":  "#a0a0b0",
        "borde":        "#2a2a4a"
    },
    "claro": {
        "fondo":        "#f5f5fa",
        "panel":        "#ffffff",
        "panel_alt":    "#eaeaf5",
        "acento":       "#7b2cbf",
        "acento_hover": "#9d4edd",
        "exito":        "#059669",
        "error":        "#dc2626",
        "texto":        "#1a1a2e",
        "texto_suave":  "#6b6b80",
        "borde":        "#d0d0e0"
    }
}

# Tema activo (se modifica en runtime)
_tema_actual = "oscuro"
COLORES = TEMAS[_tema_actual].copy()


def set_tema(nombre: str):
    global _tema_actual, COLORES
    _tema_actual = nombre
    COLORES = TEMAS[nombre].copy()


def get_tema() -> str:
    return _tema_actual 