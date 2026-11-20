"""
AutoTech JPB Solutions - Módulo de Observabilidad, Trazabilidad, Seguridad y Métricas (EP3)
=============================================================================================
Asignatura: ISY0101 - Ingeniería de Soluciones con IA
Institución: Duoc UC
Integrantes: Paolo Jorquera, Benjamín Arriaza y José Castillo
Evaluación: Evaluación Parcial N°3 (IE1, IE2, IE3, IE4, IE6, IE7, IE8)

Este módulo provee instrumentación completa para agentes de IA:
- Registro estructurado de eventos en formato JSON Lines y log plano de texto.
- Telemetría de alta resolución (latencia, consumo de tokens, uso de recursos).
- Trazabilidad determinista con identificadores UUID y huellas criptográficas SHA-256.
- Protocolos de seguridad activa, sanitización y anonimización de datos sensibles (PII).
- Métricas analíticas de precisión técnica, consistencia semántica y detección de cuellos de botella.
"""

import os
import sys
import json
import time
import uuid
import hashlib
import re
import math
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union

# Constantes de persistencia y configuración por defecto
RUTA_LOG_DEFAULT = Path("ejecuciones_autotech.jsonl")
RUTA_TRACE_TXT_DEFAULT = Path("agent.log")
MAX_CONSULTAS_DEFAULT = 15

# Estimación de costos por token (tarifa referencial estándar GPT-OSS/Groq/OpenAI)
COSTO_POR_1K_TOKENS_ENTRADA_USD = 0.00015
COSTO_POR_1K_TOKENS_SALIDA_USD = 0.00060


