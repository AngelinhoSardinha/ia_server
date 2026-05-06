import os
import google.generativeai as genai
from dotenv import load_dotenv

# Leer el archivo con la API KEY 
load_dotenv()

# Guardar el API Key en una variable 
mi_llave_secreta = os.getenv("MI_KEY") 

# Aquí va la llave de la API
genai.configure(api_key=mi_llave_secreta)

# Aquí personalizamos a la IA
instrucciones = "Eres un asistente experto en programación súper amable. Ayudas a resolver dudas de código explicando paso a paso."

# Elegimos el modelo y le damos las instrucciones
modelo = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=instrucciones
)

# ¡Hacemos la prueba!
print("Soy tu IA que te ayuda con cositas de programación UwU ¿Qué necesitas?\n")

mi_pregunta = input("\n")

print("Pensando la respuesta... (≧◡≦) \n")

respuesta = modelo.generate_content(mi_pregunta)

print("¡Aquí tienes, nya! ✨")
print(respuesta.text)