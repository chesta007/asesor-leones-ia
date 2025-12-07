import os
import json
from google import genai
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
LOCALIDAD = "Leones, Córdoba, Argentina"
# Estas son las categorías que la IA generará en el post diario
CATEGORIAS = ["Eventos y Agenda", "Clima y Consejos", "Análisis Económico Local", "Deportes y Pronósticos"]

def get_gemini_client():
    """Inicializa la conexión a Gemini usando la clave secreta de GitHub."""
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        # Esto nos avisará que necesitamos configurar la clave secreta en GitHub.
        raise ValueError("La clave GEMINI_API_KEY no está configurada en las variables de entorno.")
    return genai.Client(api_key=API_KEY)

def crear_prompt_asesor(categoria):
    """Genera el prompt detallado para la IA en base a la categoría."""
    
    # 1. Definimos el rol y el contexto del output para garantizar la calidad
    prompt = f"""
    Eres un 'Asesor Público Digital' para la localidad de {LOCALIDAD}. Tu tarea es generar un informe breve y útil para la gente de la zona.
    
    ---
    
    [INSTRUCCIONES DE FORMATO]
    * Responde SOLO con el contenido. No uses saludos, introducciones o frases de relleno.
    * El output debe ser siempre un bloque de texto en formato Markdown.
    * El título principal debe ser un H2 (##).
    
    [CONTENIDO REQUERIDO: {categoria}]
    
    Genera un análisis enfocado en {categoria} para hoy, {datetime.now().strftime('%d de %B de %Y')}.
    
    """
    
    # 2. Añadimos instrucciones específicas para las categorías difíciles (para guiar mejor a la IA)
    if 'Económico' in categoria:
        prompt += """
        * Incluye una mención sobre la tendencia del dólar Blue/CCL (ej. 'Parece estable' o 'Al alza').
        * Ofrece un consejo práctico de ahorro o inversión para un habitante de Leones.
        * No uses datos numéricos precisos, enfócate en tendencias y recomendaciones.
        """
    elif 'Deportes' in categoria:
         prompt += """
        * Analiza las chances de ganar de los equipos locales en sus próximos partidos.
        * Incluye una predicción o un resumen de resultados recientes.
        """
    
    return prompt

def generar_contenido_ia(cliente_gemini, prompt):
    """Llama a la API de Gemini y retorna el texto generado."""
    print(f"Generando contenido con prompt para: {prompt[:30]}...")
    
    try:
        response = cliente_gemini.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error al llamar a Gemini: {e}")
        return f"## Error de Generación en IA: {prompt}"

def main():
    """Función principal: Orquesta la generación de todos los contenidos."""
    
    # Inicialización
    try:
        gemini_client = get_gemini_client()
    except ValueError as e:
        print(f"Fallo crítico: {e}")
        # Si la clave API no está, el programa se detiene.
        return

    # Aquí almacenaremos todo el contenido generado para el frontend.
    noticias_generadas = {
        "last_updated": datetime.now().isoformat(),
        "localidad": LOCALIDAD,
        "categorias": []
    }

    # Proceso de Generación por Categoría
    for categoria in CATEGORIAS:
        prompt = crear_prompt_asesor(categoria)
        contenido_markdown = generar_contenido_ia(gemini_client, prompt)
        
        # Guardamos la estructura final que usará el frontend
        noticias_generadas["categorias"].append({
            "nombre": categoria,
            "contenido": contenido_markdown
        })
        
    # Guardado Final
    # Guardamos todo en un único archivo JSON que el HTML leerá después.
    # El archivo será 'noticias.json'
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_generadas, f, ensure_ascii=False, indent=4)
    
    print("--------------------------------")
    print("✅ Proceso completado. Archivo 'noticias.json' generado.")
    print("--------------------------------")

if __name__ == "__main__":
    main()
