"""
Módulo de loaders de documentos para diferentes formatos.
Suporta: TXT, PDF, MD, DOCX, HTML, CSV, XLSX, áudio e vídeo.
"""

import os
import logging
from typing import List, Optional
from pathlib import Path
from langchain.schema import Document
from langchain_community.document_loaders import UnstructuredFileLoader

logger = logging.getLogger(__name__)


class CSVLoader:
    """Loader para arquivos CSV."""
    
    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        self.file_path = file_path
        self.encoding = encoding
    
    def load(self) -> List[Document]:
        """Carrega e processa arquivo CSV."""
        try:
            import pandas as pd
            
            df = pd.read_csv(self.file_path, encoding=self.encoding)
            
            # Converte cada linha em um documento
            documents = []
            for idx, row in df.iterrows():
                # Cria texto formatado da linha
                content = "\n".join([f"{col}: {val}" for col, val in row.items()])
                
                metadata = {
                    "source": self.file_path,
                    "row": idx,
                    "type": "csv"
                }
                
                documents.append(Document(page_content=content, metadata=metadata))
            
            logger.info(f"CSV carregado: {len(documents)} linhas de {self.file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao carregar CSV {self.file_path}: {e}")
            raise


class ExcelLoader:
    """Loader para arquivos Excel (XLSX)."""
    
    def __init__(self, file_path: str, sheet_name: Optional[str] = None):
        self.file_path = file_path
        self.sheet_name = sheet_name  # None = todas as planilhas
    
    def load(self) -> List[Document]:
        """Carrega e processa arquivo Excel."""
        try:
            import pandas as pd
            
            # Lê todas as planilhas ou uma específica
            if self.sheet_name:
                dfs = {self.sheet_name: pd.read_excel(self.file_path, sheet_name=self.sheet_name)}
            else:
                dfs = pd.read_excel(self.file_path, sheet_name=None)
            
            documents = []
            
            for sheet_name, df in dfs.items():
                for idx, row in df.iterrows():
                    # Cria texto formatado da linha
                    content = "\n".join([f"{col}: {val}" for col, val in row.items()])
                    
                    metadata = {
                        "source": self.file_path,
                        "sheet": sheet_name,
                        "row": idx,
                        "type": "excel"
                    }
                    
                    documents.append(Document(page_content=content, metadata=metadata))
            
            logger.info(f"Excel carregado: {len(documents)} linhas de {len(dfs)} planilha(s) de {self.file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao carregar Excel {self.file_path}: {e}")
            raise


class AudioLoader:
    """Loader para arquivos de áudio (MP3, WAV, M4A)."""
    
    def __init__(self, file_path: str, model_size: str = "base"):
        self.file_path = file_path
        self.model_size = model_size  # tiny, base, small, medium, large
    
    def load(self) -> List[Document]:
        """Transcreve áudio usando Whisper."""
        try:
            import whisper
            
            logger.info(f"Carregando modelo Whisper '{self.model_size}'...")
            model = whisper.load_model(self.model_size)
            
            logger.info(f"Transcrevendo áudio: {self.file_path}")
            result = model.transcribe(self.file_path)
            
            metadata = {
                "source": self.file_path,
                "type": "audio",
                "language": result.get("language", "unknown")
            }
            
            document = Document(page_content=result["text"], metadata=metadata)
            
            logger.info(f"Áudio transcrito com sucesso: {len(result['text'])} caracteres")
            return [document]
            
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio {self.file_path}: {e}")
            raise


class VideoLoader:
    """Loader para arquivos de vídeo (MP4, AVI, MOV)."""
    
    def __init__(self, file_path: str, model_size: str = "base"):
        self.file_path = file_path
        self.model_size = model_size
    
    def load(self) -> List[Document]:
        """Extrai áudio do vídeo e transcreve."""
        try:
            import whisper
            from moviepy import VideoFileClip  # MoviePy 2.x usa import direto
            import tempfile
            
            # Extrai áudio do vídeo
            logger.info(f"Extraindo áudio do vídeo: {self.file_path}")
            video = VideoFileClip(self.file_path)
            
            # Verifica se o vídeo tem áudio
            if video.audio is None:
                video.close()
                error_msg = f"O vídeo {self.file_path} não possui faixa de áudio."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Salva áudio temporariamente
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            logger.info(f"Salvando áudio temporário em: {temp_audio_path}")
            video.audio.write_audiofile(temp_audio_path, logger=None)
            video.close()
            
            # Transcreve o áudio
            logger.info(f"Carregando modelo Whisper '{self.model_size}'...")
            model = whisper.load_model(self.model_size)
            
            logger.info(f"Transcrevendo áudio do vídeo...")
            result = model.transcribe(temp_audio_path, language='pt')
            
            # Remove arquivo temporário
            try:
                os.unlink(temp_audio_path)
                logger.info(f"Arquivo temporário removido: {temp_audio_path}")
            except Exception as e:
                logger.warning(f"Não foi possível remover arquivo temporário {temp_audio_path}: {e}")
            
            metadata = {
                "source": self.file_path,
                "type": "video",
                "language": result.get("language", "unknown")
            }
            
            transcription_text = result["text"].strip()
            
            if not transcription_text:
                logger.warning(f"Transcrição do vídeo {self.file_path} resultou em texto vazio.")
                transcription_text = "[Vídeo sem fala detectada]"
            
            document = Document(page_content=transcription_text, metadata=metadata)
            
            logger.info(f"Vídeo transcrito com sucesso: {len(transcription_text)} caracteres")
            return [document]
            
        except Exception as e:
            logger.error(f"Erro ao processar vídeo {self.file_path}: {e}", exc_info=True)
            raise


class DocumentLoaderFactory:
    """Factory para selecionar o loader apropriado baseado na extensão do arquivo."""
    
    SUPPORTED_EXTENSIONS = {
        # Documentos de texto
        '.txt': UnstructuredFileLoader,
        '.pdf': UnstructuredFileLoader,
        '.md': UnstructuredFileLoader,
        '.docx': UnstructuredFileLoader,
        '.html': UnstructuredFileLoader,
        
        # Dados estruturados
        '.csv': CSVLoader,
        '.xlsx': ExcelLoader,
        '.xls': ExcelLoader,
        
        # Áudio
        '.mp3': AudioLoader,
        '.wav': AudioLoader,
        '.m4a': AudioLoader,
        
        # Vídeo
        '.mp4': VideoLoader,
        '.avi': VideoLoader,
        '.mov': VideoLoader,
    }
    
    @classmethod
    def get_loader(cls, file_path: str):
        """Retorna o loader apropriado para o arquivo."""
        extension = Path(file_path).suffix.lower()
        
        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Formato de arquivo não suportado: {extension}")
        
        loader_class = cls.SUPPORTED_EXTENSIONS[extension]
        return loader_class(file_path)
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Verifica se o formato do arquivo é suportado."""
        extension = Path(file_path).suffix.lower()
        return extension in cls.SUPPORTED_EXTENSIONS
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Retorna lista de extensões suportadas."""
        return list(cls.SUPPORTED_EXTENSIONS.keys())
