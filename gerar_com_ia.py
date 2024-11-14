import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv



def app():
    def conectar_llm():
        client = OpenAI(
            base_url = "https://integrate.api.nvidia.com/v1",
            api_key = os.environ['NVIDIA_API_KEY']
        )
        return client

    def create_prompt_parts():
        with open("dados/contexto.txt", "r") as file:
            context = file.read()
        
        # Defina o limite de caracteres para cada parte (ajuste conforme necessário para não exceder os 4096 tokens)
        max_chars_per_part = 4000
        parts = [context[i:i + max_chars_per_part] for i in range(0, len(context), max_chars_per_part)]
        return [{"role": "user", "content": part} for part in parts]

    def answer(client, prompt_parts):
        full_response = ""
        for part in prompt_parts:
            completion = client.chat.completions.create(
                model=os.environ['NVIDIA_MODEL'],
                messages=[part],
                temperature=0.2,
                top_p=0.7,
                max_tokens=1024,
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
        return full_response

##########################################################################################################

    load_dotenv()

    client = conectar_llm()
    prompt_parts = create_prompt_parts()
    full_response = answer(client, prompt_parts)

    response = st.empty()
    response.markdown(full_response)

