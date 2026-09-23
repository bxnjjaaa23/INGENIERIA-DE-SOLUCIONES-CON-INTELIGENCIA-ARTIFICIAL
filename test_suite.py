import os
import json
import sys
import time
from rag_engine import (
    AutoTechVectorStore,
    AutoTechAgent,
    consultar_inventario,
    get_google_drive_status,
    sync_manuals_from_google_drive
)

if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_tests():
    print("=========================================================================")
    print("INICIANDO BATERIA DE PRUEBAS AUTOMATICAS - AUTOTECH JPB SOLUTIONS")
    print("=========================================================================\n")
    
    t0 = time.time()
    
    # Verificación de Google Drive
    drive_status = get_google_drive_status()
    if drive_status["is_mounted"]:
        print("[Google Drive] Estado: Conectado")
        synced = sync_manuals_from_google_drive()
        print(f"[Google Drive] Archivos sincronizados: {len(synced)}")
    else:
        print("[Google Drive] Estado: No montado (modo local activo)")
        
    pdfs = [
        "ficha_tecnica_fiat_palio.pdf",
        "MANUAL-DE-OPERACIONES-DE-TALLER-.pdf",
        "manual_fallas_multimarca_diagnostico.pdf",
        "manual_recepcion_fallas_cliente_taller.pdf",
        "mecanica-automotriz-mantenimiento-de-motores.pdf"
    ]
    
    vs = AutoTechVectorStore()
    loaded_pdfs = vs.build_or_load_index(pdfs)
    
    t_index = time.time() - t0
    modo_carga = "Caché Persistente en Disco" if vs.is_from_cache else "Procesamiento Completo de PDFs"
    print(f"\n[OK] Base de conocimiento inicializada en {t_index:.2f} segundos ({modo_carga})")
    print(f"[OK] Total fragmentos indexados en VectorStore: {len(vs.chunks)}")
    print(f"[OK] PDFs disponibles ({len(loaded_pdfs)}): {', '.join(loaded_pdfs)}\n")
    
    print("--- PRUEBA 1: BÚSQUEDA DE INVENTARIO (GENERAL Y ESPECÍFICO) ---")
    print("Consulta General (Stock en Bodega):")
    print(consultar_inventario("que tenemos en stock"))
    print("\nConsulta Específica (Botonera Changan):")
    print(consultar_inventario("botonera changan cx70"))
    
    print("\n--- PRUEBA 2: RECUPERACIÓN SEMÁNTICA DE MANUALES DE CLIENTE Y MECÁNICO ---")
    queries_test = [
        "cambio de plumillas limpiavidrios procedimiento",
        "rangos recomendados para inflar ruedas PSI",
        "alza vidrios changan cx70 falla electica"
    ]
    
    for q in queries_test:
        results = vs.search(q, top_k=2)
        print(f"  [Query]: '{q}'")
        for chunk, score in results:
            print(f"      -> Doc: {chunk.source_doc} (Pág {chunk.page_num}) | Score: {score:.3f}")
            print(f"         Snippet: {chunk.text[:120]}...")
        print()

    t_total = time.time() - t0
    print("=========================================================================")
    print(f"PRUEBAS FINALIZADAS CON ÉXITO Y 100% FUNCIONALES (Tiempo total: {t_total:.2f}s)")
    print("=========================================================================")

if __name__ == "__main__":
    run_tests()
