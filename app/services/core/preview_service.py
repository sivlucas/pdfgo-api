import fitz
import os
import base64
import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from PIL import Image
import io
from app.config import settings

class PreviewService:
    """Serviço para geração de pré-visualizações de PDFs"""
    
    @staticmethod
    async def generate_preview(file_path: str, pages: List[int] = None, 
                             quality: str = "medium") -> Dict[str, Any]:
        """Gera pré-visualizações das páginas do PDF"""
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Definir páginas para pré-visualização
            if not pages:
                # Pré-visualizar no máximo 5 páginas por padrão
                pages_to_preview = list(range(min(5, total_pages)))
            else:
                pages_to_preview = [p-1 for p in pages if 1 <= p <= total_pages]
            
            preview_data = {
                "total_pages": total_pages,
                "previewed_pages": len(pages_to_preview),
                "pages": [],
                "thumbnails": []
            }
            
            # Configurações de qualidade
            zoom_config = {
                "low": 1,
                "medium": 2,
                "high": 3
            }
            zoom = zoom_config.get(quality, 2)
            
            for page_num in pages_to_preview:
                page = doc[page_num]
                
                # Gerar imagem da página
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Converter para base64
                img_data = pix.tobytes("png")
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                # Extrair informações da página
                page_info = {
                    "page_number": page_num + 1,
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "rotation": page.rotation,
                    "preview_url": f"data:image/png;base64,{img_base64}",
                    "content_type": PreviewService._analyze_page_content(page)
                }
                
                preview_data["pages"].append(page_info)
                
                # Gerar thumbnail (menor)
                if len(preview_data["thumbnails"]) < 3:  # Máximo 3 thumbnails
                    thumb_base64 = await PreviewService._generate_thumbnail(page)
                    preview_data["thumbnails"].append({
                        "page": page_num + 1,
                        "thumbnail_url": f"data:image/png;base64,{thumb_base64}"
                    })
            
            doc.close()
            return preview_data
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao gerar pré-visualização: {str(e)}")
    
    @staticmethod
    async def _generate_thumbnail(page, size: tuple = (150, 200)) -> str:
        """Gera thumbnail menor para a página"""
        try:
            # Matriz para thumbnail (zoom menor)
            mat = fitz.Matrix(0.5, 0.5)
            pix = page.get_pixmap(matrix=mat)
            
            # Converter para PIL Image para redimensionar
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Converter de volta para base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_base64
            
        except Exception:
            # Fallback: usar a imagem normal em tamanho menor
            mat = fitz.Matrix(0.3, 0.3)
            pix = page.get_pixmap(matrix=mat)
            img_base64 = base64.b64encode(pix.tobytes("png")).decode('utf-8')
            return img_base64
    
    @staticmethod
    def _analyze_page_content(page) -> str:
        """Analisa o tipo de conteúdo da página para a pré-visualização"""
        try:
            text = page.get_text()
            images = page.get_images()
            
            if len(images) >= 3:
                return "image_heavy"
            elif len(text.split()) > 200:
                return "text_heavy"
            elif page.rotation != 0:
                return "rotated"
            else:
                return "mixed"
        except:
            return "unknown"
    
    @staticmethod
    async def generate_page_images(file_path: str, pages: List[int], 
                                 format: str = "png", dpi: int = 150) -> List[Dict[str, Any]]:
        """Gera imagens de páginas específicas para download"""
        try:
            doc = fitz.open(file_path)
            page_images = []
            
            for page_num in pages:
                if 1 <= page_num <= len(doc):
                    page = doc[page_num - 1]
                    
                    # Calcular matriz baseado no DPI
                    zoom = dpi / 72  # 72 é o DPI padrão do PDF
                    mat = fitz.Matrix(zoom, zoom)
                    
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes(format)
                    
                    # Salvar imagem temporariamente
                    image_id = str(uuid.uuid4())
                    image_path = f"{settings.TEMP_DIR}/{image_id}.{format}"
                    
                    with open(image_path, "wb") as f:
                        f.write(img_data)
                    
                    page_images.append({
                        "page_number": page_num,
                        "image_id": image_id,
                        "format": format,
                        "file_path": image_path,
                        "file_size": len(img_data)
                    })
            
            doc.close()
            return page_images
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao gerar imagens das páginas: {str(e)}")
    
    @staticmethod
    async def extract_text_preview(file_path: str, pages: List[int] = None, 
                                 max_chars: int = 1000) -> Dict[str, Any]:
        """Extrai pré-visualização de texto das páginas"""
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            if not pages:
                pages = list(range(min(3, total_pages)))
            else:
                pages = [p-1 for p in pages if 1 <= p <= total_pages]
            
            text_preview = {
                "total_pages": total_pages,
                "previewed_pages": len(pages),
                "pages": []
            }
            
            for page_num in pages:
                page = doc[page_num]
                text = page.get_text()
                
                # Limitar tamanho do texto
                preview_text = text[:max_chars] + "..." if len(text) > max_chars else text
                
                # Analisar conteúdo do texto
                lines = text.split('\n')
                word_count = len(text.split())
                
                text_preview["pages"].append({
                    "page_number": page_num + 1,
                    "preview_text": preview_text,
                    "word_count": word_count,
                    "line_count": len(lines),
                    "has_tables": PreviewService._detect_tables_in_text(text)
                })
            
            doc.close()
            return text_preview
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao extrair pré-visualização de texto: {str(e)}")
    
    @staticmethod
    def _detect_tables_in_text(text: str) -> bool:
        """Detecta possíveis tabelas no texto"""
        lines = text.split('\n')
        
        # Verificar padrões tabulares
        if len(lines) < 3:
            return False
        
        # Contar linhas com múltiplos espaços ou tabs (indicativo de tabela)
        table_like_lines = 0
        for line in lines:
            if len(line.split()) >= 3 and ('  ' in line or '\t' in line):
                table_like_lines += 1
        
        return table_like_lines >= len(lines) * 0.3  # 30% das linhas parecem tabela