import streamlit as st
import requests

# Retrieve the Together API key from Streamlit secrets
API_KEY = st.secrets["together_api_key"]

# Together API endpoint
API_URL = "https://api.together.xyz/v1/chat/completions"

def correct_paragraph(paragraph):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Define the system prompt to instruct the assistant
    system_prompt = (
        "Eres un asistente útil que corrige errores de ortografía y estilo en un texto, "
        "sin cambiar las citas textuales (el texto entre comillas) y preservando las notas a pie de página "
        "(indicadas como números entre corchetes, por ejemplo, [1]). "
        "Mantén las notas a pie de página en los mismos lugares del texto, incluso si las oraciones cambian."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Aquí está el párrafo:\n\n{paragraph}"}
    ]

    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": messages,
        "max_tokens": 2512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": False
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        # Extract the assistant's reply
        corrected_paragraph = result['choices'][0]['message']['content']
        return corrected_paragraph.strip()
    else:
        st.error(f"Error: {response.status_code} {response.text}")
        return None

# Streamlit app interface
st.title("Aplicación de Corrección de Textos")

st.write("Ingrese el texto que desea corregir:")

input_text = st.text_area("Texto de entrada", height=300)

if st.button("Corregir Texto"):
    if input_text:
        paragraphs = [p.strip() for p in input_text.split('\n\n') if p.strip()]
        corrected_paragraphs = []

        progress_bar = st.progress(0)
        total = len(paragraphs)

        for i, paragraph in enumerate(paragraphs):
            corrected_paragraph = correct_paragraph(paragraph)
            if corrected_paragraph:
                corrected_paragraphs.append(corrected_paragraph)
            else:
                corrected_paragraphs.append(paragraph)  # Keep the original if there's an error
            progress_bar.progress((i + 1) / total)

        progress_bar.empty()

        corrected_text = '\n\n'.join(corrected_paragraphs)

        st.write("Texto Corregido:")
        st.write(corrected_text)
    else:
        st.error("Por favor, ingrese algún texto para corregir.")
