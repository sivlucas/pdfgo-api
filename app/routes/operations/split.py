from fastapi import APIRouter, HTTPException
from app.services.operations.pdf_splitter import PDFSplitter
from app.models.schemas import SplitRequest, OperationResponse
import os
from app.config import settings

router = APIRouter(prefix="/split", tags=["Split PDF"])

@router.post("/page-range", response_model=OperationResponse)
async def split_by_page_range(request: SplitRequest):
    """Divide PDF por ranges de páginas específicos"""
    try:
        page_ranges = request.parameters.get("ranges", [])
        if not page_ranges:
            raise HTTPException(400, "Ranges de páginas não fornecidos")
        
        output_files = await PDFSplitter.split_by_page_range(
            request.file_id, page_ranges
        )
        
        # Gerar URLs de download
        download_urls = [
            f"/api/v1/upload/download/{os.path.basename(f).split('.')[0]}"
            for f in output_files
        ]
        
        return OperationResponse(
            operation_id=request.file_id,
            status="completed",
            message=f"PDF dividido em {len(output_files)} arquivos",
            download_url=download_urls[0] if len(download_urls) == 1 else None,
            output_files=download_urls
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao dividir PDF: {str(e)}")

@router.post("/every-n-pages", response_model=OperationResponse)
async def split_by_every_n_pages(request: SplitRequest):
    """Divide PDF a cada N páginas"""
    try:
        n = request.parameters.get("n", 1)
        if not isinstance(n, int) or n < 1:
            raise HTTPException(400, "N deve ser um número inteiro positivo")
        
        # Usar a função de range com páginas sequenciais
        file_path = f"{settings.UPLOAD_DIR}/{request.file_id}.pdf"
        import fitz
        doc = fitz.open(file_path)
        total_pages = len(doc)
        doc.close()
        
        page_ranges = []
        for start in range(1, total_pages + 1, n):
            end = min(start + n - 1, total_pages)
            page_ranges.append(f"{start}-{end}")
        
        output_files = await PDFSplitter.split_by_page_range(request.file_id, page_ranges)
        
        download_urls = [
            f"/api/v1/upload/download/{os.path.basename(f).split('.')[0]}"
            for f in output_files
        ]
        
        return OperationResponse(
            operation_id=request.file_id,
            status="completed",
            message=f"PDF dividido em {len(output_files)} arquivos",
            download_url=download_urls[0] if len(download_urls) == 1 else None,
            output_files=download_urls
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao dividir PDF: {str(e)}")

@router.post("/bookmarks", response_model=OperationResponse)
async def split_by_bookmarks(request: SplitRequest):
    """Divide PDF por bookmarks (tópicos)"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{request.file_id}.pdf"
        doc = fitz.open(file_path)
        
        # Extrair bookmarks
        toc = doc.get_toc()
        if not toc:
            raise HTTPException(400, "PDF não contém bookmarks")
        
        output_files = []
        
        for i, (level, title, page) in enumerate(toc):
            # Criar novo documento com página do bookmark
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page-1, to_page=page-1)
            
            # Sanitizar título para nome de arquivo
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title[:50]  # Limitar tamanho
            
            import uuid
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_{safe_title}.pdf"
            new_doc.save(output_path)
            new_doc.close()
            
            output_files.append(output_path)
        
        doc.close()
        
        download_urls = [
            f"/api/v1/upload/download/{os.path.basename(f).split('.')[0]}"
            for f in output_files
        ]
        
        return OperationResponse(
            operation_id=request.file_id,
            status="completed",
            message=f"PDF dividido em {len(output_files)} arquivos por bookmarks",
            download_url=download_urls[0] if len(download_urls) == 1 else None,
            output_files=download_urls
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao dividir PDF por bookmarks: {str(e)}")

@router.post("/content-analysis", response_model=OperationResponse)
async def split_by_content_analysis(request: SplitRequest):
    """Divide PDF baseado em análise inteligente de conteúdo"""
    try:
        output_files = await PDFSplitter.split_by_content_analysis(
            request.file_id, request.parameters
        )
        
        download_urls = [
            f"/api/v1/upload/download/{os.path.basename(f).split('.')[0]}"
            for f in output_files
        ]
        
        return OperationResponse(
            operation_id=request.file_id,
            status="completed",
            message=f"PDF dividido em {len(output_files)} arquivos por análise de conteúdo",
            download_url=download_urls[0] if len(download_urls) == 1 else None,
            output_files=download_urls
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro na divisão por análise de conteúdo: {str(e)}")