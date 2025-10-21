from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime

class OperationType(str, Enum):
    SPLIT = "split"
    MERGE = "merge"
    EDIT = "edit"
    ANALYZE = "analyze"
    PREVIEW = "preview"

class SplitMethod(str, Enum):
    PAGE_RANGE = "page_range"
    EVERY_N_PAGES = "every_n_pages"
    BOOKMARKS = "bookmarks"
    CONTENT_ANALYSIS = "content_analysis"

class EditOperation(str, Enum):
    ROTATE = "rotate"
    WATERMARK = "watermark"
    METADATA = "metadata"
    COMPRESS = "compress"

class PageOperation(str, Enum):
    DELETE = "delete"
    REORDER = "reorder"
    INSERT = "insert"
    EXTRACT = "extract"
    DUPLICATE = "duplicate"
    ROTATE_SPECIFIC = "rotate_specific"

class ContentType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    FORM = "form"

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    services: Dict[str, str]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    code: str
    suggestion: Optional[str] = None

class PDFUploadResponse(BaseModel):
    message: str
    file_id: str
    filename: str
    pages: int
    file_size: int
    analysis: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    file_id: str
    analysis: Dict[str, Any]
    quality_score: float
    recommendations: List[str]

class QualityMetrics(BaseModel):
    resolution: int
    compression_ratio: float
    text_preservation: float
    image_quality: float
    overall_score: float

class OperationResponse(BaseModel):
    operation_id: str
    status: str
    message: str
    download_url: Optional[str] = None
    output_files: Optional[List[str]] = None
    quality_metrics: Optional[Dict[str, Any]] = None

class SplitRequest(BaseModel):
    file_id: str
    method: SplitMethod
    parameters: Dict[str, Any] = Field(default_factory=dict)
    quality_preservation: bool = True

class MergeRequest(BaseModel):
    file_ids: List[str]
    output_filename: Optional[str] = "merged_document"
    optimize: bool = True

class EditRequest(BaseModel):
    file_id: str
    operations: List[Dict[str, Any]]
    preserve_quality: bool = True

class PreviewRequest(BaseModel):
    file_id: str
    pages: Optional[List[int]] = None
    quality: str = "medium"
    format: str = "png"

class PreviewResponse(BaseModel):
    file_id: str
    total_pages: int
    previewed_pages: int
    pages: List[Dict[str, Any]]
    thumbnails: List[Dict[str, Any]]

class PageEditRequest(BaseModel):
    file_id: str
    operation: PageOperation
    parameters: Dict[str, Any] = Field(default_factory=dict)

class PageReorderRequest(BaseModel):
    file_id: str
    new_order: List[int]

class PageDeleteRequest(BaseModel):
    file_id: str
    pages_to_delete: List[int]

class PageInsertRequest(BaseModel):
    target_file_id: str
    source_file_id: str
    insert_after_page: int
    source_pages: Optional[List[int]] = None

class PageExtractRequest(BaseModel):
    file_id: str
    pages_to_extract: List[int]

class PageDuplicateRequest(BaseModel):
    file_id: str
    pages_to_duplicate: List[int]

class PageRotateSpecificRequest(BaseModel):
    file_id: str
    pages_rotation: Dict[int, int]

class PageThumbnailsResponse(BaseModel):
    file_id: str
    total_pages: int
    thumbnails: List[Dict[str, Any]]