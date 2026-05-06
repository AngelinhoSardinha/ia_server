# Informe Técnico: Actualización del Motor de IA (Sprint 7)

**Proyecto:** Asistente Virtual "Globus Vermell"
**Foco del Sprint:** Estabilidad, precisión y cambio de motor NLP.

## 1. El Problema: ¿Por qué nos despedimos de Gemini?
Durante la integración de nuestra base de datos con el chat, la API de Google Gemini nos empezó a poner demasiadas barreras que bloqueaban el desarrollo. Nos enfrentamos a dos "jefes finales" bastante molestos:

* **Inestabilidad de modelos (Error 404):** Google actualiza sus servidores constantemente y retiró versiones antiguas (como `gemini-pro`) sin avisar, lo que rompía nuestro código de un día para otro.
* **El muro de la cuota (Error 429):** Para que la IA no alucine ni invente información, le inyectamos todo el contexto de nuestros edificios (`buildings`) y el texto de la web oficial. Gemini, en su versión gratuita, tiene un límite muy estricto de "tokens de entrada". Básicamente, se atragantaba con tanta información de golpe y nos bloqueaba la cuenta.

## 2. La Solución: Cohere
Necesitábamos una IA que fuera una experta leyendo bases de datos sin quejarse ni inventarse cosas. Tras analizar opciones, migramos el "cerebro" del proyecto a **Cohere**, utilizando exactamente su modelo optimizado `command-r7b-12-2024`.

**¿Por qué Cohere es nuestra mejor opción?**
1. **Es el Rey del RAG:** A diferencia de Gemini o ChatGPT (que son más creativos), los modelos "Command R" de Cohere están diseñados *específicamente* para hacer RAG (Retrieval-Augmented Generation). Son expertos en leer documentos y bases de datos para dar respuestas 100% basadas en el texto que les pasamos.
2. **Eficiencia y rapidez:** Este modelo específico (`r7b`) es pequeño, súper rápido y maneja muchísimo mejor las ventanas de contexto grandes sin que nos salte el error de cuota excedida.
3. **Cero pérdida de trabajo:** La migración fue súper limpia. Su librería de Python encajó a la perfección con nuestro backend en Supabase y nuestro frontend en Streamlit.