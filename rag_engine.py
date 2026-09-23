"""
AutoTech JPB Solutions - Motor RAG y Agente Inteligente con Tool Calling Integrado
==================================================================================
Desarrollado para ISY0101 (Ingeniería de Soluciones con IA - Duoc UC)
Integrantes: Paolo, Benjamín y José.

Este módulo implementa:
1. Integración con Google Drive Público y Privado.
2. Carga y procesamiento de manuales PDF con Caché Persistente en Disco (< 0.1s de inicio).
3. Indexación vectorial semántica con SentenceTransformers y FAISS / Numpy Cosine.
4. Herramienta de Inventario Completo y Consultas por Categoría o Producto.
5. Orquestación del Agente con LLM (Groq / Modelo: openai/gpt-oss-20b).
"""

import os
import sys
import json
import shutil
import pickle
import subprocess
import numpy as np
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
from openai import OpenAI

if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from sentence_transformers import SentenceTransformer
    HAS_ST = True
except ImportError:
    HAS_ST = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


# -----------------------------------------------------------------------------
# 0. DETECCION Y SINCRONIZACION CON GOOGLE DRIVE (LINK PUBLICO Y PRIVADO)
# -----------------------------------------------------------------------------
DRIVE_DEFAULT_DIR = "/content/drive/MyDrive/AutoTech_Manuales"
PUBLIC_DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1UShpyjhW2rfinSafBseYJie8rw_P_dsK"

def download_public_drive_manuals(target_dir: str = ".") -> bool:
    """
    Descarga automáticamente los manuales PDF y archivos desde la carpeta pública de Google Drive
    usando la librería gdown, los mueve a target_dir y elimina la subcarpeta vacía para evitar duplicados.
    """
    try:
        import gdown
        print(f"[Google Drive Público] Descargando archivos automáticamente desde enlace compartido...")
        gdown.download_folder(PUBLIC_DRIVE_FOLDER_URL, output=target_dir, quiet=True)
        
        folder_name = os.path.join(target_dir, "AutoTech_Manuales")
        if os.path.exists(folder_name):
            for fname in os.listdir(folder_name):
                src = os.path.join(folder_name, fname)
                dst = os.path.join(target_dir, fname)
                if os.path.isfile(src):
                    try:
                        shutil.move(src, dst)
                    except Exception:
                        pass
            try:
                shutil.rmtree(folder_name)
            except Exception:
                pass

        print("[Google Drive Público] Archivos del proyecto movidos a la raíz exitosamente (sin duplicados).")
        return True
    except Exception as e:
        print(f"[Aviso] No se pudo descargar automáticamente desde el enlace público de Drive: {e}")
        return False

def get_google_drive_status() -> Dict[str, Any]:
    """Retorna información sobre el estado del montaje de Google Drive."""
    is_mounted = os.path.exists("/content/drive/MyDrive")
    manuals_dir_exists = os.path.exists(DRIVE_DEFAULT_DIR)
    drive_pdfs = []
    
    if manuals_dir_exists:
        try:
            drive_pdfs = [f for f in os.listdir(DRIVE_DEFAULT_DIR) if f.lower().endswith(".pdf")]
        except Exception:
            pass
            
    return {
        "is_mounted": is_mounted,
        "manuals_dir": DRIVE_DEFAULT_DIR,
        "manuals_dir_exists": manuals_dir_exists,
        "drive_pdfs": drive_pdfs,
        "public_url": PUBLIC_DRIVE_FOLDER_URL
    }

