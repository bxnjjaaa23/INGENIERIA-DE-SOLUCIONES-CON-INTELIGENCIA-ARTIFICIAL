"""
AutoTech JPB Solutions - Interfaz Web de Agente Funcional Streamlit (EP2)
========================================================================
Asignatura: ISY0101 - Ingeniería de Soluciones con IA (Duoc UC)
Integrantes: Paolo Jorquera, Benjamín Arriaza y José Castillo

Esta aplicación web implementa la visualización interactiva del agente con:
- Estética automotriz de alto rendimiento (Dark Garage, fibra de carbono, acentos neón y telemetría OBD-II).
- Animaciones fluidas en encabezados, botones, tarjetas de diagnóstico y métricas.
- Flujo secuencial: chat con entrada fija inferior y memoria conversacional multietapa.
- Protocolo de búsqueda web asistida con autorización explícita interactiva.
- Pensamiento y ciclo ReAct en tiempo real (Planificación -> Acción -> Observación) en estilo escáner técnico.
- Pestaña de Planificación Estratégica (Plan-and-Execute / IE5).
- Gestión y persistencia en tiempo real de Órdenes de Trabajo en JSON con KPIs de taller.
- Catálogo interactivo de inventario de bodega con alertas de stock crítico.
"""

import os
import sys
import json
import time
from datetime import datetime
import streamlit as st

# 1. Intentar leer clave directamente desde Google Colab Secrets (LLM_API_KEY)
try:
    from google.colab import userdata
    try:
        _val = userdata.get("LLM_API_KEY")
        if _val:
            os.environ["LLM_API_KEY"] = str(_val).strip()
    except Exception:
        pass
except Exception:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Configurar encoding UTF-8 en consola
if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from autotech_agent_ep2 import (
    create_autotech_agent,
    execute_agent_with_backoff,
    AutoTechSessionMemory,
    generar_plan_taller,
    generar_comunicacion_multiagente,
    extraer_pasos_plan,
    obtener_ordenes_registradas,
    eliminar_orden_trabajo,
    cambiar_estado_orden_trabajo,
    registrar_orden_reparacion,
    get_or_create_vector_store,
    get_current_chile_time,
    INVENTARIO_BODEGA,
    AUTOTECH_TOOLS,
    ORDENES_TRABAJO_FILE
)

