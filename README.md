# 🎯 Habitum — Tracker de Hábitos

Aplicación de escritorio para registrar hábitos diarios, visualizar progreso, mantener rachas y exportar estadísticas. Hecha en **Python** con **CustomTkinter**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-latest-purple)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Características

- 🔐 **Autenticación por usuario** con contraseña hasheada (SHA-256)
- 📅 **Vista semanal** con checklist de hábitos y metas configurables
- 🎯 **Metas por hábito** (1-7 días, % realista)
- 🔥 **Rachas** actuales y máximas por hábito
- 🏷️ **Categorías** (Salud, Aprendizaje, Productividad, Bienestar, Social, Otros)
- 📊 **Gráficas** de barras, pastel y tendencia entre semanas
- 📆 **Vista "Hoy"** con botones grandes para uso diario
- 🗓️ **Calendario mensual** con cumplimiento por día
- 🏅 **10 logros desbloqueables**
- 🌗 **Modo claro/oscuro**
- 📤 **Exportar a PDF** resumen semanal
- 📱 **Imagen vertical 1080×1920** para historias de redes
- 💾 **Persistencia local** en JSON

## 🖼️ Capturas

*(Aquí puedes poner screenshots de tu app)*

## 🚀 Instalación

```bash
git clone https://github.com/TU_USUARIO/habitum.git
cd habitum

python3 -m venv venv
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

pip install -r requirements.txt
python main.py
```

## 📦 Dependencias

- `customtkinter`
- `matplotlib`
- `pillow`
- `reportlab`

## 📁 Estructura

```
habitum/
├── main.py              # Interfaz principal
├── auth.py              # Autenticación
├── habitos.py           # Gestión de hábitos y semanas
├── stats.py             # Gráficas y estadísticas
├── logros.py            # Sistema de logros
├── exportar.py          # Exportar a PDF/imagen
├── colores.py           # Paletas de colores
└── datos/               # (ignorado) datos de usuario
```

## 📜 Licencia

MIT