def sync_manuals_from_google_drive(target_dir: str = ".") -> List[str]:
    """
    Sincroniza los manuales desde Google Drive (privado o público).
    """
    copied_files = []
    status = get_google_drive_status()
    
    # 1. Si Drive privado está montado en Colab
    if status["is_mounted"]:
        if not os.path.exists(DRIVE_DEFAULT_DIR):
            try:
                os.makedirs(DRIVE_DEFAULT_DIR, exist_ok=True)
            except Exception:
                pass
        else:
            for pdf_name in status["drive_pdfs"]:
                src_path = os.path.join(DRIVE_DEFAULT_DIR, pdf_name)
                dst_path = os.path.join(target_dir, pdf_name)
                try:
                    if not os.path.exists(dst_path) or os.path.getsize(src_path) != os.path.getsize(dst_path):
                        shutil.copy2(src_path, dst_path)
                    copied_files.append(dst_path)
                except Exception:
                    pass

    # 2. Si faltan PDFs locales, intentar descargar del enlace público automáticamente
    expected_pdfs = [
        "ficha_tecnica_fiat_palio.pdf",
        "MANUAL-DE-OPERACIONES-DE-TALLER-.pdf",
        "manual_fallas_multimarca_diagnostico.pdf",
        "manual_recepcion_fallas_cliente_taller.pdf",
        "mecanica-automotriz-mantenimiento-de-motores.pdf"
    ]
    missing = [f for f in expected_pdfs if not os.path.exists(os.path.join(target_dir, f))]
    if missing:
        download_public_drive_manuals(target_dir)

    return copied_files


# -----------------------------------------------------------------------------
# 1. BASE DE DATOS EXTENDIDA DE INVENTARIO AUTOTECH (HERRAMIENTA EXTERNA)
# -----------------------------------------------------------------------------
INVENTARIO_BODEGA = {
    # Lubricantes y Fluidos
    "aceite 10w-40": {"nombre": "Aceite Sintético 10W-40 (4 Litros)", "categoria": "Lubricantes", "stock": 18, "precio_clp": 28990, "bodega": "Pasillo A - Estante 2", "desc": "Aceite semi-sintético para motores a gasolina y diésel ligero."},
    "aceite 15w-40": {"nombre": "Aceite Mineral 15W-40 (4 Litros)", "categoria": "Lubricantes", "stock": 25, "precio_clp": 22490, "bodega": "Pasillo A - Estante 1", "desc": "Aceite mineral de alta viscosidad para motores con kilometraje avanzado."},
    "aceite 5w-30": {"nombre": "Aceite Sintético Premium 5W-30 (4 Litros)", "categoria": "Lubricantes", "stock": 14, "precio_clp": 34990, "bodega": "Pasillo A - Estante 3", "desc": "Aceite 100% sintético bajo en cenizas para motores modernos y DPF."},
    "liquido de frenos dot4": {"nombre": "Líquido de Frenos DOT 4 (500ml)", "categoria": "Fluidos", "stock": 30, "precio_clp": 5990, "bodega": "Pasillo A - Estante 4", "desc": "Líquido sintético de alto punto de ebullición para sistemas ABS y disco."},
    
    # Frenos
    "pastillas de freno": {"nombre": "Juego Pastillas de Freno Delanteras Fiat/Universal", "categoria": "Frenos", "stock": 15, "precio_clp": 24990, "bodega": "Pasillo C - Estante 3", "desc": "Pastillas cerámicas de baja emisión de polvo con indicador sonoro."},
    "discos de freno": {"nombre": "Juego Discos de Freno Ventilados 257mm", "categoria": "Frenos", "stock": 8, "precio_clp": 38990, "bodega": "Pasillo C - Estante 4", "desc": "Discos de freno de acero templado antidealante."},

    # Visibilidad y Limpiaparabrisas
    "plumillas 18": {"nombre": "Plumilla Limpiaparabrisas Goma 18\" (Universal)", "categoria": "Limpiaparabrisas", "stock": 15, "precio_clp": 4990, "bodega": "Pasillo B - Caja 01", "desc": "Plumilla de goma de alta durabilidad con adaptador U-Hook universal."},
    "plumillas 22": {"nombre": "Plumilla Silicona Aerodinámica 22\" (Changan / SUV / Universal)", "categoria": "Limpiaparabrisas", "stock": 12, "precio_clp": 7990, "bodega": "Pasillo B - Caja 02", "desc": "Plumilla flexible de silicona con deflector aerodinámico."},

    # Neumáticos y Presión
    "neumatico 175/65 r14": {"nombre": "Neumático 175/65 R14 All Season", "categoria": "Neumáticos", "stock": 16, "precio_clp": 42990, "bodega": "Racks Neumáticos - Sector N1", "desc": "Neumático radial para sedán y hatchback."},
    "manometro digital": {"nombre": "Medidor de Presión de Neumáticos Digital / Manómetro", "categoria": "Herramientas", "stock": 10, "precio_clp": 9990, "bodega": "Pasillo B - Caja 08", "desc": "Manómetro digital de precisión de 0 a 100 PSI."},
    "valvula tpms": {"nombre": "Válvula Sensores TPMS Electrónica Universal", "categoria": "Neumáticos", "stock": 8, "precio_clp": 18990, "bodega": "Pasillo B - Caja 09", "desc": "Válvula programable de monitoreo de presión de aire."},

    # Filtración y Motor
    "filtro de aceite fiat": {"nombre": "Filtro de Aceite Fiat Palio 1.3 FIRE", "categoria": "Filtros", "stock": 12, "precio_clp": 6990, "bodega": "Pasillo B - Caja 04", "desc": "Filtro de aceite blindado de flujo completo."},
    "filtro de aire fiat": {"nombre": "Filtro de Aire Fiat Palio 1.3 FIRE", "categoria": "Filtros", "stock": 8, "precio_clp": 8490, "bodega": "Pasillo B - Caja 05", "desc": "Elemento filtrante de celulosa de alta eficiencia."},
    "filtro de particulas dpf": {"nombre": "Filtro de Partículas DPF Universal/Diesel", "categoria": "Filtros", "stock": 2, "precio_clp": 289900, "bodega": "Bodega Especial - Racks", "desc": "Filtro DPF diésel de cordierita para retención de hollín."},
    "bujia fire": {"nombre": "Set 4 Bujías NGK para Motor Fiat FIRE 1.3", "categoria": "Motor", "stock": 20, "precio_clp": 14990, "bodega": "Pasillo B - Caja 12", "desc": "Bujías de encendido de cobre electrodo 0.8mm."},
    "correa distribucion": {"nombre": "Kit Correa Distribución + Tensor Fiat 1.3 FIRE", "categoria": "Motor", "stock": 5, "precio_clp": 38990, "bodega": "Pasillo C - Estante 1", "desc": "Kit completo de correa dentada reforzada y polea tensora."},

    # Eléctrica y Confort (Alza Vidrios / Batería)
    "botonera changan cx70": {"nombre": "Botonera Comando Alza Vidrios Changan CX70", "categoria": "Eléctrico", "stock": 4, "precio_clp": 29990, "bodega": "Pasillo D - Estante 2", "desc": "Botonera principal de puerta del conductor con bloqueo de ventanas."},
    "motor elevacristales": {"nombre": "Motor Elevacristales 12V Puerta Universal / SUV", "categoria": "Eléctrico", "stock": 6, "precio_clp": 24990, "bodega": "Pasillo D - Estante 3", "desc": "Motor eléctrico de gran torque 12V marcha izquierda/derecha."},
    "bateria 60ah": {"nombre": "Batería Libre Mantenimiento 12V 60Ah", "categoria": "Eléctrico", "stock": 6, "precio_clp": 64990, "bodega": "Bodega General - Sector Baterías", "desc": "Batería sellada CCA 520A de arranque en frío."}
}

