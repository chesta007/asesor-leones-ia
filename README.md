# 🦁 Asesor Público Digital | Leones, Córdoba 📰

Este proyecto es la **Plataforma Experimental BETA** para un servicio de noticias y asesoramiento hiper-local 100% automatizado para la ciudad de **Leones, Córdoba, Argentina**.

El objetivo es crear un medio de utilidad diaria con **costo de infraestructura cero** (gracias a las herramientas gratuitas de GitHub) y con un alto potencial de crecimiento.

---

## 🤖 El Corazón del Proyecto: Automatización 100% Autónoma

El proyecto opera bajo un flujo de trabajo programado y sin intervención manual para la publicación:

1.  **Generación de Contenido (7:00 AM):** El **GitHub Action (el Reloj)** se activa automáticamente todos los días.
2.  **Motor IA:** El script `generator.py` se conecta a la **API de Gemini Plus** para compilar y redactar el post diario (eventos, economía, clima, deportes).
3.  **Publicación:** El contenido se guarda en `noticias.json` y se publica automáticamente al repositorio.

## 👥 Flujo de Revisión y Control de Calidad

Aunque la publicación es autónoma, la calidad es humana:

* **Horario de Revisión:** El equipo (Ema, Román y Pablo) tiene de **7:00 AM a 8:00 AM** para revisar y editar el borrador generado por la IA.
* **Edición Móvil:** La revisión se realiza directamente en la interfaz móvil de GitHub.

## 🛠️ Estructura del Proyecto (Fase BETA)

| Archivo | Función |
| :--- | :--- |
| **`generator.py`** | El Motor: Código de Python que contacta a Gemini y estructura las categorías. |
| **`requirements.txt`** | Dependencias: Lista de librerías (`google-genai`) que debe instalar la automatización. |
| **`index.html`** | El Frontend: La página web que lee `noticias.json` y muestra el post diario. |
| **`.github/workflows/...`** | El Reloj: La configuración YAML que ejecuta el script diariamente (el flujo autónomo). |
| **`noticias.json`** | La Memoria: Archivo generado por la IA que contiene el post del día. |

---

¡Bienvenidos al futuro de las noticias locales!
