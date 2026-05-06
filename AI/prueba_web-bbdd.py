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

# --- 3. EL ROBOTITO QUE LEE EL LINK EN VIVO ---
@st.cache_data(ttl=3600) # Lo guarda 1 hora para que tu compu no explote de tanto buscar
def leer_web_oficial():
    try:
        url = "https://elglobusvermell.org/"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Sacamos el texto limpiecito sin código feo
        texto = soup.get_text(separator=' ', strip=True)
        return texto[:5000] # Leemos los primeros 5000 caracteres para no saturar a la IA
    except Exception as e:
        return f"No pude leer la web: {e}"

# --- ¡TU TEMA ESPECÍFICO! ---
TEMA_PROYECTO = "arquitectura, edificaciones y los proyectos de Globus Vermell"

# 4. Las Reglas de Titanio Súper Blindadas 
instrucciones = f"""
Eres un asistente experto en {TEMA_PROYECTO}.
Regla 1: TU ÚNICA FUENTE DE VERDAD ES LA BASE DE DATOS Y LA WEB OFICIAL. 
Regla 2: Si el edificio, proyecto o información NO está literalmente escrito en los datos de contexto que te paso, ESTÁ ESTRICTAMENTE PROHIBIDO inventar, deducir o usar conocimiento externo de internet.
Regla 3: Si te preguntan algo que no está en los datos, debes responder EXACTAMENTE esto: "Lo siento mucho, pero no tengo esa información en mis registros de Globus Vermell."
Regla 4: NUNCA menciones que estás leyendo una base de datos, haciendo scraping ni cómo funciona tu sistema.
Regla 5: Termina SIEMPRE tu respuesta con una pregunta breve y relacionada para continuar la conversación.
"""

# 5. Configuramos la IA
modelo = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=instrucciones
)

# 6. ¡Pintamos tu página web! 
st.title("IA de Globus Vermell")
st.write("¡Holiwis! Pregúntame sobre nuestros trípticos y edificios")

# --- 7. CREAMOS LA MEMORIA DE LA SESIÓN ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Dibujamos los mensajes antiguos para que no desaparezcan
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])

# 8. La cajita de chat interactiva 
pregunta_usuario = st.chat_input("Escribe aquí tu preguntita...")

# 9. ¿Qué pasa cuando le das a Enter?
if pregunta_usuario:
    # Guardamos tu pregunta en la memoria y la mostramos
    st.session_state.mensajes.append({"role": "user", "content": pregunta_usuario})
    with st.chat_message("user"):
        st.write(pregunta_usuario)

    # Mostramos la respuesta de la IA
    with st.chat_message("assistant"):
        with st.spinner('Consultando todos los archivos y la web...'):
            
            # --- SACAMOS LOS DATOS (Supabase + Link en vivo) ---
            
            # 1. Tu base de datos manual 
            try:
                respuesta_manual = supabase.table("buildings").select("*").execute()
                datos_manuales = respuesta_manual.data if respuesta_manual.data else []
            except Exception as e:
                datos_manuales = []
                
            # 2. La web oficial directamente del link 
            datos_web = leer_web_oficial()

            # Juntamos todo en un solo bloque de contexto
            datos_contexto = f"DATOS MANUALES (EDIFICIOS):\n{datos_manuales}\n\nTEXTO DE LA WEB OFICIAL:\n{datos_web}"

            # --- TRUQUITO DE RAYOS X ---
            with st.expander("Ver contexto enviado a la IA (Rayos X)"):
                st.write(f"Se cargaron {len(datos_manuales)} edificios de la base de datos.")
                st.write("Muestra de datos de la web que leyó el robot:")
                st.write(str(datos_web)[:1000] + "... (recortado visualmente para no saturar la pantalla)")

            # Preparamos el historial
            historial = ""
            for msg in st.session_state.mensajes[-5:-1]: 
                historial += f"{msg['role']}: {msg['content']}\n"

            # Empaquetamos todo para la IA
            prompt_final = f"""
            Información de mi sistema completo (Base de Datos + Web):
            {datos_contexto}
            
            Historial reciente de nuestra conversación:
            {historial}
            
            Pregunta actual del usuario: {pregunta_usuario}
            """
            
            # Generamos la respuesta final
            respuesta = modelo.generate_content(prompt_final)
            texto_respuesta = respuesta.text
            
            # La mostramos en pantalla
            st.write(texto_respuesta)
            
            # Guardamos la respuesta
            st.session_state.mensajes.append({"role": "assistant", "content": texto_respuesta})