import os
from fastapi import HTTPException
from typing import List, Dict, Any

class Validators:
    """Utilitário de validações"""
    
    @staticmethod
    def validate_page_range(page_range: str, total_pages: int) -> List[int]:
        """Valida e converte string de range de páginas para lista"""
        try:
            pages = []
            ranges = page_range.split(',')
            
            for r in ranges:
                if '-' in r:
                    start_end = r.split('-')
                    start = int(start_end[0]) if start_end[0] else 1
                    end = int(start_end[1]) if start_end[1] else total_pages
                    if start < 1 or end > total_pages or start > end:
                        raise ValueError("Range de páginas inválido")
                    pages.extend(range(start, end + 1))
                else:
                    page = int(r)
                    if page < 1 or page > total_pages:
                        raise ValueError("Página fora do range")
                    pages.append(page)
            
            return sorted(set(pages))  # Remove duplicatas e ordena
        except ValueError as e:
            raise HTTPException(400, f"Formato de range inválido: {str(e)}")
    
    @staticmethod
    def validate_file_ids(file_ids: List[str]) -> bool:
        """Valida se todos os file_ids existem"""
        for file_id in file_ids:
            upload_path = f"storage/uploads/{file_id}.pdf"
            if not os.path.exists(upload_path):
                raise HTTPException(404, f"Arquivo {file_id} não encontrado")
        return True
    
    @staticmethod
    def validate_edit_operations(operations: List[Dict[str, Any]]) -> bool:
        """Valida operações de edição"""
        if not operations:
            raise HTTPException(400, "Nenhuma operação fornecida")
        
        valid_operations = ["rotate", "watermark", "metadata", "compress"]
        
        for op in operations:
            op_type = op.get("type")
            if op_type not in valid_operations:
                raise HTTPException(400, f"Operação inválida: {op_type}")
            
            # Validações específicas por operação
            if op_type == "rotate":
                if "pages" not in op or not op["pages"]:
                    raise HTTPException(400, "Rotação requer páginas específicas")
                if op.get("rotation") not in [0, 90, 180, 270]:
                    raise HTTPException(400, "Rotação deve ser 0, 90, 180 ou 270 graus")
            
            elif op_type == "watermark":
                if "text" not in op or not op["text"]:
                    raise HTTPException(400, "Marca d'água requer texto")
        
        return True
    
    @staticmethod
    def validate_page_operations(operation: str, parameters: Dict[str, Any], total_pages: int) -> bool:
        """Valida operações de página"""
        if operation == "delete":
            pages = parameters.get("pages_to_delete", [])
            for page in pages:
                if page < 1 or page > total_pages:
                    raise HTTPException(400, f"Página {page} fora do range (1-{total_pages})")
        
        elif operation == "reorder":
            new_order = parameters.get("new_order", [])
            if len(new_order) != total_pages:
                raise HTTPException(400, f"Nova ordem deve conter {total_pages} páginas")
            if set(new_order) != set(range(1, total_pages + 1)):
                raise HTTPException(400, "Nova ordem deve conter todas as páginas exatamente uma vez")
        
        elif operation == "extract":
            pages = parameters.get("pages_to_extract", [])
            for page in pages:
                if page < 1 or page > total_pages:
                    raise HTTPException(400, f"Página {page} fora do range")
        
        return True
    
    @staticmethod
    def validate_preview_parameters(pages: str, quality: str, format: str) -> bool:
        """Valida parâmetros de pré-visualização"""
        if pages:
            try:
                page_list = [int(p) for p in pages.split(',')]
                if any(p < 1 for p in page_list):
                    raise ValueError("Números de página devem ser positivos")
            except ValueError as e:
                raise HTTPException(400, f"Parâmetro 'pages' inválido: {str(e)}")
        
        if quality not in ["low", "medium", "high"]:
            raise HTTPException(400, "Qualidade deve ser low, medium ou high")
        
        if format not in ["png", "jpg", "jpeg"]:
            raise HTTPException(400, "Formato deve ser png, jpg ou jpeg")
        
        return True