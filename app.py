import streamlit as st
import requests
import re

# Configuración de la página
st.set_page_config(layout="wide")

# Obtener el secreto de la API de Together
TOGETHER_API_KEY = st.secrets.get("TOGETHER_API_KEY")

if not TOGETHER_API_KEY:
    st.error("La clave de la API de Together no está configurada. Por favor, verifica tus secretos.")
    st.stop()

# Función para contar palabras en el texto
def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

# Función para realizar análisis crítico literario usando la API de Together
def literary_critical_analysis(text, language):
    try:
        if not text.strip() or count_words(text) < 50:
            st.warning("Por favor, introduce un texto de al menos 50 palabras para el análisis.")
            return None

        together_url = "https://api.together.xyz/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""Realiza un análisis crítico literario del siguiente texto en {language}. Destaca sus méritos y defectos de manera detallada y constructiva:

        {text}"""

        data = {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.0,
            "stop": ["<|eot_id|>"],
            "stream": False
        }

        response = requests.post(together_url, json=data, headers=headers, timeout=60)

        if response.status_code == 200:
            response_data = response.json()
            analysis = response_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            if not analysis:
                st.error("La respuesta de la API no contiene el análisis esperado.")
                return None
            return analysis
        else:
            st.error(f"Error de la API de Together: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        st.error("La solicitud a la API de Together ha excedido el tiempo de espera.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error al realizar la solicitud a la API de Together: {e}")
        return None

# Función para realizar corrección de estilo usando la API de Together
def style_correction(text, language, analysis):
    try:
        if not text.strip() or count_words(text) < 50:
            st.warning("Por favor, introduce un texto de al menos 50 palabras para la corrección de estilo.")
            return None

        together_url = "https://api.together.xyz/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""Basándote en el siguiente análisis crítico, realiza una corrección de estilo del texto en {language}. Asegúrate de mejorar la fluidez, coherencia y claridad del texto, manteniendo el significado original:

        Análisis crítico:
        {analysis}

        Texto original:
        {text}

        Texto corregido:"""

        data = {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.0,
            "stop": ["<|eot_id|>"],
            "stream": False
        }

        response = requests.post(together_url, json=data, headers=headers, timeout=60)

        if response.status_code == 200:
            response_data = response.json()
            corrected_text = response_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            if not corrected_text:
                st.error("La respuesta de la API no contiene el texto corregido esperado.")
                return None
            return corrected_text
        else:
            st.error(f"Error de la API de Together: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        st.error("La solicitud a la API de Together ha excedido el tiempo de espera.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error al realizar la solicitud a la API de Together: {e}")
        return None

# Función principal de la aplicación
def main():
    st.sidebar.header("Instrucciones")
    st.sidebar.markdown("""
**Esta aplicación te permite:**

- Introducir un texto de hasta **2000 palabras**.
- Realizar un análisis crítico literario del texto, destacando sus méritos y defectos.
- Basado en el análisis, obtener una versión corregida del texto con mejoras en estilo y claridad.
- Recibir una explicación de las correcciones realizadas y las razones detrás de ellas.

**Idiomas soportados:**

La aplicación puede analizar y corregir textos en **inglés, español, francés, italiano, alemán y portugués**.

**Longitud del texto:**

- La aplicación está limitada a procesar hasta **2000 palabras**.
- Si el texto excede este límite, se solicitará al usuario reducir la cantidad de texto.

**Aviso legal:**

Es responsabilidad del autor verificar todos los cambios antes de utilizar el texto corregido para cualquier propósito oficial o público.

**Autor:** Dr. Moris Polanco (mp @ ufm.edu)
    """)

    st.title("Análisis Crítico y Corrección de Estilo de Textos Literarios")

    # Selección del idioma
    language_codes = ["es", "en", "fr", "it", "de", "pt"]
    language_names = {
        "es": "Español",
        "en": "Inglés",
        "fr": "Francés",
        "it": "Italiano",
        "de": "Alemán",
        "pt": "Portugués"
    }

    language = st.selectbox(
        "Selecciona el idioma del texto",
        language_codes,
        index=0,
        format_func=lambda x: language_names.get(x, x)
    )

    # Cuadro de texto para ingresar el texto a analizar
    st.subheader("Introduce tu texto aquí (máximo 2000 palabras):")
    text_input = st.text_area("", height=300, max_chars=20000)  # Aproximadamente 2000 palabras

    word_count = count_words(text_input)
    st.write(f"**Cantidad de palabras:** {word_count}/2000")

    if word_count > 2000:
        st.error("El texto excede el límite de 2000 palabras. Por favor, reduce la longitud del texto.")
    else:
        if st.button("Analizar y Corregir"):
            if word_count < 50:
                st.error("Por favor, introduce un texto de al menos 50 palabras para el análisis.")
            else:
                with st.spinner("Realizando análisis crítico..."):
                    analysis = literary_critical_analysis(text_input, language)
                
                if analysis:
                    st.subheader("Análisis Crítico Literario")
                    st.write(analysis)

                    with st.spinner("Realizando corrección de estilo..."):
                        corrected_text = style_correction(text_input, language, analysis)
                    
                    if corrected_text:
                        st.subheader("Texto Corregido")
                        st.write(corrected_text)

                        st.markdown("---")
                        st.subheader("Resumen de Cambios Realizados")
                        st.markdown("""
- **Análisis Crítico:** Se realizó un análisis detallado del texto, destacando sus **méritos** (puntos fuertes) y **defectos** (áreas de mejora) desde una perspectiva literaria.
- **Corrección de Estilo:** Basado en el análisis, se corrigió el estilo del texto para mejorar la **fluidez**, **coherencia** y **claridad**, manteniendo el significado original.
- **Justificación de Cambios:** Los cambios se realizaron para potenciar la calidad literaria del texto, asegurando que cumpla con estándares elevados de redacción y expresión.
                        """)

if __name__ == "__main__":
    main()
