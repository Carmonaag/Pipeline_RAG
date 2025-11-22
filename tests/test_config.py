import pytest
import os
from config import Config

def test_config_validation_success(monkeypatch):
    """Testa se a validação passa com as variáveis corretas."""
    monkeypatch.setenv("GROQ_API_KEY", "test_key")
    # Recarrega a classe ou apenas chama o validate se for estático/classe
    Config.GROQ_API_KEY = "test_key" # Simula o carregamento
    try:
        Config.validate()
    except ValueError:
        pytest.fail("Config.validate() levantou ValueError inesperadamente!")

def test_config_validation_failure(monkeypatch):
    """Testa se a validação falha sem a API Key."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    Config.GROQ_API_KEY = None
    
    with pytest.raises(ValueError, match="A variável de ambiente GROQ_API_KEY não está definida"):
        Config.validate()

def test_default_values():
    """Testa se os valores padrão são respeitados."""
    assert Config.QDRANT_PATH == "qdrant_db"
    assert Config.MODEL_NAME == "llama3-70b-8192"
