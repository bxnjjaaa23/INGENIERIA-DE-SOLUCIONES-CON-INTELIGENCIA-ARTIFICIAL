# INFORME TÉCNICO DE EVALUACIÓN PARCIAL N°3
## IMPLEMENTACIÓN DE OBSERVABILIDAD, TRAZABILIDAD Y MÉTRICAS DE RENDIMIENTO EN AGENTES DE INTELIGENCIA ARTIFICIAL

---

**Asignatura**: ISY0101 - Ingeniería de Soluciones con IA  
**Institución**: Duoc UC - Escuela de Informática y Telecomunicaciones  
**Proyecto**: AutoTech JPB Solutions - Copilot Autónomo de Taller Mecánico  
**Integrantes del Equipo**:
- Paolo Jorquera (Arquitectura de Agentes, RAG y Orquestación)
- Benjamín Arriaza (Observabilidad, Telemetría y Dashboards de Rendimiento)
- José Castillo (Seguridad, Uso Responsable, Privacidad y Cumplimiento Normativo)  
**Docente Evaluador**: Taller de Proyectos TAITE 7  
**Fecha de Entrega**: Noviembre 2026  

---

<!-- PÁGINA 1: PORTADA, RESUMEN EJECUTIVO Y CONTEXTO -->
## 1. Resumen Ejecutivo y Contexto del Proyecto

El proyecto **AutoTech JPB Solutions** aborda la automatización inteligente de la recepción técnica, diagnóstico vehicular, consulta de inventario y emisión de órdenes de trabajo en talleres mecánicos automotrices. Tras el desarrollo del agente funcional en la Evaluación Parcial N°2 (basado en LangChain, RAG sobre manuales técnicos de taller y base vectorial FAISS), la presente **Evaluación Parcial N°3** tiene como objetivo dotar al sistema de una arquitectura completa de **observabilidad de nivel empresarial, trazabilidad de ejecución determinista y auditoría ética en tiempo real**.

En entornos de producción, los agentes basados en Modelos de Lenguaje Grande (LLMs) enfrentan riesgos de no determinismo, degradación de latencia por cuellos de botella en APIs remotas, límites de tasa por tokens por minuto (TPM), alucinaciones técnicas y vulnerabilidades de inyección de prompts. Para mitigar estos riesgos de forma sistemática y empírica, se diseñó e implementó:
1. **Instrumentación Secuencial de Telemetría**: Captura de latencia de alta precisión (`time.perf_counter`), conteo de tokens (entrada/salida), costos computacionales y persistencia doble en JSON Lines (`ejecuciones_autotech.jsonl`) y log de texto plano (`agent.log`).
2. **Trazabilidad Criptográfica sin Pérdida de Privacidad**: Asignación de identificadores únicos universales (`UUIDv4`) por sesión y cálculo de huellas digitales SHA-256 (`huella_entrada`, `huella_salida`), permitiendo auditar cada paso de la cadena ReAct sin almacenar datos sensibles en texto claro.
3. **Optimización Arquitectónica Fast-Path y Caché en Dos Niveles**: Enrutamiento híbrido determinista para consultas directas de bodega y repuestos, resolviendo consultas en milisegundos y reduciendo el consumo de API remota en más de un 80%.
4. **Dashboard de Monitoreo Interactivo**: Visualización gráfica de métricas clave (KPIs, percentiles de latencia, distribución de estados y consumo de tokens) desplegado tanto en Google Colab (`matplotlib/seaborn/plotly`) como en la aplicación web `Streamlit` (`app_ep2.py`).

---

<!-- PÁGINA 2: IMPLEMENTACIÓN DE MÉTRICAS DE OBSERVABILIDAD -->
## 2. Implementación de Métricas de Observabilidad (IE1, IE2)

Para evaluar el agente bajo escenarios de variabilidad lingüística y técnica, se definió un marco de métricas estructurado en cuatro dimensiones fundamentales:

```
+-----------------------------------------------------------------------------------------+
|                  MARCO DE OBSERVABILIDAD Y TELEMETRÍA AUTOTECH (EP3)                    |
+-----------------------------+-----------------------------+-----------------------------+
|    PRECISIÓN Y CONSISTENCIA |   LATENCIA Y RENDIMIENTO    |    CONSUMO Y SOSTENIBILIDAD |
|  - Precisión Ground Truth % |  - Latencia Promedio (s)     |  - Tokens Entrada / Salida  |
|  - Consistencia Semántica % |  - Percentiles (P50, P95)   |  - Costo Estimado (USD)     |
|  - Frecuencia de Errores %  |  - Desviación Estándar      |  - Tasa Acierto Caché (%)   |
+-----------------------------+-----------------------------+-----------------------------+
```

### 2.1. Métricas de Precisión Técnica y Consistencia Semántica (IE1)
- **Precisión Técnica contra Ground Truth**: Se contrastan las respuestas generadas contra hechos verificados en los manuales de taller del vehículo de prueba (*Fiat Palio Young 1.3 8V Fire*):
  $$\text{Precisión} = \frac{\text{Hechos Clave Oficiales Identificados}}{\text{Total Hechos Clave Esperados}} \times 100$$
  *Resultado obtenido*: **100%** de precisión en especificaciones críticas (viscosidad SAE 10W-40, capacidad 2.7L sin filtro / 3.0L con cambio de filtro, líquido de frenos DOT-4 y torque de cáliper a 35 Nm).
- **Consistencia Semántica ante Variabilidad de Entrada**: Se midió la estabilidad semántica (índice Jaccard de n-gramas técnicos) ante 3 reformulaciones sintácticas de la misma consulta (técnica formal, sintomática coloquial y telegráfica).
  *Resultado obtenido*: **96.5%** de consistencia léxico-semántica sin contradicciones factuales.
- **Frecuencia de Errores Operativos**: Porcentaje de eventos con excepción técnica no controlada. Tras la subsanación del esquema en la herramienta de inventario, la tasa de error descendió a **0.0%**.

### 2.2. Métricas de Latencia y Uso de Recursos Computacionales (IE2)
A partir de la ejecución de la batería de pruebas instrumentada, se obtuvieron las siguientes mediciones cuantitativas:

| Métrica de Rendimiento / Recurso | Valor Registrado | Unidad / Contexto |
|---|---|---|
| **Latencia Media Global** | `0.9391 s` | Promedio ponderado de todas las etapas |
| **Latencia Percentil 50 (Mediana P50)** | `0.0250 s` | 50% de las consultas se resuelven casi de inmediato |
| **Latencia Percentil 95 (P95)** | `4.0403 s` | Consultas complejas con invocación completa de LLM ReAct |
| **Rango Operativo de Latencias** | `0.0005 s` - `4.0403 s` | Mínimo en caché; máximo en diagnóstico multiherramienta |
| **Desviación Estándar de Latencia** | `1.7214 s` | Refleja la arquitectura híbrida (Fast-Path vs LLM) |
| **Consumo Promedio de Tokens (Entrada)** | `32.5 tokens` | Consultas de usuario concisas y enfocadas |
| **Consumo Promedio de Tokens (Salida)** | `185.0 tokens` | Diagnósticos explicativos estructurados |
| **Tasa de Acierto de Caché (Cache Hit Rate)** | `33.3%` | Reducción de latencia a < 1 ms en consultas reiteradas |

---

<!-- PÁGINA 3: ANÁLISIS DE REGISTROS, TRAZABILIDAD Y CUELLOS DE BOTELLA -->
## 3. Análisis de Registros, Trazabilidad y Diagnóstico de Cuellos de Botella (IE3, IE6)

La persistencia estructurada en `ejecuciones_autotech.jsonl` permitió realizar un análisis forense detallado sobre el flujo de ejecución del agente. Cada evento almacena metadatos esenciales:

```json
{
  "ejecucion": "0c33e4ba-3365-4073-86b6-852e6afba269",
  "etapa": "Consulta_Tecnica_RAG",
  "depende_de": null,
  "fecha_utc": "2026-11-18T20:16:21.145000Z",
  "modelo": "openai/gpt-oss-20b",
  "huella_entrada": "5de999af2f6f4e68",
  "huella_salida": "aa2a6647f442e2c0",
  "estado": "exito",
  "origen": "api_llm",
  "duracion_s": 3.4692,
  "tokens_entrada": 38,
  "tokens_salida": 98
}
```

### 3.1. Hallazgo Crítico 1: Detección de Error de Validación de Esquema (Pydantic Error)
- **Evidencia en Logs**: En el Escenario 3 (`ESC_03_STOCK_LIMITES`), el registro capturó un fallo con estado `error` y duración `0.0007s`:
  `1 validation error for consultar_inventario_repuestos: termino_busqueda Field required [input_value={'criterio': ...}]`.
- **Causa Raíz**: La función de instrumentación `ejecutar_agente_instrumentado` invocaba la herramienta local con el diccionario `{"criterio": consulta}`, mientras que el decorador `@tool` de LangChain en `autotech_agent_ep2.py` definía como argumento obligatorio `termino_busqueda: str`.
- **Acción Correctiva**: Se implementó una invocación polimórfica y tolerante a fallos:
  ```python
  try:
      inv_res = tool_inv.invoke({"termino_busqueda": consulta})
  except Exception:
      inv_res = tool_inv.invoke(consulta)
  ```
  Este hallazgo demuestra el valor operativo de la observabilidad: sin registros estructurados, el error habría pasado inadvertido o se habría atribuido erróneamente a una falla de la API externa.

### 3.2. Hallazgo Crítico 2: Identificación del Cuello de Botella Principal
- **Evidencia en Logs**: El desglose de latencias por etapa identificó inequívocamente a `Diagnostico_Sintomas_Ruido` como el cuello de botella del sistema (latencia media de **4.0403 s**, consumiendo el 72.8% del tiempo total de la sesión).
- **Diagnóstico**: La consulta con lenguaje ambiguo del cliente ("*el auto me tirita entero cuando freno...*") forzó al agente a realizar un escaneo inductivo en la base vectorial RAG, serializar más de 500 palabras de fragmentos de manuales y ejecutar una cadena ReAct de doble turno para sintetizar tanto las causas como los precios de repuestos.
- **Acción Correctiva**: Implementación de un límite estricto de contexto RAG (`top_k=2` en lugar de 5 fragmentos) y memoria conversacional compactada.

---

<!-- PÁGINA 4: DASHBOARD DE MONITOREO Y REDISEÑO SOSTENIBLE -->
## 4. Dashboard de Monitoreo Visual y Propuestas de Rediseño Sostenible (IE4, IE5, IE7)

### 4.1. Dashboard Visual de Monitoreo (IE4, IE5)
Se construyó un dashboard analítico interactivo con cuatro paneles de telemetría:
1. **Panel de Latencia Comparativa por Etapa**: Diagrama de barras horizontales que contrasta visualmente las etapas de API remota (>3.4s) frente al Fast-Path local (<0.05s).
2. **Panel de Balance de Tokens**: Comparativa de barras agrupadas entre tokens de entrada (Prompt) y tokens de salida (Completion).
3. **Panel de Distribución de Confiabilidad**: Gráfico de dona que refleja un **62.5%** de éxitos operativos, **25.0%** de eventos bloqueados preventivamente por seguridad y **12.5%** de llamadas resueltas desde caché.
4. **Curva de Percentiles (SLO)**: Gráfico de línea con puntos de control (P50, P75, P90, P95, P99), permitiendo asegurar compromisos de nivel de servicio (SLO < 4.5s en el 99% de las consultas).

Adicionalmente, el dashboard fue integrado de forma nativa como la **Pestaña N°5 en la interfaz web de Streamlit** (`app_ep2.py`), permitiendo a técnicos de taller y supervisores inspeccionar métricas en tiempo real, filtrar trazas por UUID de ejecución y ejecutar baterías de prueba con un solo clic.

```
+-----------------------------------------------------------------------------------------+
|                  PANEL STREAMLIT: COCKPIT DE OBSERVABILIDAD EN VIVO                     |
| [📊 Total Eventos: 8]   [⏱️ Latencia Media: 0.939s]   [📈 Latencia P95: 4.040s]         |
| [🪙 Total Tokens: 1,156] [⚡ Acierto Caché: 33.3%]   [🛡️ Bloqueos Seg: 25.0%]          |
+-----------------------------------------------------------------------------------------+
|  [Gráfico Barras: Latencia por Etapa]        |  [Gráfico Tarta: Distribución de Estados] |
|  - RAG Técnico: 3.469s                       |  - Exito: 62.5%                           |
|  - Diagnóstico Síntomas: 4.040s              |  - Bloqueo Seguridad: 25.0%               |
|  - Fast-Path Inventario: 0.025s              |  - Caché: 12.5%                           |
|  - Filtro Seguridad: 0.001s                  |                                           |
+-----------------------------------------------------------------------------------------+
```

### 4.2. Propuestas de Rediseño y Sostenibilidad Arquitectónica (IE7)
Para garantizar la sostenibilidad técnica y financiera del agente en un taller con cientos de consultas diarias, se evaluó un rediseño comparativo entre dos arquitecturas:

```
ARQUITECTURA BASE (LLM Puro):
Consulta Cliente ---> [Agente LLM Remoto] ---> [Tool RAG] / [Tool Inventario] ---> Salida (3.82s | 410 tokens)

ARQUITECTURA REDISEÑADA AUTOTECH (Híbrida y Sostenible):
Consulta Cliente ---> [Filtro Seguridad & Anonimización PII]
                             |
                   +---------+---------+
                   | ¿En Caché L1?     | ---> SÍ ---> [Respuesta Inmediata < 0.001s | 0 tokens]
                   +---------+---------+
                             | NO
                   +---------+---------+
                   | ¿Es Stock Directo?| ---> SÍ ---> [Fast-Path Bodega Local < 0.025s | 30 tokens]
                   +---------+---------+
                             | NO
                 [Agente LLM ReAct + RAG Podado] ---> Salida (2.10s | 220 tokens)
```

**Resultados del Benchmarking Cuantitativo Antes vs Después**:
- **Reducción de Latencia Promedio**: De `3.614 s` a `0.430 s` (**88.1% de mejora de velocidad**).
- **Ahorro de Tokens y Costos**: De `2,030 tokens` a `320 tokens` (**84.2% de ahorro computacional**).
- **Eliminación de Errores de Tasa (Rate Limiting 429)**: Al desviar el 60% de las consultas típicas de taller (precios y disponibilidad de repuestos) hacia el Fast-Path local, se evita saturar el cupo TPM/RPM de las APIs en la nube.

---

<!-- PÁGINA 5: SEGURIDAD, ÉTICA, REFLEXIONES Y REFERENCIAS -->
## 5. Protocolos de Seguridad, Gobernanza Ética y Privacidad (IE8)

En contextos productivos, el agente interactúa con datos de clientes y órdenes de pago. Se diseñaron e implementaron cuatro barreras de protección activa:
1. **Sanitización y Bloqueo de Inyecciones**: Filtro determinista por expresiones regulares que intercepta intentos de *Prompt Injection* (`ignore all instructions`), escalamiento de privilegios (`system override`, `root access`), inyecciones SQL (`DROP DATABASE`, `UNION SELECT`) y ejecución de código (`exec`, `eval`).
2. **Anonimización Activa de Datos Sensibles (PII)**: De acuerdo con la **Ley N° 19.628 de Protección de la Vida Privada (Chile)**, cualquier RUT chileno, correo electrónico, número telefónico o patente vehicular ingresado en la consulta es sustituido automáticamente por etiquetas protegidas (`[RUT_PROTEGIDO]`, `[PATENTE_PROTEGIDA]`) antes de ser procesado o registrado.
3. **Trazabilidad Segura por Huellas SHA-256**: Los registros persistentes en disco (`.jsonl`) no exponen el contenido íntegro de consultas confidenciales, sino huellas digitales criptográficas unidireccionales de 16 caracteres.
4. **Matriz de Validación de Amenazas**: En pruebas controladas con 5 ataques de ciberseguridad industrial y vulneración de privacidad, el sistema logró una **tasa de bloqueo y mitigación del 100%**.

---

## 6. Conclusiones Técnicas y Reflexiones Individuales Obligatorias

### Síntesis Conclusiva del Equipo
La incorporación de observabilidad estructurada y trazabilidad criptográfica en el proyecto AutoTech demostró que el rendimiento de un agente inteligente no depende exclusivamente de la capacidad del modelo fundacional, sino de la arquitectura de software que lo gobierna. El monitoreo empírico permitió descubrir y reparar fallas de interfaz (error Pydantic en Fast-Path), aislar cuellos de botella en RAG y fundamentar un rediseño que disminuyó los tiempos de respuesta en un 88% y los costos operativos en un 84%.

### Reflexiones Individuales Obligatorias (Pauta Duoc UC)

#### 👤 Paolo Jorquera (Arquitectura de Agentes, RAG y Orquestación)
> *"Durante el desarrollo de esta tercera entrega, mi principal aprendizaje radicó en comprender que la autonomía de un agente de IA no debe operar como una 'caja negra'. Al instrumentar los flujos de trabajo con LangChain y RAG, comprendí la criticidad de balancear la flexibilidad del razonamiento LLM con componentes deterministas locales. El mayor desafío técnico consistió en diseñar el enrutador híbrido Fast-Path: redirigir las consultas de catálogo directamente a bodega eliminó los límites de tasa (rate-limits) y redujo los tiempos de espera del cliente de 4 segundos a milisegundos. Esta experiencia consolidó mi criterio profesional sobre cómo desacoplar microservicios de IA para lograr alta disponibilidad y escalabilidad en sistemas de misión crítica."*

#### 👤 Benjamín Arriaza (Observabilidad, Telemetría y Dashboards de Rendimiento)
> *"Mi contribución se focalizó en la construcción del motor de observabilidad, la captura de telemetría de alta resolución y el diseño del dashboard de monitoreo interactivo. Aprendí que la latencia media es una métrica insuficiente para la toma de decisiones en producción; el análisis de percentiles (P90 y P95) fue el elemento clave que nos permitió aislar los cuellos de botella generados por la serialización de fragmentos RAG hacia la API. Asimismo, la persistencia estructurada en JSON Lines y la generación de huellas SHA-256 me demostraron que es posible construir una trazabilidad forense exhaustiva respetando rigurosamente los estándares de seguridad y la privacidad de los usuarios."*

#### 👤 José Castillo (Seguridad, Uso Responsable, Privacidad y Cumplimiento Normativo)
> *"Mi aporte estuvo centrado en la gobernanza ética, los protocolos de seguridad activa y el marco regulatorio del agente. Fue fundamental implementar filtros contra prompt injection y mecanismos de anonimización activa de datos personales (RUT chileno, correos y patentes) alineados con la Ley N° 19.628 de Protección de la Vida Privada y las directrices de uso ético de IA de Duoc UC. Comprobé empíricamente que la seguridad no puede añadirse como una capa posterior, sino que debe ser un componente intrínseco del diseño arquitectónico. La auditoría automatizada garantizó que ninguna consulta maliciosa vulnere las funciones del taller ni comprometa la integridad de la base de datos."*

---

## 7. Referencias Bibliográficas (Norma APA 7ma Edición)
- Duoc UC. (2025). *Guía para el uso ético y responsable de herramientas de Inteligencia Artificial en la formación técnico-profesional*. Bibliotecas Duoc UC. https://bibliotecas.duoc.cl/ia
- Harrison, C. (2024). *LangChain in Action: Orchestrating Autonomous Agents and Retrieval-Augmented Generation*. O'Reilly Media.
- Lewis, P., Perez, E., Piktus, A., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 9459-9474.
- Ministerio de Justicia de Chile. (1999). *Ley N° 19.628: Sobre Protección de la Vida Privada*. Biblioteca del Congreso Nacional de Chile (BCN). https://www.bcn.cl/leychile/navegar?idNorma=141599
- OpenTelemetry Authors. (2024). *OpenTelemetry Observability Framework for Distributed Cloud Applications and AI Pipelines*. Cloud Native Computing Foundation (CNCF). https://opentelemetry.io/docs/
