# AutoTech JPB Solutions - Copiloto RAG Multimarca & Agente de Inventario 🚗

[![Duoc UC](https://img.shields.io/badge/Duoc_UC-ISY0101-blue.svg)](https://www.duoc.cl)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io)
[![Groq API](https://img.shields.io/badge/LLM-Groq_API-f60.svg)](https://groq.com)
[![FAISS](https://img.shields.io/badge/VectorStore-FAISS-green.svg)](https://github.com/facebookresearch/faiss)

---
> **Institución:** Duoc UC  
> **Integrantes del Equipo:** Paolo Jorquera, Benjamín Arriaza y José Castillo  
---

##  Tabla de Contenidos
- [1. Descripción del Proyecto](#1-descripción-del-proyecto)
- [2. Cuellos de Botella Organizacionales y Solución](#2-cuellos-de-botella-organizacionales-y-solución)
- [3. Características Clave](#3-características-clave)
- [4. Manuales Técnicos Indexados en RAG](#5-manuales-técnicos-indexados-en-rag)
- [5. Estructura del Proyecto](#6-estructura-del-proyecto)
- [6. Guía de Ejecución en Google Colab](#7-guía-de-ejecución-en-google-colab)
- [7. Guía de Ejecución en Entorno Local](#8-guía-de-ejecución-en-entorno-local)
- [8. Batería de Pruebas y Resultados](#9-batería-de-pruebas-y-resultados)

---

## 1. Descripción del Proyecto

**AutoTech JPB Solutions** es un centro de servicio técnico automotriz especializado en mantenimiento preventivo y correctivo, diagnóstico electrónico multimarca, atención al cliente en recepción e importación de repuestos.

Para optimizar la operación y reducir tiempos de respuesta, se desarrolló **AutoTech Copilot**: un asistente virtual inteligente impulsado por modelos de lenguaje (LLM vía Groq API) con integración de **Retrieval-Augmented Generation (RAG)** sobre 5 manuales de taller PDF y un **Agente con Tool Calling** (`consultar_inventario`) para consultar disponibilidad y precios de bodega en tiempo real.

---

## 2. Cuellos de Botella Organizacionales y Solución

| Cuello de Botella en Taller | Solución con AutoTech Copilot |
|---|---|
| **Alta latencia (15-25 min)** buscando datos técnicos (torques, viscosidades PSI, diagramas). | **Búsqueda Semántica Vectorial (RAG):** Respuesta inmediata citing documento y página exacta (`[Fuente: manual..., Pág. X]`). |
| **Brecha recepción/mecánico:** Síntomas informales del cliente ("limpiavidrios raya", "ruido al frenar"). | **System Prompt con Guardrails:** Traducción automática de quejas de clientes a listas de comprobación paso a paso. |
| **Desconexión con Bodega:** Consultas manuales para cotizar precios y verificar stock de repuestos. | **Agente de Inventario (Tool Calling):** Invocación en tiempo real de `consultar_inventario` con stock, precio CLP y pasillo. |

---

## 3. Características Clave

-  **RAG Multimarca sobre 5 Manuales PDF:** Indexación semántica usando `SentenceTransformers` (`all-MiniLM-L6-v2`) y `FAISS`.
-  **Agente con Tool Calling (`consultar_inventario`):** Permite al LLM consultar stock general, categorías o repuestos específicos en CLP y su ubicación física.
-  **Caché Persistente en Disco (< 0.1s de Carga):** Almacenamiento optimizado `.pkl` que elimina la re-indexación de PDFs en cada inicio.
-   **Integración Automática con Google Drive:** Auto-descarga desde enlaces públicos de Google Drive (`gdown`) o desde la carpeta montada en `/content/drive/MyDrive/AutoTech_Manuales`.
-  **Interfaz Conversacional Cyber-Glow en Streamlit:** UI animada con diseño moderno, badges de herramientas y detalles expandibles de fuentes.
-  **Fallback de Modelos en Groq API:** Soporte resiliente con cambio automático entre `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, y otros.

---

## 4. Manuales Técnicos Indexados en RAG

1.  `ficha_tecnica_fiat_palio.pdf`: Especificaciones exactas de motor FIRE 1.3, torques de apriete, viscosidades y capacidades de lubricantes.
2.  `MANUAL-DE-OPERACIONES-DE-TALLER-.pdf`: Listas de comprobación paso a paso para frenos, batería, inyectores y DPF.
3.  `manual_fallas_multimarca_diagnostico.pdf`: Diagnóstico de luces del tablero (Check Engine, Aceite, Batería) y guía eléctrica de alza vidrios para Changan CX70 y SUVs.
4.  `manual_recepcion_fallas_cliente_taller.pdf`: Guía de recepción cliente/mecánico, procedimiento de cambio de plumillas y tabla de rangos PSI de inflado de ruedas.
5.  `mecanica-automotriz-mantenimiento-de-motores.pdf`: Libro de texto con teoría y fundamentos de mantenimiento de motores automotrices.

---

## 5. Estructura del Proyecto

```text
autotech/
├── README.md                                 # Documentación principal del proyecto
├── informe_tecnico_autotech.md               # Informe técnico académico completo
├── AutoTech_Copilot_Colab.ipynb              # Notebook optimizado para Google Colab
├── archivos necesarios/                      # Módulo distribuible de la aplicación
│   ├── app.py                                # Interfaz gráfica web Streamlit Cyber-Glow
│   ├── rag_engine.py                         # Motor RAG, FAISS VectorStore y Agente Groq
│   ├── test_suite.py                         # Batería de pruebas automatizadas
│   ├── autotech_vector_cache.pkl             # Caché persistente vectorial (<0.1s de inicio)
│   ├── AutoTech_Copilot_Colab.ipynb          # Copia distribuible del notebook
│   └── *.pdf                                 # Los 5 manuales de taller PDF
└── AutoTech_Manuales/                        # Directorio alternativo de manuales local
```

---

## 6. Guía de Ejecución en Google Colab

### Paso 1: Abrir el Notebook en Colab
Abre [`AutoTech.ipynb`](./AutoTech.ipynb) directamente en [Google Colab](https://colab.research.google.com).

### Paso 2: Configurar la API Key de Groq
1. En el panel izquierdo de Colab, haz clic en el ícono de **Llave (Secretos / Secrets)**.
2. Agrega un nuevo secreto con el nombre `LLM_API_KEY`.
3. Pega tu API Key de Groq (la obtienes gratis en [console.groq.com](https://console.groq.com)).

### Paso 3: Ejecutar las Celdas
1. Ejecuta la **Celda 1** para instalar las librerías (`openai`, `faiss-cpu`, `sentence-transformers`, `streamlit`, `gdown`).
2. Ejecuta la **Celda 2 y 3** para descargar automáticamente los manuales PDF e inicializar los archivos.
3. Ejecuta la **Celda 4** para verificar que `LLM_API_KEY` se cargó con éxito.
4. Ejecuta la **Celda 5** para correr la batería de pruebas automatizadas (`test_suite.py`).
5. Ejecuta la **Celda 6** para iniciar Streamlit con el túnel público de Cloudflare y haz clic en el enlace `.trycloudflare.com` generado.

---

## 8. Guía de Ejecución en Entorno Local

### Requisitos Previos
- Python 3.10 o superior.
- Git (opcional para clonar el repositorio).

### Instalación y Configuración

```bash
# 1. Clonar o descargar el proyecto
git clone https://github.com/TU_USUARIO/autotech.git
cd autotech

# 2. Crear entorno virtual (Recomendado)
python -m venv venv
# En Windows PowerShell:
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install openai pypdf sentence-transformers faiss-cpu streamlit reportlab gdown

# 4. Configurar la API Key de Groq en PowerShell
$env:LLM_API_KEY="tu_api_key_de_groq"

# 5. Ejecutar la batería de pruebas
python test_suite.py

# 6. Iniciar la interfaz conversacional de Streamlit
streamlit run app.py
```
Abre tu navegador en `http://localhost:8501`.

---

## 9. Batería de Pruebas y Resultados

La batería de pruebas automatizadas (`test_suite.py`) verifica el correcto funcionamiento del pipeline RAG y del Agente con Tool Calling:

| ID | Consulta de Prueba | Módulo Utilizado | Resultado Esperado | Estado |
|---|---|---|---|---|
| **P1** | Torque de apriete tapón de cárter Fiat Palio 1.3 | RAG (`ficha_tecnica_fiat_palio.pdf`) | 20 Nm (Tapón) / 12 Nm (Filtro) + Cita Pág. 1 | ✅ PASADO |
| **P2** | Falla alza vidrios Changan CX70 diagnóstico | RAG (`manual_fallas_multimarca_diagnostico.pdf`) | Pasos 1, 2 y 3 (Fusibles 20A/30A, Botonera, Motor 12V) + Cita Pág. 2 | ✅ PASADO |
| **P3** | Cambio de plumillas limpiavidrios y medidas | RAG (`manual_recepcion_fallas_cliente_taller.pdf`) | Clip U-Hook, medidas 18"/20"/22", prueba de agua | ✅ PASADO |
| **P4** | Rangos recomendados para inflar ruedas PSI | RAG (`manual_recepcion_fallas_cliente_taller.pdf`) | Tabla PSI (Hatchback 28-30, Sedán 30-32, SUV 32-35, Camionetas 35-45) | ✅ PASADO |
| **P5** | ¿Qué repuestos tenemos en stock en bodega? | Tool (`consultar_inventario`) | Listado por categorías (Lubricantes, Frenos, Limpiaparabrisas, Eléctrico, etc.) | ✅ PASADO |
| **P6** | Botonera alza vidrios Changan CX70 stock/precio | Tool (`consultar_inventario`) | Stock: 4 un. \| Precio: $29.990 CLP \| Ubicación: Pasillo D - Estante 2 | ✅ PASADO |