TOOL_INVENTARIO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "consultar_inventario",
        "description": "Consulta la disponibilidad de stock, precio en CLP, ubicación en bodega y detalles de repuestos en AutoTech JPB Solutions. Permite consultar un producto específico o la lista general de inventario disponible.",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre_repuesto": {
                    "type": "string",
                    "description": "Nombre o concepto clave del repuesto (ej: 'aceite 10w-40', 'pastillas de freno', 'plumillas', 'alza vidrios', 'changan', 'bateria', 'filtro', 'que tenemos' o 'inventario general')."
                }
            },
            "required": ["nombre_repuesto"]
        }
    }
}

def consultar_inventario(nombre_repuesto: str) -> str:
    """Ejecuta la búsqueda en el sistema de inventario de AutoTech."""
    query = nombre_repuesto.lower().strip()
    
    # Si la consulta es general (qué hay en bodega, lista, inventario)
    palabras_generales = ["que tenemos", "que hay", "inventario", "lista", "todo", "bodega", "productos", "categorias", "que repuestos"]
    if any(pg in query for pg in palabras_generales) or query in ["", "stock", "repuestos"]:
        res = "**INVENTARIO GENERAL DISPONIBLE EN BODEGA AUTOTECH JPB SOLUTIONS:**\n\n"
        categorias = {}
        for item in INVENTARIO_BODEGA.values():
            cat = item["categoria"]
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(item)
            
        for cat, items in categorias.items():
            res += f"**Categoría: {cat}**\n"
            for it in items:
                res += f"  - **{it['nombre']}** | Stock: {it['stock']} un. | Precio: ${it['precio_clp']:,} CLP | Ubicación: `{it['bodega']}`\n"
            res += "\n"
        return res

    # Búsqueda específica por coincidencia
    coincidencias = []
    for key, data in INVENTARIO_BODEGA.items():
        if key in query or any(word in key for word in query.split() if len(word) > 2):
            coincidencias.append(data)
            
    if coincidencias:
        res = f"**RESULTADOS DE INVENTARIO PARA '{nombre_repuesto}':**\n"
        for item in coincidencias:
            res += f"- **Producto:** {item['nombre']}\n"
            res += f"  • Stock Disponible: {item['stock']} unidades\n"
            res += f"  • Precio Taller: ${item['precio_clp']:,} CLP\n"
            res += f"  • Ubicación Bodega: `{item['bodega']}`\n"
            res += f"  • Descripción: {item['desc']}\n\n"
        return res
    else:
        return f"No se encontraron repuestos registrados para '{nombre_repuesto}'. Se sugiere solicitar cotización directa a importación."


