import os
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

class Settings:
    # App Info
    APP_NAME: str = "PDFGo API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API profissional para manipulação de PDFs - Dividir, Juntar e Editar com qualidade PDFGo"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Storage
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]
    UPLOAD_DIR: str = "storage/uploads"
    OUTPUT_DIR: str = "storage/outputs"
    TEMP_DIR: str = "storage/temp"
    
    # Processing
    DEFAULT_DPI: int = 300
    MAX_PAGES_FOR_ANALYSIS: int = 50
    OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "True").lower() == "true"
    
    # Quality
    MIN_QUALITY_SCORE: float = 0.7
    COMPRESSION_QUALITY: Dict[str, int] = {
        "low": 72,
        "medium": 150,
        "high": 300
    }
    
    # Design System
    COLORS: Dict[str, str] = {
        "primary": "#FF6B35",
        "secondary": "#64748b",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "error": "#ef4444"
    }
    
    # External Services
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pdfgo-secret-key-change-in-production")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    def __init__(self):
        # Create required directories
        for directory in [self.UPLOAD_DIR, self.OUTPUT_DIR, self.TEMP_DIR]:
            os.makedirs(directory, exist_ok=True)

settings = Settings()