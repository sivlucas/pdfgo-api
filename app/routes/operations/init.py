"""
Operations routes for PDF manipulation
"""

from app.routes.operations.split import router as split_router
from app.routes.operations.merge import router as merge_router
from app.routes.operations.edit import router as edit_router
from app.routes.operations.page_editor import router as page_editor_router

__all__ = ["split_router", "merge_router", "edit_router", "page_editor_router"]