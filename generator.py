import os
import json
import requests
import sys
from datetime import datetime, timedelta
# Importar la librería de Google Gemini
from google import genai
from google.genai.errors import APIError 

# --- 1. CONFIGURACIÓN Y CONTEXTO LOCAL ESCALABLE ---
FIREBASE_BASE_URL = "https://proyecto-asesor-publico-default-rtdb.firebaseio.com"
BASE_CIUDAD_PATH = 'PAISES/argentina/provincias/cordoba/ciudades'

# BASE DE DATOS DE CONTEXTO LOCAL ÚNICO POR CIUDAD (AMPLIADO)
LOCAL_CONTEXT = {
    "leones": {
        "nombre_corto": "Leones",
        "evento_local": "Gran partido de fútbol en el Club Atlético Leones (19:30 hs).",
        # 🟢 CONTEXTO AMPLIADO PARA TELÉFONOS (con URL simulada)
        "farmacia_turno_contexto": "La farmacia de turno es 'Farmacia Central', ubicada en Bv. San Martín 123. Su teléfono es 472-5555. Enlace a Google Maps: [Ubicación Farmacia Central](https://maps.app.goo.gl/LeonesFarmaciaCentral)",
    },
    "marcos_juarez": {
        "nombre_corto": "Marcos Juarez",
        "evento_local": "Festival de cine independiente en el Teatro Colón (20:00 hs).",
        # 🟢 CONTEXTO AMPLIADO PARA TELÉFONOS (con URL simulada)
        "farmacia_turno_contexto": "La farmacia de turno es 'Farmacia Nueva', ubicada en Av. Belgrano 500. Su teléfono es 473-8888. Enlace a Google Maps: [Ubicación Farmacia Nueva](https://maps.app.goo.gl/MarcosJuarezFarmaciaNueva)",
    }
}
# --- FIN CONTEXTO LOCAL ---

# --- 2. PROMPT MAESTRO DE GEMINI (MODIFICADO) ---
def get_gemini_prompt(city_name, contexto, yesterday_analysis="No hay análisis previo."):
    """Genera el prompt maestro para Gemini con todo el contexto, solicitando más detalles."""
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    return f"""
    Eres el 'Asesor Público Digital' para {city_name}. Tu misión es generar el informe diario de noticias locales.
    
    Contexto Local Adicional:
    * Farmacia de Turno: {contexto['farmacia_turno_contexto']}
    * Evento Principal de Hoy: {contexto['evento_local']}
    * Análisis de Interacción de Ayer: {yesterday_analysis}
    
    Reglas de Contenido:
    1. El tono debe ser profesional, local y muy útil para el ciudadano.
    2. El contenido debe ser único y relevante para {city_name}.
    3. Siempre genera la respuesta en formato JSON.
    4. El JSON debe tener la siguiente estructura estricta: {{ "title": "...", "last_updated": "...", "categorias": [{{ "nombre": "...", "contenido": "..." }}, ...] }}
    5. **Estructura de la Categoría "☎️ Teléfonos Útiles":**
        * Debes usar el texto completo del contexto de la Farmacia de Turno, incluyendo el **nombre, la dirección y el enlace de Google Maps en formato Markdown**, además de otros teléfonos de emergencia.
    6. La fecha del informe es {current_date} y la del adelanto es {tomorrow_date}.
    7. Debes generar el contenido de todas estas categorías:
        * "☎️ Teléfonos Útiles"
        * "⚽ Eventos y Agenda"
        * "☀️ Clima y Consejos"
        * "🚨 Recomendación Inteligente (Adelanto)"

    Simulación de datos externos (para la IA):
    - Clima: Soleado, 29°C.
    - Economía local: Dólar Blue estable en $1.445.
    
    Genera el JSON completo ahora.
    """

# --- 3. LÓGICA DE EJECUCIÓN DEL ROBOT (SIN CAMBIOS) ---
def generate_and_save_report(locality_id):
    """Llama a Gemini, analiza la respuesta y guarda el JSON."""
    
    if locality_id not in LOCAL_CONTEXT:
        print(f"❌ ID de localidad desconocido: {locality_id}")
        return

    contexto = LOCAL_CONTEXT[locality_id]
    city_name = contexto['nombre_corto']
    
    # Obtener el historial de likes/dislikes de Firebase (Simulación)
    # 🟢 Aquí la IA leerá en el futuro los votos por categoría
    yesterday_analysis = "El reporte de ayer en la categoría 'Deportes' tuvo un alto índice de 'Like' en ambas ciudades." 

    prompt = get_gemini_prompt(city_name, contexto, yesterday_analysis)
    
    try:
        # Inicialización de la API de Gemini
        client = genai.Client()

        # Llamada al modelo Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # 3. Limpieza y Parseo del JSON
        json_text = response.text
        # Quita markdown si existe (```json...```)
        json_text = json_text.strip().lstrip("```json").rstrip("```").strip()
            
        final_json_content = json.loads(json_text)
        
        # 4. Añadir timestamp de actualización
        final_json_content['last_updated'] = datetime.now().isoformat()

        # 5. Escribir JSON en el repositorio
        output_filename = f"noticias_{locality_id}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_json_content, f, ensure_ascii=False, indent=4)
        print(f"✅ Generación de {output_filename} exitosa.")
        
        # 6. Subir JSON a Firebase (Simulación)
        print(f"✅ Post guardado en Firebase: /{BASE_CIUDAD_PATH}/{locality_id}/posts/{datetime.now().strftime('%Y%m%d')}.json")

    except APIError as e:
        print(f"❌ Error de la API de Gemini. Verifica la clave y permisos: {e}")
    except json.JSONDecodeError:
        print(f"❌ Error: Gemini no devolvió un JSON válido. Respuesta: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error en la generación o subida: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python generator.py <locality_id>")
        sys.exit(1)
        
    locality_id = sys.argv[1]
    generate_and_save_report(locality_id)
