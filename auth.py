import json
import os
import hashlib
from pathlib import Path

DATOS_DIR = Path("datos")
DATOS_DIR.mkdir(exist_ok=True)
USUARIOS_FILE = DATOS_DIR / "usuarios.json"


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _cargar_usuarios() -> dict:
    if not USUARIOS_FILE.exists():
        return {}
    with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _guardar_usuarios(usuarios: dict):
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)


def registrar_usuario(usuario: str, password: str) -> tuple[bool, str]:
    usuario = usuario.strip().lower()
    if not usuario or not password:
        return False, "Usuario y contraseña son obligatorios"
    if len(password) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres"

    usuarios = _cargar_usuarios()
    if usuario in usuarios:
        return False, "El usuario ya existe"

    usuarios[usuario] = {"password": _hash(password)}
    _guardar_usuarios(usuarios)
    return True, "Usuario registrado correctamente"


def autenticar(usuario: str, password: str) -> bool:
    usuario = usuario.strip().lower()
    usuarios = _cargar_usuarios()
    if usuario not in usuarios:
        return False
    return usuarios[usuario]["password"] == _hash(password)