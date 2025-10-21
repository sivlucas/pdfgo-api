from fastapi import APIRouter, HTTPException
from app.services.operations.pdf_merger import PDFMerger
from app.services.operations.pdf_editor import PDFEditor
from app.models.schemas import MergeRequest, OperationResponse
import os
from app.config import settings

router = APIRouter(prefix="/merge", tags=["Merge PDF"])

@router.post("/simple", response_model=OperationResponse)
async def merge_pdfs_simple(request: MergeRequest):
    """Junta múltiplos PDFs em ordem sequencial"""
    try:
        output_file = await PDFMerger.merge_pdfs(
            request.file_ids, request.output_filename
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id="merge_" + "_".join(request.file_ids),
            status="completed",
            message="PDFs mesclados com sucesso",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao juntar PDFs: {str(e)}")

@router.post("/custom-order", response_model=OperationResponse)
async def merge_pdfs_custom_order(request: MergeRequest):
    """Junta PDFs com ordem personalizada de páginas"""
    try:
        page_order = request.parameters.get("page_order", [])
        if not page_order:
            raise HTTPException(400, "Ordem de páginas não fornecida")
        
        output_file = await PDFMerger.merge_with_custom_order(
            request.file_ids, page_order, request.output_filename
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id="merge_custom_" + "_".join(request.file_ids),
            status="completed",
            message="PDFs mesclados com ordem personalizada",
            download_url=download_url,
            output_files=[download_url]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao juntar PDFs: {str(e)}")

@router.post("/optimized", response_model=OperationResponse)
async def merge_pdfs_optimized(request: MergeRequest):
    """Junta PDFs com otimização de tamanho"""
    try:
        # Primeiro mesclar normalmente
        output_file = await PDFMerger.merge_pdfs(
            request.file_ids, request.output_filename
        )
        
        # Aplicar compressão
        compressed_file = await PDFEditor.compress_pdf(
            os.path.basename(output_file).split('.')[0], "medium"
        )
        
        download_url = f"/api/v1/upload/download/{os.path.basename(compressed_file).split('.')[0]}"
        
        return OperationResponse(
            operation_id="merge_optimized_" + "_".join(request.file_ids),
            status="completed",
            message="PDFs mesclados e otimizados com sucesso",
            download_url=download_url,
            output_files=[download_url],
            quality_metrics={
                "original_size": os.path.getsize(output_file),
                "optimized_size": os.path.getsize(compressed_file),
                "reduction_percent": round((1 - os.path.getsize(compressed_file) / os.path.getsize(output_file)) * 100, 2)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao juntar e otimizar PDFs: {str(e)}")

@router.post("/batch")
async def batch_merge_operations(requests: list[MergeRequest]):
    """Executa múltiplas operações de junção em lote"""
    try:
        results = []
        
        for request in requests:
            try:
                output_file = await PDFMerger.merge_pdfs(
                    request.file_ids, request.output_filename
                )
                
                download_url = f"/api/v1/upload/download/{os.path.basename(output_file).split('.')[0]}"
                
                results.append({
                    "operation_id": f"merge_batch_{'_'.join(request.file_ids)}",
                    "status": "completed",
                    "message": "PDFs mesclados com sucesso",
                    "download_url": download_url,
                    "file_ids": request.file_ids
                })
            except Exception as e:
                results.append({
                    "operation_id": f"merge_batch_{'_'.join(request.file_ids)}",
                    "status": "failed",
                    "message": f"Erro: {str(e)}",
                    "file_ids": request.file_ids
                })
        
        return {
            "batch_results": results,
            "total_operations": len(requests),
            "successful_operations": len([r for r in results if r["status"] == "completed"]),
            "failed_operations": len([r for r in results if r["status"] == "failed"])
        }
        
    except Exception as e:
        raise HTTPException(500, f"Erro ao executar operações em lote: {str(e)}")