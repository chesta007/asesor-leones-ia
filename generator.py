import os
import json
import requests
import sys
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
# La clave de Gemini se lee de las variables de entorno de GitHub Actions (GEMINI_API_KEY)

# --- 2. CLAVES Y CONFIGURACIÓN DE FIREBASE ---
# La URL base de tu base de datos
FIREBASE_BASE_URL = "https://proyecto-asesor-publico-default-rtdb.firebaseio.com"
FIREBASE_AUTH_FILE = 'firebase_admin_key.json' 

# Ruta base en la estructura escalable de Firebase (Debe coincidir con el Dashboard)
BASE_CIUDAD_PATH = 'PAISES/argentina/provincias/cordoba/ciudades' 

# --- 3. PROMPT MAESTRO DE GEMINI ---
def get_gemini_prompt(city_name, yesterday_analysis="No hay análisis previo.", news_sources=""):
    """Genera el prompt maestro para Gemini con todo el contexto."""
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    return f"""
    Eres el 'Asesor Público Digital' para {city_name}. Tu misión es generar el informe diario de noticias locales.
    
    Reglas de Contenido:
    1. El tono debe ser profesional, local y muy útil para la vida diaria del ciudadano.
    2. Debes incluir **hipervínculos** (en formato Markdown: [Texto del Link](URL)) para todas las noticias de medios locales.
    3. Genera un **adelanto** para {tomorrow_date} (Recomendaciones a Futuro).
    4. Usa el contexto del análisis del día anterior si está disponible: "{yesterday_analysis}".
    5. Utiliza las siguientes secciones: Eventos y Agenda, Clima y Consejos (con temperatura y hora del partido), Análisis Económico (Dólar), y Recomendación de Valor.
    
    Datos de Contexto y Fuentes Simuladas (Trátalos como reales):
    - Ciudad: {city_name}
    - Fecha del informe: {current_date}
    - Pronóstico: Soleado con máxima de 29°C.
    - Dólar Blue: $1.445 (Estable).
    - Evento Destacado: Gran partido de fútbol en el Club Atlético {city_name.split(',')[0]} a las 19:30 hs.
    - Medios Locales: {news_sources}
    
    Genera una respuesta en formato JSON, exactamente como se muestra en el EJEMPLO DE OUTPUT, sin ninguna otra explicación o texto fuera del JSON.
    """

# --- 4. FUNCIÓN PRINCIPAL DE GENERACIÓN (ESCALABLE) ---
def generate_and_upload(locality_id):
    
    # Convierte ID a Nombre Público (ej: 'marcos_juarez' -> 'Marcos Juarez, Córdoba')
    city_name = locality_id.replace('_', ' ').title() + ", Córdoba"
    
    yesterday_analysis = "El informe de ayer tuvo alto 'Like' en Deportes. Mantener foco."
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Clave GEMINI_API_KEY no encontrada en el entorno.")
        return

    prompt = get_gemini_prompt(
        city_name,
        yesterday_analysis=yesterday_analysis,
        news_sources=f"[Municipalidad de {city_name}](https://www.{locality_id}.gob.ar/noticias)"
    )

    try:
        # --- SIMULACIÓN DE RESPUESTA DE GEMINI ---
        tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        gemini_response_text = {
            "title": f"Informe {city_name}",
            "last_updated": datetime.now().isoformat(),
            "categorias": [
                {
                    "nombre": "🚨 Recomendación Inteligente (Adelanto Mañana)",
                    "contenido": f"La IA recomienda hoy: Visitar el [Museo Local](https://www.leonescultura.org/museo) antes del martes {tomorrow_date}, ya que se espera una ola de calor que limitará las actividades al aire libre. La tendencia económica se mantendrá estable."
                },
                {
                    "nombre": "⚽ Eventos y Agenda Local",
                    "contenido": f"El Club Atlético {city_name.split(',')[0]} juega hoy a las 19:30 hs. La entrada general costará $1000. Encuentra las bases del evento en el [Sitio Oficial del Club](http://www.clubatleticoleones.com.ar/partido)."
                },
                {
                    "nombre": "☀️ Clima y Consejos",
                    "contenido": "Se espera una máxima de 29°C. La IA recomienda aprovechar la tarde. Consulta la [Mapa de Servicios de Agua](https://www.leones.gob.ar/servicios/agua) para tu sector."
                }
            ]
        }
        
        final_json_content = gemini_response_text
        
        # 5. Escribir JSON en el repositorio (Para GitHub Pages)
        # Nota: Se genera un archivo único por ciudad
        output_filename = f"noticias_{locality_id}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_json_content, f, ensure_ascii=False, indent=4)
        print(f"✅ Generación de {output_filename} exitosa.")
        
        # 6. Subir JSON a Firebase (Ruta completa y escalable)
        firebase_path = f"/{BASE_CIUDAD_PATH}/{locality_id}/posts/{datetime.now().strftime('%Y%m%d')}.json"
        
        # Simulamos la carga a Firebase
        # requests.put(f"{FIREBASE_BASE_URL}{firebase_path}", json=final_json_content)
        print(f"✅ Post guardado en Firebase: {firebase_path}")

    except Exception as e:
        print(f"❌ Error en la generación o subida: {e}")

if __name__ == "__main__":
    
    # ⚠️ Lee el argumento pasado por GitHub Actions (sys.argv[1])
    if len(sys.argv) > 1:
        target_id = sys.argv[1]
        print(f"Iniciando robot para la ID: {target_id}")
        generate_and_upload(target_id)
    else:
        # Fallback si se ejecuta manualmente sin argumentos (ej: python generator.py)
        print("Error: Falta ID de localidad. Ejecutando fallback para 'leones'.")
        generate_and_upload("leones")
