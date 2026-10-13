import json
from pathlib import Path
from datetime import date

DATOS_DIR = Path("datos")
DATOS_DIR.mkdir(exist_ok=True)

# Definición de logros: id -> {nombre, descripcion, icono}
LOGROS = {
    "primera_semana":     {"nombre": "Primer paso", "icono": "🌱",
                           "desc": "Crea tu primera semana con hábitos"},
    "primera_racha_3":    {"nombre": "En racha", "icono": "🔥",
                           "desc": "Consigue una racha de 3 días"},
    "racha_7":            {"nombre": "Semana perfecta", "icono": "🏅",
                           "desc": "Racha de 7 días en un hábito"},
    "racha_30":           {"nombre": "Imparable", "icono": "🚀",
                           "desc": "Racha de 30 días en un hábito"},
    "semana_completa":    {"nombre": "Semana redonda", "icono": "💯",
                           "desc": "Completa el 100% de una semana"},
    "100_checks":         {"nombre": "Centenario", "icono": "💎",
                           "desc": "Acumula 100 checks en total"},
    "500_checks":         {"nombre": "Veterano", "icono": "👑",
                           "desc": "Acumula 500 checks en total"},
    "todas_categorias":   {"nombre": "Bien redondeado", "icono": "🎯",
                           "desc": "Usa al menos 4 categorías distintas"},
    "10_habitos":         {"nombre": "Coleccionista", "icono": "📦",
                           "desc": "Crea 10 hábitos en una semana"},
    "5_semanas":          {"nombre": "Constante", "icono": "📅",
                           "desc": "Ten 5 semanas registradas"},
}


def _archivo(usuario: str) -> Path:
    return DATOS_DIR / f"logros_{usuario}.json"


def cargar_logros(usuario: str) -> dict:
    archivo = _archivo(usuario)
    if not archivo.exists():
        return {}
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            if not contenido:
                return {}
            return json.loads(contenido)
    except (json.JSONDecodeError, OSError):
        return {}


def guardar_logros(usuario: str, logros: dict):
    archivo = _archivo(usuario)
    tmp = archivo.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(logros, f, indent=4, ensure_ascii=False)
    tmp.replace(archivo)


def _total_checks(usuario: str) -> int:
    import habitos as hb
    data = hb._cargar(usuario)
    total = 0
    for sid, sem in data["semanas"].items():
        for h in sem["habitos"]:
            total += sum(h["checks"])
    return total


def _mejor_racha_historica(usuario: str) -> int:
    import habitos as hb
    data = hb._cargar(usuario)
    mejor = 0
    nombres = set()
    for sid, sem in data["semanas"].items():
        for h in sem["habitos"]:
            nombres.add(h["nombre"])

    for nombre in nombres:
        stats = hb.calcular_racha_global(usuario, nombre)
        mejor = max(mejor, stats["racha_maxima"])
    return mejor


def _categorias_usadas(usuario: str) -> set:
    import habitos as hb
    data = hb._cargar(usuario)
    cats = set()
    for sid, sem in data["semanas"].items():
        for h in sem["habitos"]:
            cats.add(h.get("categoria", "Otros"))
    return cats


def _cantidad_semanas(usuario: str) -> int:
    import habitos as hb
    data = hb._cargar(usuario)
    return len(data["semanas"])


def _mejor_semana_pct(usuario: str) -> float:
    import habitos as hb
    data = hb._cargar(usuario)
    mejor = 0
    for sid, sem in data["semanas"].items():
        total_c = 0
        total_m = 0
        for h in sem["habitos"]:
            total_c += sum(h["checks"])
            total_m += hb._meta_de(h)
        if total_m:
            pct = min(100, total_c / total_m * 100)
            mejor = max(mejor, pct)
    return mejor


def _max_habitos_una_semana(usuario: str) -> int:
    import habitos as hb
    data = hb._cargar(usuario)
    return max((len(sem["habitos"]) for sem in data["semanas"].values()), default=0)


def comprobar_logros(usuario: str) -> list[str]:
    """
    Comprueba todos los logros y devuelve la lista de IDs NUEVOS desbloqueados
    en esta llamada (para poder mostrar notificación).
    """
    logros_actuales = cargar_logros(usuario)
    nuevos = []

    def desbloquear(logro_id, condicion):
        if condicion and not logros_actuales.get(logro_id):
            logros_actuales[logro_id] = date.today().isoformat()
            nuevos.append(logro_id)

    # Calcular métricas una vez
    total_checks = _total_checks(usuario)
    mejor_racha = _mejor_racha_historica(usuario)
    cats = _categorias_usadas(usuario)
    num_semanas = _cantidad_semanas(usuario)
    mejor_sem_pct = _mejor_semana_pct(usuario)
    max_habitos = _max_habitos_una_semana(usuario)

    # Comprobar
    desbloquear("primera_semana", num_semanas >= 1 and max_habitos >= 1)
    desbloquear("primera_racha_3", mejor_racha >= 3)
    desbloquear("racha_7", mejor_racha >= 7)
    desbloquear("racha_30", mejor_racha >= 30)
    desbloquear("semana_completa", mejor_sem_pct >= 100)
    desbloquear("100_checks", total_checks >= 100)
    desbloquear("500_checks", total_checks >= 500)
    desbloquear("todas_categorias", len(cats) >= 4)
    desbloquear("10_habitos", max_habitos >= 10)
    desbloquear("5_semanas", num_semanas >= 5)

    guardar_logros(usuario, logros_actuales)
    return nuevos