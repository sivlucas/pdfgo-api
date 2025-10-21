from typing import Dict, Any
from app.services.core.pdf_analyzer import PDFAnalyzer

class QualityValidator:
    """Validador de qualidade pós-processamento"""
    
    @staticmethod
    async def validate_conversion_quality(original_path: str, processed_path: str) -> Dict[str, Any]:
        """Compara qualidade antes e depois do processamento"""
        
        original_analysis = await PDFAnalyzer.enhanced_content_analysis(original_path)
        processed_analysis = await PDFAnalyzer.enhanced_content_analysis(processed_path)
        
        # Calcular métricas de preservação
        preservation_metrics = {
            "text_preservation": QualityValidator._calculate_text_preservation(
                original_analysis, processed_analysis
            ),
            "layout_preservation": QualityValidator._calculate_layout_preservation(
                original_analysis, processed_analysis
            ),
            "image_quality_preservation": QualityValidator._calculate_image_preservation(
                original_analysis, processed_analysis
            ),
            "overall_quality_score": 0.0  # Será calculado
        }
        
        preservation_metrics["overall_quality_score"] = (
            preservation_metrics["text_preservation"] * 0.4 +
            preservation_metrics["layout_preservation"] * 0.3 +
            preservation_metrics["image_quality_preservation"] * 0.3
        )
        
        return {
            "preservation_metrics": preservation_metrics,
            "passed_quality_check": preservation_metrics["overall_quality_score"] >= 0.85,
            "recommendations": QualityValidator._generate_quality_recommendations(preservation_metrics)
        }
    
    @staticmethod
    def _calculate_text_preservation(original: Dict, processed: Dict) -> float:
        """Calcula quanto do texto foi preservado"""
        original_text = sum(page.get("word_count", 0) for page in original["content_types"])
        processed_text = sum(page.get("word_count", 0) for page in processed["content_types"])
        
        if original_text == 0:
            return 1.0  # Não havia texto para preservar
        
        return min(1.0, processed_text / original_text)
    
    @staticmethod
    def _calculate_layout_preservation(original: Dict, processed: Dict) -> float:
        """Calcula preservação do layout"""
        # Implementar cálculo de preservação de layout
        return 0.9  # Placeholder
    
    @staticmethod
    def _calculate_image_preservation(original: Dict, processed: Dict) -> float:
        """Calcula preservação da qualidade das imagens"""
        # Implementar cálculo de preservação de imagens
        return 0.85  # Placeholder
    
    @staticmethod
    def _generate_quality_recommendations(metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nas métricas de qualidade"""
        recommendations = []
        
        if metrics["text_preservation"] < 0.9:
            recommendations.append("Considere usar processamento com OCR para melhor preservação de texto")
        
        if metrics["layout_preservation"] < 0.8:
            recommendations.append("Use modo de preservação de layout para documentos complexos")
        
        if metrics["image_quality_preservation"] < 0.7:
            recommendations.append("Aumente a qualidade de processamento para imagens")
        
        return recommendations