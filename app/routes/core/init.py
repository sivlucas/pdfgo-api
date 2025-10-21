"""
Core routes for PDFGo API
"""

from app.routes.core.upload import router as upload_router
from app.routes.core.analyze import router as analyze_router
from app.routes.core.preview import router as preview_router

__all__ = ["upload_router", "analyze_router", "preview_router"]