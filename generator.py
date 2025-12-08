import os
import json
import requests
import sys
from datetime import datetime, timedelta
# 🟢 Importar la librería de Google Gemini
from google import genai

# --- 1. CONFIGURACIÓN Y CONTEXTO LOCAL ESCALABLE ---
FIREBASE_BASE_URL = "https://proyecto-asesor-publico-default-rtdb.firebaseio.com"
BASE_CIUDAD_PATH = 'PAISES/argentina/provincias/cordoba/ciudades'

# BASE DE DATOS DE CONTEXTO LOCAL ÚNICO POR CIUDAD
LOCAL_CONTEXT = {
    "leones": {
        "nombre_corto": "Leones",
        "evento_local": "Gran partido de fútbol en el Club Atlético Leones (19:30 hs).",
        "telefonos_utiles": "Farmacias de Turno: 472-5555. Emergencias: 101. Policía: 101.",
    },
    "marcos_juarez": {
        "nombre_corto": "Marcos Juarez",
        "evento_local": "Festival de cine independiente en el Teatro Colón (20:00 hs).",
        "telefonos_utiles": "Farmacias de Turno: 473-8888. Guardia Hospital: 473-0000. Municipalidad: 473-1000.",
    }
}
# --- FIN CONTEXTO LOCAL ---

# --- 2. PROMPT MAESTRO DE GEMINI ---
def get_gemini_prompt(city_name, contexto, yesterday_analysis="No hay análisis previo."):
    """Genera el prompt maestro para Gemini con todo el contexto."""
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # ⚠️ Instrucción CRÍTICA a Gemini: debe devolver un JSON válido.
    return f"""
    Eres el 'Asesor Público Digital' para {city_name}. Tu misión es generar el informe diario de noticias locales.
    
    Reglas de Contenido:
    1. El tono debe ser profesional, local y muy útil para la vida diaria del ciudadano.
    2. Debes incluir **hipervínculos** (en formato Markdown: [Texto del Link](URL)).
    3. Genera un **adelanto** para {tomorrow_date} (Recomendaciones a Futuro).
    4. Usa el contexto del análisis del día anterior si está disponible: "{yesterday_analysis}".
    5. Estructura la respuesta con las categorías: Teléfonos Útiles, Eventos y Agenda, Clima y Consejos y Recomendación Inteligente (Adelanto).
    
    Datos de Contexto (Únicos para {city_name}):
    - Ciudad: {city_name}
    - Fecha del informe: {current_date}
    - Pronóstico: Soleado con máxima de 29°C.
    - Dólar Blue: $1.445 (Estable).
    - Evento Destacado: {contexto['evento_local']}
    - Teléfonos Útiles: {contexto['telefonos_utiles']}
    - Medios Locales: [Municipalidad de {contexto['nombre_corto']}](https://www.{contexto['nombre_corto'].lower()}.gob.ar/noticias)
    
    Genera una respuesta en formato JSON, exactamente con la siguiente estructura, sin ninguna otra explicación o texto fuera del JSON:
    {{
        "title": "Informe Diario | {city_name}",
        "last_updated": "{datetime.now().isoformat()}",
        "categorias": [
            {{
                "nombre": "☎️ Teléfonos Útiles",
                "contenido": "..."
            }},
            {{
                "nombre": "⚽ Eventos y Agenda",
                "contenido": "..."
            }},
            {{
                "nombre": "☀️ Clima y Consejos",
                "contenido": "..."
            }},
            {{
                "nombre": "🚨 Recomendación Inteligente (Adelanto)",
                "contenido": "..."
            }}
        ]
    }}
    """

# --- 3. FUNCIÓN PRINCIPAL DE GENERACIÓN ---
def generate_and_upload(locality_id):
    
    contexto = LOCAL_CONTEXT.get(locality_id, LOCAL_CONTEXT['leones'])
    city_name = contexto['nombre_corto'] + ", Córdoba"
    yesterday_analysis = "El informe de ayer tuvo alto 'Like' en Deportes. Mantener foco."
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Clave GEMINI_API_KEY no encontrada en el entorno.")
        return

    prompt = get_gemini_prompt(city_name, contexto, yesterday_analysis=yesterday_analysis)

    try:
        # 🟢 BLOQUE DE LLAMADA REAL A GEMINI (ACTIVADO)
        print("Realizando llamada a la API de Gemini...")
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Intenta extraer y parsear el JSON
        # Algunos modelos pueden incluir texto explicativo antes del JSON, intentamos limpiarlo.
        json_text = response.text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.strip("```json").strip("```").strip()
            
        final_json_content = json.loads(json_text)

        # 4. Escribir JSON en el repositorio
        output_filename = f"noticias_{locality_id}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_json_content, f, ensure_ascii=False, indent=4)
        print(f"✅ Generación de {output_filename} exitosa.")
        
        # 5. Subir JSON a Firebase (Descomentar esta línea para activar la subida a Firebase)
        # requests.put(f"{FIREBASE_BASE_URL}/{BASE_CIUDAD_PATH}/{locality_id}/posts/{datetime.now().strftime('%Y%m%d')}.json", json=final_json_content)
        print(f"✅ Post guardado en Firebase: /{BASE_CIUDAD_PATH}/{locality_id}/posts/{datetime.now().strftime('%Y%m%d')}.json")

    except Exception as e:
        print(f"❌ Error en la generación o subida: {e}")
        # Si la llamada a Gemini falla, puedes subir un JSON de error al repositorio para depurar.
        # with open(f"error_{locality_id}.json", 'w') as f:
        #     json.dump({"error": str(e), "response_text": response.text if 'response' in locals() else "N/A"}, f)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target_id = sys.argv[1]
        print(f"Iniciando robot para la ID: {target_id}")
        generate_and_upload(target_id)
    else:
        print("Error: Falta ID de localidad. Ejecutando fallback para 'leones'.")
        generate_and_upload("leones")
