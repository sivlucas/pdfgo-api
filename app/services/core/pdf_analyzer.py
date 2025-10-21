import fitz
import os
from typing import Dict, Any, List, Tuple
from app.services.core.quality_engine import QualityEngine
from app.config import settings

class PDFAnalyzer:
    """Serviço avançado de análise de PDFs"""
    
    @staticmethod
    async def comprehensive_analysis(file_path: str) -> Dict[str, Any]:
        """Realiza análise completa do PDF"""
        try:
            doc = fitz.open(file_path)
            analysis = {
                "basic_info": {},
                "content_analysis": {},
                "structure_analysis": {},
                "quality_assessment": {},
                "recommendations": []
            }
            
            # Informações básicas
            analysis["basic_info"] = PDFAnalyzer._get_basic_info(doc, file_path)
            
            # Análise de conteúdo
            analysis["content_analysis"] = PDFAnalyzer._analyze_content(doc)
            
            # Análise estrutural
            analysis["structure_analysis"] = PDFAnalyzer._analyze_structure(doc)
            
            # Avaliação de qualidade
            analysis["quality_assessment"] = QualityEngine.analyze_pdf_quality(file_path)
            
            # Recomendações
            analysis["recommendations"] = PDFAnalyzer._generate_recommendations(analysis)
            
            doc.close()
            return analysis
            
        except Exception as e:
            raise Exception(f"Erro na análise do PDF: {str(e)}")
    
    @staticmethod
    def _get_basic_info(doc, file_path: str) -> Dict[str, Any]:
        """Extrai informações básicas do PDF"""
        metadata = doc.metadata
        return {
            "pages": len(doc),
            "file_size": os.path.getsize(file_path),
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", "")
        }
    
    @staticmethod
    def _analyze_content(doc) -> Dict[str, Any]:
        """Analisa o conteúdo do PDF"""
        content_analysis = {
            "text_pages": 0,
            "image_pages": 0,
            "mixed_pages": 0,
            "forms_detected": 0,
            "tables_detected": 0,
            "page_details": []
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_analysis = PDFAnalyzer._analyze_page_content(page, page_num)
            content_analysis["page_details"].append(page_analysis)
            
            # Contar tipos de página
            if page_analysis["content_type"] == "text":
                content_analysis["text_pages"] += 1
            elif page_analysis["content_type"] == "image":
                content_analysis["image_pages"] += 1
            else:
                content_analysis["mixed_pages"] += 1
            
            content_analysis["tables_detected"] += page_analysis["tables_count"]
            content_analysis["forms_detected"] += page_analysis["forms_count"]
        
        return content_analysis
    
    @staticmethod
    def _analyze_page_content(page, page_num: int) -> Dict[str, Any]:
        """Analisa o conteúdo de uma página específica"""
        # Extrair texto
        text = page.get_text()
        text_blocks = page.get_text("blocks")
        
        # Extrair imagens
        image_list = page.get_images()
        
        # Detectar tabelas
        tables = QualityEngine.detect_tables_in_page(page)
        
        # Determinar tipo de conteúdo
        content_type = PDFAnalyzer._determine_content_type(
            len(text_blocks), len(image_list), len(tables), len(text)
        )
        
        return {
            "page_number": page_num + 1,
            "content_type": content_type,
            "text_blocks": len(text_blocks),
            "images": len(image_list),
            "tables_count": len(tables),
            "forms_count": PDFAnalyzer._count_form_elements(page),
            "has_headers": PDFAnalyzer._detect_headers_footers(page, "header"),
            "has_footers": PDFAnalyzer._detect_headers_footers(page, "footer"),
            "word_count": len(text.split()),
            "table_details": tables
        }
    
    @staticmethod
    def _determine_content_type(text_blocks: int, images: int, tables: int, text_length: int) -> str:
        """Determina o tipo predominante de conteúdo na página"""
        if text_blocks > 10 and text_length > 500:
            return "text"
        elif images >= 3 and text_blocks < 5:
            return "image"
        elif tables >= 1:
            return "table"
        elif text_blocks <= 2 and images <= 1:
            return "form"
        else:
            return "mixed"
    
    @staticmethod
    def _count_form_elements(page) -> int:
        """Conta elementos de formulário na página"""
        try:
            widgets = page.widgets
            return len(list(widgets))
        except:
            return 0
    
    @staticmethod
    def _detect_headers_footers(page, element_type: str) -> bool:
        """Detecta cabeçalhos ou rodapés na página"""
        text_blocks = page.get_text("blocks")
        page_height = page.rect.height
        
        for block in text_blocks:
            y_position = block[1]  # Coordenada y do bloco
            
            if element_type == "header" and y_position < 100:  # Topo da página
                return True
            elif element_type == "footer" and y_position > page_height - 100:  # Base da página
                return True
        
        return False
    
    @staticmethod
    def _analyze_structure(doc) -> Dict[str, Any]:
        """Analisa a estrutura do documento"""
        structure = {
            "has_bookmarks": False,
            "has_links": False,
            "has_annotations": False,
            "page_layouts": [],
            "outline": []
        }
        
        # Verificar bookmarks/toc
        toc = doc.get_toc()
        if toc:
            structure["has_bookmarks"] = True
            structure["outline"] = toc
        
        # Analisar layout das páginas
        for page_num in range(len(doc)):
            page = doc[page_num]
            structure["page_layouts"].append({
                "page": page_num + 1,
                "width": page.rect.width,
                "height": page.rect.height,
                "rotation": page.rotation
            })
            
            # Verificar links e anotações
            links = page.get_links()
            annotations = page.annots()
            
            if links:
                structure["has_links"] = True
            if annotations:
                structure["has_annotations"] = True
        
        return structure
    
    @staticmethod
    def _generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        basic_info = analysis["basic_info"]
        content_analysis = analysis["content_analysis"]
        quality = analysis["quality_assessment"]
        
        # Recomendações baseadas no número de páginas
        if basic_info["pages"] > 50:
            recommendations.append("Documento extenso - considere dividir para melhor processamento")
        
        # Recomendações baseadas em conteúdo
        if content_analysis["image_pages"] > content_analysis["text_pages"]:
            recommendations.append("Documento com muitas imagens - use compressão para otimizar tamanho")
        
        if content_analysis["tables_detected"] > 0:
            recommendations.append("Tabelas detectadas - use extração específica para melhor qualidade")
        
        # Recomendações de qualidade
        if quality["quality_score"] < 70:
            recommendations.append("Qualidade abaixo do ideal - considere reprocessar o documento de origem")
        
        if not analysis["structure_analysis"]["has_bookmarks"] and basic_info["pages"] > 10:
            recommendations.append("Documento longo sem bookmarks - adicione índice para melhor navegação")
        
        return recommendations
    
    @staticmethod
    async def enhanced_content_analysis(file_path: str) -> Dict[str, Any]:
        """Análise MUITO mais precisa do conteúdo"""
        try:
            doc = fitz.open(file_path)
            analysis = {
                "content_types": [],
                "needs_ocr": False,
                "layout_complexity": "simple",
                "recommended_processing": "standard"
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Análise AVANÇADA da página
                page_analysis = await PDFAnalyzer._advanced_page_analysis(page, page_num)
                analysis["content_types"].append(page_analysis)
                
                # Detectar se precisa de OCR
                if page_analysis["text_quality"] < 0.3 and page_analysis["image_density"] > 0.5:
                    analysis["needs_ocr"] = True
                    analysis["recommended_processing"] = "ocr_enhanced"
                
                # Avaliar complexidade do layout
                if page_analysis["table_count"] > 0 or page_analysis["column_count"] > 1:
                    analysis["layout_complexity"] = "complex"
                    analysis["recommended_processing"] = "layout_preservation"
            
            doc.close()
            return analysis
            
        except Exception as e:
            raise Exception(f"Erro na análise avançada: {str(e)}")
    
    @staticmethod
    async def _advanced_page_analysis(page, page_num: int) -> Dict[str, Any]:
        """Análise MUITO detalhada de cada página"""
        # Extrair texto com diferentes métodos
        raw_text = page.get_text()
        dict_text = page.get_text("dict")
        
        # Calcular qualidade do texto
        text_quality = PDFAnalyzer._calculate_text_quality(raw_text, dict_text)
        
        # Detectar colunas
        column_count = PDFAnalyzer._detect_columns(dict_text)
        
        # Analisar imagens
        image_analysis = PDFAnalyzer._analyze_images(page.get_images())
        
        return {
            "page_number": page_num + 1,
            "text_quality": text_quality,
            "word_count": len(raw_text.split()),
            "column_count": column_count,
            "image_density": image_analysis["density"],
            "table_count": len(QualityEngine.detect_tables_in_page(page)),
            "needs_ocr": text_quality < 0.5,
            "recommended_dpi": 300 if image_analysis["needs_quality"] else 150
        }
    
    @staticmethod
    def _calculate_text_quality(raw_text: str, dict_text: Dict) -> float:
        """Calcula a qualidade do texto extraído"""
        if not raw_text.strip():
            return 0.0
        
        # Verificar se o texto tem estrutura
        lines = raw_text.split('\n')
        avg_line_length = sum(len(line.strip()) for line in lines) / len(lines) if lines else 0
        
        # Verificar caracteres especiais (indicativo de OCR ruim)
        special_chars = sum(1 for char in raw_text if not char.isalnum() and not char.isspace())
        special_ratio = special_chars / len(raw_text) if raw_text else 0
        
        quality = 1.0
        if avg_line_length < 10:
            quality *= 0.7
        if special_ratio > 0.3:
            quality *= 0.8
        
        return max(0.0, min(1.0, quality))
    
    @staticmethod
    def _detect_columns(text_dict: Dict) -> int:
        """Detecta número de colunas no texto"""
        try:
            blocks = text_dict.get("blocks", [])
            x_positions = []
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            x_positions.append(span["bbox"][0])  # Posição x
            
            if not x_positions:
                return 1
            
            # Agrupar posições x para detectar colunas
            import numpy as np
            from sklearn.cluster import KMeans
            
            x_array = np.array(x_positions).reshape(-1, 1)
            kmeans = KMeans(n_clusters=min(3, len(set(x_positions))), random_state=42)
            kmeans.fit(x_array)
            
            return len(set(kmeans.labels_))
        except:
            return 1
    
    @staticmethod
    def _analyze_images(images: List) -> Dict[str, Any]:
        """Analisa as imagens do PDF"""
        if not images:
            return {"density": 0.0, "needs_quality": False}
        
        total_size = sum(img[2] for img in images)  # Tamanho estimado
        density = min(1.0, total_size / (1024 * 1024))  # Normalizar para 0-1
        
        return {
            "density": density,
            "needs_quality": density > 0.5,  # Muitas imagens precisam de qualidade
            "total_images": len(images)
        }