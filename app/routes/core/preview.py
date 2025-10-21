from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response
import os
from typing import List, Optional
from app.services.core.preview_service import PreviewService
from app.services.operations.page_editor_service import PageEditorService
from app.models.schemas import PreviewResponse, PageThumbnailsResponse
from app.config import settings

router = APIRouter(prefix="/preview", tags=["PDF Preview"])

@router.get("/{file_id}/images", response_model=PreviewResponse)
async def get_pdf_preview(
    file_id: str,
    pages: Optional[str] = Query(None, description="Páginas para pré-visualizar (ex: 1,2,3 ou 1-5)"),
    quality: str = Query("medium", regex="^(low|medium|high)$")
):
    """Gera pré-visualização em imagem das páginas do PDF"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        # Processar parâmetro de páginas
        page_list = []
        if pages:
            if '-' in pages:
                start, end = map(int, pages.split('-'))
                page_list = list(range(start, end + 1))
            else:
                page_list = [int(p) for p in pages.split(',')]
        
        preview_data = await PreviewService.generate_preview(file_path, page_list, quality)
        
        return PreviewResponse(
            file_id=file_id,
            total_pages=preview_data["total_pages"],
            previewed_pages=preview_data["previewed_pages"],
            pages=preview_data["pages"],
            thumbnails=preview_data["thumbnails"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao gerar pré-visualização: {str(e)}")

@router.get("/{file_id}/text")
async def get_text_preview(
    file_id: str,
    pages: Optional[str] = Query(None, description="Páginas para extrair texto"),
    max_chars: int = Query(1000, ge=100, le=5000)
):
    """Extrai pré-visualização de texto do PDF"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        page_list = []
        if pages:
            if '-' in pages:
                start, end = map(int, pages.split('-'))
                page_list = list(range(start, end + 1))
            else:
                page_list = [int(p) for p in pages.split(',')]
        
        text_preview = await PreviewService.extract_text_preview(file_path, page_list, max_chars)
        
        return {
            "file_id": file_id,
            "text_preview": text_preview
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao extrair pré-visualização de texto: {str(e)}")

@router.post("/{file_id}/export-images")
async def export_pages_as_images(
    file_id: str,
    pages: List[int],
    format: str = Query("png", regex="^(png|jpg|jpeg)$"),
    dpi: int = Query(150, ge=72, le=300)
):
    """Exporta páginas específicas como imagens"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        page_images = await PreviewService.generate_page_images(file_path, pages, format, dpi)
        
        # Se for apenas uma imagem, retorna diretamente
        if len(page_images) == 1:
            image_path = page_images[0]["file_path"]
            return FileResponse(
                path=image_path,
                filename=f"page_{page_images[0]['page_number']}.{format}",
                media_type=f"image/{format}"
            )
        
        # Para múltiplas imagens, retornar informações
        return {
            "file_id": file_id,
            "exported_images": page_images,
            "download_urls": [
                f"/api/v1/preview/download/{img['image_id']}" for img in page_images
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao exportar páginas como imagens: {str(e)}")

@router.get("/download/{image_id}")
async def download_image(image_id: str):
    """Download de imagem gerada da pré-visualização"""
    try:
        # Procurar arquivo de imagem
        import glob
        image_files = glob.glob(f"{settings.TEMP_DIR}/{image_id}.*")
        
        if not image_files:
            raise HTTPException(404, "Imagem não encontrada")
        
        image_path = image_files[0]
        format = image_path.split('.')[-1]
        
        return FileResponse(
            path=image_path,
            filename=f"preview_{image_id}.{format}",
            media_type=f"image/{format}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao baixar imagem: {str(e)}")

@router.get("/{file_id}/thumbnail")
async def get_pdf_thumbnail(file_id: str):
    """Gera thumbnail da primeira página do PDF"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        preview_data = await PreviewService.generate_preview(file_path, [1], "low")
        
        if preview_data["pages"]:
            thumbnail_data = preview_data["pages"][0]["preview_url"]
            # Retornar apenas a URL da imagem base64
            return {"thumbnail": thumbnail_data}
        else:
            raise HTTPException(404, "Não foi possível gerar thumbnail")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao gerar thumbnail: {str(e)}")

@router.get("/{file_id}/minimal-editor")
async def get_minimal_editor_data(file_id: str):
    """Obtém todos os dados necessários para o editor minimalista"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        import fitz
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        # Obter thumbnails pequenas
        thumbnails = await PageEditorService.get_page_thumbnails(file_id)
        
        # Obter análise básica de cada página
        page_analysis = []
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text()
            images = page.get_images()
            
            page_analysis.append({
                "page_number": page_num + 1,
                "has_text": len(text.strip()) > 0,
                "image_count": len(images),
                "is_mostly_images": len(images) >= 3 and len(text.strip()) < 100
            })
        
        doc.close()
        
        return {
            "file_id": file_id,
            "total_pages": total_pages,
            "thumbnails": thumbnails,
            "page_analysis": page_analysis,
            "available_operations": [
                "delete", "reorder", "extract", "duplicate", "rotate_specific"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao obter dados do editor: {str(e)}")

@router.get("/{file_id}/page-previews")
async def get_individual_page_previews(file_id: str, pages: str):
    """Obtém pré-visualizações individuais de páginas específicas"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        # Processar lista de páginas
        page_list = [int(p) for p in pages.split(',')]
        
        import fitz
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        previews = []
        for page_num in page_list:
            if 1 <= page_num <= total_pages:
                page = doc[page_num - 1]
                
                # Gerar preview de qualidade média
                mat = fitz.Matrix(1.5, 1.5)
                pix = page.get_pixmap(matrix=mat)
                
                import base64
                img_base64 = base64.b64encode(pix.tobytes("png")).decode('utf-8')
                
                # Extrair texto de preview
                text = page.get_text()
                preview_text = text[:300] + "..." if len(text) > 300 else text
                
                previews.append({
                    "page_number": page_num,
                    "preview_url": f"data:image/png;base64,{img_base64}",
                    "preview_text": preview_text,
                    "width": pix.width,
                    "height": pix.height
                })
        
        doc.close()
        
        return {
            "file_id": file_id,
            "previews": previews
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao obter pré-visualizações individuais: {str(e)}")