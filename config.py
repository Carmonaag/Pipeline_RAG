import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env se existir
load_dotenv()

class Config:
    """Centraliza as configurações da aplicação."""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Caminhos e Nomes
    QDRANT_PATH = os.getenv("QDRANT_PATH", "qdrant_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_documents")
    DATA_DIR = os.getenv("DATA_DIR", "data")
    
    # Configurações do Modelo
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    
    # Configurações de Chunking
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Configurações de Upload
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "200"))
    
    # Configurações de Áudio/Vídeo
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
    USE_LOCAL_WHISPER = os.getenv("USE_LOCAL_WHISPER", "true").lower() == "true"

    @classmethod
    def validate(cls):
        """Valida se as configurações críticas estão presentes."""
        if not cls.GROQ_API_KEY:
            raise ValueError("A variável de ambiente GROQ_API_KEY não está definida. Verifique seu arquivo .env.")

# Instância global para uso fácil
config = Config()
