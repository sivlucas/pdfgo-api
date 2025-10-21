FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema para PDF e OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements/base.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r base.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p storage/uploads storage/outputs storage/temp

# Expor porta
EXPOSE 8000

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando para rodar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]