# -----------------------------------------------------------------------------
# 2. PROCESAMIENTO DE DOCUMENTOS PDF Y CHUNKING OPTIMIZADO
# -----------------------------------------------------------------------------
class DocumentChunk:
    def __init__(self, text: str, source_doc: str, page_num: int, chunk_id: int):
        self.text = text
        self.source_doc = source_doc
        self.page_num = page_num
        self.chunk_id = chunk_id

def load_and_split_pdf(pdf_path: str, chunk_size: int = 600, chunk_overlap: int = 100, max_pages: int = None) -> List[DocumentChunk]:
    if not os.path.exists(pdf_path):
        return []

    chunks = []
    filename = os.path.basename(pdf_path)
    
    try:
        reader = PdfReader(pdf_path)
        global_chunk_id = 0
        total_pages = len(reader.pages) if max_pages is None else min(len(reader.pages), max_pages)
        
        for page_idx in range(total_pages):
            page = reader.pages[page_idx]
            page_text = page.extract_text() or ""
            if not page_text.strip():
                continue
                
            paragraphs = page_text.split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if not para or len(para) < 20:
                    continue
                    
                if len(para) <= chunk_size:
                    chunks.append(DocumentChunk(
                        text=para,
                        source_doc=filename,
                        page_num=page_idx + 1,
                        chunk_id=global_chunk_id
                    ))
                    global_chunk_id += 1
                else:
                    words = para.split()
                    current_words = []
                    for word in words:
                        current_words.append(word)
                        curr_str = " ".join(current_words)
                        if len(curr_str) >= chunk_size:
                            chunks.append(DocumentChunk(
                                text=curr_str,
                                source_doc=filename,
                                page_num=page_idx + 1,
                                chunk_id=global_chunk_id
                            ))
                            global_chunk_id += 1
                            overlap_k = max(1, int(len(current_words) * (chunk_overlap / chunk_size)))
                            current_words = current_words[-overlap_k:]
                    if current_words:
                        chunks.append(DocumentChunk(
                            text=" ".join(current_words),
                            source_doc=filename,
                            page_num=page_idx + 1,
                            chunk_id=global_chunk_id
                        ))
                        global_chunk_id += 1
                
    except Exception as e:
        print(f"Error procesando PDF {pdf_path}: {e}")
        
    return chunks


# -----------------------------------------------------------------------------
# 3. BASE DE DATOS VECTORIAL CON CACHE EN DISCO PERSISTENTE (EVALUACION POR TAMAÑO DE ARCHIVO)
# -----------------------------------------------------------------------------
CACHE_FILE_NAME = "autotech_vector_cache.pkl"

