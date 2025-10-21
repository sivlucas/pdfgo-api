from fastapi import APIRouter, HTTPException
from app.services.operations.page_editor_service import PageEditorService
from app.models.schemas import (
    PageEditRequest, PageReorderRequest, PageDeleteRequest,
    PageInsertRequest, PageExtractRequest, PageDuplicateRequest,
    PageRotateSpecificRequest, PageThumbnailsResponse,
    OperationResponse
)
import os
from app.config import settings

router = APIRouter(prefix="/editor", tags=["Page Editor"])

@router.post("/delete-pages", response_model=OperationResponse)
async def delete_pages(request: PageDeleteRequest):
    """Exclui páginas específicas do PDF"""
    try:
        output_file = await PageEditorService.delete_pages(
            request.file_id, request.pages_to_delete
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id=f"delete_pages_{request.file_id}",
            status="completed",
            message=f"{len(request.pages_to_delete)} páginas excluídas com sucesso",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao excluir páginas: {str(e)}")

@router.post("/reorder-pages", response_model=OperationResponse)
async def reorder_pages(request: PageReorderRequest):
    """Reorganiza a ordem das páginas do PDF"""
    try:
        output_file = await PageEditorService.reorder_pages(
            request.file_id, request.new_order
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id=f"reorder_pages_{request.file_id}",
            status="completed",
            message="Páginas reorganizadas com sucesso",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao reorganizar páginas: {str(e)}")

@router.post("/insert-pages", response_model=OperationResponse)
async def insert_pages(request: PageInsertRequest):
    """Insere páginas de outro PDF"""
    try:
        output_file = await PageEditorService.insert_pages(
            request.target_file_id,
            request.source_file_id,
            request.insert_after_page,
            request.source_pages
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        source_pages_count = len(request.source_pages) if request.source_pages else "todas"
        
        return OperationResponse(
            operation_id=f"insert_pages_{request.target_file_id}",
            status="completed",
            message=f"{source_pages_count} páginas inseridas após página {request.insert_after_page}",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao inserir páginas: {str(e)}")

@router.post("/extract-pages", response_model=OperationResponse)
async def extract_pages(request: PageExtractRequest):
    """Extrai páginas específicas para um novo PDF"""
    try:
        output_file = await PageEditorService.extract_pages(
            request.file_id, request.pages_to_extract
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id=f"extract_pages_{request.file_id}",
            status="completed",
            message=f"{len(request.pages_to_extract)} páginas extraídas para novo PDF",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao extrair páginas: {str(e)}")

@router.post("/duplicate-pages", response_model=OperationResponse)
async def duplicate_pages(request: PageDuplicateRequest):
    """Duplica páginas específicas no PDF"""
    try:
        output_file = await PageEditorService.duplicate_pages(
            request.file_id, request.pages_to_duplicate
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id=f"duplicate_pages_{request.file_id}",
            status="completed",
            message=f"{len(request.pages_to_duplicate)} páginas duplicadas",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao duplicar páginas: {str(e)}")

@router.post("/rotate-specific", response_model=OperationResponse)
async def rotate_specific_pages(request: PageRotateSpecificRequest):
    """Rotaciona páginas específicas com ângulos diferentes"""
    try:
        output_file = await PageEditorService.rotate_specific_pages(
            request.file_id, request.pages_rotation
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id=f"rotate_specific_{request.file_id}",
            status="completed",
            message=f"{len(request.pages_rotation)} páginas rotacionadas com ângulos específicos",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao rotacionar páginas específicas: {str(e)}")

@router.get("/{file_id}/thumbnails", response_model=PageThumbnailsResponse)
async def get_page_thumbnails(file_id: str):
    """Obtém thumbnails pequenas de todas as páginas para interface minimalista"""
    try:
        file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        
        import fitz
        doc = fitz.open(file_path)
        total_pages = len(doc)
        doc.close()
        
        thumbnails = await PageEditorService.get_page_thumbnails(file_id)
        
        return PageThumbnailsResponse(
            file_id=file_id,
            total_pages=total_pages,
            thumbnails=thumbnails
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao obter thumbnails: {str(e)}")

@router.post("/batch-operations", response_model=OperationResponse)
async def batch_page_operations(request: PageEditRequest):
    """Executa múltiplas operações de edição de páginas em lote"""
    try:
        operation = request.operation
        parameters = request.parameters
        
        if operation == "delete":
            output_file = await PageEditorService.delete_pages(
                request.file_id, parameters.get("pages_to_delete", [])
            )
        elif operation == "reorder":
            output_file = await PageEditorService.reorder_pages(
                request.file_id, parameters.get("new_order", [])
            )
        elif operation == "extract":
            output_file = await PageEditorService.extract_pages(
                request.file_id, parameters.get("pages_to_extract", [])
            )
        elif operation == "duplicate":
            output_file = await PageEditorService.duplicate_pages(
                request.file_id, parameters.get("pages_to_duplicate", [])
            )
        else:
            raise HTTPException(400, f"Operação não suportada: {operation}")
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id=f"batch_{operation}_{request.file_id}",
            status="completed",
            message=f"Operação {operation} executada com sucesso",
            download_url=download_url,
            output_files=[download_url]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao executar operações em lote: {str(e)}")

@router.post("/advanced-rearrange")
async def advanced_page_rearrange(file_id: str, operations: list[dict]):
    """Rearranjo avançado de páginas com múltiplas operações"""
    try:
        current_file_id = file_id
        
        for i, operation in enumerate(operations):
            op_type = operation.get("type")
            
            if op_type == "delete":
                current_file_id = os.path.basename(await PageEditorService.delete_pages(
                    current_file_id, operation.get("pages", [])
                )).split('.')[0]
                
            elif op_type == "reorder":
                current_file_id = os.path.basename(await PageEditorService.reorder_pages(
                    current_file_id, operation.get("new_order", [])
                )).split('.')[0]
                
            elif op_type == "duplicate":
                current_file_id = os.path.basename(await PageEditorService.duplicate_pages(
                    current_file_id, operation.get("pages", [])
                )).split('.')[0]
        
        download_url = f"/api/v1/upload/download/{current_file_id}"
        
        return OperationResponse(
            operation_id=f"advanced_rearrange_{file_id}",
            status="completed",
            message=f"{len(operations)} operações de rearranjo executadas com sucesso",
            download_url=download_url,
            output_files=[download_url]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro no rearranjo avançado de páginas: {str(e)}")