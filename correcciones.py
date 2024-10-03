import streamlit as st
import requests
import json  
from textwrap import dedent

# Configuración de la página
st.set_page_config(
    page_title="Análisis Literario y Corrección de Estilo",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("🔍 Análisis Literario y Corrección de Estilo")

# Instrucciones
st.markdown("""
Bienvenido a la herramienta de análisis literario y corrección de estilo. Por favor, completa los campos a continuación para obtener una crítica literaria detallada, recomendaciones de estilo específicas y una versión corregida de tu texto con justificaciones de los cambios realizados.
""")

# Formulario de entrada
with st.form(key='literary_analysis_form'):
    # Área de texto para el contenido
    text_input = st.text_area(
        "Pega tu texto (máximo 2000 palabras):",
        height=300,
        help="Asegúrate de que tu texto no exceda las 2000 palabras."
    )

    # Selección de género
    genre = st.selectbox(
        "Selecciona el género:",
        options=[
            "Fantasía", "Ciencia Ficción", "Misterio", "Romance",
            "Terror", "Aventura", "Drama", "Histórico", "Otro"
        ]
    )

    # Entrada de audiencia
    audience = st.text_input(
        "Define la audiencia:",
        help="Por ejemplo: adolescentes, adultos jóvenes, adultos, etc."
    )

    # Botón de envío
    submit_button = st.form_submit_button(label='Analizar y Corregir')

# Función para contar palabras
def count_words(text):
    return len(text.split())

# Función para llamar a la API de Together para Análisis Literario
def call_together_api_analysis(api_key, genre, audience, text):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Construcción de los mensajes para la API con instrucciones claras y específicas
    messages = [
        {
            "role": "system",
            "content": dedent("""
                Eres un crítico literario experto que proporciona análisis detallados y recomendaciones de estilo basadas en el género y la audiencia especificados.
                **No debes corregir, modificar ni repetir el texto proporcionado.**
                Tu única tarea es analizar el texto y ofrecer sugerencias de mejora enfocadas en aspectos literarios específicos como temas, desarrollo de personajes, estructura narrativa, tono y estilo.
            """)
        },
        {
            "role": "user",
            "content": dedent(f"""
                Por favor, analiza el siguiente texto y proporciona una crítica literaria junto con recomendaciones de estilo específicas.

                **Instrucciones adicionales:**
                - No repitas el análisis previamente proporcionado.
                - No corrijas ni modifiques el texto original de ninguna manera.
                - Enfócate únicamente en proporcionar observaciones, críticas constructivas y sugerencias de mejora relacionadas directamente con el contenido del texto.
                - Preserva todos los hipervínculos existentes en el texto. No agregues nuevos hipervínculos a menos que sean necesarios.
                - No alteres las URLs de los hipervínculos existentes.
                - Organiza el análisis en secciones claras como **Temas**, **Desarrollo de Personajes**, **Estructura Narrativa**, **Estilo y Tono**, etc.

                **Género:** {genre}
                **Audiencia:** {audience}

                **Texto:**
                {text}
            """)
        }
    ]

    payload = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "messages": messages,
        "max_tokens": 2000,  # Ajusta según tus necesidades y límites de la API
        "temperature": 0.5,  # Reducida para respuestas más enfocadas
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": False  # Mantener como False para simplificar
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Esto lanzará una excepción si hay un error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al comunicarse con la API de Análisis: {e}")
        return None

# Función para llamar a la API de Together para Corrección de Estilo y Ortografía con Justificaciones Inline
def call_together_api_style_correction_with_justifications(api_key, analysis, text):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Construcción de los mensajes para la API con instrucciones claras y específicas
    messages = [
        {
            "role": "system",
            "content": dedent("""
                Eres un editor experto en corrección de estilo, ortografía, gramática y puntuación que revisa textos literarios.
                **No debes realizar cambios que alteren el contenido original del autor.**
                Tu tarea es corregir el estilo, ortografía, gramática y puntuación del texto proporcionado basado en el análisis y las recomendaciones previas.
                **Preserva todos los hipervínculos existentes en el texto. No agregues nuevos hipervínculos a menos que sean necesarios. No alteres las URLs de los hipervínculos existentes.**
                **Después de cada cambio realizado, añade una justificación entre corchetes y en color rojo.**
            """)
        },
        {
            "role": "user",
            "content": dedent(f"""
                Basado en el siguiente análisis y recomendaciones, realiza una corrección de estilo del texto proporcionado. Incluye también correcciones ortográficas, gramaticales y de puntuación. Después de cada cambio realizado, añade una justificación entre corchetes y en color rojo.

                **Análisis y Recomendaciones:**
                {analysis}

                **Texto Original:**
                {text}

                **Instrucciones adicionales:**
                - No corrijas ni modifiques el contenido del texto.
                - Enfócate únicamente en mejorar la claridad, el flujo, el estilo, la ortografía, la gramática y la puntuación.
                - Preserva todos los hipervínculos existentes en el texto. No agregues nuevos hipervínculos a menos que sean necesarios.
                - No alteres las URLs de los hipervínculos existentes.
                - Para cada cambio realizado, proporciona una justificación detallada entre corchetes y estilizada en color rojo.
                - Presenta el texto corregido con las justificaciones inline.
            """)
        }
    ]

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": messages,
        "max_tokens": 3000,  # Aumentado para acomodar justificaciones
        "temperature": 0.5,  # Reducida para respuestas más enfocadas
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": False  # Mantener como False para simplificar
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al comunicarse con la API de Corrección de Estilo: {e}")
        return None

# Acción al enviar el formulario
if submit_button:
    # Validación de entrada
    if not text_input.strip():
        st.error("Por favor, pega tu texto para analizar y corregir.")
    elif not audience.strip():
        st.error("Por favor, define la audiencia.")
    else:
        word_count = count_words(text_input)
        if word_count > 2000:
            st.error(f"El texto excede el límite de 2000 palabras. Actualmente tiene {word_count} palabras.")
        else:
            # Mostrar spinner mientras se procesa la solicitud
            with st.spinner("Procesando tu solicitud..."):
                # Obtener la API Key desde los secretos
                try:
                    api_key = st.secrets["TOGETHER_API_KEY"]
                except KeyError:
                    st.error("La clave de la API no está configurada correctamente en los secrets.")
                    st.stop()

                # Primera llamada a la API para Análisis Literario
                api_response_analysis = call_together_api_analysis(api_key, genre, audience, text_input)

                if api_response_analysis:
                    # Extraer la respuesta del modelo para el análisis
                    try:
                        analysis = api_response_analysis['choices'][0]['message']['content']
                        st.subheader("📄 Análisis Literario")
                        st.write(analysis)
                    except (KeyError, IndexError):
                        st.error("Respuesta inesperada de la API de Análisis.")
                        analysis = None

                # Segunda llamada a la API para Corrección de Estilo y Ortografía con Justificaciones Inline, si el análisis fue exitoso
                if analysis:
                    api_response_correction = call_together_api_style_correction_with_justifications(api_key, analysis, text_input)

                    if api_response_correction:
                        # Extraer la respuesta del modelo para la corrección de estilo con justificaciones
                        try:
                            correction = api_response_correction['choices'][0]['message']['content']
                            st.subheader("✍️ Corrección de Estilo, Ortográfica, Gramatical y de Puntuación con Justificaciones")
                            # Renderizar el texto corregido con justificaciones en rojo
                            st.markdown(correction, unsafe_allow_html=True)
                        except (KeyError, IndexError):
                            st.error("Respuesta inesperada de la API de Corrección de Estilo.")