# Definición de respaldo de la constante de persistencia para evitar cualquier NameError
if "ORDENES_TRABAJO_FILE" not in globals() or not ORDENES_TRABAJO_FILE:
    ORDENES_TRABAJO_FILE = "ordenes_trabajo_autotech.json"

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA (SIN PANEL LATERAL) Y ESTILOS AUTOMOTRICES
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AutoTech JPB Solutions",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS avanzados con temática de taller mecánico y ocultación total del panel lateral
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700;800&family=Rajdhani:wght@600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Ocultar completamente el panel lateral de Streamlit */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    :root {
        --carbon-dark: #070a12;
        --carbon-card: #0c1322;
        --metal-border: #1e293b;
        --turbo-gold: #f59e0b;
        --turbo-cyan: #06b6d4;
        --neon-blue: #38bdf8;
        --racing-red: #ef4444;
        --pitstop-green: #10b981;
        --jdm-purple: #8b5cf6;
    }

    /* Fondo principal con textura de fibra de carbono JDM */
    .stApp {
        background-color: #070a12;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(6, 182, 212, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(245, 158, 11, 0.07) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(239, 68, 68, 0.04) 0%, transparent 60%),
            linear-gradient(45deg, #070b13 25%, #090f1c 25%, #090f1c 50%, #070b13 50%, #070b13 75%, #090f1c 75%, #090f1c 100%);
        background-size: 100% 100%, 100% 100%, 100% 100%, 6px 6px;
    }

    /* Animaciones JDM */
    @keyframes neonGlow {
        0% { box-shadow: 0 0 14px rgba(245, 158, 11, 0.25), inset 0 0 10px rgba(245, 158, 11, 0.05); }
        50% { box-shadow: 0 0 28px rgba(245, 158, 11, 0.55), inset 0 0 18px rgba(245, 158, 11, 0.15); }
        100% { box-shadow: 0 0 14px rgba(245, 158, 11, 0.25), inset 0 0 10px rgba(245, 158, 11, 0.05); }
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Encabezado Principal Cockpit */
    .cockpit-header {
        background: linear-gradient(135deg, #070c17 0%, #0f192d 45%, #191c38 80%, #060a13 100%);
        background-size: 250% 250%;
        animation: gradientShift 12s ease infinite;
        padding: 1.8rem 2.2rem;
        border-radius: 18px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.65), 0 0 25px rgba(6, 182, 212, 0.2);
        position: relative;
        overflow: hidden;
    }

    /* Barra Superior JDM Redline */
    .cockpit-header::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #ef4444 0%, #f59e0b 35%, #06b6d4 70%, #10b981 100%);
        box-shadow: 0 0 12px rgba(6, 182, 212, 0.8);
    }

    .brand-title {
        font-family: 'Chakra Petch', sans-serif;
        color: #f8fafc;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 14px;
        text-shadow: 0 3px 15px rgba(0, 0, 0, 0.8);
    }

    .brand-title span.accent {
        color: #f59e0b;
        background: linear-gradient(90deg, #fcd34d 0%, #f59e0b 50%, #fb923c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.4));
    }

    .brand-sub {
        font-family: 'Chakra Petch', sans-serif;
        color: #38bdf8;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        margin-top: 0.5rem;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 8px;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }

    /* Estilos de Métricas / KPIs */
    [data-testid="stMetric"] {
        background: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-left: 4px solid #06b6d4 !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 18px rgba(6, 182, 212, 0.25) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.3px !important;
        color: #94a3b8 !important;
        text-transform: uppercase !important;
    }

    [data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.35rem !important;
        color: #f8fafc !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    /* Pestañas JDM (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: rgba(10, 16, 28, 0.7) !important;
        padding: 6px 8px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Chakra Petch', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        color: #94a3b8 !important;
        transition: all 0.25s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.22) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid #06b6d4 !important;
        box-shadow: 0 0 14px rgba(6, 182, 212, 0.3) !important;
    }

    /* Botones Tuning de Alto Rendimiento */
    .stButton > button {
        background: linear-gradient(145deg, #10192e 0%, #162444 100%) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 10px !important;
        font-family: 'Chakra Petch', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        padding: 0.55rem 1.1rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        border-color: #f59e0b !important;
        color: #fbbf24 !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.35), 0 0 12px rgba(245, 158, 11, 0.2) !important;
    }

    .stButton > button:active {
        transform: translateY(1px) !important;
    }

    /* Tarjetas de Órdenes de Trabajo */
    .ot-card {
        background: linear-gradient(145deg, #0c1322 0%, #121c32 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1.3rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
        position: relative;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(8px);
    }

    .ot-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6), 0 0 15px rgba(56, 189, 248, 0.25);
    }

    .ot-card.alta {
        border-left: 5px solid #ef4444;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.15), 0 4px 15px rgba(0,0,0,0.4);
    }
    .ot-card.media {
        border-left: 5px solid #f59e0b;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.15), 0 4px 15px rgba(0,0,0,0.4);
    }
    .ot-card.baja {
        border-left: 5px solid #10b981;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.15), 0 4px 15px rgba(0,0,0,0.4);
    }

    /* Badges */
    .badge-obd {
        display: inline-block;
        background: rgba(6, 182, 212, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(6, 182, 212, 0.5);
        padding: 4px 10px;
        border-radius: 6px;
        font-family: 'Inter', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
        box-shadow: 0 0 8px rgba(6, 182, 212, 0.2);
    }

    .badge-tag {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 5px;
        font-family: 'Chakra Petch', sans-serif;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    .badge-alta { background: rgba(239, 68, 68, 0.22); color: #f87171; border: 1px solid #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.3); }
    .badge-media { background: rgba(245, 158, 11, 0.22); color: #fbbf24; border: 1px solid #f59e0b; box-shadow: 0 0 8px rgba(245, 158, 11, 0.3); }
    .badge-baja { background: rgba(16, 185, 129, 0.22); color: #34d399; border: 1px solid #10b981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.3); }

    .permission-card {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.14), rgba(15, 23, 42, 0.95));
        border: 2px solid #f59e0b;
        border-radius: 14px;
        padding: 1.4rem;
        margin: 1.2rem 0;
        animation: neonGlow 2.8s infinite ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. GESTIÓN DE SESIÓN Y MEMORIA PERSISTENTE
# -----------------------------------------------------------------------------
if "memory" not in st.session_state:
    st.session_state.memory = AutoTechSessionMemory()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_plan" not in st.session_state:
    st.session_state.last_plan = None

if "last_plan_steps" not in st.session_state:
    st.session_state.last_plan_steps = []

if "plan_completed_steps" not in st.session_state:
    st.session_state.plan_completed_steps = set()

if "last_multiagent_dialogue" not in st.session_state:
    st.session_state.last_multiagent_dialogue = []

if "plan_goal" not in st.session_state:
    st.session_state.plan_goal = ""

if "pending_web_permission" not in st.session_state:
    st.session_state.pending_web_permission = None

# Modelo 100% NO-LLAMA oficial fijado por la cátedra
selected_model = os.environ.get("LLM_MODEL", "openai/gpt-oss-20b")
active_api_key = os.environ.get("LLM_API_KEY", "")

# -----------------------------------------------------------------------------
# 3. FACTORY DE AGENTE CACHEADO INTELIGENTEMENTE
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_agent(api_key: str, model_name: str):
    """Crea una instancia única del agente vinculada a la clave y modelo NO-LLAMA activos."""
    if not api_key:
        return None
    return create_autotech_agent(model_name=model_name, api_key=api_key)

agent_executor = load_agent(active_api_key, selected_model) if active_api_key else None

# -----------------------------------------------------------------------------
# 4. ENCABEZADO EXACTO SOLICITADO
# -----------------------------------------------------------------------------
st.markdown("""
<div class="cockpit-header">
    <div class="brand-title">
        <span style="font-size: 2.6rem;">⚙️</span>
        <span>AUTOTECH <span class="accent">JPB SOLUTIONS</span></span>
    </div>
    <div class="brand-sub">
        SISTEMA ORQUESTADOR DE TALLER & AGENTE INTELIGENTE AUTÓNOMO
    </div>
</div>
""", unsafe_allow_html=True)

# Verificación de credenciales sin panel lateral
if not active_api_key:
    with st.expander("🔑 Configuración de Credencial LLM_API_KEY (Requerida)", expanded=True):
        st.warning("⚠️ No se detectó LLM_API_KEY en variables de entorno o Secretos de Colab.")
        input_key = st.text_input("Ingresa tu LLM_API_KEY:", type="password", placeholder="gsk_...")
        if input_key:
            os.environ["LLM_API_KEY"] = input_key
            st.rerun()

# -----------------------------------------------------------------------------
# 5. PESTAÑAS PRINCIPALES DEL SISTEMA
# -----------------------------------------------------------------------------
tab_chat, tab_plan, tab_ordenes, tab_stock = st.tabs([
    "💬 Cockpit de Diagnóstico y Chat ReAct",
    "📋 Planificador Técnico (Plan-and-Execute)",
    "📑 Órdenes de Trabajo Persistidas",
    "📦 Inventario en Bodega en Tiempo Real"
])

# -----------------------------------------------------------------------------
# TAB 1: COCKPIT DE DIAGNÓSTICO Y CHAT REACT
# -----------------------------------------------------------------------------
with tab_chat:
    st.markdown("##### 🏁 Atajos Rápidos de Prueba (Pitstop Presets):")
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    quick_input = None

    with col_p1:
        if st.button("🏎️ 1. Ficha Palio & Frenos", use_container_width=True, help="Demuestra RAG técnico y criticidad de seguridad activa."):
            quick_input = "Hola, tengo un Fiat Palio 1.3 Fire 2008. ¿Qué aceite de motor recomienda el fabricante y qué capacidad lleva? Además el auto frena largo y hace un chillido fuerte."

    with col_p2:
        if st.button("📦 2. Stock & Ubicación", use_container_width=True, help="Consulta el inventario y estanterías en bodega."):
            quick_input = "¿Tienen en bodega el aceite 10W-40 y las pastillas de freno para mi Fiat Palio? ¿Cuánto cuestan y en qué estantería están guardados?"

    with col_p3:
        if st.button("📑 3. Formalizar Orden OT", use_container_width=True, help="Registra y persiste la orden de trabajo calculando totales."):
            quick_input = "Soy Carlos Mendoza. Deseo formalizar el servicio de cambio de aceite y cambio de pastillas de freno para mi Fiat Palio 1.3. Calcula automáticamente la mano de obra del taller según las operaciones y genera la orden oficial de trabajo."

    with col_p4:
        if st.button("🌐 4. Vehículo Externo (Toyota)", use_container_width=True, help="Demuestra el protocolo de autorización previa para búsqueda web."):
            quick_input = "Tengo un Toyota Yaris 2018 con problemas en la distribución y necesito el procedimiento oficial de cambio de correa."

    st.markdown("---")

    # Contenedor para el historial de mensajes
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.chat_history:
            avatar = "🏎️" if msg["role"] == "user" else "🔧"
            with st.chat_message(msg["role"], avatar=avatar):
                if "steps" in msg and msg["steps"]:
                    with st.expander(f"🔍 Escáner Telemetría ReAct ({len(msg['steps'])} llamadas a herramientas)", expanded=False):
                        for step_idx, step in enumerate(msg["steps"], 1):
                            tool_action = step[0]
                            tool_output = step[1]
                            st.markdown(f'<div class="badge-obd">[OBD-II SCAN] PASO {step_idx}: {tool_action.tool}</div>', unsafe_allow_html=True)
                            st.caption(f"Parámetros: `{tool_action.tool_input}`")
                            st.markdown(f"```text\n{str(tool_output)[:550]}\n```")
                
                st.markdown(msg["content"])

        # Interfaz interactiva de solicitud de permiso de búsqueda en internet
        if st.session_state.pending_web_permission:
            pending_query = st.session_state.pending_web_permission
            st.markdown(f"""
            <div class="permission-card">
                <h4 style="color: #f59e0b; margin: 0 0 0.5rem 0;">⚠️ AUTORIZACIÓN REQUERIDA PARA ACCESO EXTERNO</h4>
                <p style="color: #cbd5e1; margin: 0 0 0.8rem 0; font-size: 0.95rem;">
                    El agente detectó que las especificaciones para <b>'{pending_query}'</b> no forman parte de los 5 manuales locales indexados de AutoTech.
                    Conforme al protocolo de seguridad de taller, ¿autorizas realizar una búsqueda técnica en internet en portales especializados (TodoMecánica / AutoDoc Club)?
                </p>
            </div>
            """, unsafe_allow_html=True)

            col_aut_yes, col_aut_no = st.columns([1.5, 3.5])
            with col_aut_yes:
                if st.button("✅ Sí, Autorizo Búsqueda Web", use_container_width=True):
                    quick_input = f"Sí, autorizo la búsqueda en internet. Por favor consulta en portales especializados sobre: {pending_query} y entrega el diagnóstico."
                    st.session_state.pending_web_permission = None
            with col_aut_no:
                if st.button("❌ No, Mantener Solo Manuales Locales", use_container_width=True):
                    quick_input = "No autorizo buscar en internet, mantente únicamente con la información disponible en los manuales de AutoTech."
                    st.session_state.pending_web_permission = None

    # ENTRADA DE TEXTO AL FINAL DE LA PÁGINA
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    user_prompt = st.chat_input("Escribe tu consulta mecánica, síntoma o requerimiento de taller...")
    if quick_input:
        user_prompt = quick_input

    if user_prompt:
        if not active_api_key:
            st.error("⚠️ Configura tu Groq API Key para interactuar con el agente.")
            st.stop()

        if agent_executor is None:
            agent_executor = create_autotech_agent(model_name=selected_model, api_key=active_api_key)

        # 1. Registrar mensaje del usuario
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        # 2. Ejecutar agente
        with chat_container:
            with st.chat_message("user", avatar="🏎️"):
                st.markdown(user_prompt)

            with st.chat_message("assistant", avatar="🔧"):
                with st.spinner("🔧 AutoTech Copilot analizando telemetría, manuales y stock..."):
                    try:
                        resultado = execute_agent_with_backoff(agent_executor, {
                            "input": user_prompt,
                            "chat_history": st.session_state.memory.get_messages()
                        })

                        respuesta_final = resultado.get("output", "")
                        pasos_intermedios = resultado.get("intermediate_steps", [])

                        # Detectar si el agente consultó por autorización para buscar en la web
                        lower_resp = respuesta_final.lower()
                        frases_permiso = [
                            "buscar en internet", "búsqueda en internet", "solicite autorización", 
                            "autorización y realice una búsqueda", "no se encuentra disponible en los manuales",
                            "deseas que busque en internet"
                        ]
                        if any(p in lower_resp for p in frases_permiso):
                            st.session_state.pending_web_permission = user_prompt

                        # Mostrar llamadas a herramientas si existieron
                        if pasos_intermedios:
                            with st.expander(f"🔍 Escáner Telemetría ReAct ({len(pasos_intermedios)} llamadas a herramientas)", expanded=True):
                                for step_idx, step in enumerate(pasos_intermedios, 1):
                                    tool_action = step[0]
                                    tool_output = step[1]
                                    st.markdown(f'<div class="badge-obd">[OBD-II SCAN] PASO {step_idx}: {tool_action.tool}</div>', unsafe_allow_html=True)
                                    st.caption(f"Parámetros: `{tool_action.tool_input}`")
                                    st.markdown(f"```text\n{str(tool_output)[:550]}\n```")

                        st.markdown(respuesta_final)

                        # Persistir en memorias
                        st.session_state.memory.add_user_message(user_prompt)
                        st.session_state.memory.add_ai_message(respuesta_final)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": respuesta_final,
                            "steps": pasos_intermedios
                        })

                    except Exception as e:
                        st.error(f"Error de ejecución del agente: {str(e)}")

        st.rerun()

# -----------------------------------------------------------------------------
# TAB 2: PLANIFICADOR TÉCNICO (PLAN-AND-EXECUTE) - IE5
# -----------------------------------------------------------------------------
with tab_plan:
    st.markdown("### 📋 Planificación Estratégica Previa (Plan-and-Execute)")
    st.info("""
    **Módulo de Planificación Secuencial:**
    Analiza y descompone requerimientos mecánicos complejos en un plan de acción ordenado por criticidad técnica
    antes de interactuar con las herramientas de inventario, manuales o presupuesto.
    """)
    
    if "input_plan_text" not in st.session_state:
        st.session_state.input_plan_text = "Recepcionar un Fiat Palio 1.3 con chillido severo en frenos y nivel bajo de lubricante, verificar stock de repuestos y formalizar orden de trabajo con mano de obra."

    col_pl1, col_pl2 = st.columns([3, 1])
    with col_pl2:
        st.markdown("**Ejemplos rápidos:**")
        if st.button("🔧 Plan: Frenos & Aceite Palio", use_container_width=True):
            st.session_state.input_plan_text = "Recepcionar un Fiat Palio 1.3 con chillido severo en frenos y nivel bajo de lubricante, verificar stock de repuestos y formalizar orden de trabajo con mano de obra."
            st.rerun()
        if st.button("⚡ Plan: Falla Eléctrica Changan", use_container_width=True):
            st.session_state.input_plan_text = "Diagnosticar falla de alza vidrios en puerta delantera de Changan CX70, validar existencia de botonera o motor elevacristales en bodega y presupuestar reparación."
            st.rerun()

    with col_pl1:
        objetivo_input = st.text_area(
            "Objetivo mecánico complejo a planificar:",
            value=st.session_state.input_plan_text,
            height=100
        )

    if st.button("🚀 Generar Plan de Trabajo Secuencial", use_container_width=True):
        if not active_api_key:
            st.error("Configura tu LLM_API_KEY para planificar.")
        else:
            with st.spinner("Evaluando criticidad técnica y coordinando entre agentes especializados..."):
                try:
                    # 1. Simulación y registro de diálogo multi-agente
                    dialogo = generar_comunicacion_multiagente(objetivo_input)
                    st.session_state.last_multiagent_dialogue = dialogo

                    # 2. Generación del plan con el LLM
                    plan_obtenido = generar_plan_taller(objetivo_input)
                    st.session_state.last_plan = plan_obtenido

                    # 3. Extracción de pasos estructurados para el mecánico
                    pasos = extraer_pasos_plan(plan_obtenido, objetivo_input)
                    st.session_state.last_plan_steps = pasos
                    st.session_state.plan_completed_steps = set()
                    st.session_state.plan_goal = objetivo_input
                except Exception as e:
                    st.error(f"Error generando plan: {e}")

    # Registro de comunicación entre los agentes (oculto por defecto, se despliega al hacer click)
    if st.session_state.get("last_multiagent_dialogue"):
        st.markdown("---")
        with st.expander("Comunicación entre Agentes (Click para ver)", expanded=False):
            st.caption("Coordinación y validación entre agentes especializados:")
            for d in st.session_state.last_multiagent_dialogue:
                c_border = d.get("color", "#38bdf8")
                st.markdown(f"""
                <div style="background: #0f172a; border-left: 4px solid {c_border}; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-weight: 700; font-size: 0.88rem; color: #f8fafc;">{d['emisor']} ➔ {d['receptor']}</span>
                        <span style="font-size: 0.72rem; background: rgba(56, 189, 248, 0.15); color: {c_border}; border: 1px solid {c_border}44; padding: 2px 8px; border-radius: 4px; font-weight: 700;">{d['tipo']}</span>
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.86rem; line-height: 1.45;">{d['mensaje']}</div>
                </div>
                """, unsafe_allow_html=True)

    # Visualización del Plan Estratégico Generado
    if st.session_state.get("last_plan"):
        st.markdown("---")
        st.markdown("#### Plan de Trabajo Generado")
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.7); border-left: 4px solid #f59e0b; padding: 1.2rem; border-radius: 0 10px 10px 0; margin-bottom: 1rem;">
            {st.session_state.last_plan}
        </div>
        """, unsafe_allow_html=True)

        # Panel de ejecución secuencial del mecánico con checks progresivos
        st.markdown("---")
        st.markdown("#### Ejecución de Pasos en Taller")
        st.caption("Control de avance del mecánico. Cada paso se valida antes de habilitar el siguiente:")

        pasos = st.session_state.get("last_plan_steps", [])
        completed = st.session_state.get("plan_completed_steps", set())
        total_p = len(pasos)
        n_done = len(completed)

        pct = (n_done / total_p) if total_p > 0 else 0.0
        st.progress(pct)

        col_pr1, col_pr2 = st.columns([3, 1])
        with col_pr1:
            st.markdown(f"**Avance en taller:** `{n_done}/{total_p} pasos completados` ({int(pct * 100)}%)")
        with col_pr2:
            if n_done > 0:
                if st.button("Reiniciar Pasos", key="btn_reset_checks", use_container_width=True):
                    st.session_state.plan_completed_steps = set()
                    st.rerun()

        # Renderizar los pasos progresivamente
        for idx, paso in enumerate(pasos):
            p_num = paso.get("num", idx + 1)
            is_done = p_num in completed

            if is_done:
                # Paso completado previamente
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-left: 5px solid #10b981; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #10b981; font-size: 0.95rem;">Paso {p_num}: {paso.get('titulo', '')}</span>
                        <span style="font-size: 0.72rem; background: #10b981; color: #022c22; font-weight: 800; padding: 2px 8px; border-radius: 4px;">REALIZADO</span>
                    </div>
                    <div style="color: #94a3b8; font-size: 0.84rem; margin-top: 4px;">{paso.get('detalle', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            elif idx == n_done:
                # Paso activo actual: muestra la información y el checkbox
                st.markdown(f"""
                <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.4); border-left: 5px solid #38bdf8; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #38bdf8; font-size: 1rem;">Paso {p_num} (En Proceso): {paso.get('titulo', '')}</span>
                        <span style="font-size: 0.72rem; background: #38bdf8; color: #082f49; font-weight: 800; padding: 2px 8px; border-radius: 4px;">ACTIVO</span>
                    </div>
                    <div style="color: #f1f5f9; font-size: 0.9rem; margin-bottom: 6px;"><strong>Instrucción:</strong> {paso.get('detalle', '')}</div>
                    <div style="color: #94a3b8; font-size: 0.82rem;"><strong>Herramienta:</strong> <code>{paso.get('herramienta', 'Taller')}</code> &nbsp;|&nbsp; <strong>Justificación:</strong> {paso.get('justificacion', 'Seguridad y norma técnica')}</div>
                </div>
                """, unsafe_allow_html=True)

                check_activo = st.checkbox(
                    f"Marcar Paso {p_num} como realizado",
                    key=f"chk_p_{p_num}_{n_done}"
                )
                if check_activo:
                    st.session_state.plan_completed_steps.add(p_num)
                    st.rerun()

                # Detener el ciclo para que los pasos posteriores aparezcan sucesivamente
                break

        # Si ya se completaron todos los pasos
        if total_p > 0 and n_done == total_p:
            st.success("Todos los pasos del plan de trabajo han sido completados y verificados. El vehículo está listo para entrega al cliente.")
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                st.info("Puedes revisar o emitir la Orden de Trabajo formal en la pestaña Órdenes de Trabajo.")
            with c_f2:
                if st.button("Iniciar Nuevo Plan", use_container_width=True):
                    st.session_state.last_plan = None
                    st.session_state.last_plan_steps = []
                    st.session_state.plan_completed_steps = set()
                    st.session_state.last_multiagent_dialogue = []
                    st.rerun()

# -----------------------------------------------------------------------------
# TAB 3: ÓRDENES DE TRABAJO REGISTRADAS Y PERSISTIDAS (IE1)
# -----------------------------------------------------------------------------
with tab_ordenes:
    st.markdown("### 📑 Órdenes de Trabajo Persistidas en Sistema Local")
    
    ordenes = obtener_ordenes_registradas()
    
    # KPIs de Taller
    total_ots = len(ordenes)
    ots_pendientes = sum(1 for o in ordenes if str(o.get("estado", "Pendiente")) == "Pendiente")
    ots_taller = sum(1 for o in ordenes if "Taller" in str(o.get("estado", "")) or "Proceso" in str(o.get("estado", "")))
    ots_resueltas = sum(1 for o in ordenes if "Resuelta" in str(o.get("estado", "")) or "Solucionada" in str(o.get("estado", "")))
    facturacion_total = sum(o.get("total_estimado_clp", 0) for o in ordenes)

    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns([1, 1, 1, 1, 1.45])
    col_m1.metric("📋 Total Órdenes", total_ots)
    col_m2.metric("⏳ Pendientes", ots_pendientes)
    col_m3.metric("🔧 En Taller", ots_taller)
    col_m4.metric("✅ Resueltas", ots_resueltas)
    col_m5.metric("💰 Facturación Est.", f"${facturacion_total:,} CLP")

    st.markdown("---")

    # Formulario rápido para emitir nueva orden manual de demostración
    with st.expander("➕ Emitir Nueva Orden de Trabajo Manual (Demo)", expanded=False):
        with st.form("form_nueva_ot"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                n_cliente = st.text_input("Nombre del Cliente:", value="María Fernández")
                n_vehiculo = st.text_input("Vehículo (Marca, Modelo, Año):", value="Fiat Palio 1.3 FIRE 2008")
                n_diag = st.text_area("Diagnóstico Técnico:", value="Cambio de pastillas de freno y cambio de aceite de motor.")
            with f_col2:
                n_rep = st.text_input("Repuestos requeridos (separados por coma):", value="aceite 10w-40, pastillas de freno")
                n_mo = st.number_input("Costo Mano de Obra (CLP):", value=35000, step=5000)
                n_prio = st.selectbox("Prioridad:", ["Alta", "Media", "Baja"], index=0)
                n_cita = st.text_input("Cita Programada:", value="29-10-2026 16:30 hrs")
            
            btn_emitir = st.form_submit_button("🏁 Registrar Orden de Trabajo en Sistema", use_container_width=True)
            if btn_emitir:
                res_ot = registrar_orden_reparacion.invoke({
                    "cliente": n_cliente,
                    "vehiculo": n_vehiculo,
                    "diagnostico": n_diag,
                    "repuestos_requeridos": n_rep,
                    "costo_mano_obra_clp": n_mo,
                    "prioridad": n_prio,
                    "fecha_cita_programada": n_cita
                })
                st.success(res_ot)
                st.rerun()

    # Filtro de visualización
    filtro_estado = st.radio(
        "Filtrar órdenes por estado:",
        ["Todas", "Pendientes", "En Taller", "Resueltas / Solucionadas"],
        horizontal=True
    )

    ordenes_mostradas = []
    for o in reversed(ordenes):
        st_actual = str(o.get("estado", "Pendiente"))
        es_resuelta = "Resuelta" in st_actual or "Solucionada" in st_actual
        es_taller = "Taller" in st_actual or "Proceso" in st_actual
        
        if filtro_estado == "Todas":
            ordenes_mostradas.append(o)
        elif filtro_estado == "Pendientes" and st_actual == "Pendiente":
            ordenes_mostradas.append(o)
        elif filtro_estado == "En Taller" and es_taller:
            ordenes_mostradas.append(o)
        elif filtro_estado == "Resueltas / Solucionadas" and es_resuelta:
            ordenes_mostradas.append(o)

    if not ordenes_mostradas:
        st.info(f"No hay órdenes en la categoría '{filtro_estado}'.")

    for ot in ordenes_mostradas:
        id_ot = ot.get('id_orden')
        st_actual = str(ot.get('estado', 'Pendiente'))
        prio = str(ot.get('prioridad', 'Media'))
        prio_class = "alta" if prio.lower() == "alta" else ("media" if prio.lower() == "media" else "baja")

        with st.container():
            st.markdown(f"""
            <div class="ot-card {prio_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                    <div>
                        <span style="font-size: 1.15rem; font-weight: 700; color: #f8fafc;">🏷️ ORDEN {id_ot}</span>
                        <span class="badge-tag badge-{prio_class}" style="margin-left: 8px;">Prioridad {prio}</span>
                    </div>
                    <div>
                        <span style="font-weight: 600; color: {'#34d399' if 'Resuelta' in st_actual else ('#38bdf8' if 'Taller' in st_actual else '#fbbf24')};">
                            ● {st_actual}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**👤 Cliente:** {ot.get('cliente')}")
            c2.markdown(f"**🚘 Vehículo:** {ot.get('vehiculo')}")
            c3.markdown(f"**📅 Ingreso:** {ot.get('fecha_ingreso')}")
            cita_val = ot.get('fecha_cita_programada') or 'Por coordinar'
            c4.markdown(f"**⏰ Cita:** `{cita_val}`")

            st.markdown(f"**🔧 Diagnóstico:** {ot.get('diagnostico')}")
            
            rep_list = ot.get("repuestos", [])
            if rep_list:
                st.markdown("**Piezas asignadas de bodega:**")
                for r in rep_list:
                    precio = f"${r.get('precio_clp', 0):,} CLP" if r.get('precio_clp') else r.get('nota', 'N/A')
                    st.markdown(f"• {r.get('repuesto')} — `{precio}` *(Ubicación: {r.get('bodega', 'Externa')})*")

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Repuestos", f"${ot.get('costo_repuestos_clp', 0):,} CLP")
            col_b.metric("Mano de Obra", f"${ot.get('costo_mano_obra_clp', 0):,} CLP")
            col_c.metric("TOTAL ESTIMADO", f"${ot.get('total_estimado_clp', 0):,} CLP")

            desglose_mo = ot.get("desglose_mano_obra", [])
            if desglose_mo:
                with st.expander("🛠️ Desglose Técnico de Mano de Obra (Baremo Automático)", expanded=False):
                    for t in desglose_mo:
                        st.markdown(f"• **{t.get('tarea')}**: `${t.get('costo_clp', 0):,} CLP`")

            # Botones de acción operativa
            b_col1, b_col2, b_col3, b_col4 = st.columns([1.5, 1.5, 1.5, 2.5])
            
            with b_col1:
                if st_actual != "En Taller / Proceso":
                    if st.button("🔧 A Taller", key=f"taller_{id_ot}"):
                        cambiar_estado_orden_trabajo(id_ot, "En Taller / Proceso")
                        st.rerun()

            with b_col2:
                if "Resuelta" not in st_actual:
                    if st.button("✅ Resolver", key=f"res_{id_ot}"):
                        cambiar_estado_orden_trabajo(id_ot, "Resuelta / Solucionada")
                        st.rerun()
                else:
                    if st.button("↩️ Reabrir", key=f"pend_{id_ot}"):
                        cambiar_estado_orden_trabajo(id_ot, "Pendiente")
                        st.rerun()

            with b_col3:
                if st.button("🗑️ Eliminar", key=f"del_{id_ot}"):
                    st.session_state[f"confirm_del_{id_ot}"] = True

            # Cuadro de confirmación de eliminación segura
            if st.session_state.get(f"confirm_del_{id_ot}", False):
                st.warning(f"⚠️ ¿Seguro que deseas eliminar la orden `{id_ot}`?")
                c_del1, c_del2 = st.columns([1, 1])
                with c_del1:
                    if st.button("🚨 Confirmar Eliminación", key=f"btn_confirm_del_{id_ot}"):
                        eliminar_orden_trabajo(id_ot)
                        st.session_state.pop(f"confirm_del_{id_ot}", None)
                        st.success(f"Orden {id_ot} eliminada.")
                        st.rerun()
                with c_del2:
                    if st.button("✖️ Cancelar", key=f"btn_cancel_{id_ot}"):
                        st.session_state.pop(f"confirm_del_{id_ot}", None)
                        st.rerun()

            st.markdown("---")

# -----------------------------------------------------------------------------
# TAB 4: CATÁLOGO DE INVENTARIO EN TIEMPO REAL
# -----------------------------------------------------------------------------
with tab_stock:
    st.markdown("### 📦 Inventario General de Bodega AutoTech JPB Solutions")
    
    total_articulos = len(INVENTARIO_BODEGA)
    total_unidades = sum(item["stock"] for item in INVENTARIO_BODEGA.values())
    valor_inventario = sum(item["stock"] * item["precio_clp"] for item in INVENTARIO_BODEGA.values())
    criticos = sum(1 for item in INVENTARIO_BODEGA.values() if item["stock"] <= 5)

    k1, k2, k3, k4 = st.columns([1, 1, 1.45, 1.1])
    k1.metric("📦 Variedad de Productos", total_articulos)
    k2.metric("🔢 Total Unidades Físicas", total_unidades)
    k3.metric("💰 Valorización Bodega", f"${valor_inventario:,} CLP")
    k4.metric("⚠️ Stock Crítico (≤ 5 un.)", criticos)

    st.markdown("---")

    col_f1, col_f2 = st.columns([1.5, 2.5])
    with col_f1:
        categorias = sorted(list(set(item["categoria"] for item in INVENTARIO_BODEGA.values())))
        filtro_cat = st.selectbox("Filtrar por categoría:", ["Todas"] + categorias)
    with col_f2:
        busqueda_txt = st.text_input("🔍 Buscar repuesto por nombre o ubicación:", placeholder="ej: aceite, pastillas, botonera, pasillo A...")

    items_mostrar = []
    for cod, data in INVENTARIO_BODEGA.items():
        cumple_cat = (filtro_cat == "Todas" or data["categoria"] == filtro_cat)
        cumple_txt = (not busqueda_txt.strip() or 
                      busqueda_txt.lower() in cod.lower() or 
                      busqueda_txt.lower() in data["nombre"].lower() or 
                      busqueda_txt.lower() in data["bodega"].lower())
        
        if cumple_cat and cumple_txt:
            stock_num = data["stock"]
            stock_badge = f"🟢 {stock_num}" if stock_num > 15 else (f"🟡 {stock_num}" if stock_num > 5 else f"🔴 {stock_num} (Crítico)")
            
            items_mostrar.append({
                "Código": cod,
                "Producto": data["nombre"],
                "Categoría": data["categoria"],
                "Stock": stock_badge,
                "Precio (CLP)": f"${data['precio_clp']:,}",
                "Ubicación en Bodega": data["bodega"],
                "Descripción": data["desc"]
            })

    if items_mostrar:
        st.dataframe(items_mostrar, use_container_width=True, height=600)
    else:
        st.warning("No se encontraron repuestos con los filtros seleccionados.")
