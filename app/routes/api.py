from fastapi import APIRouter
from app.routes.core.upload import router as upload_router
from app.routes.core.analyze import router as analyze_router
from app.routes.core.preview import router as preview_router
from app.routes.operations.split import router as split_router
from app.routes.operations.merge import router as merge_router
from app.routes.operations.edit import router as edit_router
from app.routes.operations.page_editor import router as page_editor_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(upload_router, prefix="/api/v1")
api_router.include_router(analyze_router, prefix="/api/v1")
api_router.include_router(preview_router, prefix="/api/v1")
api_router.include_router(split_router, prefix="/api/v1")
api_router.include_router(merge_router, prefix="/api/v1")
api_router.include_router(edit_router, prefix="/api/v1")
api_router.include_router(page_editor_router, prefix="/api/v1")

__all__ = ["api_router"]