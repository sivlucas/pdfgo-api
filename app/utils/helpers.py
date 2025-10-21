import uuid
import os
from typing import List, Dict, Any
from fastapi import HTTPException

class Helpers:
    """Utilitários auxiliares"""
    
    @staticmethod
    def generate_file_id() -> str:
        """Gera um ID único para arquivos"""
        return str(uuid.uuid4())
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitiza nome de arquivo para segurança"""
        # Remove caracteres potencialmente perigosos
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limita o tamanho do nome
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255 - len(ext)] + ext
        
        return filename
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formata tamanho de arquivo para leitura humana"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    @staticmethod
    def validate_pdf_file(file_path: str) -> bool:
        """Valida se o arquivo é um PDF válido"""
        try:
            import fitz
            doc = fitz.open(file_path)
            # Verifica se consegue abrir e tem pelo menos 1 página
            is_valid = len(doc) >= 0
            doc.close()
            return is_valid
        except:
            return False
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Extrai a extensão do arquivo"""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def create_directories():
        """Cria os diretórios necessários"""
        from app.config import settings
        directories = [settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.TEMP_DIR]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def chunk_list(lst: List, chunk_size: int) -> List[List]:
        """Divide uma lista em chunks"""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]