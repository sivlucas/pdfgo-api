from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import aiofiles
import uuid
from app.services.core.pdf_analyzer import PDFAnalyzer
from app.utils.file_processor import FileProcessor
from app.models.schemas import PDFUploadResponse, ErrorResponse
from app.config import settings

router = APIRouter(prefix="/upload", tags=["File Upload"])

@router.post("/pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Faz upload de um arquivo PDF e realiza análise inicial"""
    try:
        # Verificar se é PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Arquivo deve ser PDF")
        
        # Salvar arquivo
        file_data = await FileProcessor.save_uploaded_file(file)
        file_path = file_data["file_path"]
        
        # Realizar análise inicial
        analysis = await PDFAnalyzer.comprehensive_analysis(file_path)
        
        return PDFUploadResponse(
            message="PDF carregado com sucesso",
            file_id=file_data["file_id"],
            filename=file.filename,
            pages=analysis["basic_info"]["pages"],
            file_size=analysis["basic_info"]["file_size"],
            analysis=analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Limpar arquivo em caso de erro
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, f"Erro ao processar arquivo: {str(e)}")

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download de um arquivo processado"""
    try:
        # Procurar arquivo nos outputs
        import glob
        output_files = glob.glob(f"{settings.OUTPUT_DIR}/*{file_id}*.pdf")
        
        if not output_files:
            # Tentar encontrar no uploads
            upload_file = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            if os.path.exists(upload_file):
                output_files = [upload_file]
            else:
                raise HTTPException(404, "Arquivo não encontrado")
        
        file_path = output_files[0]
        filename = os.path.basename(file_path)
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao baixar arquivo: {str(e)}")

@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Remove arquivos temporários"""
    try:
        deleted_files = []
        
        # Remover do uploads
        upload_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
        if os.path.exists(upload_path):
            os.remove(upload_path)
            deleted_files.append("upload")
        
        # Remover dos outputs
        import glob
        output_files = glob.glob(f"{settings.OUTPUT_DIR}/*{file_id}*.pdf")
        for output_file in output_files:
            os.remove(output_file)
            deleted_files.append("output")
        
        return {
            "message": "Arquivos removidos com sucesso",
            "deleted_files": deleted_files
        }
        
    except Exception as e:
        raise HTTPException(500, f"Erro ao remover arquivos: {str(e)}")

@router.get("/cleanup")
async def cleanup_files():
    """Limpa arquivos temporários antigos"""
    try:
        await FileProcessor.cleanup_old_files(max_age_hours=1)
        return {"message": "Limpeza de arquivos temporários concluída"}
    except Exception as e:
        raise HTTPException(500, f"Erro na limpeza de arquivos: {str(e)}")