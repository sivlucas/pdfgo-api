from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from datetime import datetime

from app.config import settings
from app.routes.api import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "PDFGo Team",
        "url": "https://pdfgo.app",
        "email": "suporte@pdfgo.app",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "PDFGo API - Manipulação Profissional de PDFs",
        "version": settings.VERSION,
        "description": "API completa para dividir, juntar e editar PDFs com qualidade profissional",
        "endpoints": {
            "upload": "/api/v1/upload",
            "analyze": "/api/v1/analyze",
            "preview": "/api/v1/preview",
            "split": "/api/v1/split",
            "merge": "/api/v1/merge", 
            "edit": "/api/v1/edit",
            "editor": "/api/v1/editor",
            "docs": "/docs"
        },
        "features": {
            "preview": "Pré-visualização de páginas em imagem e texto",
            "editor": "Editor minimalista - excluir, inserir, reorganizar páginas",
            "analysis": "Análise inteligente de conteúdo",
            "quality": "Métricas de qualidade detalhadas",
            "split": "Divisão por conteúdo, páginas ou bookmarks",
            "merge": "Junção otimizada com compressão",
            "edit": "Rotação, marca d'água, metadados e mais"
        },
        "colors": settings.COLORS,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat(),
        "services": {
            "upload": "active",
            "analysis": "active",
            "preview": "active",
            "split": "active",
            "merge": "active",
            "edit": "active",
            "page_editor": "active"
        }
    }

@app.get("/api/v1/info")
async def api_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "features": [
            "Análise inteligente de PDFs com detecção de conteúdo",
            "Pré-visualização em imagem e texto",
            "Divisão por conteúdo, seções ou páginas",
            "Junção otimizada com preservação de qualidade",
            "Edição avançada: rotação, marca d'água, metadados, compressão",
            "Editor de páginas: excluir, inserir, reorganizar páginas",
            "Detecção automática de tabelas e formulários",
            "Métricas de qualidade detalhadas"
        ],
        "quality_standards": {
            "max_file_size": f"{settings.MAX_FILE_SIZE // (1024 * 1024)}MB",
            "default_dpi": settings.DEFAULT_DPI,
            "ocr_enabled": settings.OCR_ENABLED,
            "content_analysis": "advanced"
        },
        "design_system": "PDFGo Colors and Branding"
    }

# Middleware para logging
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-PDFGo-API"] = settings.VERSION
    return response

# Handler de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "details": str(exc),
            "code": "INTERNAL_SERVER_ERROR",
            "suggestion": "Tente novamente ou entre em contato com o suporte"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )