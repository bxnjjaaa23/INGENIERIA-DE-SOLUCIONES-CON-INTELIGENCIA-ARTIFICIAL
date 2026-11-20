# GUIÓN DE PRESENTACIÓN Y DEFENSA ORAL - EVALUACIÓN PARCIAL N°3
## SISTEMA DE OBSERVABILIDAD, TELEMETRÍA Y SEGURIDAD EN AGENTES DE IA (AUTOTECH)

> **Asignatura**: ISY0101 - Ingeniería de Soluciones con IA  
> **Formato**: 20 Minutos (10 minutos de exposición + 10 minutos de ronda de preguntas del docente)  
> **Integrantes**: Paolo Jorquera, Benjamín Arriaza y José Castillo  
> **Apoyo Visual**: Dashboard interactivo en Streamlit (`app_ep2.py` - Tab 5) y gráficos del Colab (`dashboard_autotech_ep3.png`).

---

## ESTRUCTURA DE LA EXPOSICIÓN (10 MINUTOS)

```
[00:00 - 02:00] INTRODUCCIÓN Y ARQUITECTURA (Paolo Jorquera)
[02:00 - 05:00] TELEMETRÍA, LOGS FORENSES Y HALLAZGOS CRÍTICOS (Benjamín Arriaza)
[05:00 - 07:30] REDISEÑO, BENCHMARKING Y ESCALABILIDAD SOSTENIBLE (Paolo Jorquera)
[07:30 - 10:00] SEGURIDAD ACTIVA, PRIVACIDAD LEY 19.628 Y ÉTICA (José Castillo)
[10:00 - 20:00] RONDA DE PREGUNTAS Y DEFENSA TÉCNICA (Todo el equipo)
```

---

### MINUTO 00:00 - 02:00: INTRODUCCIÓN Y CONTEXTO OPERATIVO
**Orador: Paolo Jorquera**
> *"Buenas tardes profesor. Hoy junto a Benjamín Arriaza y José Castillo presentamos la Evaluación Parcial N°3 de Ingeniería de Soluciones con IA. En la etapa anterior construimos un agente autónomo para el taller mecánico AutoTech JPB Solutions, capaz de diagnosticar fallas y emitir órdenes de trabajo mediante RAG y LangChain.*  
> *Sin embargo, llevar un agente de IA a producción real exige superar el problema de la 'caja negra'. Un taller no puede tolerar latencias impredecibles de 8 segundos mientras un cliente espera en recepción, ni errores de límite de tokens (TPM) en horas punta, ni fallas silenciosas en la recuperación de especificaciones técnicas. Para resolver esto, implementamos una arquitectura integral de observabilidad estructurada, trazabilidad criptográfica y rediseño sostenible basado en evidencia empírica."*

---

### MINUTO 02:00 - 05:00: ANÁLISIS CRÍTICO DE EJECUCIÓN Y HALLAZGOS EN LOGS (IE6, IE9)
**Orador: Benjamín Arriaza** *(Proyectando el Dashboard de Streamlit o los gráficos de Colab)*
> *"Para medir objetivamente el comportamiento del agente, instrumentamos el ciclo de ejecución en dos capas de persistencia: `ejecuciones_autotech.jsonl` y `agent.log`. Asignamos un UUID universal a cada sesión y calculamos huellas SHA-256 para entrada y salida. Evaluamos cuatro escenarios con variabilidad técnica y sintomática.*  
> *El examen forense de los registros reveló dos hallazgos críticos:*  
> *1. **Detección y Corrección de un Error de Esquema Pydantic**: En la etapa `Consulta_Inventario_Limites`, el sistema registró un fallo en 0.0007 segundos. La traza nos mostró que la función de instrumentación enviaba la clave `'criterio'`, mientras que la herramienta esperaba `'termino_busqueda'`. Gracias a la observabilidad estructurada, identificamos el error de interfaz inmediatamente y aplicamos una invocación polimórfica que redujo la tasa de error al 0.0%.*  
> *2. **Aislamiento del Cuello de Botella Principal**: Al analizar la distribución de latencias, observamos que el Percentil 95 (P95) alcanzaba **4.0403 segundos**, concentrado en la etapa `Diagnostico_Sintomas_Ruido`. Descubrimos que las consultas informales provocaban cadenas ReAct redundantes con más de 700 tokens de salida, mientras que el 60% de las consultas de un taller son simples verificaciones de stock que no requieren inferencia remota."*

---

### MINUTO 05:00 - 07:30: PROPUESTA DE REDISEÑO Y ESCALABILIDAD SOSTENIBLE (IE7, IE9)
**Orador: Paolo Jorquera**
> *"Frente al cuello de botella diagnosticado por Benjamín, propusimos un rediseño arquitectónico fundamentado en tres pilares de sostenibilidad:*  
> *1. **Patrón de Enrutamiento Híbrido (Fast-Path Local)**: Desviamos determinísticamente las consultas de inventario directo hacia la bodega local sin tocar la API del LLM, resolviendo la solicitud en apenas **0.025 segundos**.*  
> *2. **Caché Jerárquica en Dos Niveles (L1 en RAM + L2 Vectorial)**: Las consultas recurrentes se sirven en **0.0006 segundos** con cero consumo de tokens.*  
> *3. **Poda de Contexto RAG**: Redujimos los fragmentos devueltos por FAISS de 5 a los 2 más pertinentes, acotando el prompt a 200 tokens.*  
> *Ejecutamos un benchmark formal comparativo entre la arquitectura base y la optimizada:*  
> *- La **latencia promedio cayó de 3.61 segundos a 0.43 segundos**, representando una **mejora de velocidad del 88.1%**.*  
> *- El **consumo de tokens se redujo de 2,030 a 320 tokens**, logrando un **ahorro de costos del 84.2%** y garantizando un 0% de errores por cuotas de rate-limiting (TPM/RPM)."*

