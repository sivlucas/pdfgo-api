#!/bin/bash

set -e

echo "🚀 Iniciando deploy do PDFGo API..."

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Build das imagens
echo "🔨 Construindo imagens..."
docker-compose build

# Iniciar containers
echo "🚀 Iniciando containers..."
docker-compose up -d

# Verificar saúde
echo "🔍 Verificando saúde da aplicação..."
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "✅ Deploy concluído com sucesso!"
echo "📚 API disponível em: http://localhost:8000"
echo "📖 Documentação em: http://localhost:8000/docs"