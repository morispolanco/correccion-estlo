import streamlit as st
import requests
import json
from textwrap import dedent

# Configuración de la página
st.set_page_config(
    page_title="Análisis Literario con Together API",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación 
st.title("🔍 Análisis Literario y Recomendaciones de Estilo")

# Instrucciones
st.markdown("""
Bienvenido a la herramienta de análisis literario. Por favor, completa los campos a continuación para obtener una crítica literaria detallada y recomendaciones de estilo.
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
    submit_button = st.form_submit_button(label='Analizar')

# Función para contar palabras
def count_words(text):
    return len(text.split())

# Función para llamar a la API de Together
def call_together_api(api_key, genre, audience, text):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Construcción de los mensajes para la API con instrucciones claras
    messages = [
        {
            "role": "system",
            "content": dedent("""
                Eres un crítico literario experto que proporciona análisis detallados y recomendaciones de estilo basadas en el género y la audiencia especificados.
                **No debes repetir el análisis anterior ni corregir el texto proporcionado.**
            """)
        },
        {
            "role": "user",
            "content": dedent(f"""
                Por favor, analiza el siguiente texto y proporciona una crítica literaria junto con recomendaciones de estilo.

                **Instrucciones adicionales:**
                - No repitas el análisis previamente proporcionado.
                - No corrijas ni modifiques el texto original.
                - Enfócate únicamente en proporcionar observaciones, críticas y sugerencias de mejora.

                **Género:** {genre}
                **Audiencia:** {audience}

                **Texto:**
                {text}
            """)
        }
    ]

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": messages,
        "max_tokens": 2000,  # Ajusta según tus necesidades y límites de la API
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": False  # Para simplificar, se usa stream=False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Esto lanzará una excepción si hay un error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al comunicarse con la API: {e}")
        return None

# Acción al enviar el formulario
if submit_button:
    # Validación de entrada
    if not text_input.strip():
        st.error("Por favor, pega tu texto para analizar.")
    elif not audience.strip():
        st.error("Por favor, define la audiencia.")
    else:
        word_count = count_words(text_input)
        if word_count > 2000:
            st.error(f"El texto excede el límite de 2000 palabras. Actualmente tiene {word_count} palabras.")
        else:
            # Mostrar spinner mientras se procesa la solicitud
            with st.spinner("Analizando tu texto..."):
                # Obtener la API Key desde los secretos
                try:
                    api_key = st.secrets["TOGETHER_API_KEY"]
                except KeyError:
                    st.error("La clave de la API no está configurada correctamente en los secrets.")
                    st.stop()

                # Llamar a la API
                api_response = call_together_api(api_key, genre, audience, text_input)

                if api_response:
                    # Extraer la respuesta del modelo
                    try:
                        analysis = api_response['choices'][0]['message']['content']
                        st.subheader("📄 Análisis Literario")
                        st.write(analysis)
                    except (KeyError, IndexError):
                        st.error("Respuesta inesperada de la API.")