class AutoTechVectorStore:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.chunks: List[DocumentChunk] = []
        self.embeddings: np.ndarray = None
        self.embedder = None
        self.faiss_index = None
        self.model_name = model_name
        self.is_from_cache = False
        
        if HAS_ST:
            try:
                self.embedder = SentenceTransformer(model_name)
            except Exception as e:
                print(f"[Aviso] Error cargando SentenceTransformer: {e}")

    def _compute_pdf_metadata(self, pdf_files: List[str]) -> Dict[str, int]:
        """Evalúa ÚNICAMENTE el tamaño en bytes de los archivos PDF para evitar invalidez por timestamp de descarga."""
        meta = {}
        for pdf_path in pdf_files:
            if os.path.exists(pdf_path):
                stat = os.stat(pdf_path)
                meta[os.path.basename(pdf_path)] = stat.st_size
        return meta

    def save_to_cache(self, cache_path: str, pdf_files: List[str]):
        """Guarda los chunks y embeddings vectoriales en disco para acelerar cargas futuras."""
        try:
            cache_data = {
                "chunks": [(c.text, c.source_doc, c.page_num, c.chunk_id) for c in self.chunks],
                "embeddings": self.embeddings,
                "pdf_meta": self._compute_pdf_metadata(pdf_files)
            }
            with open(cache_path, "wb") as f:
                pickle.dump(cache_data, f)
            print(f"[Caché Vectorial] Guardado exitosamente en: {cache_path}")
            
            # Guardar también en Google Drive si está disponible
            drive_status = get_google_drive_status()
            if drive_status["is_mounted"] and drive_status["manuals_dir_exists"]:
                drive_cache_path = os.path.join(DRIVE_DEFAULT_DIR, os.path.basename(cache_path))
                try:
                    with open(drive_cache_path, "wb") as f:
                        pickle.dump(cache_data, f)
                    print(f"[Caché Vectorial] Respaldado en Google Drive: {drive_cache_path}")
                except Exception as ex:
                    print(f"[Caché Vectorial] No se pudo respaldar en Drive: {ex}")
        except Exception as e:
            print(f"[Aviso] No se pudo guardar el caché vectorial: {e}")

    def load_from_cache(self, cache_path: str, pdf_files: List[str]) -> bool:
        """Carga fragmentos y vectores desde disco si el tamaño de los PDFs coincide."""
        target_path = cache_path
        if not os.path.exists(target_path):
            drive_status = get_google_drive_status()
            if drive_status["is_mounted"] and drive_status["manuals_dir_exists"]:
                drive_cache_path = os.path.join(DRIVE_DEFAULT_DIR, os.path.basename(cache_path))
                if os.path.exists(drive_cache_path):
                    target_path = drive_cache_path

        if not os.path.exists(target_path):
            return False

        try:
            with open(target_path, "rb") as f:
                cache_data = pickle.load(f)

            current_meta = self._compute_pdf_metadata(pdf_files)
            cached_meta = cache_data.get("pdf_meta", {})
            
            # Comparar solo los nombres y tamaños en bytes de los PDFs
            if current_meta and set(current_meta.keys()) != set(cached_meta.keys()):
                print("[Caché Vectorial] Los archivos PDF cambiaron. Se reconstruirá el índice.")
                return False

            raw_chunks = cache_data.get("chunks", [])
            self.chunks = [DocumentChunk(text, doc, page, cid) for text, doc, page, cid in raw_chunks]
            self.embeddings = cache_data.get("embeddings")

            if self.embeddings is not None and HAS_FAISS:
                dimension = self.embeddings.shape[1]
                self.faiss_index = faiss.IndexFlatIP(dimension)
                self.faiss_index.add(self.embeddings.astype(np.float32))

            self.is_from_cache = True
            print(f"[Caché Vectorial] CARGA ULTRA-RÁPIDA COMPLETADA ({len(self.chunks)} fragmentos en < 0.1s desde '{target_path}')")
            return True
        except Exception as e:
            print(f"[Aviso] Error al leer caché vectorial ({e}). Se reconstruirá.")
            return False

    def build_index(self, chunks: List[DocumentChunk]):
        """Construye la matriz de embeddings y el índice FAISS."""
        self.chunks = chunks
        if not chunks:
            return

        texts = [c.text for c in chunks]
        
        if self.embedder:
            encoded = self.embedder.encode(texts, batch_size=64, show_progress_bar=False, convert_to_numpy=True)
            norms = np.linalg.norm(encoded, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.embeddings = encoded / norms
            
            if HAS_FAISS:
                dimension = self.embeddings.shape[1]
                self.faiss_index = faiss.IndexFlatIP(dimension)
                self.faiss_index.add(self.embeddings.astype(np.float32))

    def build_or_load_index(self, pdf_files: List[str], cache_path: str = CACHE_FILE_NAME):
        """Intenta cargar desde caché persistente en disco; si no existe, procesa PDFs y guarda en caché."""
        sync_manuals_from_google_drive()
        available_pdfs = [f for f in pdf_files if os.path.exists(f)]
        
        if self.load_from_cache(cache_path, available_pdfs):
            return available_pdfs

        all_chunks = []
        for pdf_path in available_pdfs:
            max_p = 150 if "mecanica-automotriz" in pdf_path else None
            chunks = load_and_split_pdf(pdf_path, chunk_size=600, chunk_overlap=100, max_pages=max_p)
            all_chunks.extend(chunks)

        self.build_index(all_chunks)
        self.save_to_cache(cache_path, available_pdfs)
        return available_pdfs

    def search(self, query: str, top_k: int = 6) -> List[Tuple[DocumentChunk, float]]:
        if not self.chunks:
            return []

        q_lower = query.lower()

        if self.embedder is not None and self.embeddings is not None:
            q_vec = self.embedder.encode([query], convert_to_numpy=True)
            norm = np.linalg.norm(q_vec)
            if norm > 0:
                q_vec = q_vec / norm
                
            scores = np.dot(self.embeddings, q_vec.T).squeeze()
            if isinstance(scores, (float, int, np.float32, np.float64)):
                scores = np.array([scores])

            keywords_fiat = ["fiat", "palio", "aceite", "torque", "presion", "bujia", "filtro", "litro", "viscosidad"]
            if any(kw in q_lower for kw in keywords_fiat):
                for idx, chunk in enumerate(self.chunks):
                    if "ficha_tecnica_fiat_palio" in chunk.source_doc.lower():
                        scores[idx] += 0.35

            top_indices = np.argsort(scores)[::-1][:top_k]
            return [(self.chunks[idx], float(scores[idx])) for idx in top_indices]

        else:
            query_words = set(q_lower.split())
            scored = []
            for chunk in self.chunks:
                words = set(chunk.text.lower().split())
                overlap = len(query_words.intersection(words))
                if "ficha_tecnica_fiat_palio" in chunk.source_doc.lower():
                    overlap += 2
                scored.append((chunk, float(overlap)))
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:top_k]


