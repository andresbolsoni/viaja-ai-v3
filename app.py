import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Viaja-AI Pro", page_icon="✈️")
st.title("✈️ Viaja-AI Pro")
st.caption("Agente de Viagens (Gemini 2.0)")

# 2. Carrega a Chave API
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("❌ Chave GEMINI_API_KEY não encontrada nos Secrets!")
    st.stop()

# 3. Histórico Visual
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Função de Resposta
def conectar_e_responder(prompt_usuario):
    try:
        client = genai.Client(api_key=API_KEY)
        google_search_tool = types.Tool(google_search=types.GoogleSearch())
        hoje = datetime.now().strftime("%d/%m/%Y")
        
        chat = client.chats.create(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                system_instruction=f"Hoje é {hoje}. Você é um agente de viagens."
            )
        )
        
        response = chat.send_message(prompt_usuario)
        return response.text
    except Exception as e:
        return f"⚠️ Erro: {e}"

# 5. Entrada de Texto
if prompt := st.chat_input("Para onde vamos viajar?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Pesquisando..."):
            resposta = conectar_e_responder(prompt)
            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})

# DICA PARA VOZ:
st.info("💡 Dica: No celular ou Windows/Mac, você pode usar o microfone do próprio teclado para ditar sua viagem!")
