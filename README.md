# Pipeline RAG com Streamlit

Este projeto implementa um sistema de **RAG (Retrieval-Augmented Generation)** robusto e interativo, permitindo que usuários façam upload de documentos e realizem perguntas sobre seu conteúdo utilizando LLMs (Large Language Models) via Groq API.

## 🚀 Funcionalidades

*   **Upload de Múltiplos Formatos**: Suporte a documentos (TXT, PDF, MD, DOCX, HTML), dados estruturados (CSV, XLSX), áudio (MP3, WAV, M4A) e vídeo (MP4, AVI, MOV).
*   **Processamento Inteligente**: Chunking automático e geração de embeddings eficientes.
*   **Transcrição de Áudio/Vídeo**: Utiliza Whisper (OpenAI) para transcrever conteúdo de mídia.
*   **Busca Semântica**: Utiliza Qdrant para armazenamento e recuperação vetorial de alta performance.
*   **Respostas Contextuais**: Integração com Llama 3 (via Groq) para gerar respostas precisas baseadas no contexto dos documentos.
*   **Interface Amigável**: UI desenvolvida com Streamlit para fácil interação.

## 🛠️ Tecnologias Utilizadas

*   **Python 3.12+**
*   **LangChain**: Orquestração do fluxo RAG.
*   **Streamlit**: Interface de usuário.
*   **Qdrant**: Banco de dados vetorial.
*   **Groq API**: Acesso a modelos LLM de alta performance (Llama 3).
*   **FastEmbed**: Geração de embeddings leve e rápida.

## ⚙️ Configuração e Instalação

### Pré-requisitos

*   Python 3.12 ou superior instalado.
*   Uma chave de API da Groq (obtenha em [console.groq.com](https://console.groq.com)).

### Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/pipeline-rag.git
    cd pipeline-rag
    ```

2.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    # ou
    .venv\Scripts\activate  # Windows
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure as variáveis de ambiente:
    *   Copie o arquivo de exemplo:
        ```bash
        cp .env.example .env
        ```
    *   Edite o arquivo `.env` e adicione sua `GROQ_API_KEY`.

## ▶️ Como Usar

1.  Inicie a aplicação:
    ```bash
    streamlit run main.py
    ```

2.  Acesse a interface no navegador (geralmente `http://localhost:8501`).

3.  Na barra lateral:
    *   Faça upload dos seus documentos.
    *   Clique em "Processar Documentos".

4.  Na área principal:
    *   Digite sua pergunta sobre os documentos.
    *   Receba a resposta gerada pela IA.

## 📁 Estrutura do Projeto

*   `main.py`: Interface do usuário (Streamlit).
*   `rag_pipeline.py`: Lógica do pipeline RAG (carregamento, indexação, busca).
*   `config.py`: Centralização de configurações e variáveis de ambiente.
*   `data/`: Diretório temporário para armazenamento de uploads.
*   `qdrant_db/`: Persistência local do banco vetorial.

## 🛡️ Boas Práticas Implementadas

*   **Segurança**: Uso de `.gitignore` para não expor chaves e dados sensíveis.
*   **Configuração**: Gestão centralizada via variáveis de ambiente.
*   **Robustez**: Tratamento de erros e logging para facilitar o debug.

---
Desenvolvido com ❤️ para demonstrar o poder de RAG com Python.
