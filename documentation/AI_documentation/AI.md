# Documentación Técnica de la Inteligencia Artificial Seleccionada

## 1. Selección del Modelo de IA
Para la implementación de la Prueba de Concepto (PoC) en el Sprint 4, se ha seleccionado la API de Google AI Studio, utilizando específicamente el modelo **Gemini Flash**. La decisión se fundamenta en la eficiencia de recursos: al consumir el modelo mediante una API, todo el procesamiento intensivo se delega a la infraestructura en la nube, eliminando la necesidad de contar con almacenamiento local para modelos de lenguaje de gran tamaño (LLMs) y optimizando el rendimiento del entorno de desarrollo.

## 2. Arquitectura e Integración de Seguridad
El desarrollo de la integración se está realizando en Python. Para garantizar la seguridad de las credenciales y cumplir con las mejores prácticas de desarrollo, se implementó el siguiente esquema:
* Creación de un archivo `.env` para almacenar la API Key de forma local y segura.
* Uso de la librería `python-dotenv` en el script principal para cargar las variables de entorno, evitando exponer las credenciales directamente en el código fuente (`.py`) o en futuros repositorios de control de versiones.

## 3. Resolución de Cuotas y Justificación (Flash vs. Pro)
Durante las pruebas de viabilidad iniciales, se evaluó la versión Gemini Pro. Sin embargo, las políticas de cuota para entornos de desarrollo sin facturación configurada generaron excepciones de tipo HTTP 429 (`ResourceExhausted`). Para asegurar la fluidez del desarrollo y evitar bloqueos por límites de peticiones (*rate limits*), se migró la integración a la versión **Gemini Flash**. Este modelo ofrece una latencia mínima, capacidades de razonamiento adecuadas para el proyecto y una cuota de uso lo suficientemente amplia para completar la fase de pruebas sin interrupciones.

## 4. Configuración del Comportamiento (System Instructions)
Para garantizar que las respuestas de la IA sean precisas y estén orientadas al contexto del proyecto, se ha implementado el uso del parámetro `system_instruction` en la instanciación del modelo. Esto permite asignar un rol predefinido y directrices específicas desde el backend. Adicionalmente, se implementará un bucle de ejecución continua que permite al usuario interactuar mediante consola en tiempo real, facilitando la validación de múltiples *prompts*. Conjuntamente se plantea desarrollar una interficie gráfica para un manejo más cómodo de la IA.