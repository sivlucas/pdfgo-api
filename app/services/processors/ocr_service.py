import pdf2image
import pytesseract
from typing import List, Dict, Any
import os
from app.config import settings

class OCRService:
    """Serviço de OCR para PDFs digitalizados"""
    
    @staticmethod
    async def extract_text_from_scanned_pdf(file_path: str) -> str:
        """Usa Tesseract OCR para extrair texto de PDFs digitalizados"""
        try:
            # Converter PDF para imagens
            images = pdf2image.convert_from_path(file_path, dpi=300)
            
            extracted_text = ""
            for i, image in enumerate(images):
                # OCR em cada página
                text = pytesseract.image_to_string(image, lang='por+eng')
                extracted_text += f"--- Página {i+1} ---\n{text}\n"
            
            return extracted_text
        except Exception as e:
            raise Exception(f"Erro no OCR: {str(e)}")
    
    @staticmethod
    async def enhance_ocr_quality(image_path: str) -> str:
        """Melhora a qualidade da imagem para OCR"""
        try:
            from PIL import Image, ImageEnhance, ImageFilter
            import cv2
            import numpy as np
            
            # Abrir imagem
            img = Image.open(image_path)
            
            # Converter para escala de cinza
            img = img.convert('L')
            
            # Aumentar contraste
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Aumentar nitidez
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Aplicar filtro para reduzir ruído
            img = img.filter(ImageFilter.MedianFilter(size=3))
            
            # Salvar imagem melhorada
            enhanced_path = image_path.replace('.', '_enhanced.')
            img.save(enhanced_path, quality=95)
            
            return enhanced_path
            
        except Exception as e:
            # Se houver erro, retorna o caminho original
            return image_path
    
    @staticmethod
    async def detect_ocr_need(file_path: str) -> Dict[str, Any]:
        """Detecta se o PDF precisa de OCR"""
        try:
            import fitz
            
            doc = fitz.open(file_path)
            needs_ocr = False
            confidence_scores = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Se há pouquíssimo texto mas muitas imagens, provavelmente precisa de OCR
                images = page.get_images()
                text_ratio = len(text) / (page.rect.width * page.rect.height) if page.rect.width * page.rect.height > 0 else 0
                
                if len(text.strip()) < 100 and len(images) > 0 and text_ratio < 0.001:
                    needs_ocr = True
                    confidence_scores.append(0.9)
                else:
                    confidence_scores.append(0.1)
            
            doc.close()
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            return {
                "needs_ocr": needs_ocr,
                "confidence": avg_confidence,
                "pages_analyzed": len(confidence_scores)
            }
            
        except Exception as e:
            raise Exception(f"Erro ao detectar necessidade de OCR: {str(e)}")