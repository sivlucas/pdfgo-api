#!/usr/bin/env python3
"""
Script para limpeza de arquivos temporários
"""

import os
import time
import glob
from datetime import datetime, timedelta

def cleanup_old_files():
    """Remove arquivos antigos dos diretórios de armazenamento"""
    
    # Configurações
    max_age_hours = 24  # Remover arquivos com mais de 24 horas
    directories = [
        "storage/uploads",
        "storage/outputs", 
        "storage/temp"
    ]
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    total_removed = 0
    
    for directory in directories:
        print(f"🔍 Verificando {directory}...")
        
        # Encontrar todos os arquivos
        pattern = os.path.join(directory, "*")
        files = glob.glob(pattern)
        
        for file_path in files:
            # Pular diretórios e arquivos .gitkeep
            if os.path.isdir(file_path) or file_path.endswith('.gitkeep'):
                continue
            
            # Verificar idade do arquivo
            file_age = current_time - os.path.getctime(file_path)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    print(f"🗑️  Removido: {file_path}")
                    total_removed += 1
                except Exception as e:
                    print(f"❌ Erro ao remover {file_path}: {e}")
    
    print(f"✅ Limpeza concluída! {total_removed} arquivos removidos.")

if __name__ == "__main__":
    print("🧹 Iniciando limpeza de arquivos temporários...")
    cleanup_old_files()