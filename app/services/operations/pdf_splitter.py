import fitz
import os
import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from app.config import settings
from app.services.core.pdf_analyzer import PDFAnalyzer
from app.services.core.quality_engine import QualityEngine

class PDFSplitter:
    """Serviço avançado para divisão de PDFs com análise de conteúdo"""
    
    @staticmethod
    async def split_by_content_analysis(file_id: str, parameters: Dict[str, Any]) -> List[str]:
        """Divide PDF baseado em análise inteligente de conteúdo"""
        try:
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            analysis = await PDFAnalyzer.comprehensive_analysis(file_path)
            
            output_files = []
            
            # Estratégias de divisão baseadas no conteúdo
            if parameters.get("strategy") == "by_content_type":
                output_files = await PDFSplitter._split_by_content_type(doc, analysis)
            elif parameters.get("strategy") == "by_sections":
                output_files = await PDFSplitter._split_by_sections(doc, analysis)
            elif parameters.get("strategy") == "auto_chapters":
                output_files = await PDFSplitter._split_by_auto_chapters(doc, analysis)
            else:
                # Divisão padrão por páginas com análise de conteúdo
                page_ranges = parameters.get("ranges", ["1-"])
                output_files = await PDFSplitter._split_by_smart_ranges(doc, page_ranges, analysis)
            
            doc.close()
            return output_files
            
        except Exception as e:
            raise HTTPException(500, f"Erro na divisão inteligente: {str(e)}")
    
    @staticmethod
    async def _split_by_content_type(doc, analysis: Dict[str, Any]) -> List[str]:
        """Divide PDF agrupando páginas por tipo de conteúdo"""
        content_groups = {}
        
        for page_info in analysis["content_analysis"]["page_details"]:
            content_type = page_info["content_type"]
            page_num = page_info["page_number"] - 1  # Converter para índice 0-based
            
            if content_type not in content_groups:
                content_groups[content_type] = []
            content_groups[content_type].append(page_num)
        
        output_files = []
        for content_type, pages in content_groups.items():
            if pages:
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=min(pages), to_page=max(pages))
                
                output_id = str(uuid.uuid4())
                output_path = f"{settings.OUTPUT_DIR}/{output_id}_{content_type}.pdf"
                new_doc.save(output_path)
                new_doc.close()
                
                output_files.append(output_path)
        
        return output_files
    
    @staticmethod
    async def _split_by_sections(doc, analysis: Dict[str, Any]) -> List[str]:
        """Divide PDF em seções baseado em mudanças de conteúdo"""
        sections = []
        current_section = []
        page_details = analysis["content_analysis"]["page_details"]
        
        for i, page_info in enumerate(page_details):
            if not current_section:
                current_section.append(i)
                continue
            
            # Verificar mudança significativa no conteúdo
            prev_page = page_details[i-1]
            current_page = page_info
            
            content_changed = (
                prev_page["content_type"] != current_page["content_type"] or
                abs(prev_page["text_blocks"] - current_page["text_blocks"]) > 5 or
                current_page.get("has_headers", False) and not prev_page.get("has_headers", False)
            )
            
            if content_changed and len(current_section) > 0:
                sections.append(current_section)
                current_section = [i]
            else:
                current_section.append(i)
        
        if current_section:
            sections.append(current_section)
        
        # Criar documentos para cada seção
        output_files = []
        for i, section_pages in enumerate(sections):
            new_doc = fitz.open()
            for page_idx in section_pages:
                new_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
            
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_section_{i+1}.pdf"
            new_doc.save(output_path)
            new_doc.close()
            
            output_files.append(output_path)
        
        return output_files
    
    @staticmethod
    async def _split_by_smart_ranges(doc, page_ranges: List[str], analysis: Dict[str, Any]) -> List[str]:
        """Divide PDF com ranges inteligentes que consideram a estrutura do conteúdo"""
        output_files = []
        total_pages = len(doc)
        
        for range_str in page_ranges:
            if '-' in range_str:
                start_end = range_str.split('-')
                start = int(start_end[0]) - 1 if start_end[0] else 0
                end = int(start_end[1]) - 1 if start_end[1] else total_pages - 1
            else:
                start = end = int(range_str) - 1
            
            # Ajustar range para limites de conteúdo coerentes
            start, end = PDFSplitter._adjust_range_to_content(start, end, analysis)
            
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start, to_page=end)
            
            output_id = str(uuid.uuid4())
            output_path = f"{settings.OUTPUT_DIR}/{output_id}_pages_{start+1}-{end+1}.pdf"
            new_doc.save(output_path)
            new_doc.close()
            
            output_files.append(output_path)
        
        return output_files
    
    @staticmethod
    def _adjust_range_to_content(start: int, end: int, analysis: Dict[str, Any]) -> tuple:
        """Ajusta o range de páginas para limites de conteúdo naturais"""
        page_details = analysis["content_analysis"]["page_details"]
        
        # Expandir start para trás até encontrar início de seção
        while start > 0:
            current_page = page_details[start]
            prev_page = page_details[start - 1]
            
            # Se houver mudança significativa, manter start atual
            if (current_page["content_type"] != prev_page["content_type"] or
                current_page.get("has_headers", False)):
                break
            start -= 1
        
        # Expandir end para frente até encontrar fim de seção
        while end < len(page_details) - 1:
            current_page = page_details[end]
            next_page = page_details[end + 1]
            
            # Se houver mudança significativa, manter end atual
            if (current_page["content_type"] != next_page["content_type"] or
                next_page.get("has_headers", False)):
                break
            end += 1
        
        return start, end

    @staticmethod
    async def split_by_page_range(file_id: str, page_ranges: List[str]) -> List[str]:
        """Divide PDF por ranges de páginas específicos"""
        try:
            file_path = f"{settings.UPLOAD_DIR}/{file_id}.pdf"
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            output_files = []
            
            for page_range in page_ranges:
                # Validar range
                pages = PDFSplitter._validate_page_range(page_range, total_pages)
                
                # Criar novo documento
                new_doc = fitz.open()
                
                # Adicionar páginas selecionadas
                for page_num in pages:
                    new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
                
                # Salvar arquivo
                output_id = str(uuid.uuid4())
                output_path = f"{settings.OUTPUT_DIR}/{output_id}.pdf"
                new_doc.save(output_path)
                new_doc.close()
                
                output_files.append(output_path)
            
            doc.close()
            return output_files
            
        except Exception as e:
            raise HTTPException(500, f"Erro ao dividir PDF: {str(e)}")
    
    @staticmethod
    def _validate_page_range(page_range: str, total_pages: int) -> List[int]:
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