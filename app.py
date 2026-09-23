"""
AutoTech JPB Solutions - Interfaz Conversacional Streamlit (5 Manuales & Inventario Inteligente)
================================================================================================
Aplicación Web de Chatbot Inteligente con RAG y Agente de Inventario
Asignatura: ISY0101 - Duoc UC
"""

import os
import streamlit as st
from rag_engine import (
    AutoTechVectorStore,
    AutoTechAgent,
    INVENTARIO_BODEGA
)

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y REMOCIÓN COMPLETA DEL SIDEBAR
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AutoTech JPB Solutions",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS Animados, Cyber-Glow y Colores Vibrantes
st.markdown("""
<style>
    /* Ocultar Sidebar completamente */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Animación de fondo Aurora Neón en movimiento continuo */
    @keyframes auroraBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    html, body, .stApp, [data-testid="stHeader"], [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #090d16, #111827, #1e1b4b, #0f172a) !important;
        background-size: 400% 400% !important;
        animation: auroraBG 16s ease infinite !important;
        color: #f8fafc !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Contenedor Principal */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1000px !important;
    }

    /* Titulo Animado con Brillo Neón */
    @keyframes glowingTitle {
        0%, 100% { filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.4)); }
        50% { filter: drop-shadow(0 0 30px rgba(129, 140, 248, 0.8)); }
    }
    
    .main-title {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc, #38bdf8);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.7rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        margin-bottom: 1.5rem;
        text-align: left;
        animation: glowingTitle 5s ease-in-out infinite alternate;
    }

    /* Badges de Herramienta Ejecutada */
    .badge-tool {
        background: linear-gradient(90deg, #0284c7 0%, #3b82f6 100%);
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 8px;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }

    /* Citas de RAG en HTML Details (Sin salto de página/rebote y con renderizado limpio) */
    .rag-details {
        margin-top: 12px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px;
        padding: 10px 14px;
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .rag-details:hover {
        border-color: #38bdf8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .rag-details summary {
        cursor: pointer;
        font-weight: 600;
        font-size: 0.88rem;
        color: #38bdf8;
        outline: none;
    }
    .source-card-single {
        border-left: 4px solid #38bdf8;
        padding: 10px 14px;
        margin: 10px 0 4px 0;
        font-size: 0.88rem;
        background: rgba(56, 189, 248, 0.1);
        border-radius: 0 8px 8px 0;
        color: #f1f5f9;
        line-height: 1.5;
    }

    /* Mensajes de Chat Animados con Glassmorphism */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    [data-testid="stChatMessage"] {
        animation: fadeInUp 0.35s ease-out forwards;
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 14px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
        margin-bottom: 14px !important;
        color: #f8fafc !important;
    }

    /* Input de Chat Estilizado */
    .stChatInputContainer, [data-testid="stChatInput"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }
    
    .stChatInput input, textarea {
        color: #f8fafc !important;
        background-color: transparent !important;
    }

    /* Botones de sugerencias rápidas interactivos con elevación y sombras */
    .stButton>button {
        width: 100% !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.4) !important;
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. CARGA AUTOMÁTICA DE MANUALES RAG (@st.cache_resource)
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Inicializando base de conocimiento...")
def load_rag_knowledge_base():
    pdf_files = [
        "ficha_tecnica_fiat_palio.pdf",
        "MANUAL-DE-OPERACIONES-DE-TALLER-.pdf",
        "manual_fallas_multimarca_diagnostico.pdf",
        "manual_recepcion_fallas_cliente_taller.pdf",
        "mecanica-automotriz-mantenimiento-de-motores.pdf"
    ]
    vs = AutoTechVectorStore()
    loaded_pdfs = vs.build_or_load_index(pdf_files)
    return vs, len(vs.chunks), loaded_pdfs


vector_store, total_chunks, loaded_pdfs = load_rag_knowledge_base()


# -----------------------------------------------------------------------------
# 3. ENCABEZADO Y CONSULTAS FRECUENTES
# -----------------------------------------------------------------------------
st.markdown('<h1 class="main-title">AutoTech JPB Solutions</h1>', unsafe_allow_html=True)

st.markdown("##### Consultas Frecuentes de Prueba:")
col1, col2, col3 = st.columns(3)

prompt_to_submit = None

with col1:
    if st.button("¿Qué repuestos tenemos en stock?", use_container_width=True):
        prompt_to_submit = "¿Qué repuestos tenemos en stock en la bodega de AutoTech?"

with col2:
    if st.button("Cambio Plumillas y Rangos PSI Ruedas", use_container_width=True):
        prompt_to_submit = "Un cliente viene porque sus limpiaparabrisas rayan el cristal y quiere saber la presión adecuada para las ruedas de su SUV. ¿Qué procedimiento sigo y qué PSI se recomienda?"

with col3:
    if st.button("Diagnóstico Alza Vidrios Changan", use_container_width=True):
        prompt_to_submit = "El cliente trae una Changan CX70 y no le baja el alza vidrios de la puerta del copiloto, ¿qué debo diagnosticar paso a paso y tenemos el motor o botonera en stock?"


# -----------------------------------------------------------------------------
# 4. RENDERIZADO LIMPIO DE FUENTE PRINCIPAL RAG (SOLO LA FUENTE MAS RELEVANTE)
# -----------------------------------------------------------------------------
def render_sources_html(sources):
    if not sources:
        return ""
    
    # Tomar únicamente la fuente más relevante para evitar mostrar bloques sobrantes
    top_src = sources[0]
    doc = str(top_src.get('doc', '')).replace('<', '&lt;').replace('>', '&gt;')
    page = top_src.get('page', '')
    score = top_src.get('score', 0)
    text = str(top_src.get('text', '')).replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    card_html = f'<div class="source-card-single"><b>Documento:</b> {doc} (Página {page}) | <b>Relevancia:</b> {score:.2f}<br><i style="color:#cbd5e1;">&quot;{text}&quot;</i></div>'
    
    return f'<details class="rag-details"><summary>Citas y Trazabilidad de Fuentes (RAG)</summary>{card_html}</details>'


# -----------------------------------------------------------------------------
# 5. CHAT Y PROCESAMIENTO CONVERSACIONAL CON AVATARES NATIVOS
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Avatares nativos
AVATAR_USER = "👤"
AVATAR_BOT = "🤖"

for msg in st.session_state.messages:
    avatar_src = AVATAR_USER if msg["role"] == "user" else AVATAR_BOT
    with st.chat_message(msg["role"], avatar=avatar_src):
        if "tool_executed" in msg and msg["tool_executed"]:
            st.markdown(f'<div class="badge-tool">Herramienta: {msg["tool_executed"]}</div>', unsafe_allow_html=True)
        st.markdown(msg["content"])
        
        if "sources" in msg and msg["sources"]:
            st.markdown(render_sources_html(msg["sources"]), unsafe_allow_html=True)

user_input = st.chat_input("Escribe tu pregunta sobre atención de clientes, fallas de taller, stock o procedimientos...")

if prompt_to_submit:
    user_input = prompt_to_submit

if user_input:
    api_key_env = os.environ.get("LLM_API_KEY", "")
    if not api_key_env:
        st.error("La clave 'LLM_API_KEY' no está configurada en las variables de entorno.")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(user_input)
        
    with st.chat_message("assistant", avatar=AVATAR_BOT):
        with st.spinner("Consultando manuales del taller y verificando bodega..."):
            agent = AutoTechAgent(
                api_key=api_key_env,
                vector_store=vector_store,
                model_name="openai/gpt-oss-20b"
            )
            
            response_data = agent.run(user_input, chat_history=st.session_state.messages)
            
            tool_name = None
            if response_data["tool_calls"]:
                tool_name = response_data["tool_calls"][0]["tool"]
                st.markdown(f'<div class="badge-tool">Herramienta ejecutada: {tool_name}</div>', unsafe_allow_html=True)
                
            st.markdown(response_data["answer"])
            
            if response_data["sources"]:
                st.markdown(render_sources_html(response_data["sources"]), unsafe_allow_html=True)
                        
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data["answer"],
                "sources": response_data["sources"],
                "tool_executed": tool_name
            })
