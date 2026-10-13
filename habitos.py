import json
from pathlib import Path
from datetime import date, timedelta

DATOS_DIR = Path("datos")
DATOS_DIR.mkdir(exist_ok=True)

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

CATEGORIAS = {
    "Salud":         {"color": "#06d6a0", "icono": "💪"},
    "Aprendizaje":   {"color": "#7b2cbf", "icono": "📚"},
    "Productividad": {"color": "#4361ee", "icono": "⚡"},
    "Bienestar":     {"color": "#f72585", "icono": "🧘"},
    "Social":        {"color": "#ffb703", "icono": "👥"},
    "Otros":         {"color": "#a0a0b0", "icono": "📌"},
}

META_DEFAULT = 7


# ---------- RUTAS Y PERSISTENCIA ----------
def _archivo_usuario(usuario: str) -> Path:
    return DATOS_DIR / f"habitos_{usuario}.json"


def _cargar(usuario: str) -> dict:
    archivo = _archivo_usuario(usuario)
    if not archivo.exists():
        return {"semanas": {}}
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            if not contenido:
                return {"semanas": {}}
            data = json.loads(contenido)
            if "semanas" not in data:
                data["semanas"] = {}
            return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"[habitos] Error leyendo {archivo}: {e}")
        return {"semanas": {}}


def _guardar(usuario: str, data: dict):
    archivo = _archivo_usuario(usuario)
    tmp = archivo.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    tmp.replace(archivo)


# ---------- FECHAS Y SEMANAS ----------
def semana_actual_id() -> str:
    hoy = date.today()
    año, semana, _ = hoy.isocalendar()
    return f"{año}-W{semana:02d}"


def fechas_semana(semana_id: str) -> list[str]:
    año, semana = semana_id.split("-W")
    año, semana = int(año), int(semana)
    lunes = date.fromisocalendar(año, semana, 1)
    return [(lunes + timedelta(days=i)).strftime("%d/%m") for i in range(7)]


def obtener_semana(usuario: str, semana_id: str) -> dict:
    data = _cargar(usuario)
    if semana_id not in data["semanas"]:
        data["semanas"][semana_id] = {"habitos": []}
        _guardar(usuario, data)
    return data["semanas"][semana_id]


def guardar_semana(usuario: str, semana_id: str, semana: dict):
    data = _cargar(usuario)
    data["semanas"][semana_id] = semana
    _guardar(usuario, data)


def listar_semanas(usuario: str) -> list[str]:
    data = _cargar(usuario)
    return sorted(data["semanas"].keys(), reverse=True)


# ---------- METAS ----------
def _meta_de(habito: dict) -> int:
    """Devuelve la meta del hábito (default 7 si no existe)."""
    return max(1, min(7, int(habito.get("meta", META_DEFAULT))))


# ---------- CRUD DE HÁBITOS ----------
def agregar_habito(usuario: str, semana_id: str, nombre: str,
                   categoria: str = "Otros", meta: int = META_DEFAULT):
    semana = obtener_semana(usuario, semana_id)
    if any(h["nombre"].lower() == nombre.lower() for h in semana["habitos"]):
        return False
    meta = max(1, min(7, int(meta)))
    semana["habitos"].append({
        "nombre": nombre,
        "categoria": categoria,
        "meta": meta,
        "checks": [False] * 7
    })
    guardar_semana(usuario, semana_id, semana)
    return True


def eliminar_habito(usuario: str, semana_id: str, nombre: str):
    semana = obtener_semana(usuario, semana_id)
    semana["habitos"] = [h for h in semana["habitos"] if h["nombre"] != nombre]
    guardar_semana(usuario, semana_id, semana)


def editar_habito(usuario: str, semana_id: str, nombre_viejo: str,
                  nombre_nuevo: str, categoria_nueva: str,
                  meta_nueva: int = META_DEFAULT) -> tuple[bool, str]:
    """Edita nombre, categoría y meta de un hábito."""
    semana = obtener_semana(usuario, semana_id)

    habito = next((h for h in semana["habitos"] if h["nombre"] == nombre_viejo), None)
    if not habito:
        return False, "El hábito no existe"

    if nombre_nuevo.lower() != nombre_viejo.lower():
        if any(h["nombre"].lower() == nombre_nuevo.lower() for h in semana["habitos"]):
            return False, "Ya existe otro hábito con ese nombre"

    habito["nombre"] = nombre_nuevo
    habito["categoria"] = categoria_nueva
    habito["meta"] = max(1, min(7, int(meta_nueva)))
    guardar_semana(usuario, semana_id, semana)
    return True, "Hábito actualizado"


def toggle_check(usuario: str, semana_id: str, nombre: str, dia_idx: int):
    semana = obtener_semana(usuario, semana_id)
    for h in semana["habitos"]:
        if h["nombre"] == nombre:
            h["checks"][dia_idx] = not h["checks"][dia_idx]
            break
    guardar_semana(usuario, semana_id, semana)


def eliminar_semana(usuario: str, semana_id: str) -> bool:
    data = _cargar(usuario)
    if semana_id in data["semanas"]:
        del data["semanas"][semana_id]
        _guardar(usuario, data)
        return True
    return False