class AutoTechObservability:
    """
    Motor centralizado de observabilidad, trazabilidad estructurada y auditoría ética
    para el agente autónomo de taller mecánico AutoTech.
    """

    def __init__(
        self,
        ruta_log: Union[str, Path] = RUTA_LOG_DEFAULT,
        ruta_txt: Union[str, Path] = RUTA_TRACE_TXT_DEFAULT
    ):
        self.ruta_log = Path(ruta_log)
        self.ruta_txt = Path(ruta_txt)
        self.cache: Dict[str, str] = {}
        self.registros_sesion: List[Dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # SEGURIDAD, ANONIMIZACIÓN Y HUELLAS CRIPTOGRÁFICAS (IE8)
    # -------------------------------------------------------------------------
    @staticmethod
    def calcular_huella(texto: Any) -> str:
        """
        Calcula una huella digital SHA-256 (16 caracteres hexadecimales) para
        trazabilidad y comprobación de integridad sin persistir datos en texto plano.
        """
        if texto is None:
            return "none"
        cadena = str(texto).strip().encode("utf-8")
        return hashlib.sha256(cadena).hexdigest()[:16]

    @staticmethod
    def anonimizar_datos_sensibles(texto: str) -> str:
        """
        Filtro de privacidad (Ley Chilena 19.628 y RGPD): detecta y enmascara
        RUT chileno, correos electrónicos, teléfonos y patentes vehiculares.
        """
        if not isinstance(texto, str):
            return ""

        # Enmascarar RUT chileno (ej: 12.345.678-9 o 12345678-k)
        texto = re.sub(r"\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b", "[RUT_PROTEGIDO]", texto)
        # Enmascarar correos electrónicos
        texto = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_PROTEGIDO]", texto)
        # Enmascarar teléfonos chilenos (+56 9 ..., 912345678)
        texto = re.sub(r"(\+?56\s?9\s?\d{4}\s?\d{4}|\b9\d{8}\b)", "[TELEFONO_PROTEGIDO]", texto)
        # Enmascarar patentes vehiculares chilenas (formato antiguo ABCD12 o nuevo BB-CC-11)
        texto = re.sub(r"\b[A-Z]{2,4}[- ]?\d{2,4}\b", "[PATENTE_PROTEGIDA]", texto)

        return texto

    @staticmethod
    def validar_entrada_segura(texto: str) -> Tuple[bool, str]:
        """
        Protocolo de validación ética y de seguridad previa a la invocación del agente (IE8).
        Bloquea intentos de jailbreak, inyección de comandos, extracción de prompts
        y solicitudes incompatibles con las operaciones de taller mecánico.
        """
        if not isinstance(texto, str) or not texto.strip():
            return False, "La consulta no puede estar vacía o contener solo espacios."

        if len(texto) > 1500:
            return False, "Longitud de consulta excede el límite máximo permitido (1500 caracteres)."

        # Patrones de ataque, jailbreak e inyección
        patrones_peligrosos = [
            (r"ignore\s+(all\s+)?instructions", "Intento de jailbreak / override de instrucciones"),
            (r"system\s+override", "Intento de anulación del sistema"),
            (r"acceso\s+root", "Intento de escalamiento de privilegios"),
            (r"exec\(|eval\(|__import__", "Intento de ejecución de código arbitrario"),
            (r"hackear|craquear|crack\b", "Solicitud maliciosa no permitida"),
            (r"drop\s+database|delete\s+from|union\s+select", "Intento de inyección SQL"),
            (r"bypass\s+security", "Intento de elusión de filtros de seguridad"),
            (r"obd-?ii.*firmware.*flash", "Manipulación no autorizada de firmware de seguridad ECU"),
            (r"<script|javascript:", "Intento de inyección XSS")
        ]

        texto_lower = texto.lower()
        for pat, descripcion in patrones_peligrosos:
            if re.search(pat, texto_lower, re.IGNORECASE):
                return False, f"Consulta bloqueada por protocolo de seguridad y uso responsable: {descripcion} ('{pat}')."

        return True, "Entrada validada correctamente."

    # -------------------------------------------------------------------------
    # INSTRUMENTACIÓN Y REGISTRO DE ETAPAS (IE1, IE2, IE3)
    # -------------------------------------------------------------------------
    def registrar_etapa(
        self,
        id_ejecucion: str,
        etapa: str,
        depende_de: Optional[str] = None,
        entrada: Any = "",
        salida: Any = "",
        duracion_s: float = 0.0,
        tokens_entrada: Optional[int] = 0,
        tokens_salida: Optional[int] = 0,
        estado: str = "exito",
        origen: str = "api",
        error_tipo: Optional[str] = None,
        modelo: str = "openai/gpt-oss-20b",
        metadatos: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Registra una etapa del ciclo de vida del agente con metadatos de telemetría.
        Persiste secuencialmente en JSON Lines (.jsonl) y log plano (.log).
        """
        # Anonimizar antes de registrar y calcular huellas
        texto_in_anon = self.anonimizar_datos_sensibles(str(entrada))
        texto_out_anon = self.anonimizar_datos_sensibles(str(salida))

        huella_in = self.calcular_huella(texto_in_anon)
        huella_out = self.calcular_huella(texto_out_anon)

        t_in = int(tokens_entrada or 0)
        t_out = int(tokens_salida or 0)
        costo_est = (t_in / 1000.0 * COSTO_POR_1K_TOKENS_ENTRADA_USD) + (t_out / 1000.0 * COSTO_POR_1K_TOKENS_SALIDA_USD)

        registro = {
            "ejecucion": str(id_ejecucion),
            "etapa": str(etapa),
            "depende_de": str(depende_de) if depende_de else None,
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            "modelo": str(modelo),
            "huella_entrada": huella_in,
            "huella_salida": huella_out,
            "estado": str(estado),
            "origen": str(origen),
            "duracion_s": round(float(duracion_s), 4),
            "tokens_entrada": t_in,
            "tokens_salida": t_out,
            "tokens_totales": t_in + t_out,
            "costo_estimado_usd": round(costo_est, 6),
            "error_tipo": str(error_tipo) if error_tipo else None,
            "metadatos": metadatos or {}
        }

        self.registros_sesion.append(registro)

        # 1. Persistencia secuencial estructurada en JSON Lines
        try:
            with open(self.ruta_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[Aviso Observabilidad] Error al escribir en {self.ruta_log}: {e}")

        # 2. Persistencia en log plano para trazabilidad directa en terminal
        try:
            with open(self.ruta_txt, "a", encoding="utf-8") as f:
                f.write(
                    f"[{registro['fecha_utc']}] [{id_ejecucion[:8]}] [{etapa}] "
                    f"estado={estado} origen={origen} duracion={registro['duracion_s']}s "
                    f"tokens_in={t_in} tokens_out={t_out} costo=${costo_est:.6f}\n"
                )
        except Exception:
            pass

        return registro

    def obtener_trazas_ejecucion(self, id_ejecucion: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Recupera todos los registros persistidos en JSON Lines, opcionalmente
        filtrados por un UUID de ejecución.
        """
        trazas = []
        if not self.ruta_log.exists():
            return trazas

        try:
            with open(self.ruta_log, "r", encoding="utf-8") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    try:
                        evento = json.loads(linea)
                        if id_ejecucion is None or evento.get("ejecucion") == id_ejecucion:
                            trazas.append(evento)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[Aviso Observabilidad] Error al leer {self.ruta_log}: {e}")

        return trazas

    # -------------------------------------------------------------------------
    # FORMATO Y PRESENTACIÓN EN MARKDOWN / TABLAS (IE3)
    # -------------------------------------------------------------------------
    def generar_tabla_markdown(self, trazas: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Genera una tabla Markdown estructurada para visualización inmediata en Jupyter/Colab.
        """
        filas_data = trazas if trazas is not None else self.registros_sesion
        if not filas_data:
            return "*(No hay eventos registrados en esta sesión)*"

        filas = [
            "| Etapa / Herramienta | Depende De | Estado | Origen | Duración (s) | Tokens In | Tokens Out | Huella In / Out |",
            "|---|---|---|---|---:|---:|---:|:---:|"
        ]
        for r in filas_data:
            dur = f"{r.get('duracion_s', 0):.4f}"
            t_in = r.get("tokens_entrada", "-")
            t_out = r.get("tokens_salida", "-")
            dep = r.get("depende_de") or "Raíz"
            huellas = f"`{r.get('huella_entrada','')}` / `{r.get('huella_salida','')}`"
            filas.append(
                f"| {r.get('etapa')} | {dep} | {r.get('estado')} | {r.get('origen')} | "
                f"{dur} | {t_in} | {t_out} | {huellas} |"
            )
        return "\n".join(filas)

    # -------------------------------------------------------------------------
    # CÁLCULO DE KPIS GLOBALES Y PERCENTILES (IE1, IE2)
    # -------------------------------------------------------------------------
    def calcular_metricas_globales(self) -> Dict[str, Any]:
        """
        Calcula estadísticas descriptivas completas sobre el total de eventos registrados:
        - Latencias: media, mediana (P50), P90, P95, P99, desviación estándar, mín, máx.
        - Consumo acumulado de tokens (in, out, total) y costo estimado.
        - Tasas operativas: éxito, error técnico, eventos bloqueados por seguridad, tasa de acierto de caché.
        - Identificación del cuello de botella analítico.
        """
        trazas = self.obtener_trazas_ejecucion()
        if not trazas:
            return {
                "total_eventos": 0,
                "latencia_promedio_s": 0.0,
                "latencia_mediana_s": 0.0,
                "latencia_p90_s": 0.0,
                "latencia_p95_s": 0.0,
                "latencia_p99_s": 0.0,
                "latencia_desv_std_s": 0.0,
                "latencia_maxima_s": 0.0,
                "latencia_minima_s": 0.0,
                "total_tokens_entrada": 0,
                "total_tokens_salida": 0,
                "total_tokens": 0,
                "costo_acumulado_usd": 0.0,
                "tasa_acierto_cache_pct": 0.0,
                "tasa_exito_pct": 0.0,
                "tasa_error_pct": 0.0,
                "tasa_seguridad_pct": 0.0,
                "cuello_de_botella_principal": "Sin datos",
                "detalle_etapas_promedio_s": {}
            }

        latencias = [float(r["duracion_s"]) for r in trazas if isinstance(r.get("duracion_s"), (int, float))]
        tokens_in = sum(int(r.get("tokens_entrada") or 0) for r in trazas)
        tokens_out = sum(int(r.get("tokens_salida") or 0) for r in trazas)
        costo_total = sum(float(r.get("costo_estimado_usd") or 0.0) for r in trazas)

        errores = sum(1 for r in trazas if r.get("estado") == "error")
        bloqueados = sum(1 for r in trazas if r.get("estado") in ("bloqueado", "bloqueado_seguridad"))
        exitos = sum(1 for r in trazas if r.get("estado") in ("exito", "exito_cache"))
        en_cache = sum(1 for r in trazas if r.get("origen") == "cache" or r.get("estado") == "exito_cache")

        # Percentiles y dispersión
        lat_sort = sorted(latencias) if latencias else [0.0]
        n = len(lat_sort)

        def calc_percentil(p: float) -> float:
            if not lat_sort:
                return 0.0
            idx = int(n * p)
            return lat_sort[min(idx, n - 1)]

        p50 = calc_percentil(0.50)
        p90 = calc_percentil(0.90)
        p95 = calc_percentil(0.95)
        p99 = calc_percentil(0.99)
        prom = sum(latencias) / len(latencias) if latencias else 0.0

        varianza = sum((x - prom) ** 2 for x in latencias) / len(latencias) if len(latencias) > 1 else 0.0
        desv_std = math.sqrt(varianza)

        # Desglose de latencia y cuellos de botella por etapa
        tiempos_por_etapa: Dict[str, List[float]] = {}
        for r in trazas:
            etapa = r.get("etapa", "desconocida")
            tiempos_por_etapa.setdefault(etapa, []).append(float(r.get("duracion_s", 0.0)))

        promedios_etapas = {
            et: sum(tiempos) / len(tiempos)
            for et, tiempos in tiempos_por_etapa.items()
        }
        cuello_botella = max(promedios_etapas.items(), key=lambda x: x[1])[0] if promedios_etapas else "N/A"

        total_evt = len(trazas)
        return {
            "total_eventos": total_evt,
            "latencia_promedio_s": round(prom, 4),
            "latencia_mediana_s": round(p50, 4),
            "latencia_p90_s": round(p90, 4),
            "latencia_p95_s": round(p95, 4),
            "latencia_p99_s": round(p99, 4),
            "latencia_desv_std_s": round(desv_std, 4),
            "latencia_maxima_s": round(max(latencias), 4) if latencias else 0.0,
            "latencia_minima_s": round(min(latencias), 4) if latencias else 0.0,
            "total_tokens_entrada": tokens_in,
            "total_tokens_salida": tokens_out,
            "total_tokens": tokens_in + tokens_out,
            "costo_acumulado_usd": round(costo_total, 6),
            "tasa_acierto_cache_pct": round((en_cache / total_evt) * 100, 2) if total_evt else 0.0,
            "tasa_exito_pct": round((exitos / total_evt) * 100, 2) if total_evt else 0.0,
            "tasa_error_pct": round((errores / total_evt) * 100, 2) if total_evt else 0.0,
            "tasa_seguridad_pct": round((bloqueados / total_evt) * 100, 2) if total_evt else 0.0,
            "cuello_de_botella_principal": cuello_botella,
            "detalle_etapas_promedio_s": {k: round(v, 4) for k, v in promedios_etapas.items()}
        }

    # -------------------------------------------------------------------------
    # EVALUACIÓN DE PRECISIÓN Y CONSISTENCIA TÉCNICA (IE1)
    # -------------------------------------------------------------------------
    @staticmethod
    def evaluar_precision_tecnica(
        respuesta: str,
        hechos_clave_esperados: List[str]
    ) -> Dict[str, Any]:
        """
        Evalúa la precisión técnica de una respuesta del agente comparando la presencia
        de hechos clave oficiales de los manuales del taller (Ground Truth).
        Retorna porcentaje de acierto, hechos presentes y hechos omitidos.
        """
        if not respuesta or not isinstance(respuesta, str):
            return {"precision_pct": 0.0, "aciertos": 0, "total_esperados": len(hechos_clave_esperados), "hechos_faltantes": hechos_clave_esperados}

        resp_lower = respuesta.lower()
        aciertos = []
        faltantes = []

        for hecho in hechos_clave_esperados:
            h_clean = hecho.strip().lower()
            if h_clean in resp_lower:
                aciertos.append(hecho)
            else:
                faltantes.append(hecho)

        total = len(hechos_clave_esperados)
        precision = round((len(aciertos) / total) * 100, 2) if total > 0 else 100.0

        return {
            "precision_pct": precision,
            "aciertos": len(aciertos),
            "total_esperados": total,
            "hechos_encontrados": aciertos,
            "hechos_faltantes": faltantes
        }

    @staticmethod
    def evaluar_consistencia_semantica(respuestas: List[str]) -> float:
        """
        Evalúa la consistencia de respuestas emitidas ante reformulaciones o repeticiones
        de la misma consulta técnica, utilizando solapamiento de n-gramas clave.
        """
        if not respuestas or len(respuestas) < 2:
            return 100.0

        # Tokenización básica de palabras con significado técnico (longitud >= 4)
        conjuntos = []
        for r in respuestas:
            palabras = set(re.findall(r"\b[a-zA-Z0-9áéíóúñ]{4,}\b", r.lower()))
            conjuntos.append(palabras)

        # Calcular coeficiente de similitud Jaccard promedio entre pares
        similitudes = []
        for i in range(len(conjuntos)):
            for j in range(i + 1, len(conjuntos)):
                inter = len(conjuntos[i] & conjuntos[j])
                union = len(conjuntos[i] | conjuntos[j])
                sim = (inter / union) if union > 0 else 1.0
                similitudes.append(sim)

        prom_sim = sum(similitudes) / len(similitudes) if similitudes else 1.0
        return round(prom_sim * 100, 2)

    # -------------------------------------------------------------------------
    # DETECCIÓN DE ANOMALÍAS Y ANÁLISIS FORENSE DE LOGS (IE3, IE6)
    # -------------------------------------------------------------------------
    def detectar_anomalias_y_cuellos_de_botella(
        self,
        umbral_latencia_s: float = 3.5,
        umbral_tokens: int = 600
    ) -> List[Dict[str, Any]]:
        """
        Examina las trazas persistidas para detectar patrones anómalos:
        - Consultas con latencia fuera de límites (posible cuello de botella de red/TPM).
        - Consultas con sobreconsumo de tokens (posible bucle de razonamiento ReAct).
        - Eventos con errores de validación de esquemas en llamadas de herramientas.
        """
        trazas = self.obtener_trazas_ejecucion()
        anomalias = []

        for idx, t in enumerate(trazas, 1):
            dur = float(t.get("duracion_s", 0.0))
            tok = int(t.get("tokens_totales", 0) or 0)
            estado = t.get("estado", "")
            error_tipo = t.get("error_tipo")

            if estado == "error" or error_tipo:
                anomalias.append({
                    "indice_evento": idx,
                    "ejecucion": t.get("ejecucion"),
                    "etapa": t.get("etapa"),
                    "tipo_anomalia": "Falla Técnica / Error de Ejecución",
                    "descripcion": f"Error tipo '{error_tipo}' registrado en etapa '{t.get('etapa')}'.",
                    "severidad": "ALTA"
                })

            if dur >= umbral_latencia_s:
                anomalias.append({
                    "indice_evento": idx,
                    "ejecucion": t.get("ejecucion"),
                    "etapa": t.get("etapa"),
                    "tipo_anomalia": "Cuello de Botella de Latencia",
                    "descripcion": f"Latencia de {dur:.3f}s supera el umbral operativo ({umbral_latencia_s}s).",
                    "severidad": "MEDIA"
                })

            if tok >= umbral_tokens:
                anomalias.append({
                    "indice_evento": idx,
                    "ejecucion": t.get("ejecucion"),
                    "etapa": t.get("etapa"),
                    "tipo_anomalia": "Consumo Excesivo de Tokens",
                    "descripcion": f"Consumo de {tok} tokens excede el presupuesto por turno ({umbral_tokens} tokens).",
                    "severidad": "BAJA"
                })

        return anomalias

    # -------------------------------------------------------------------------
    # CONVERSIÓN A DATAFRAME DE PANDAS (IE4)
    # -------------------------------------------------------------------------
    def to_dataframe(self, trazas: Optional[List[Dict[str, Any]]] = None):
        """
        Convierte los registros de ejecución en un DataFrame de pandas para
        fácil graficación en Streamlit, Matplotlib o Seaborn.
        """
        try:
            import pandas as pd
            data = trazas if trazas is not None else self.obtener_trazas_ejecucion()
            if not data:
                return pd.DataFrame()
            df = pd.DataFrame(data)
            if "fecha_utc" in df.columns:
                df["timestamp"] = pd.to_datetime(df["fecha_utc"], errors="coerce")
            return df
        except ImportError:
            print("[Aviso] pandas no está instalado. Retornando lista de diccionarios.")
            return trazas or []


# Alias para compatibilidad hacia atrás total con la celda del notebook
AutoTechObservabilityEngine = AutoTechObservability

# Instancia global por defecto
observability_engine = AutoTechObservability()
observability = observability_engine
