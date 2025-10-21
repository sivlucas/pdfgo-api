from typing import Dict, Any, List, Optional
from datetime import datetime
from app.config import settings

class ResponseFormatter:
    """Utilitário para formatação de respostas da API"""
    
    @staticmethod
    def format_success_response(
        message: str,
        data: Optional[Dict[str, Any]] = None,
        operation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Formata resposta de sucesso"""
        response = {
            "status": "success",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if data:
            response["data"] = data
        
        if operation_id:
            response["operation_id"] = operation_id
        
        return response
    
    @staticmethod
    def format_error_response(
        error: str,
        details: Optional[str] = None,
        code: str = "INTERNAL_ERROR",
        suggestion: Optional[str] = None
    ) -> Dict[str, Any]:
        """Formata resposta de erro"""
        response = {
            "status": "error",
            "error": error,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            response["details"] = details
        
        if suggestion:
            response["suggestion"] = suggestion
        
        return response
    
    @staticmethod
    def format_operation_response(
        operation_id: str,
        status: str,
        message: str,
        download_url: Optional[str] = None,
        output_files: Optional[List[str]] = None,
        quality_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Formata resposta de operação"""
        response = {
            "operation_id": operation_id,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if download_url:
            response["download_url"] = download_url
        
        if output_files:
            response["output_files"] = output_files
        
        if quality_metrics:
            response["quality_metrics"] = quality_metrics
        
        return response
    
    @staticmethod
    def format_preview_response(
        file_id: str,
        total_pages: int,
        previewed_pages: int,
        pages: List[Dict[str, Any]],
        thumbnails: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Formata resposta de pré-visualização"""
        return {
            "file_id": file_id,
            "total_pages": total_pages,
            "previewed_pages": previewed_pages,
            "pages": pages,
            "thumbnails": thumbnails,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def format_analysis_response(
        file_id: str,
        analysis: Dict[str, Any],
        quality_score: float,
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """Formata resposta de análise"""
        return {
            "file_id": file_id,
            "analysis": analysis,
            "quality_score": quality_score,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def format_upload_response(
        message: str,
        file_id: str,
        filename: str,
        pages: int,
        file_size: int,
        analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Formata resposta de upload"""
        response = {
            "message": message,
            "file_id": file_id,
            "filename": filename,
            "pages": pages,
            "file_size": file_size,
            "timestamp": datetime.now().isoformat()
        }
        
        if analysis:
            response["analysis"] = analysis
        
        return response