import fitz
import os
import uuid
import base64
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from PIL import Image
import io
from app.config import settings

class PageEditorService:
    """Serviço avançado para edição de páginas PDF"""
    
    @staticmethod
    async def delete_pages(file_id: str, pages_to_delete: List[int]) -> str:
        """Exclui páginas específicas do PDF"""
        try:
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Validar páginas
            for page_num in pages_to_delete:
                if page_num < 1 or page_num > total_pages:
                    raise HTTPException(400, f"Página {page_num} fora do range (1-{total_pages})")
            
            # Criar novo documento excluindo as páginas
            new_doc = fitz.open()
            
            for page_num in range(1, total_pages + 1):
                if page_num not in pages_to_delete:
                    new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
            
            # Salvar arquivo editado
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_pages_removed.pdf"
            new_doc.save(output_path)
            
            doc.close()
            new_doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao excluir páginas: {str(e)}")
    
    @staticmethod
    async def reorder_pages(file_id: str, new_order: List[int]) -> str:
        """Reorganiza páginas em uma nova ordem"""
        try:
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Validar nova ordem
            if len(new_order) != total_pages:
                raise HTTPException(400, f"Nova ordem deve conter {total_pages} páginas")
            
            if set(new_order) != set(range(1, total_pages + 1)):
                raise HTTPException(400, "Nova ordem deve conter todas as páginas exatamente uma vez")
            
            # Criar novo documento com nova ordem
            new_doc = fitz.open()
            
            for page_num in new_order:
                new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
            
            # Salvar arquivo reorganizado
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_reordered.pdf"
            new_doc.save(output_path)
            
            doc.close()
            new_doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao reorganizar páginas: {str(e)}")
    
    @staticmethod
    async def insert_pages(target_file_id: str, source_file_id: str, 
                          insert_after_page: int, source_pages: Optional[List[int]] = None) -> str:
        """Insere páginas de outro PDF em uma posição específica"""
        try:
            target_path = f"{settings.UPLOAD_DIR}/{target_file_id}.pdf"
            source_path = f"{settings.UPLOAD_DIR}/{source_file_id}.pdf"
            
            target_doc = fitz.open(target_path)
            source_doc = fitz.open(source_path)
            
            total_target_pages = len(target_doc)
            total_source_pages = len(source_doc)
            
            # Validar posição de inserção
            if insert_after_page < 0 or insert_after_page > total_target_pages:
                raise HTTPException(400, f"Posição de inserção inválida (0-{total_target_pages})")
            
            # Validar páginas fonte
            if source_pages:
                for page_num in source_pages:
                    if page_num < 1 or page_num > total_source_pages:
                        raise HTTPException(400, f"Página fonte {page_num} fora do range")
            else:
                # Usar todas as páginas se não especificado
                source_pages = list(range(1, total_source_pages + 1))
            
            # Criar novo documento com páginas inseridas
            new_doc = fitz.open()
            
            # Inserir páginas antes da posição
            for page_num in range(1, insert_after_page + 1):
                new_doc.insert_pdf(target_doc, from_page=page_num-1, to_page=page_num-1)
            
            # Inserir páginas do arquivo fonte
            for page_num in source_pages:
                new_doc.insert_pdf(source_doc, from_page=page_num-1, to_page=page_num-1)
            
            # Inserir páginas restantes
            for page_num in range(insert_after_page + 1, total_target_pages + 1):
                new_doc.insert_pdf(target_doc, from_page=page_num-1, to_page=page_num-1)
            
            # Salvar arquivo com páginas inseridas
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_pages_inserted.pdf"
            new_doc.save(output_path)
            
            target_doc.close()
            source_doc.close()
            new_doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao inserir páginas: {str(e)}")
    
    @staticmethod
    async def extract_pages(file_id: str, pages_to_extract: List[int]) -> str:
        """Extrai páginas específicas para um novo PDF"""
        try:
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Validar páginas
            for page_num in pages_to_extract:
                if page_num < 1 or page_num > total_pages:
                    raise HTTPException(400, f"Página {page_num} fora do range")
            
            # Criar novo documento apenas com páginas extraídas
            new_doc = fitz.open()
            
            for page_num in pages_to_extract:
                new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
            
            # Salvar arquivo extraído
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_extracted_pages.pdf"
            new_doc.save(output_path)
            
            doc.close()
            new_doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao extrair páginas: {str(e)}")
    
    @staticmethod
    async def duplicate_pages(file_id: str, pages_to_duplicate: List[int]) -> str:
        """Duplica páginas específicas no PDF"""
        try:
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Validar páginas
            for page_num in pages_to_duplicate:
                if page_num < 1 or page_num > total_pages:
                    raise HTTPException(400, f"Página {page_num} fora do range")
            
            # Criar novo documento com páginas duplicadas
            new_doc = fitz.open()
            
            for page_num in range(1, total_pages + 1):
                # Inserir página original
                new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
                
                # Se esta página deve ser duplicada, inserir novamente
                if page_num in pages_to_duplicate:
                    new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
            
            # Salvar arquivo com páginas duplicadas
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_duplicated_pages.pdf"
            new_doc.save(output_path)
            
            doc.close()
            new_doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao duplicar páginas: {str(e)}")
    
    @staticmethod
    async def rotate_specific_pages(file_id: str, pages_rotation: Dict[int, int]) -> str:
        """Rotaciona páginas específicas com ângulos diferentes"""
        try:
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Validar páginas e rotações
            for page_num, rotation in pages_rotation.items():
                if page_num < 1 or page_num > total_pages:
                    raise HTTPException(400, f"Página {page_num} fora do range")
                if rotation not in [0, 90, 180, 270]:
                    raise HTTPException(400, f"Rotação {rotation} inválida para página {page_num}")
            
            # Aplicar rotações específicas
            for page_num, rotation in pages_rotation.items():
                page = doc[page_num - 1]
                page.set_rotation(rotation)
            
            # Salvar arquivo com rotações aplicadas
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_rotated_specific.pdf"
            doc.save(output_path)
            doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao rotacionar páginas específicas: {str(e)}")
    
    @staticmethod
    async def get_page_thumbnails(file_id: str, size: tuple = (100, 150)) -> List[Dict[str, Any]]:
        """Gera thumbnails pequenas para todas as páginas (interface minimalista)"""
        try:
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            
            thumbnails = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Gerar thumbnail pequena
                mat = fitz.Matrix(0.3, 0.3)  # Zoom bem reduzido
                pix = page.get_pixmap(matrix=mat)
                
                # Converter para base64
                img_base64 = base64.b64encode(pix.tobytes("png")).decode('utf-8')
                
                thumbnails.append({
                    "page_number": page_num + 1,
                    "thumbnail_url": f"data:image/png;base64,{img_base64}",
                    "width": pix.width,
                    "height": pix.height
                })
            
            doc.close()
            return thumbnails
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao gerar thumbnails: {str(e)}")