import os
import requests
import cohere
from dotenv import load_dotenv
from supabase import create_client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
co = cohere.Client(os.getenv("MI_KEY"))

# Inicializamos la API (El nuevo servidor)
app = FastAPI(title="Globus Vermell API", description="El corazón de la IA para Flutter")

# CORS: Permite que tu app de Flutter se conecte sin problemas de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definimos el molde de los datos que recibiremos desde Flutter
class PeticionUsuario(BaseModel):
    pregunta: str

# --- 2. MOTOR DE BÚSQUEDA ---
def buscar_en_base_datos(pregunta_usuario):
    pregunta_limpia = pregunta_usuario.replace("?","").replace("¿","").replace(",","").lower()
    
    sinonimos_publicaciones = ["libro", "guia", "triptico", "catalogo", "bibliografia", "isbn", "editorial", "edicion", "paginas", "deposito legal"]
    palabras_prohibidas = ["globus", "vermell", "hablame", "sobre", "dime", "como", "para", "este", "esta", "quiero", "saber"]
    palabras_clave = [p.lower() for p in pregunta_limpia.split() if len(p) > 3 and p.lower() not in palabras_prohibidas]
    
    es_busqueda_publicacion = any(x in pregunta_limpia for x in ["publicacion", "publicaciones", "publicacions", "libros", "que han hecho"])
    
    if es_busqueda_publicacion:
        palabras_clave.extend(["libro", "guia", "isbn", "edicion"])
    
    if not palabras_clave:
        palabras_clave = ["asociación", "arquitectura"]
        
    edificios_dict = {}
    textos_web_dict = {}
    publicaciones_api = [] 
    
    for palabra in palabras_clave[:4]: 
        try:
            # MAGIA 1: ¡Ampliamos el límite a 15 para que quepan tus listas, nya~!
            res_ed = supabase.table("buildings").select("*").ilike("name", f"%{palabra}%").limit(15).execute()
            for ed in res_ed.data:
                llave_unica = ed.get('id', ed.get('name')) 
                edificios_dict[llave_unica] = ed 
                
            raiz = palabra[:5] if len(palabra) > 5 else palabra
            res_web = supabase.table("info_web").select("url, contenido").ilike("contenido", f"%{raiz}%").limit(8).execute()
            for web in res_web.data:
                textos_web_dict[web['url']] = web 
        except Exception as e:
            print(f"Error en Supabase: {e}")

        try:
            url_api = "https://e878e260-ae1f-4d8f-bda4.c44fbdcb2969.isard.nuvulet.itb.cat/publications/api/list"
            pagina_actual = 1
            max_paginas = 10 
            
            while pagina_actual <= max_paginas:
                respuesta_api = requests.get(url_api, params={"page": pagina_actual}, timeout=5)
                
                if respuesta_api.status_code != 200:
                    break
                    
                datos_api = respuesta_api.json()
                lista_resultados = datos_api.get("publications", []) if isinstance(datos_api, dict) else datos_api
                
                if not lista_resultados:
                    break
                    
                if isinstance(lista_resultados, list):
                    for pub in lista_resultados:
                        terminos_generales = ["publicaciones", "publicacion", "libro", "libros", "guia", "guias", "publicacions"]
                        if palabra.lower() in terminos_generales:
                            if pub not in publicaciones_api:
                                publicaciones_api.append(pub)
                        elif palabra.lower() in str(pub).lower():
                            if pub not in publicaciones_api:
                                publicaciones_api.append(pub)
                                
                pagina_actual += 1 
                
        except Exception as e:
            print(f"Error API: {e}")
            
    # MAGIA 2: Devolvemos hasta 15 edificios al contexto de la IA
    return list(edificios_dict.values())[:15], list(textos_web_dict.values())[:8], publicaciones_api[:5]

# --- 3. LÓGICA DE GENERACIÓN AISLADA ---
def generar_respuesta_ia(pregunta_final: str):
    edificios_contexto, web_contexto, api_contexto = buscar_en_base_datos(pregunta_final)
    
    historial = "" 

    prompt_final = f"""
    Eres el asistente oficial de "Globus Vermell", un experto en arquitectura y divulgación.
    
    REGLAS DE ORO:
    1. PARA EDIFICIOS: Tu fuente de verdad es el "CONTEXTO DE BASE DE DATOS".
    2. PARA PUBLICACIONES Y GUÍAS: Prioriza rigurosamente la información del "CONTEXTO DE LA API DE PUBLICACIONES".
    3. PARA PREGUNTAS GENERALES: Usa el "CONTEXTO DE LA WEB OFICIAL".
    4. LA REGLA DEL SILENCIO: NUNCA uses frases como "según el contexto proporcionado", "en la base de datos", "en la API" o "en el historial". Habla con naturalidad, como si supieras la información de memoria.
    5. LISTAS Y CONOCIMIENTO EXTERNO: Si el usuario pide listas generales de arquitectura (ej. "10 masías" o "10 edificios del GATCPAC") y no hay suficientes en la base de datos, usa tu conocimiento experto para completar la lista. Aclara sutilmente cuáles pertenecen a los registros de Globus Vermell y cuáles son otros ejemplos notables.
    
    CADENA DE PENSAMIENTO (Instrucciones internas de razonamiento):
    - Analiza en silencio qué tipo de pregunta es (edificio, publicación o general).
    - Revisa TODOS los contextos proporcionados abajo.
    - IMPORTANTE: NO escribas "Paso 1", "Paso 2", ni muestres tus pensamientos al usuario. Tu respuesta debe ser ÚNICAMENTE el resultado final, conversacional.
    
    --- CONTEXTO DE BASE DE DATOS (EDIFICIOS FILTRADOS) ---
    {edificios_contexto}
    
    --- CONTEXTO DE LA API DE PUBLICACIONES (LIBROS Y GUÍAS) ---
    {api_contexto}
    
    --- CONTEXTO DE LA WEB OFICIAL (PÁGINAS RELEVANTES) ---
    {web_contexto}
    
    --- HISTORIAL DEL CHAT ---
    {historial}
    
    PREGUNTA DEL USUARIO: {pregunta_final}
    """
    
    try:
        respuesta = co.chat(
            message=prompt_final,
            model="command-r7b-12-2024",
            temperature=0.1
        )
        # MAGIA 3: Devolvemos el texto Y la lista de edificios pura
        return respuesta.text, edificios_contexto
    except Exception as e:
        return f"Error de conexión con la API de Cohere. Detalles: {e}", []

# --- 4. LA PUERTA DE ENTRADA (ENDPOINT) ---
@app.post("/api/chat")
async def chatear(peticion: PeticionUsuario):
    try:
        # Recibimos las dos cosas de la función de arriba
        texto_ia, lista_edificios = generar_respuesta_ia(peticion.pregunta)
        
        # MAGIA 4: Le enviamos a Flutter un paquetito con el texto y los datos
        return {
            "respuesta": texto_ia,
            "edificios_relacionados": lista_edificios
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))