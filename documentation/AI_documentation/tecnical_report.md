# Informe Técnico Final: Prueba de Concepto (PoC) - IA Globus Vermell

## 1. Introducción y Objetivo
El presente documento detalla los resultados de la Prueba de Concepto (PoC) desarrollada para el proyecto "Globus Vermell". El objetivo principal de esta PoC fue evaluar la viabilidad técnica de integrar un asistente virtual (chatbot) impulsado por Inteligencia Artificial generativa, capaz de responder preguntas específicas sobre arquitectura, edificaciones y los trípticos de la organización, utilizando un contexto cerrado basado en bases de datos propias y la web oficial.

## 2. Arquitectura de la Prueba de Concepto (PoC)
Para la fase de pruebas, se implementó una arquitectura ágil y modular compuesta por las siguientes tecnologías:
* **Frontend / Interfaz de Usuario:** `Streamlit` (Framework de Python para despliegue rápido de aplicaciones de datos).
* **Base de Datos / Backend:** `Supabase` (PostgreSQL), utilizada para almacenar el catálogo de edificios (`buildings`).
* **Motor de Inteligencia Artificial:** `Google Generative AI (Gemini API)`, encargado del Procesamiento de Lenguaje Natural (NLP) y la generación de respuestas.
* **Extracción de Datos (Scraping):** `BeautifulSoup` y `Requests` para la lectura en tiempo real del contenido de la web oficial.

## 3. Obstáculos Encontrados y Soluciones Aplicadas
Durante el desarrollo de la PoC, se identificaron y superaron diversas barreras técnicas críticas:

1.  **Bloqueos de Seguridad en Base de Datos (RLS):** * *Problema:* La IA no podía acceder a los datos de la tabla, devolviendo arreglos vacíos (`[]`).
    * *Solución:* Se identificó que las políticas de seguridad a nivel de fila (Row Level Security - RLS) de Supabase estaban bloqueando la lectura externa. Se desactivaron temporalmente para la PoC y se validó el acceso a los 49 registros.
2.  **Límites de Cuota de la API (Error 429 - Resource Exhausted):** * *Problema:* El uso del modelo `gemini-2.5-flash` en el Free Tier provocó el agotamiento rápido de la cuota permitida (límite de peticiones por minuto).
    * *Solución:* Transición a modelos con límites más permisivos para desarrollo.
3.  **Conflictos de Dependencias y Modelos Obsoletos (Error 404 - Not Found):**
    * *Problema:* Discrepancias entre las versiones de la librería local de Python y los modelos en la nube provocaron que el sistema no reconociera modelos heredados como `gemini-pro`.
    * *Solución:* Forzar la actualización del entorno virtual (`python3 -m pip install --upgrade google-generativeai`).
4.  **Desbordamiento de Tokens (Input Token Count):**
    * *Problema:* Al inyectar la base de datos completa y el texto íntegro de la web en el prompt, se superó el límite de tokens de entrada del modelo gratuito.
    * *Solución:* Implementación del modelo optimizado **`gemini-2.0-flash-lite`** (diseñado para alta eficiencia) y truncamiento preventivo del texto extraído de la web (limitado a 1500 caracteres).

## 4. Viabilidad del Proyecto
Tras la resolución de los incidentes mencionados, **se determina que el proyecto es viable**. 
La PoC demostró con éxito que es posible:
* Conectar una interfaz interactiva a una base de datos remota.
* Inyectar contexto dinámico (Base de Datos + Web).
* Restringir las respuestas de la IA mediante "System Instructions" (Prompt Engineering) para evitar alucinaciones y garantizar que la información provenga exclusivamente de las fuentes de Globus Vermell.

## 5. Arquitectura Recomendada para Implementación Real
Para llevar este proyecto a un entorno de producción estable y escalable, se recomienda la siguiente evolución arquitectónica:

1.  **Transición de Web Scraping en vivo a Arquitectura RAG:** * En lugar de realizar scraping de la web en tiempo real con cada mensaje (lo cual genera latencia y consume tokens excesivos), se debe implementar un rastreador (Crawler) asíncrono que guarde y vectorice el texto de la web en Supabase de forma periódica.
2.  **Gestión de Cuotas y Facturación:** * Migrar de la API de prueba (Free Tier) a un plan *Pay-as-you-go* en Google AI Studio o Vertex AI para eliminar las restricciones de tokens de entrada (`input_token_count`) y soportar múltiples usuarios simultáneos.
3.  **Seguridad en Base de Datos:** * Reactivar las políticas RLS en Supabase, configurando claves de servicio (Service Roles) específicas para el backend, garantizando así la seguridad de los datos.