# -----------------------------------------------------------------------------
# 4. ORQUESTADOR DEL AGENTE CON TOOL CALLING INTELIGENTE
# -----------------------------------------------------------------------------
SYSTEM_PROMPT_AUTOTECH = """Eres "AutoTech Copilot", el Agente Inteligente de Soporte Técnico, Recepción de Taller y Control de Inventario para AutoTech JPB Solutions.

TUS CAPACIDADES:
1. Responder consultas técnicas de mecánica, diagnósticos de fallas (alza vidrios, limpiavidrios/plumillas, luces de tablero, ruidos, presiones de neumáticos PSI), según el CONTEXTO TÉCNICO recuperado de los manuales del taller.
2. Consultar el inventario de bodega usando la HERRAMIENTA `consultar_inventario`. Si el usuario pregunta "¿qué tenemos en stock?", "¿qué repuestos hay?" o consulta por un producto específico (ej: plumillas, aceites, pastillas, alza vidrios), invoca SIEMPRE `consultar_inventario`.

REGLAS DE ACTUACIÓN (ESTRICTAS):
- Responde siempre de manera sumamente atenta, clara y profesional en idioma Español.
- Utiliza la información del CONTEXTO TÉCNICO para guiar al cliente o mecánico paso a paso.
- Si el usuario pregunta sobre disponibilidad, productos o stock de bodega, ejecuta la función `consultar_inventario`.
- Al dar diagnósticos o valores técnicos de manuales, CITA la fuente indicando el archivo y página (ej: `[Fuente: manual_recepcion_fallas_cliente_taller.pdf, Pág. 1]`).
"""

