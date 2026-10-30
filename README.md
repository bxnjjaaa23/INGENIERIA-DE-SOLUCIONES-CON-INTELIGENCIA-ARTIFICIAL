# AutoTech JPB Solutions - Agente Autónomo Orquestador de Taller ⚙️

[![Duoc UC](https://img.shields.io/badge/Duoc_UC-ISY0101-002B49.svg)](https://www.duoc.cl)
[![Evaluación](https://img.shields.io/badge/Evaluaci%C3%B3n-EP2_Agente_Funcional-orange.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![LangChain](https://img.shields.io/badge/Framework-LangChain_0.1+-1C3C3C.svg)](https://www.langchain.com)
[![Model](https://img.shields.io/badge/LLM-openai%2Fgpt--oss--20b_(NO--LLAMA)-10a37f.svg)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit_1.30+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![FAISS](https://img.shields.io/badge/VectorStore-FAISS_IndexFlatIP-00599C.svg)](https://github.com/facebookresearch/faiss)

---

> **Institución:** Duoc UC — Escuela de Informática y Telecomunicaciones  
> **Asignatura:** ISY0101 — Ingeniería de Soluciones con Inteligencia Artificial  
> **Evaluación:** Evaluación Parcial N°2 (EP2) — Encargo y Presentación: Agente Funcional  
> **Integrantes:** Paolo Jorquera, Benjamín Arriaza y José Castillo  
> **Repositorio Oficial:** [github.com/bxnjjaaa23/INGENIERIA-DE-SOLUCIONES-CON-INTELIGENCIA-ARTIFICIAL](https://github.com/bxnjjaaa23/INGENIERIA-DE-SOLUCIONES-CON-INTELIGENCIA-ARTIFICIAL)  
> **Cuaderno Interactivo Colab:** [`AutoTech_EP2.ipynb`](./AutoTech_EP2.ipynb)  

---

## 📑 Tabla de Contenidos

1. [Resumen Ejecutivo y Contexto Organizacional](#1-resumen-ejecutivo-y-contexto-organizacional)
2. [Arquitectura General y Orquestación del Agente (IE8)](#2-arquitectura-general-y-orquestación-del-agente-ie8)
3. [Herramientas Autónomas Integradas (IE1)](#3-herramientas-autónomas-integradas-ie1)
4. [Procesos de Memoria y Recuperación de Contexto (IE3, IE4)](#4-procesos-de-memoria-y-recuperación-de-contexto-ie3-ie4)
5. [Estrategias de Planificación y Toma de Decisiones (IE5, IE7)](#5-estrategias-de-planificación-y-toma-de-decisiones-ie5-ie7)
6. [Justificación Técnica de Decisiones de Diseño e Integración (IE2, IE9)](#6-justificación-técnica-de-decisiones-de-diseño-e-integración-ie2-ie9)
7. [Diagramas de Flujo y Protocolo de Coordinación (IE6, IE8)](#7-diagramas-de-flujo-y-protocolo-de-coordinación-ie6-ie8)
8. [Estructura del Repositorio](#8-estructura-del-repositorio)
9. [Guía de Instalación y Demostración en Vivo (IE10)](#9-guía-de-instalación-y-demostración-en-vivo-ie10)
10. [Evidencias de la Batería de Pruebas](#10-evidencias-de-la-batería-de-pruebas)
11. [Referencias Bibliográficas (Formato APA 7ma Edición)](#11-referencias-bibliográficas-formato-apa-7ma-edición)

---

## 1. Resumen Ejecutivo y Contexto Organizacional

**AutoTech JPB Solutions** es un taller de mantenimiento preventivo, correctivo y diagnóstico multimarca ubicado en Santiago. Como muchos talleres del país, enfrenta varios problemas cotidianos:

1. **Pérdida de tiempo buscando información técnica:** Los mecánicos tienen que revisar manuales largos y pesados para encontrar torques, capacidades de aceite o el procedimiento correcto de desmontaje.
2. **Desconexión entre recepción y bodega:** Se pierde tiempo cotizando stock, precios en CLP y la ubicación exacta de cada repuesto.
3. **Presupuestos de mano de obra inconsistentes:** Las tarifas no siempre coinciden con el baremo de tiempos de taller ni con la complejidad real del trabajo.
4. **Falta de trazabilidad:** Las órdenes de trabajo escritas a mano se pierden o se llenan de errores.

### Solución Implementada: Agente Autónomo Funcional EP2

En esta EP2 el copiloto de la EP1 se transformó en un **Agente Autónomo Orquestador**. Usa el patrón **ReAct (Reasoning + Acting)** junto con **Plan-and-Execute**, y está impulsado por el modelo **`openai/gpt-oss-20b` (100% NO-LLAMA)** a través de la API de Groq. El agente puede:

* Planificar trabajos mecánicos dando prioridad a la **seguridad vial** (frenos, dirección y neumáticos).
* Coordinar sub-agentes especializados (Diagnóstico RAG, Bodega y Baremo de Taller).
* Guiar al mecánico paso a paso con **checkpoints interactivos** y feedback en tiempo real.
* Crear, consultar, actualizar y guardar órdenes de trabajo formales en un archivo local (`ordenes_trabajo_autotech.json`).

---

## 2. Arquitectura General y Orquestación del Agente (IE8)

La solución está dividida en tres capas bien separadas: **Interfaz y Despliegue**, **Inteligencia y Orquestación con LangChain**, y **Almacenamiento + Herramientas Locales**.

```mermaid
graph TD
    subgraph UI ["Capa de Interfaz de Usuario & Despliegue"]
        A[Usuario / Mecánico / Cliente] --> B[Streamlit Cockpit Dark Theme - app_ep2.py]
        B --> C[Túnel Cifrado Cloudflare - trycloudflare]
    end

    subgraph AGENT_CORE ["Capa de Orquestación Inteligente (LangChain)"]
        B --> D[AgentExecutor / ReAct Engine]
        D --> E[Prompt Template con Contexto Temporal Chileno]
        E --> F[LLM: openai/gpt-oss-20b en Groq LPU]
        D <--> G[AutoTechSessionMemory - Buffer Deslizante 6 Turnos]
        D --> H[Módulo Plan-and-Execute & Coordinación Inter-Agentes]
    end

    subgraph TOOLS ["Capa de Herramientas Autónomas (Tool Calling)"]
        D --> T1[consulta_manual_tecnico]
        D --> T2[consultar_inventario_repuestos]
        D --> T3[registrar_orden_reparacion]
        D --> T4[buscar_en_internet]
    end

    subgraph STORAGE ["Capa de Almacenamiento & Conocimiento"]
        T1 <--> K1[(FAISS VectorStore - 553 Chunks - all-MiniLM-L6-v2)]
        K1 <--> K1_CACHE[autotech_vector_cache.pkl - Carga < 0.05s]
        T2 <--> K2[(Inventario Bodega Central en Memoria)]
        T3 <--> K3[(ordenes_trabajo_autotech.json - Persistencia Local)]
        T4 <--> K4[Búsqueda Web Externa - Protocolo Ético con Permiso]
    end

    H --> CHK[Checkpoints Progresivos del Mecánico en Taller]
    CHK --> T3
```

---

## 3. Herramientas Autónomas Integradas (IE1)

El agente cuenta con **4 herramientas** que cubren las tres dimensiones que pide la rúbrica: consulta, escritura/persistencia y razonamiento adaptativo.

| Herramienta | Tipo | Dimensión | Descripción Técnica |
|---|---|---|---|
| `consulta_manual_tecnico` | Consulta | RAG / Semántica | Busca en los 5 manuales locales (Fiat Palio 1.3, Changan CX70, Manual de Operaciones, Diagnóstico Multimarca y Mantenimiento de Motores) y devuelve el texto exacto con cita `[Manual, Pág. X]`. |
| `consultar_inventario_repuestos` | Consulta | Datos Locales | Consulta el stock de bodega (20 SKU). Puede listar categorías o buscar por palabra clave y entrega stock, precio en CLP y ubicación (pasillo + estantería). |
| `registrar_orden_reparacion` | Escritura | Persistencia | Guarda órdenes en `ordenes_trabajo_autotech.json`. Calcula mano de obra según baremo chileno ($20.000 - $45.000 CLP), valida el nombre del cliente y permite actualizar una orden existente sin duplicarla. |
| `buscar_en_internet` | Consulta / Adaptación | Búsqueda Externa | Consulta sitios como TodoMecánica o AutoDoc Club. **Solo se activa** si los manuales locales no tienen la información y el usuario da permiso explícito. |

---

## 4. Procesos de Memoria y Recuperación de Contexto (IE3, IE4)

### 4.1. Memoria de Corto Plazo: `AutoTechSessionMemory` (IE3)

* Usa una ventana deslizante de **6 turnos** (`ConversationBufferWindowMemory` con `max_history_turns=6`).
* Protege el límite de tokens de Groq Free (8.000 TPM y 200.000 TPD). Así el historial no se desborda y el agente sigue recordando el vehículo y la falla aunque la conversación se alargue.
* Ejemplo práctico: si en el primer turno el cliente dice *"Tengo un Fiat Palio 2008 con chillido en frenos"*, en el segundo puede preguntar solo *"¿Tienen repuestos para eso?"* y el agente ya sabe de qué auto se trata.

### 4.2. Memoria de Largo Plazo y Persistencia: JSON Transaccional (IE3)

* Archivo: `ordenes_trabajo_autotech.json`.
* Estructura de ejemplo:

```json
{
  "id_orden": "OT-2026-0001",
  "fecha_creacion": "29-10-2026 21:30",
  "cliente": "Carlos Mendoza",
  "vehiculo": "Fiat Palio 1.3 Fire 2008",
  "diagnostico": "Desgaste severo en pastillas de freno y nivel bajo de lubricante.",
  "repuestos_requeridos": ["Pastillas de freno delanteras", "Aceite 10W-40 (4L)"],
  "costo_repuestos_clp": 50980,
  "costo_mano_obra_clp": 45000,
  "total_estimado_clp": 95980,
  "cita_programada": "30-10-2026 10:00 hrs",
  "prioridad": "Alta",
  "estado": "En Taller"
}
```

* Las funciones `_guardar_orden_local`, `eliminar_orden_trabajo` y `cambiar_estado_orden_trabajo` leen y escriben de forma síncrona para mantener consistencia.

### 4.3. Recuperación de Contexto Semántico: Motor RAG (IE4)

* Chunking de 800 caracteres con overlap de 120 para no cortar instrucciones ni tablas.
* Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensiones, normalizados con norma L2).
* VectorStore: FAISS con `IndexFlatIP` (equivalente a similitud de coseno sobre vectores unitarios).
* Caché en disco: `autotech_vector_cache.pkl` con 553 chunks. Carga en frío en alrededor de 0.03 segundos, así no hay que reindexar los PDFs cada vez que se abre el Colab.

---

## 5. Estrategias de Planificación y Toma de Decisiones (IE5, IE7)

### 5.1. Esquema Plan-and-Execute y Prioridad por Criticidad (IE5)

Antes de llamar herramientas, el agente arma un plan secuencial. Aplica una regla simple de criticidad:

* **Prioridad ALTA:** Frenos, dirección o neumáticos → siempre van en el Paso 1 (inspección inmediata).
* **Prioridad MEDIA:** Tren motriz, lubricación, refrigeración, encendido.
* **Prioridad BAJA / CONFORT:** Alza cristales, luces, plumillas, estética.

### 5.2. Protocolo de Coordinación y Negociación Inter-Agentes

El sistema simula la colaboración entre 4 roles:

```
[Agente Orquestador] ────> [Agente de Diagnóstico RAG]  : Pide criticidad y tolerancias
[Agente de Diagnóstico] ──> [Agente Orquestador]         : Confirma falla crítica en frenos (Prioridad Alta)
[Agente Orquestador] ────> [Agente de Bodega]           : Verifica stock de pastillas y aceite
[Agente de Bodega] ──────> [Agente Orquestador]         : Confirma disponibilidad en estanterías
[Agente Orquestador] ────> [Agente de Taller]           : Solicita horas-hombre y baremo
[Agente de Taller] ──────> [Agente Orquestador]         : Asigna 2.3 horas estándar ($45.000 CLP)
[Agente Orquestador] ────> [Mecánico en Elevador]       : Entrega el plan listo para ejecutar
```

### 5.3. Checkpoints Progresivos para el Mecánico

En la interfaz el plan se convierte en una hoja de ruta interactiva:

1. El Paso 1 aparece activo con su instrucción y un checkbox.
2. Al marcar el check, el paso se pone en verde (`REALIZADO`) y se desbloquea el siguiente.
3. La barra de progreso avanza en tiempo real (0% → 25% → 50% → 75% → 100%).
4. Cuando se completa el último paso se certifica el control de calidad final.

### 5.4. Toma de Decisiones Adaptativas ante Imprevistos (IE7)

* Si el auto no está en los 5 manuales (ej. Toyota Yaris o Hyundai Tucson), el agente no inventa datos: avisa que el RAG falló y pide permiso para buscar en internet.
* Si un repuesto tiene stock 0, avisa y sugiere alternativas o reprogramar la cita.
* Si el cliente completa o modifica una orden ya creada, el agente detecta el `id_orden_existente` y actualiza en lugar de generar un duplicado.

---

## 6. Justificación Técnica de Decisiones de Diseño e Integración (IE2, IE9)

| Decisión de Diseño | Opción Seleccionada | Alternativas Descartadas | Justificación Técnica y Alineación con la Rúbrica |
|---|---|---|---|
| **Modelo Fundacional LLM** | `openai/gpt-oss-20b` (NO-LLAMA) vía Groq API | Modelos LLaMA (Meta), GPT-4o directo, Claude 3.5 | Cumple con la exigencia de la cátedra de no usar LLaMA. Arquitectura MoE de 20B parámetros, muy rápida en las LPU de Groq (~1.000 tokens/s), function calling nativo y costo cero en Free Tier. |
| **Framework de Agentes** | LangChain (Agents + Tools) | Autogen, CrewAI, Haystack | Es el ecosistema más maduro y documentado para prompts tipados, memorias deslizantes y tool calling. |
| **Indexación Vectorial** | FAISS (`IndexFlatIP`) | ChromaDB, Pinecone, Qdrant | Corre en memoria RAM sin servicios externos, se serializa fácil en `.pkl` y funciona bien en Colab. |
| **Modelo de Embeddings** | `all-MiniLM-L6-v2` (SentenceTransformers) | OpenAI text-embedding-3-small, Cohere | Ligero (384 dim), corre 100% local en CPU y no consume cuota de API. |
| **Persistencia Local** | JSON transaccional | SQLite, MongoDB, PostgreSQL | Portátil, legible en texto plano, sin dependencias de red y fácil de inspeccionar desde el notebook. |
| **Despliegue Web** | Streamlit + Cloudflare Tunnel | Gradio, Flask/FastAPI, ngrok | Streamlit maneja bien el estado de sesión. Cloudflare Tunnel da URL pública TLS sin necesidad de tokens de pago (a diferencia de ngrok). |

---

## 7. Diagramas de Flujo y Protocolo de Coordinación (IE6, IE8)

### 7.1. Flujo de Decisión y Razonamiento ReAct del Agente

```mermaid
flowchart TD
    IN([Inicio: Requerimiento del Usuario]) --> MEM[Cargar Contexto desde AutoTechSessionMemory]
    MEM --> PROMPT[Inyectar System Prompt + Fecha/Hora UTC-3 Chile]
    PROMPT --> LLM{Razonamiento LLM: ¿Requiere Herramientas?}

    LLM -- Sí: Tool Call --> T_DEC{¿Qué herramienta?}
    
    T_DEC -- Manual Técnico --> RAG[consulta_manual_tecnico]
    RAG --> RAG_CHECK{¿Encontrado en Manuales?}
    RAG_CHECK -- Sí --> OBS1[Observación con Cita y Página]
    RAG_CHECK -- No: Falla/Marca Externa --> PERM{¿Usuario autoriza Web?}
    PERM -- Sí --> TAVILY[buscar_en_internet]
    PERM -- No --> RECH[Limitar respuesta a manuales locales]
    TAVILY --> OBS1
    RECH --> OBS1

    T_DEC -- Bodega --> INV[consultar_inventario_repuestos]
    INV --> OBS2[Observación: Stock, Precio CLP, Pasillo]

    T_DEC -- Orden de Trabajo --> ORD[registrar_orden_reparacion]
    ORD --> VAL_NAME{¿Cliente Válido?}
    VAL_NAME -- No --> ASK_NAME[Solicitar nombre formal del cliente]
    VAL_NAME -- Sí --> CALC_MO[Calcular Mano de Obra Baremo Chileno]
    CALC_MO --> SAVE_JSON[(Escribir en ordenes_trabajo_autotech.json)]
    SAVE_JSON --> OBS3[Observación: OT Generada/Actualizada]

    OBS1 --> REASON[Ciclo ReAct: Evaluar Observación]
    OBS2 --> REASON
    OBS3 --> REASON
    ASK_NAME --> REASON

    REASON --> LLM
    LLM -- No: Respuesta Final --> OUT[Emitir Respuesta al Usuario en Streamlit]
    OUT --> UPDATE_MEM[Actualizar Buffer de Memoria con Turno Actual]
    UPDATE_MEM --> END([Fin de Turno])
```

### 7.2. Secuencia Temporal de Negociación Inter-Agentes y Ejecución

```mermaid
sequenceDiagram
    autonumber
    actor U as Mecánico / Cliente
    participant O as Agente Orquestador (Plan-and-Execute)
    participant D as Agente Diagnóstico (RAG)
    participant B as Agente de Bodega
    participant T as Agente de Taller (Baremo)
    participant M as Panel de Checkpoints Taller

    U->>O: Requerimiento complejo (Frenos + Aceite Fiat Palio)
    Note over O: Analiza criticidad del requerimiento
    O->>D: Consulta gravedad técnica y tolerancias de fabricante
    D-->>O: Dictamen: Falla crítica en frenos (Prioridad ALTA). Requiere pastillas, líquido DOT4 y aceite 10W-40
    O->>B: Consulta disponibilidad física y precios de repuestos
    B-->>O: Confirma stock: pastillas ($28.000), aceite ($22.000) y líquido ($8.000)
    O->>T: Solicita cálculo de horas de faena y baremo de taller
    T-->>O: Asigna 2.3 horas estándar. Mano de obra: $45.000 CLP
    O->>U: Despliega Plan de Trabajo Consolidado en 4 Pasos
    
    rect rgb(15, 23, 42)
        Note over M: Ejecución secuencial en elevador
        U->>M: Marca [x] Check Paso 1 (Inspección inicial de frenos)
        M-->>U: Paso 1 completado (25%). Desbloquea Paso 2
        U->>M: Marca [x] Check Paso 2 (Retiro de repuestos en bodega)
        M-->>U: Paso 2 completado (50%). Desbloquea Paso 3
        U->>M: Marca [x] Check Paso 3 (Cambio de pastillas y aceite)
        M-->>U: Paso 3 completado (75%). Desbloquea Paso 4
        U->>M: Marca [x] Check Paso 4 (Control de calidad y prueba de ruta)
        M-->>U: ¡100% Completado! Vehículo certificado para entrega
    end
```

---

## 8. Estructura del Repositorio

```text
INGENIERIA-DE-SOLUCIONES-CON-INTELIGENCIA-ARTIFICIAL/
├── README.md                                 # Informe técnico académico completo (Este documento)
├── AutoTech_EP2.ipynb                        # Cuaderno Google Colab interactivo de presentación
├── app_ep2.py                                # Interfaz gráfica web Streamlit Cockpit Dark Theme
├── autotech_agent_ep2.py                     # Núcleo del Agente LangChain, Herramientas y Memoria
├── rag_engine.py                             # Motor RAG, FAISS VectorStore y embeddings locales
├── test_suite.py                             # Batería de pruebas automatizadas unitarias
├── ordenes_trabajo_autotech.json             # Persistencia local de órdenes de trabajo
├── autotech_vector_cache.pkl                 # Caché vectorial serializada (< 0.05s de carga)
├── .env.example                              # Plantilla de variables de entorno (LLM_API_KEY)
├── ficha_tecnica_fiat_palio.pdf              # Manual 1: Ficha técnica y torques Fiat Palio 1.3 FIRE
├── MANUAL-DE-OPERACIONES-DE-TALLER-.pdf      # Manual 2: Procedimientos operativos de taller mecánico
├── manual_fallas_multimarca_diagnostico.pdf  # Manual 3: Diagnóstico OBD-II y fallas eléctricas
├── manual_recepcion_fallas_cliente_taller.pdf# Manual 4: Guía de recepción de clientes y neumáticos
└── mecanica-automotriz-mantenimiento-de-motores.pdf # Manual 5: Mantenimiento avanzado de motores
```

---

## 9. Guía de Instalación y Demostración en Vivo (IE10)

### 9.1. Opción A: Demostración Interactiva en Google Colab (Recomendada)

Para la presentación oral se usa el cuaderno [`AutoTech_EP2.ipynb`](./AutoTech_EP2.ipynb):

1. Abrir el notebook en Google Colab.
2. Configurar la clave `LLM_API_KEY` en **Secrets** (ícono de llave).
3. Ejecutar las celdas en orden:
   * **Celdas 1 a 6:** Instalación de dependencias y validación de credenciales.
   * **Celdas 7 a 12:** Carga del caché RAG (~0.03 s), inicialización del agente y la memoria.
   * **Celda 14:** Batería interactiva que muestra autonomía, memoria y decisiones adaptativas.
   * **Celda 16:** Inspección del archivo `ordenes_trabajo_autotech.json`.
   * **Celda 18:** Lanzamiento de Streamlit a través del túnel de Cloudflare (URL pública `.trycloudflare.com`).

### 9.2. Opción B: Ejecución en Entorno Local (Windows / Linux / macOS)

```bash
# 1. Clonar el repositorio
git clone https://github.com/bxnjjaaa23/INGENIERIA-DE-SOLUCIONES-CON-INTELIGENCIA-ARTIFICIAL.git
cd INGENIERIA-DE-SOLUCIONES-CON-INTELIGENCIA-ARTIFICIAL

# 2. Crear y activar entorno virtual Python 3.10+
python -m venv venv
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Linux/macOS:
source venv/bin/activate

# 3. Instalar librerías requeridas
pip install langchain langchain-openai langchain-community sentence-transformers faiss-cpu streamlit python-dotenv

# 4. Configurar la variable de entorno de la API Key
# En Windows PowerShell:
$env:LLM_API_KEY="gsk_tu_clave_aqui"
# En Linux/macOS:
export LLM_API_KEY="gsk_tu_clave_aqui"

# 5. Ejecutar la batería de pruebas automatizadas
python test_suite.py

# 6. Iniciar la aplicación web Streamlit
streamlit run app_ep2.py
```

Abre el navegador en `http://localhost:8501`.

---

## 10. Evidencias de la Batería de Pruebas

| Caso de Prueba | Entrada de Prueba | Módulo Validado | Criterio de Aceptación | Estado |
|---|---|---|---|---|
| **Test RAG 1** | *"Capacidad y tipo de aceite para Fiat Palio 1.3 con cambio de filtro"* | `consulta_manual_tecnico` | Cita exacta: 2.7L (3.0L con filtro) o 3.5L según versión, viscosidad 10W-40, Fuente `ficha_tecnica_fiat_palio.pdf`. | ✅ Aprobado |
| **Test RAG 2** | *"Diagnóstico de alza vidrios eléctrico Changan CX70"* | `consulta_manual_tecnico` | Pasos ordenados: fusibles 20A/30A, conector de botonera y motor 12V. Fuente `manual_fallas_multimarca_diagnostico.pdf`. | ✅ Aprobado |
| **Test Stock** | *"Botonera alza vidrios Changan CX70 en bodega"* | `consultar_inventario_repuestos` | Producto encontrado: Stock 4 un, Precio $34.990 CLP, Ubicación `Pasillo D - Estante 2`. | ✅ Aprobado |
| **Test Memoria** | *"¿Tienen en stock los repuestos para ese mismo auto?"* | `AutoTechSessionMemory` | Identifica "Fiat Palio" sin que el usuario lo vuelva a nombrar en el segundo turno. | ✅ Aprobado |
| **Test Planificación** | *"Recepcionar Palio con chillido en frenos y nivel bajo de lubricante"* | `generar_plan_taller` | Clasifica con Prioridad ALTA en Paso 1 al sistema de frenos por seguridad vial. | ✅ Aprobado |
| **Test Persistencia** | *"Registrar orden para María Fernández, cambio de pastillas y aceite"* | `registrar_orden_reparacion` | Archivo `ordenes_trabajo_autotech.json` actualizado con ID único, mano de obra calculada y total CLP. | ✅ Aprobado |
| **Test No-Duplicación**| Re-emisión de orden complementando datos del cliente | `_guardar_orden_local` | Actualiza la orden existente mediante `id_orden_existente` sin crear duplicados huérfanos. | ✅ Aprobado |

---

## 11. Referencias Bibliográficas (Formato APA 7ma Edición)

* Chase, H. (2023). *LangChain: Building applications with LLMs through composability*. LangChain Inc. https://github.com/langchain-ai/langchain
* Douze, M., Guzhva, A., Deng, C., Johnson, J., Szilvasy, G., Mazaré, P. E., Lomeli, M., Lucas, H., & Jégou, H. (2024). *The Faiss library*. IEEE Transactions on Pattern Analysis and Machine Intelligence. https://github.com/facebookresearch/faiss
* Groq Inc. (2024). *Groq LPU Inference Engine: Deterministic, Ultra-Low Latency LLM Serving*. Groq Cloud Documentation. https://console.groq.com/docs
* Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 9459–9474.
* Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP 2019), 3982–3992. https://doi.org/10.18653/v1/D19-1410
* Streamlit Inc. (2024). *Streamlit: The fastest way to build and share data apps*. Snowflake Inc. https://docs.streamlit.io
* Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models*. International Conference on Learning Representations (ICLR 2023). https://arxiv.org/abs/2210.03629
```
