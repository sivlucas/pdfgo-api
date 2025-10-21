from fastapi import APIRouter, HTTPException
from app.services.core.pdf_analyzer import PDFAnalyzer
from app.services.core.quality_engine import QualityEngine
from app.models.schemas import AnalysisResponse
import os
from app.config import settings

router = APIRouter(prefix="/analyze", tags=["PDF Analysis"])

@router.get("/{file_id}", response_model=AnalysisResponse)
async def analyze_pdf(file_id: str):
    """Realiza análise completa e detalhada do PDF"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        analysis = await PDFAnalyzer.comprehensive_analysis(file_path)
        
        return AnalysisResponse(
            file_id=file_id,
            analysis=analysis,
            quality_score=analysis["quality_assessment"]["quality_score"],
            recommendations=analysis["recommendations"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro na análise do PDF: {str(e)}")

@router.get("/{file_id}/quality")
async def get_pdf_quality(file_id: str):
    """Retorna métricas de qualidade do PDF"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        quality_metrics = QualityEngine.analyze_pdf_quality(file_path)
        
        return {
            "file_id": file_id,
            "quality_metrics": quality_metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao analisar qualidade: {str(e)}")

@router.get("/{file_id}/content")
async def get_pdf_content(file_id: str):
    """Analisa o conteúdo do PDF (texto, imagens, tabelas)"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        import fitz
        doc = fitz.open(file_path)
        
        content_analysis = {
            "total_pages": len(doc),
            "pages": []
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            images = page.get_images()
            
            page_analysis = {
                "page_number": page_num + 1,
                "word_count": len(text.split()),
                "image_count": len(images),
                "has_tables": len(text.split('\n')) > 10 and '  ' in text,
                "preview_text": text[:200] + "..." if len(text) > 200 else text
            }
            
            content_analysis["pages"].append(page_analysis)
        
        doc.close()
        return content_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao analisar conteúdo: {str(e)}")

@router.get("/{file_id}/ocr-check")
async def check_ocr_need(file_id: str):
    """Verifica se o PDF precisa de OCR"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        from app.services.processors.ocr_service import OCRService
        ocr_analysis = await OCRService.detect_ocr_need(file_path)
        
        return {
            "file_id": file_id,
            "ocr_analysis": ocr_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao verificar necessidade de OCR: {str(e)}")