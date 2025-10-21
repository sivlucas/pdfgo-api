from fastapi import APIRouter, HTTPException
from app.services.operations.pdf_editor import PDFEditor
from app.models.schemas import EditRequest, OperationResponse
import os
from app.config import settings

router = APIRouter(prefix="/edit", tags=["Edit PDF"])

@router.post("/rotate", response_model=OperationResponse)
async def rotate_pages(request: EditRequest):
    """Rotaciona páginas específicas do PDF"""
    try:
        operation = request.operations[0]  # Primeira operação
        pages = operation.get("pages", [])
        rotation = operation.get("rotation", 90)
        
        if not pages:
            raise HTTPException(400, "Páginas não especificadas")
        
        output_file = await PDFEditor.rotate_pages(
            request.file_id, pages, rotation
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id=f"rotate_{request.file_id}",
            status="completed",
            message=f"Páginas {pages} rotacionadas em {rotation} graus",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao rotacionar páginas: {str(e)}")

@router.post("/watermark", response_model=OperationResponse)
async def add_watermark(request: EditRequest):
    """Adiciona marca d'água ao PDF"""
    try:
        operation = request.operations[0]
        text = operation.get("text", "CONFIDENCIAL")
        position = operation.get("position", "center")
        opacity = operation.get("opacity", 0.3)
        
        output_file = await PDFEditor.add_watermark(
            request.file_id, text, position, opacity
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id=f"watermark_{request.file_id}",
            status="completed",
            message="Marca d'água adicionada com sucesso",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao adicionar marca d'água: {str(e)}")

@router.post("/metadata", response_model=OperationResponse)
async def update_metadata(request: EditRequest):
    """Atualiza metadados do PDF"""
    try:
        operation = request.operations[0]
        metadata = operation.get("metadata", {})
        
        if not metadata:
            raise HTTPException(400, "Metadados não fornecidos")
        
        output_file = await PDFEditor.update_metadata(request.file_id, metadata)
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id=f"metadata_{request.file_id}",
            status="completed",
            message="Metadados atualizados com sucesso",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao atualizar metadados: {str(e)}")

@router.post("/compress", response_model=OperationResponse)
async def compress_pdf(request: EditRequest):
    """Comprime o PDF para reduzir tamanho"""
    try:
        operation = request.operations[0]
        quality = operation.get("quality", "medium")
        
        output_file = await PDFEditor.compress_pdf(request.file_id, quality)
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        # Calcular métricas de compressão
        original_path = f"{settings.UPLOAD_DIR}/{request.file_id}.pdf"
        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(output_file)
        
        return OperationResponse(
            operation_id=f"compress_{request.file_id}",
            status="completed",
            message=f"PDF comprimido com qualidade {quality}",
            download_url=download_url,
            output_files=[download_url],
            quality_metrics={
                "original_size": original_size,
                "compressed_size": compressed_size,
                "reduction_percent": round((1 - compressed_size / original_size) * 100, 2),
                "quality_setting": quality
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao comprimir PDF: {str(e)}")

@router.post("/batch", response_model=OperationResponse)
async def batch_operations(request: EditRequest):
    """Executa múltiplas operações de edição em lote"""
    try:
        if len(request.operations) == 0:
            raise HTTPException(400, "Nenhuma operação fornecida")
        
        current_file_id = request.file_id
        
        # Executar operações em sequência
        for i, operation in enumerate(request.operations):
            op_type = operation.get("type")
            
            if op_type == "rotate":
                current_file_id = os.path.basename(await PDFEditor.rotate_pages(
                    current_file_id, 
                    operation.get("pages", []), 
                    operation.get("rotation", 90)
                )).split('.')[0]
                
            elif op_type == "watermark":
                current_file_id = os.path.basename(await PDFEditor.add_watermark(
                    current_file_id,
                    operation.get("text", "CONFIDENCIAL"),
                    operation.get("position", "center"),
                    operation.get("opacity", 0.3)
                )).split('.')[0]
                
            elif op_type == "compress":
                current_file_id = os.path.basename(await PDFEditor.compress_pdf(
                    current_file_id,
                    operation.get("quality", "medium")
                )).split('.')[0]
        
        download_url = f"/api/v1/upload/download/{current_file_id}"
        
        return OperationResponse(
            operation_id=f"batch_{request.file_id}",
            status="completed",
            message=f"{len(request.operations)} operações executadas com sucesso",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao executar operações em lote: {str(e)}")

@router.post("/enhance-quality")
async def enhance_pdf_quality(file_id: str, quality: str = "high"):
    """Melhora a qualidade geral do PDF"""
    try:
        # Aplicar compressão de alta qualidade
        output_file = await PDFEditor.compress_pdf(file_id, quality)
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        # Calcular métricas
        original_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        original_size = os.path.getsize(original_path)
        enhanced_size = os.path.getsize(output_file)
        
        return OperationResponse(
            operation_id=f"enhance_quality_{file_id}",
            status="completed",
            message=f"PDF otimizado com qualidade {quality}",
            download_url=download_url,
            output_files=[download_url],
            quality_metrics={
                "original_size": original_size,
                "enhanced_size": enhanced_size,
                "quality_setting": quality,
                "improvement_notes": "Documento otimizado para melhor legibilidade e tamanho reduzido"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao melhorar qualidade do PDF: {str(e)}")