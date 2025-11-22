import pytest
from unittest.mock import MagicMock, patch
from rag_pipeline import RAGPipeline

@pytest.fixture
def mock_config(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake_key")
    import config
    # Patch the class attribute because validate is a classmethod
    config.Config.GROQ_API_KEY = "fake_key"
    return config

@patch("rag_pipeline.qdrant_client.QdrantClient")
@patch("rag_pipeline.Qdrant")
@patch("rag_pipeline.FastEmbedEmbeddings")
@patch("rag_pipeline.ChatGroq")
def test_pipeline_initialization(mock_chat, mock_embed, mock_qdrant, mock_client, mock_config):
    """Testa se o pipeline inicializa corretamente com mocks."""
    pipeline = RAGPipeline()
    assert pipeline.client is not None
    assert pipeline.vector_store is not None
    assert pipeline.rag_chain is not None

@patch("rag_pipeline.UnstructuredFileLoader")
@patch("rag_pipeline.RecursiveCharacterTextSplitter")
def test_add_documents(mock_splitter, mock_loader, mock_config):
    """Testa o fluxo de adição de documentos."""
    # Mock das dependências
    mock_loader_instance = MagicMock()
    mock_loader_instance.load.return_value = ["doc1", "doc2"]
    mock_loader.return_value = mock_loader_instance

    mock_splitter_instance = MagicMock()
    mock_splitter_instance.split_documents.return_value = ["chunk1", "chunk2"]
    mock_splitter.return_value = mock_splitter_instance

    # Mock do pipeline (parcial)
    with patch("rag_pipeline.qdrant_client.QdrantClient"), \
         patch("rag_pipeline.Qdrant") as mock_qdrant_cls, \
         patch("rag_pipeline.FastEmbedEmbeddings"), \
         patch("rag_pipeline.ChatGroq"):
        
        pipeline = RAGPipeline()
        pipeline.vector_store = MagicMock() # Mock do vector store da instância

        pipeline.add_documents(["dummy_path.txt"])

        # Verificações
        mock_loader.assert_called_with("dummy_path.txt")
        pipeline.vector_store.add_documents.assert_called()