# ---------- ESTADÍSTICAS POR CATEGORÍA (usan metas) ----------
def calcular_por_categoria(semana: dict) -> dict:
    """
    Devuelve {categoria: (checks_totales, checks_posibles, porcentaje)}
    El % se calcula respecto a las METAS, no a 7 días.
    """
    resumen = {}
    for h in semana["habitos"]:
        cat = h.get("categoria", "Otros")
        if cat not in resumen:
            resumen[cat] = [0, 0]
        resumen[cat][0] += sum(h["checks"])
        resumen[cat][1] += _meta_de(h)

    return {
        cat: (v[0], v[1], min(100, (v[0] / v[1]) * 100) if v[1] else 0)
        for cat, v in resumen.items()
    }


def calcular_porcentajes_habitos(semana: dict) -> list[tuple[str, float, int, int]]:
    """
    Devuelve lista de (nombre, porcentaje, cumplidos, meta) ordenada por %.
    """
    resultado = []
    for h in semana["habitos"]:
        meta = _meta_de(h)
        cumplidos = sum(h["checks"])
        porcentaje = min(100, (cumplidos / meta) * 100)
        resultado.append((h["nombre"], porcentaje, cumplidos, meta))
    return sorted(resultado, key=lambda x: x[1], reverse=True)


# ---------- COPIAR SEMANA ANTERIOR (ahora con meta) ----------
def copiar_habitos_semana_anterior(usuario: str, semana_destino: str) -> tuple[bool, str, int]:
    """
    Copia los hábitos (nombres, categorías y metas) de la semana anterior a la destino.
    NO copia los checks (empiezan vacíos).
    Devuelve (ok, mensaje, cantidad_copiada).
    """
    data = _cargar(usuario)
    semanas = data["semanas"]

    if semana_destino not in semanas:
        return False, "La semana destino no existe", 0

    # Buscar la semana anterior más cercana que tenga hábitos
    semanas_con_habitos = sorted(
        [s for s in semanas.keys() if semanas[s]["habitos"] and s != semana_destino],
        reverse=True
    )

    anteriores = [s for s in semanas_con_habitos if s < semana_destino]
    if not anteriores:
        return False, "No hay semanas anteriores con hábitos", 0

    semana_origen = anteriores[0]
    origen = semanas[semana_origen]

    nombres_destino = {h["nombre"].lower() for h in semanas[semana_destino]["habitos"]}

    copiados = 0
    for h in origen["habitos"]:
        if h["nombre"].lower() in nombres_destino:
            continue
        semanas[semana_destino]["habitos"].append({
            "nombre": h["nombre"],
            "categoria": h.get("categoria", "Otros"),
            "meta": _meta_de(h),               # ✅ ahora sí copia la meta
            "checks": [False] * 7
        })
        copiados += 1

    _guardar(usuario, data)

    if copiados == 0:
        return False, f"Todos los hábitos de {semana_origen} ya estaban en esta semana", 0

    return True, f"Se copiaron {copiados} hábito(s) desde {semana_origen}", copiados


# ---------- RACHAS ----------
def calcular_rachas_semana(checks: list[bool]) -> tuple[int, int]:
    """
    Devuelve (racha_actual, racha_maxima) para los 7 días de una semana.
    - racha_actual: días consecutivos desde el primer check hasta el primer False
    - racha_maxima: la mejor racha dentro de la semana
    """
    max_racha = 0
    actual = 0
    for c in checks:
        if c:
            actual += 1
            max_racha = max(max_racha, actual)
        else:
            actual = 0

    racha_actual = 0
    for c in checks:
        if c:
            racha_actual += 1
        else:
            if racha_actual > 0:
                break

    return racha_actual, max_racha


def calcular_racha_global(usuario: str, nombre_habito: str) -> dict:
    """
    Calcula la racha global de un hábito mirando todas las semanas hacia atrás.
    """
    data = _cargar(usuario)
    semanas = data["semanas"]

    ids_ordenados = sorted(semanas.keys())

    tira = []
    for sid in ids_ordenados:
        for h in semanas[sid]["habitos"]:
            if h["nombre"] == nombre_habito:
                tira.extend(h["checks"])
                break

    if not tira:
        return {"racha_actual": 0, "racha_maxima": 0}

    max_racha = 0
    actual = 0
    for c in tira:
        if c:
            actual += 1
            max_racha = max(max_racha, actual)
        else:
            actual = 0

    racha_actual = 0
    for c in reversed(tira):
        if c:
            racha_actual += 1
        else:
            break

    return {
        "racha_actual": racha_actual,
        "racha_maxima": max_racha
    }


def calcular_rachas_todos(usuario: str, semana_id: str) -> dict:
    """
    Para la semana indicada, devuelve un dict:
      {nombre_habito: {"actual": int, "maxima_semana": int, "maxima_global": int}}
    """
    semana = obtener_semana(usuario, semana_id)
    resultado = {}

    for h in semana["habitos"]:
        _, racha_max_sem = calcular_rachas_semana(h["checks"])
        global_stats = calcular_racha_global(usuario, h["nombre"])

        resultado[h["nombre"]] = {
            "actual": global_stats["racha_actual"],
            "maxima_semana": racha_max_sem,
            "maxima_global": global_stats["racha_maxima"]
        }

    return resultado