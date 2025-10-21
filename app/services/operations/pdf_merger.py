import fitz
import os
import uuid
from typing import List
from fastapi import HTTPException
from app.config import settings

class PDFMerger:
    """Serviço para junção de PDFs com otimização"""
    
    @staticmethod
    async def merge_pdfs(file_ids: List[str], output_filename: str = "merged_document") -> str:
        """Junta múltiplos PDFs em um único arquivo"""
        try:
            if len(file_ids) < 2:
                raise HTTPException(400, "É necessário pelo menos 2 arquivos para juntar")
            
            # Criar documento de saída
            merged_doc = fitz.open()
            
            # Adicionar páginas de cada arquivo
            for file_id in file_ids:
                file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
                if not os.path.exists(file_path):
                    raise HTTPException(404, f"Arquivo {file_id} não encontrado")
                
                doc = fitz.open(file_path)
                merged_doc.insert_pdf(doc)
                doc.close()
            
            # Salvar arquivo mesclado
            output_id = str(uuid.uuid4())
            safe_filename = "".join(c for c in output_filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_{safe_filename}.pdf"
            
            merged_doc.save(output_path)
            merged_doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao juntar PDFs: {str(e)}")
    
    @staticmethod
    async def merge_with_custom_order(file_ids: List[str], page_order: List[int], output_filename: str) -> str:
        """Junta PDFs com ordem personalizada de páginas"""
        try:
            if len(file_ids) != len(page_order):
                raise HTTPException(400, "Número de arquivos e ordem de páginas não correspondem")
            
            merged_doc = fitz.open()
            
            for file_id, page_indices in zip(file_ids, page_order):
                file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
                if not os.path.exists(file_path):
                    raise HTTPException(404, f"Arquivo {file_id} não encontrado")
                
                doc = fitz.open(file_path)
                
                if isinstance(page_indices, list):
                    # Lista específica de páginas
                    for page_idx in page_indices:
                        if 0 <= page_idx < len(doc):
                            merged_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
                else:
                    # Todas as páginas
                    merged_doc.insert_pdf(doc)
                
                doc.close()
            
            output_id = str(uuid.uuid4())
            safe_filename = "".join(c for c in output_filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_{safe_filename}.pdf"
            
            merged_doc.save(output_path)
            merged_doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao juntar PDFs com ordem personalizada: {str(e)}")