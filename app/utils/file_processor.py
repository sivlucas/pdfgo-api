import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import Dict, Any
from app.config import settings

class FileProcessor:
    """Utilitário para processamento de arquivos"""
    
    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> Dict[str, Any]:
        """Salva arquivo enviado e retorna metadados"""
        try:
            # Verificar extensão
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(400, "Arquivo deve ser PDF")
            
            # Gerar ID único
            file_id = str(uuid.uuid4())
            file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.pdf")
            
            # Salvar arquivo
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                if len(content) > settings.MAX_FILE_SIZE:
                    raise HTTPException(400, f"Arquivo muito grande. Máximo: {settings.MAX_FILE_SIZE // (1024 * 1024)}MB")
                await f.write(content)
            
            return {
                "file_id": file_id,
                "filename": file.filename,
                "file_path": file_path,
                "file_size": len(content)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Erro ao processar arquivo: {str(e)}")
    
    @staticmethod
    def get_file_path(file_id: str, directory: str = "uploads") -> str:
        """Retorna caminho do arquivo pelo ID"""
        if directory == "uploads":
            file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.pdf")
        elif directory == "outputs":
            file_path = os.path.join(settings.OUTPUT_DIR, f"{file_id}.pdf")
        else:
            file_path = os.path.join(directory, f"{file_id}.pdf")
            
        if not os.path.exists(file_path):
            raise HTTPException(404, "Arquivo não encontrado")
        return file_path
    
    @staticmethod
    def cleanup_file(file_path: str):
        """Remove arquivo temporário"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass  # Ignora erros na limpeza
    
    @staticmethod
    def validate_file_exists(file_id: str, directory: str = "uploads") -> bool:
        """Valida se o arquivo existe"""
        if directory == "uploads":
            file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.pdf")
        elif directory == "outputs":
            file_path = os.path.join(settings.OUTPUT_DIR, f"{file_id}.pdf")
        else:
            file_path = os.path.join(directory, f"{file_id}.pdf")
            
        return os.path.exists(file_path)
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Retorna informações do arquivo"""
        try:
            import fitz
            doc = fitz.open(file_path)
            info = {
                "pages": len(doc),
                "file_size": os.path.getsize(file_path),
                "metadata": doc.metadata
            }
            doc.close()
            return info
        except Exception as e:
            raise HTTPException(500, f"Erro ao obter informações do arquivo: {str(e)}")
    
    @staticmethod
    async def cleanup_old_files(max_age_hours: int = 24):
        """Limpa arquivos antigos dos diretórios temporários"""
        import time
        import glob
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        # Limpar uploads
        for file_path in glob.glob(f"{settings.UPLOAD_DIR}/*.pdf"):
            if os.path.getctime(file_path) < current_time - max_age_seconds:
                try:
                    os.remove(file_path)
                except:
                    pass
        
        # Limpar outputs
        for file_path in glob.glob(f"{settings.OUTPUT_DIR}/*.pdf"):
            if os.path.getctime(file_path) < current_time - max_age_seconds:
                try:
                    os.remove(file_path)
                except:
                    pass
        
        # Limpar temp
        for file_path in glob.glob(f"{settings.TEMP_DIR}/*"):
            if os.path.getctime(file_path) < current_time - max_age_seconds:
                try:
                    os.remove(file_path)
                except:
                    pass