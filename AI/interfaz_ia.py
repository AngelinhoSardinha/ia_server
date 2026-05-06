import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Cargamos la llave mágica escondidita 
load_dotenv()
mi_llave_secreta = os.getenv("MI_KEY")
genai.configure(api_key=mi_llave_secreta)

# 2. Configuramos la IA Flash que elegimos
instrucciones = "Eres un asistente experto en programación súper amable."
modelo = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=instrucciones
)

# 3. Diseñamos la Interfaz Gráfica (GUI)
st.title(" Mi IA (actualmente DEMO Sprint 5)")
st.write("¡Holi! Soy tu asistente de programación. ¿Qué necesitas hoy?")

# 4. Creamos la cajita de chat abajo del todo
pregunta = st.chat_input("Escribe tu preguntita aquí...")

# 5. ¿Qué pasa cuando escribes algo y le das Enter?
if pregunta:
    # Mostramos tu mensaje en la pantalla con un iconito de usuario
    with st.chat_message("user"):
        st.write(pregunta)

    # Mostramos el mensaje de la IA con un iconito de robotito
    with st.chat_message("assistant"):
        # Mostramos un mensajito de "pensando" mientras la IA busca la respuesta
        with st.spinner('Pensando la respuesta... '):
            respuesta = modelo.generate_content(pregunta)
            st.write(respuesta.text)