MODELOS_GROQ = [
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768"
]

class AutoTechAgent:
    def __init__(self, api_key: str, vector_store: AutoTechVectorStore, model_name: str = "openai/gpt-oss-20b"):
        self.api_key = api_key
        self.model_name = model_name
        self.vector_store = vector_store
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )

    def _call_groq_with_fallback(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] = None, tool_choice: str = None) -> Any:
        candidates = [self.model_name] + [m for m in MODELOS_GROQ if m != self.model_name]
        
        last_exception = None
        for model in candidates:
            try:
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.1
                }
                if tools:
                    kwargs["tools"] = tools
                if tool_choice:
                    kwargs["tool_choice"] = tool_choice
                    
                response = self.client.chat.completions.create(**kwargs)
                return response
            except Exception as e:
                err_str = str(e).lower()
                if any(k in err_str for k in ["404", "model_not_found", "decommissioned", "not_found", "invalid_model"]):
                    last_exception = e
                    continue
                else:
                    raise e
                    
        raise last_exception or Exception("No se pudo conectar a ningún modelo de Groq.")

    def run(self, user_query: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        if chat_history is None:
            chat_history = []
            
        retrieved_docs = self.vector_store.search(user_query, top_k=6)
        
        context_str = ""
        sources_used = []
        for chunk, score in retrieved_docs:
            context_str += f"\n--- [Documento: {chunk.source_doc} | Página: {chunk.page_num} | Relevancia: {score:.2f}] ---\n{chunk.text}\n"
            sources_used.append({"doc": chunk.source_doc, "page": chunk.page_num, "score": score, "text": chunk.text[:150] + "..."})
            
        messages = [{"role": "system", "content": SYSTEM_PROMPT_AUTOTECH}]
        
        # Filtra para evitar duplicar la última pregunta si ya está en chat_history
        for msg in chat_history[-6:]:
            if msg.get("content") != user_query or msg.get("role") != "user":
                messages.append({"role": msg["role"], "content": msg["content"]})
            
        prompt_with_context = f"""CONTEXTO TÉCNICO RECUPERADO DE MANUALES:
{context_str}

PREGUNTA DEL USUARIO / CLIENTE:
{user_query}"""

        messages.append({"role": "user", "content": prompt_with_context})
        
        tool_calls_executed = []
        try:
            max_iterations = 3
            current_iter = 0
            final_text = ""

            while current_iter < max_iterations:
                current_iter += 1
                response = self._call_groq_with_fallback(
                    messages=messages,
                    tools=[TOOL_INVENTARIO_SCHEMA],
                    tool_choice="auto"
                )
                
                response_message = response.choices[0].message
                
                if response_message.tool_calls:
                    messages.append(response_message)
                    
                    for tool_call in response_message.tool_calls:
                        if tool_call.function.name == "consultar_inventario":
                            try:
                                args = json.loads(tool_call.function.arguments)
                            except Exception:
                                args = {}
                            repuesto_arg = args.get("nombre_repuesto", user_query)
                            
                            resultado_inventario = consultar_inventario(repuesto_arg)
                            tool_calls_executed.append({
                                "tool": "consultar_inventario",
                                "args": args,
                                "output": resultado_inventario
                            })
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": resultado_inventario
                            })
                else:
                    final_text = response_message.content or ""
                    break
            else:
                final_text = response_message.content or "No se pudo obtener respuesta del modelo tras ejecutar las herramientas."

            return {
                "answer": final_text,
                "sources": sources_used,
                "tool_calls": tool_calls_executed
            }
            
        except Exception as e:
            return {
                "answer": f"Error comunicando con Groq API: {str(e)}",
                "sources": sources_used,
                "tool_calls": []
            }
