import fitz
import os
import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List, Tuple
from sklearn.cluster import KMeans
import pytesseract
from app.config import settings

class QualityEngine:
    """Motor de análise de qualidade para garantir conversões precisas"""
    
    @staticmethod
    def analyze_pdf_quality(file_path: str) -> Dict[str, Any]:
        """Analisa a qualidade do PDF e retorna métricas detalhadas"""
        try:
            doc = fitz.open(file_path)
            metrics = {
                "total_pages": len(doc),
                "file_size": os.path.getsize(file_path),
                "page_sizes": [],
                "content_analysis": [],
                "text_density": 0,
                "image_count": 0,
                "table_count": 0,
                "form_count": 0,
                "quality_score": 0
            }
            
            total_text_blocks = 0
            total_images = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_metrics = QualityEngine._analyze_page(page, page_num)
                metrics["content_analysis"].append(page_metrics)
                metrics["page_sizes"].append({
                    "width": page.rect.width,
                    "height": page.rect.height
                })
                total_text_blocks += page_metrics["text_blocks"]
                total_images += page_metrics["images"]
            
            # Calcular métricas gerais
            metrics["text_density"] = total_text_blocks / len(doc) if doc else 0
            metrics["image_count"] = total_images
            metrics["quality_score"] = QualityEngine._calculate_quality_score(metrics)
            
            doc.close()
            return metrics
            
        except Exception as e:
            raise Exception(f"Erro na análise de qualidade: {str(e)}")
    
    @staticmethod
    def _analyze_page(page, page_num: int) -> Dict[str, Any]:
        """Analisa uma página individual do PDF"""
        page_metrics = {
            "page_number": page_num + 1,
            "text_blocks": 0,
            "images": 0,
            "tables": 0,
            "forms": 0,
            "resolution": 0,
            "content_type": "unknown"
        }
        
        # Extrair texto
        text = page.get_text()
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block["type"] == 0:  # Text block
                page_metrics["text_blocks"] += 1
            elif block["type"] == 1:  # Image block
                page_metrics["images"] += 1
        
        # Determinar tipo de conteúdo predominante
        if page_metrics["text_blocks"] > 5 and page_metrics["images"] < 3:
            page_metrics["content_type"] = "text_document"
        elif page_metrics["images"] >= 3:
            page_metrics["content_type"] = "image_heavy"
        elif page_metrics["text_blocks"] <= 2 and page_metrics["images"] <= 1:
            page_metrics["content_type"] = "form"
        
        return page_metrics
    
    @staticmethod
    def _calculate_quality_score(metrics: Dict[str, Any]) -> float:
        """Calcula score de qualidade baseado em múltiplos fatores"""
        score = 100.0
        
        # Penalizar por poucas páginas (possível documento vazio)
        if metrics["total_pages"] == 0:
            return 0.0
        
        # Penalizar por baixa densidade de texto em documentos textuais
        if metrics["text_density"] < 0.5:
            score -= 20
        
        # Verificar consistência de tamanho de página
        page_sizes = metrics["page_sizes"]
        if len(page_sizes) > 1:
            first_size = page_sizes[0]
            for size in page_sizes[1:]:
                if abs(size["width"] - first_size["width"]) > 50 or abs(size["height"] - first_size["height"]) > 50:
                    score -= 10
        
        return max(0, min(100, score))
    
    @staticmethod
    def detect_tables_in_page(page) -> List[Dict[str, Any]]:
        """Detecta tabelas em uma página usando análise de layout"""
        try:
            tables = []
            text_blocks = page.get_text("dict")["blocks"]
            
            # Agrupar blocos de texto que podem formar tabelas
            text_elements = []
            for block in text_blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_elements.append({
                                "text": span["text"],
                                "bbox": span["bbox"],
                                "font_size": span["size"]
                            })
            
            # Análise de padrões tabulares
            table_candidates = QualityEngine._find_table_candidates(text_elements)
            tables.extend(table_candidates)
            
            return tables
            
        except Exception as e:
            return []
    
    @staticmethod
    def _find_table_candidates(text_elements: List[Dict]) -> List[Dict]:
        """Encontra candidatos a tabelas baseado em alinhamento e padrões"""
        if len(text_elements) < 4:
            return []
        
        # Agrupar por linhas baseado na coordenada y
        y_coords = sorted(list(set([elem["bbox"][1] for elem in text_elements])))
        row_tolerance = 5  # pixels
        
        rows = []
        current_row = []
        current_y = y_coords[0]
        
        for elem in sorted(text_elements, key=lambda x: x["bbox"][1]):
            if abs(elem["bbox"][1] - current_y) <= row_tolerance:
                current_row.append(elem)
            else:
                if current_row:
                    rows.append(sorted(current_row, key=lambda x: x["bbox"][0]))
                    current_row = [elem]
                    current_y = elem["bbox"][1]
        
        if current_row:
            rows.append(sorted(current_row, key=lambda x: x["bbox"][0]))
        
        # Verificar padrões tabulares (múltiplas linhas com elementos alinhados)
        tables = []
        if len(rows) >= 3:  # Mínimo de 3 linhas para considerar como tabela
            # Verificar alinhamento vertical consistente
            column_positions = QualityEngine._detect_columns(rows)
            if len(column_positions) >= 2:
                tables.append({
                    "rows": len(rows),
                    "columns": len(column_positions),
                    "confidence": 0.8
                })
        
        return tables
    
    @staticmethod
    def _detect_columns(rows: List[List[Dict]]) -> List[float]:
        """Detecta posições de colunas baseado no alinhamento do texto"""
        all_x_positions = []
        for row in rows:
            for elem in row:
                all_x_positions.append(elem["bbox"][0])
        
        if not all_x_positions:
            return []
        
        # Usar K-means para agrupar posições x similares
        positions_array = np.array(all_x_positions).reshape(-1, 1)
        n_clusters = min(10, len(set(all_x_positions)))
        
        if n_clusters < 2:
            return []
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(positions_array)
        
        # Retornar centros dos clusters ordenados
        return sorted([float(center[0]) for center in kmeans.cluster_centers_])
    
    @staticmethod
    async def enhance_text_quality(text: str) -> str:
        """Melhora qualidade do texto extraído"""
        # Corrigir quebras de linha mal detectadas
        text = text.replace('-\n', '')  # Remove hífen de quebra de linha
        text = text.replace('\n', ' ')  # Une linhas muito próximas
        
        # Corrigir caracteres comuns de OCR
        corrections = {
            '0': 'O', '1': 'I', '5': 'S', 
            '|': 'I', '€': 'C', '£': 'E'
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
            
        return text