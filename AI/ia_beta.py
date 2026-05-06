import os
import requests
import io
import streamlit as st
import cohere
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
from supabase import create_client

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
co = cohere.Client(os.getenv("MI_KEY"))

# --- 2. MOTOR DE BÚSQUEDA ---
def buscar_en_base_datos(pregunta_usuario):
    pregunta_limpia = pregunta_usuario.replace("?","").replace("¿","").replace(",","").lower()
    
    # Diccionario de expansión para capturar lo que no dice "publicación"
    sinonimos_publicaciones = ["libro", "guia", "triptico", "catalogo", "bibliografia", "isbn", "editorial", "edicion", "paginas", "deposito legal"]
    
    # Filtro de ruido
    palabras_prohibidas = ["globus", "vermell", "hablame", "sobre", "dime", "como", "para", "este", "esta", "quiero", "saber"]
    palabras_clave = [p.lower() for p in pregunta_limpia.split() if len(p) > 3 and p.lower() not in palabras_prohibidas]
    
    # Si el usuario pregunta por publicaciones, expandimos la búsqueda automáticamente
    es_busqueda_publicacion = any(x in pregunta_limpia for x in ["publicacion", "publicaciones", "publicacions", "libros", "que han hecho"])
    
    if es_busqueda_publicacion:
        palabras_clave.extend(["libro", "guia", "isbn", "edicion"])
    
    # Fallback general
    if not palabras_clave:
        palabras_clave = ["asociación", "arquitectura"]
        
    edificios_dict = {}
    textos_web_dict = {}
    publicaciones_api = [] 
    
    # Limitamos a las 4 palabras clave más potentes para no saturar
    for palabra in palabras_clave[:4]: 
        try:
            # Búsqueda en buildings
            res_ed = supabase.table("buildings").select("*").ilike("name", f"%{palabra}%").limit(3).execute()
            for ed in res_ed.data:
                llave_unica = ed.get('id', ed.get('name')) 
                edificios_dict[llave_unica] = ed 
                
            # Búsqueda en info_web (Buscamos la palabra o su raíz)
            raiz = palabra[:5] if len(palabra) > 5 else palabra
            res_web = supabase.table("info_web").select("url, contenido").ilike("contenido", f"%{raiz}%").limit(8).execute()
            for web in res_web.data:
                textos_web_dict[web['url']] = web 
        except Exception as e:
            print(f"Error en Supabase: {e}")

        # --- B. BÚSQUEDA EN API ---
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
            
    return list(edificios_dict.values())[:3], list(textos_web_dict.values())[:8], publicaciones_api[:5]

# --- 3. INTERFAZ DE USUARIO (STREAMLIT) ---
st.title(" IA de Globus Vermell")
st.write("Pregúntame sobre nuestros trípticos, proyectos, edificios y publicaciones. ¡También puedes usar tu voz!")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])

# Entrada de texto tradicional
pregunta_escrita = st.chat_input("...o escribe tu pregunta aquí directamente")

# --- SISTEMA SPEECH-TO-TEXT ---
texto_transcrito = None

col1, col2 = st.columns([1, 5])
with col1:
    # Botón visual del micrófono
    audio_bytes = audio_recorder(text="Hablar", icon_name="microphone", icon_size="2x")

if audio_bytes:
    audio_file = io.BytesIO(audio_bytes)
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            with st.spinner("Transcribiendo la voz"):
                texto_transcrito = recognizer.recognize_google(audio_data, language="es-ES")
        except sr.UnknownValueError:
            st.error("¡Ups! No he podido entender el audio. ¿Puedes hablar más cerca?")
        except sr.RequestError:
            st.error("Error de conexión con el servicio de reconocimiento de voz.")

# Consolidamos la pregunta (voz o texto)
pregunta_final = pregunta_escrita or texto_transcrito

# --- 4. LÓGICA DEL CHAT Y GENERACIÓN NLP ---
if pregunta_final:
    st.session_state.mensajes.append({"role": "user", "content": pregunta_final})
    with st.chat_message("user"):
        st.write(pregunta_final)

    with st.chat_message("assistant"):
        with st.spinner('Moviendo engranajes en Bases de Datos y API externa...'):
            
            edificios_contexto, web_contexto, api_contexto = buscar_en_base_datos(pregunta_final)
            
            with st.expander("Ver Rayos X del Contexto (Debugging)"):
                st.write(f"Edificios (Supabase): {len(edificios_contexto)}")
                st.write(f"Web Oficial (Supabase): {len(web_contexto)}")
                st.write(f"Publicaciones (API Isard): {len(api_contexto)}")
                if api_contexto:
                    st.write("Conexión con la API exitosa")

            historial = ""
            for msg in st.session_state.mensajes[-5:-1]: 
                historial += f"{msg['role']}: {msg['content']}\n"

            prompt_final = f"""
            Eres el asistente oficial de "Globus Vermell", un experto en arquitectura y divulgación.
            
            REGLAS DE ORO:
            1. PARA EDIFICIOS: Tu fuente de verdad es el "CONTEXTO DE BASE DE DATOS".
            2. PARA PUBLICACIONES Y GUÍAS: Prioriza rigurosamente la información del "CONTEXTO DE LA API DE PUBLICACIONES".
            3. PARA PREGUNTAS GENERALES: Usa el "CONTEXTO DE LA WEB OFICIAL".
            4. LA REGLA DEL SILENCIO: NUNCA uses frases como "según el contexto proporcionado", "en la base de datos", "en la API" o "en el historial". Habla con naturalidad, como si supieras la información de memoria.
            5. PROHIBICIÓN DE ALUCINAR: Si la información no está en los contextos, tienes ESTRICTAMENTE PROHIBIDO inventar o aportar datos externos. Debes decir EXACTAMENTE: "Lo siento mucho, pero no tengo esa información en mis registros de Globus Vermell." y TERMINAR TU RESPUESTA AHÍ MISMO. NO añadas "Sin embargo..." ni ninguna otra frase de relleno.
            
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
                texto_respuesta = respuesta.text
            except Exception as e:
                texto_respuesta = f"Error de conexión con la API de Cohere. Detalles: {e}"
            
            st.write(texto_respuesta)
            st.session_state.mensajes.append({"role": "assistant", "content": texto_respuesta})