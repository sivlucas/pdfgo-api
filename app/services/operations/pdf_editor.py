import fitz
import os
import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from app.config import settings

class PDFEditor:
    """Serviço para edição avançada de PDFs"""
    
    @staticmethod
    async def rotate_pages(file_id: str, pages: List[int], rotation: int) -> str:
        """Rotaciona páginas específicas do PDF"""
        try:
            if rotation not in [0, 90, 180, 270]:
                raise HTTPException(400, "Rotação deve ser 0, 90, 180 ou 270 graus")
            
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Validar páginas
            for page_num in pages:
                if page_num < 1 or page_num > total_pages:
                    raise HTTPException(400, f"Página {page_num} fora do range (1-{total_pages})")
                
                # Aplicar rotação (subtrair 1 para índice base 0)
                page = doc[page_num - 1]
                page.set_rotation(rotation)
            
            # Salvar arquivo editado
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_rotated.pdf"
            doc.save(output_path)
            doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao rotacionar páginas: {str(e)}")
    
    @staticmethod
    async def add_watermark(file_id: str, watermark_text: str, 
                          position: str = "center", opacity: float = 0.3) -> str:
        """Adiciona marca d'água ao PDF"""
        try:
            if opacity < 0 or opacity > 1:
                raise HTTPException(400, "Opacidade deve estar entre 0 e 1")
            
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Calcular posição
                rect = page.rect
                if position == "center":
                    text_position = fitz.Point(rect.width / 2, rect.height / 2)
                elif position == "top-left":
                    text_position = fitz.Point(50, 50)
                elif position == "top-right":
                    text_position = fitz.Point(rect.width - 100, 50)
                elif position == "bottom-left":
                    text_position = fitz.Point(50, rect.height - 50)
                elif position == "bottom-right":
                    text_position = fitz.Point(rect.width - 100, rect.height - 50)
                else:
                    text_position = fitz.Point(rect.width / 2, rect.height / 2)
                
                # Inserir texto da marca d'água
                page.insert_text(
                    text_position,
                    watermark_text,
                    fontsize=48,
                    color=(0.5, 0.5, 0.5),  # Cinza
                    rotate=45,
                    opacity=opacity
                )
            
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_watermarked.pdf"
            doc.save(output_path)
            doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao adicionar marca d'água: {str(e)}")
    
    @staticmethod
    async def update_metadata(file_id: str, metadata: Dict[str, str]) -> str:
        """Atualiza metadados do PDF"""
        try:
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            
            # Atualizar metadados
            current_metadata = doc.metadata
            current_metadata.update(metadata)
            
            # Salvar com novos metadados
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_updated.pdf"
            doc.save(output_path, metadata=current_metadata)
            doc.close()
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao atualizar metadados: {str(e)}")
    
    @staticmethod
    async def compress_pdf(file_id: str, quality: str = "medium") -> str:
        """Comprime o PDF para reduzir tamanho"""
        try:
            if quality not in ["low", "medium", "high"]:
                raise HTTPException(400, "Qualidade deve ser low, medium ou high")
            
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            
            # Configurações de compressão baseadas na qualidade
            compress_settings = {
                "low": {"images": 72, "graphics": 72},
                "medium": {"images": 150, "graphics": 150},
                "high": {"images": 300, "graphics": 300}
            }
            
            settings_config = compress_settings[quality]
            
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_compressed.pdf"
            
            # Salvar com compressão
            doc.save(output_path, 
                    garbage=4,  # Remover objetos não utilizados
                    deflate=True,  # Comprimir
                    clean=True,
                    dpi=settings_config["images"])
            
            doc.close()
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao comprimir PDF: {str(e)}")