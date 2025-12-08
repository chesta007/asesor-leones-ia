import os
import json
import requests
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
# La clave de Gemini se lee de las variables de entorno de GitHub Actions
# (La configuraste como GEMINI_API_KEY)
# La clave de Firebase se carga del JSON de configuración que DEBES SUBIR (ver Tarea 1.2)

# --- 2. CLAVES Y CONFIGURACIÓN DE FIREBASE ---
# La URL base para el Live Counter y Likes/Dislikes (proyecto-asesor-publico)
FIREBASE_BASE_URL = "https://proyecto-asesor-publico-default-rtdb.firebaseio.com"
FIREBASE_AUTH_FILE = 'firebase_admin_key.json' # Archivo de credenciales de servicio (ver Tarea 1.2)

# --- 3. PROMPT MAESTRO DE GEMINI ---
def get_gemini_prompt(city_name, yesterday_analysis="No hay análisis previo.", news_sources=""):
    """Genera el prompt maestro para Gemini con todo el contexto."""
    
    # Simulación de datos externos (en la V1.0, esto se obtendría de APIs reales)
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
    - Evento Destacado: Gran partido de fútbol en el Club Atlético Leones a las 19:30 hs.
    - Medios Locales: {news_sources}
    
    Genera una respuesta en formato JSON, exactamente como se muestra en el EJEMPLO DE OUTPUT, sin ninguna otra explicación o texto fuera del JSON.
    """

# --- 4. FUNCIÓN PRINCIPAL DE GENERACIÓN ---
def generate_and_upload():
    # 🚨 NOTA: En la escalabilidad, la ciudad se leería de un archivo de configuración
    city_name = "Leones, Córdoba"
    
    # 1. Obtener Análisis Previo (Simulación)
    # En la V2.0, esto obtendría el reporte semanal de Gemini. Por ahora, es una simulación.
    yesterday_analysis = "El informe de ayer tuvo alto 'Like' en Deportes. Mantener foco."
    
    # 2. Llamada a la API de Gemini (Usando la clave de GitHub Secrets)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Clave GEMINI_API_KEY no encontrada en el entorno.")
        return

    prompt = get_gemini_prompt(
        city_name,
        yesterday_analysis=yesterday_analysis,
        news_sources="[Municipalidad de Leones](https://www.leones.gob.ar/noticias)"
    )

    try:
        # Aquí se realizaría la llamada real a Gemini con el modelo apropiado
        # Por ahora, simulamos una respuesta compleja de Gemini con hipervínculos
        
        # 3. Respuesta Simulada (Debería venir de Gemini en JSON)
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
                    "contenido": "El Club Atlético Leones juega hoy a las 19:30 hs. La entrada general costará $1000. Encuentra las bases del evento en el [Sitio Oficial del Club](http://www.clubatleticoleones.com.ar/partido)."
                },
                {
                    "nombre": "☀️ Clima y Consejos",
                    "contenido": "Se espera una máxima de 29°C. La IA recomienda aprovechar la tarde. La Municipalidad de Leones anuncia cortes de agua preventivos; consulta el [Mapa de Cortes](https://www.leones.gob.ar/servicios/agua) para tu sector."
                }
            ]
        }
        
        # 4. Guardar JSON Final (Simulado)
        final_json_content = gemini_response_text
        
        # 5. Escribir noticias.json en el repositorio
        with open('noticias.json', 'w', encoding='utf-8') as f:
            json.dump(final_json_content, f, ensure_ascii=False, indent=4)
        print("✅ Generación de noticias.json exitosa.")
        
        # 6. Subir noticias.json a Firebase (Para futuras lecturas de otras apps)
        firebase_path = f"/leones/posts/{datetime.now().strftime('%Y%m%d')}.json"
        
        # Simulamos la carga a Firebase
        # requests.put(f"{FIREBASE_BASE_URL}{firebase_path}", json=final_json_content)
        # print(f"✅ Post guardado en Firebase: {firebase_path}")

    except Exception as e:
        print(f"❌ Error en la generación o subida: {e}")

if __name__ == "__main__":
    generate_and_upload()