---

### MINUTO 07:30 - 10:00: DEFENSA DE CRITERIOS ÉTICOS, SEGURIDAD Y PRIVACIDAD (IE8, IE9)
**Orador: José Castillo**
> *"Finalmente, abordamos la seguridad y el uso responsable en un entorno productivo de taller automotriz. Un agente conectado a internet y a bases de datos puede ser blanco de inyecciones o vulnerar la confidencialidad de los clientes.*  
> *Implementamos un protocolo de cuatro barreras alineado con la **Ley N° 19.628 de Protección de la Vida Privada de Chile** y las directrices éticas de Duoc UC:*  
> *1. **Filtro Determinista Multi-Patrón**: Neutralizamos en 0.001 segundos intentos de Prompt Injection (`ignore all instructions`), sobreescritura de sistema (`system override`) e inyecciones SQL destructivas.*  
> *2. **Anonimización Activa de Datos Personales (PII)**: El motor detecta expresiones regulares de RUT chileno, correos electrónicos, teléfonos celulares y patentes vehiculares, sustituyéndolos por tokens enmascarados antes de enviarlos al modelo o guardarlos en disco.*  
> *3. **Trazabilidad Criptográfica Inmutable**: El archivo `.jsonl` no persiste datos en texto claro, sino huellas unidireccionales SHA-256 de 16 caracteres. Si un tercero accede a los logs del servidor, no puede reconstruir los datos privados de los clientes.*  
> *En la matriz de auditoría automatizada con 5 vectores de ciberataque, obtuvimos un **100% de efectividad de bloqueo y protección**, demostrando que la solución cumple con los más altos estándares normativos y de gobernanza de IA. Quedamos a su disposición para la ronda de preguntas."*

---

## BANCO DE PREGUNTAS FRECUENTES Y RESPUESTAS TÉCNICAS (DEFENSA 10 MINUTOS)

### Pregunta 1: ¿Por qué eligieron JSON Lines (`.jsonl`) y huellas SHA-256 en lugar de una base de datos relacional para los logs?
**Respuesta (Benjamín / José)**:
> *"JSON Lines es el estándar en observabilidad de alto rendimiento (usado por Fluentd, Logstash y OpenTelemetry) porque permite escrituras append-only secuenciales de $O(1)$ sin bloquear hilos ni sobrecargar I/O en disco. El uso de huellas SHA-256 de 16 caracteres garantiza la trazabilidad forense: podemos verificar si una entrada o salida fue alterada sin necesidad de almacenar texto plano, cumpliendo por diseño el principio de minimización de datos del RGPD y de la Ley 19.628."*

### Pregunta 2: ¿Cómo garantizan que el Fast-Path no impida responder consultas complejas de repuestos?
**Respuesta (Paolo)**:
> *"El enrutador Fast-Path aplica una heurística condicional: se activa únicamente si la consulta contiene palabras clave de inventario y simultáneamente carece de marcadores de diagnóstico complejo (como 'por qué falla', 'tirita', 'diagnóstico'). Si el cliente dice 'el auto tirita y quiero saber qué repuesto necesito', el sistema clasifica la consulta como diagnóstico complejo y la deriva al agente ReAct completo con RAG para no perder capacidad analítica."*

### Pregunta 3: ¿Qué diferencia práctica observaron entre la latencia media y la latencia P95?
**Respuesta (Benjamín)**:
> *"La latencia media ($0.939s$) enmascara la realidad del usuario: parecía indicar un sistema rápido, pero estaba sesgada por las respuestas de caché y el filtro de seguridad de $0.001s$. Al calcular el Percentil 95 ($4.040s$), descubrimos que 1 de cada 20 clientes esperaba más de 4 segundos. Fue la métrica P95 la que justificó técnicamente la necesidad de implementar el Fast-Path y la poda del contexto RAG."*

### Pregunta 4: ¿Cómo se asegura la precisión técnica del agente para que no alucine tolerancias de apriete o capacidades de fluidos?
**Respuesta (Paolo / José)**:
> *"La precisión está garantizada mediante RAG acotado sobre los manuales oficiales de taller cargados en FAISS. El prompt del sistema prohíbe explícitamente inventar datos técnicos: si un valor no está en el manual, el agente solicita autorización para búsqueda externa o declara que el dato requiere inspección de taller. En nuestra batería de pruebas cuantitativas sobre el Fiat Palio 1.3 Fire, la precisión frente al Ground Truth fue del 100%."*
