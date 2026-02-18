import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
from streamlit_audiorecorder import audiorecorder

# 1. Configuração da página
st.set_page_config(page_title="Viaja-AI Pro", page_icon="✈️")
st.title("✈️ Viaja-AI Pro")
st.caption("Agente de Viagens (Gemini 2.0 - Voz e Texto)")

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

# 4. Função Blindada (Aceita Texto OU Áudio)
def conectar_e_responder(entrada_usuario, tipo="texto"):
    try:
        client = genai.Client(api_key=API_KEY)
        google_search_tool = types.Tool(google_search=types.GoogleSearch())
        hoje = datetime.now().strftime("%d/%m/%Y")
        
        # Reconstrói histórico (apenas partes de texto para contexto)
        historico_gemini = []
        for msg in st.session_state.messages:
            if msg.get("tipo") == "texto": # Só mandamos texto antigo para não pesar
                role = "user" if msg["role"] == "user" else "model"
                historico_gemini.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
        
        # Configura o Chat
        chat = client.chats.create(
            model='gemini-2.0-flash',
            history=historico_gemini,
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                system_instruction=f"Hoje é {hoje}. Você é um agente de viagens. Se receber áudio, ouça com atenção e responda em texto."
            )
        )
        
        # Prepara a mensagem (Texto ou Áudio)
        mensagem_envio = []
        if tipo == "audio":
            # O Gemini ouve o áudio direto!
            mensagem_envio = [
                types.Part.from_bytes(data=entrada_usuario, mime_type="audio/wav"),
                "O usuário enviou este áudio. Responda à dúvida dele."
            ]
        else:
            mensagem_envio = entrada_usuario

        # Envia
        response = chat.send_message(mensagem_envio)
        return response.text
        
    except Exception as e:
        return f"⚠️ Erro técnico: {e}"

# --- INTERFACE DE ENTRADA ---

# 5. Coluna de Áudio (Microfone)
st.write("---")
col_audio, col_texto = st.columns([1, 4])

with col_audio:
    st.write("🎙️ **Falar:**")
    # O botão de gravar
    audio = audiorecorder("", "")

# Lógica do Áudio
if len(audio) > 0:
    # Só processa se for um áudio novo (evita repetição automática)
    if "ultimo_audio" not in st.session_state or st.session_state.ultimo_audio != audio:
        
        st.session_state.ultimo_audio = audio # Marca que já usou este áudio
        
        # Mostra "Áudio Enviado" na tela
        st.chat_message("user").markdown("🎤 *[Áudio enviado pelo usuário]*")
        st.session_state.messages.append({"role": "user", "content": "🎤 *[Áudio enviado]*", "tipo": "audio"})
        
        with st.chat_message("assistant"):
            with st.spinner("Ouvindo e pesquisando..."):
                # Envia os bytes do áudio direto pro Gemini
                resposta = conectar_e_responder(audio.export().read(), tipo="audio")
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta, "tipo": "texto"})

# 6. Lógica do Texto (Input normal)
if prompt := st.chat_input("Ou digite sua dúvida aqui..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt, "tipo": "texto"})
    
    with st.chat_message("assistant"):
        with st.spinner("Pesquisando..."):
            resposta = conectar_e_responder(prompt, tipo="texto")
            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta, "tipo": "texto"})
