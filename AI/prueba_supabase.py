import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

# 1. Cargamos TODAS tus llaves secretas 
load_dotenv()
mi_llave_ia = os.getenv("MI_KEY")
supa_url = os.getenv("SUPABASE_URL")
supa_key = os.getenv("SUPABASE_KEY")

# 2. Conexión a Supabase 
@st.cache_resource
def iniciar_supabase():
    return create_client(supa_url, supa_key)

supabase = iniciar_supabase()
genai.configure(api_key=mi_llave_ia)

# --- 3. NUEVO: EL ROBOT QUE LEE LA WEB ---
@st.cache_data(ttl=3600) # Guarda la info por 1 hora para no saturar la web
def leer_web_globus():
    try:
        url = "https://elglobusvermell.org/"
        respuesta = requests.get(url)
        # Extraemos solo el texto limpio sin código HTML feo
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        texto_limpio = soup.get_text(separator=' ', strip=True)
        # Le pasamos los primeros 5000 caracteres para no saturar a la IA
        return texto_limpio[:5000] 
    except Exception as e:
        return "No pude leer la página web."

# --- ¡TU TEMA ESPECÍFICO! ---
TEMA_PROYECTO = "arquitectura, edificaciones y los proyectos de Globus Vermell"

# 4. Las Reglas de Titanio Súper Blindadas 
instrucciones = f"""
Eres un asistente experto en {TEMA_PROYECTO}.
Regla 1: TU ÚNICA FUENTE DE VERDAD ES LA BASE DE DATOS Y EL TEXTO DE LA WEB OFICIAL QUE TE PASO. 
Regla 2: Si el edificio o proyecto NO está en los datos de contexto ni en el texto de la web, ESTÁ ESTRICTAMENTE PROHIBIDO inventar o deducir información.
Regla 3: Si te preguntan algo que no está en los textos, responde: "Lo siento mucho, pero no tengo información sobre ese edificio en mis registros de Globus Vermell."
Regla 4: NUNCA menciones que estás leyendo una base de datos o haciendo scraping de una web.
Regla 5: Termina SIEMPRE tu respuesta con una pregunta breve y relacionada para continuar la conversación.
"""

modelo = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=instrucciones
)

# 5. Realizamos la interfaz gráfica 
st.title("IA de Globus Vermell")
st.write("¡Holiwis! Pregúntame sobre nuestros trípticos y edificios.")

# --- 6. MEMORIA DE LA SESIÓN ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])

# 7. La cajita de chat interactiva 
pregunta_usuario = st.chat_input("Escribe aquí tu preguntita...")

if pregunta_usuario:
    st.session_state.mensajes.append({"role": "user", "content": pregunta_usuario})
    with st.chat_message("user"):
        st.write(pregunta_usuario)

    with st.chat_message("assistant"):
        with st.spinner('Consultando archivos y la web oficial...'):
            
            # Sacamos los datos de Supabase
            try:
                # Acuérdate de poner el nombre de tu tabla 
                respuesta_db = supabase.table("mi_tabla").select("*").execute()
                datos_db = respuesta_db.data if respuesta_db.data else "BASE DE DATOS VACÍA"
            except Exception as e:
                datos_db = f"ERROR DE CONEXIÓN DB"

            # Sacamos los datos de la web oficial
            datos_web = leer_web_globus()

            with st.expander("Haz clic aquí para ver qué lee la IA (Rayos X) 🕵️‍♀️"):
                st.write("--- DATOS SUPABASE ---")
                st.write(datos_db)
                st.write("--- DATOS WEB ---")
                st.write(datos_web)

            historial = ""
            for msg in st.session_state.mensajes[-5:-1]: 
                historial += f"{msg['role']}: {msg['content']}\n"

            # 8. Empaquetamos BASE DE DATOS + WEB + HISTORIAL
            prompt_final = f"""
            Información de la base de datos interna:
            {datos_db}
            
            Información extraída de la web oficial elglobusvermell.org:
            {datos_web}
            
            Historial reciente de nuestra conversación:
            {historial}
            
            Pregunta actual del usuario: {pregunta_usuario}
            """
            
            respuesta = modelo.generate_content(prompt_final)
            texto_respuesta = respuesta.text
            
            st.write(texto_respuesta)
            st.session_state.mensajes.append({"role": "assistant", "content": texto_respuesta})