import os
import logging
from typing import List, Optional
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_qdrant import Qdrant
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import qdrant_client
from config import config

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        # Valida configurações antes de iniciar
        try:
            config.validate()
        except ValueError as e:
            logger.error(f"Erro de configuração: {e}")
            raise

        self.db_path = config.QDRANT_PATH
        self.collection_name = config.COLLECTION_NAME
        self.embeddings = FastEmbedEmbeddings()
        
        # Garante que o diretório do banco de dados exista
        os.makedirs(self.db_path, exist_ok=True)
        
        try:
            self.client = qdrant_client.QdrantClient(path=self.db_path)
            
            # Verifica se a coleção existe, se não, cria uma vazia
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Criando coleção '{self.collection_name}'...")
                # Cria a coleção com um documento dummy para inicializar
                from langchain.schema import Document
                dummy_doc = Document(page_content="Inicialização", metadata={})
                Qdrant.from_documents(
                    [dummy_doc],
                    self.embeddings,
                    path=self.db_path,
                    collection_name=self.collection_name,
                )
                logger.info(f"Coleção '{self.collection_name}' criada com sucesso.")
            
            self.vector_store = Qdrant(
                client=self.client,
                collection_name=self.collection_name,
                embeddings=self.embeddings,
            )
            self.retriever = self.vector_store.as_retriever()
            self.rag_chain = self._create_rag_chain()
            logger.info(f"Pipeline RAG inicializado com sucesso. DB: {self.db_path}, Coleção: {self.collection_name}")
        except Exception as e:
            logger.critical(f"Falha ao inicializar o Pipeline RAG: {e}")
            raise

    def _create_rag_chain(self):
        template = """
        Você é um assistente que responde a perguntas de forma útil.
        Use os seguintes trechos de contexto recuperado para responder à pergunta.
        Se você não sabe a resposta, apenas diga que não sabe, não tente inventar uma resposta.
        Use no máximo cinco sentenças. Mantenha a resposta concisa e em português.

        Contexto: {context}
        Pergunta: {question}
        Resposta útil:
        """
        prompt = ChatPromptTemplate.from_template(template)
        llm = ChatGroq(model=config.MODEL_NAME, api_key=config.GROQ_API_KEY)

        rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return rag_chain

    def add_documents(self, file_paths: List[str]):
        """Carrega, processa e adiciona documentos ao vector store."""
        documents = []
        for file_path in file_paths:
            try:
                logger.info(f"Carregando arquivo: {file_path}")
                loader = UnstructuredFileLoader(file_path)
                loaded_docs = loader.load()
                documents.extend(loaded_docs)
            except Exception as e:
                logger.error(f"Erro ao carregar o arquivo {file_path}: {e}")
                continue

        if not documents:
            logger.warning("Nenhum documento foi carregado com sucesso.")
            return

        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.CHUNK_SIZE, 
                chunk_overlap=config.CHUNK_OVERLAP
            )
            text_chunks = text_splitter.split_documents(documents)
            
            self.vector_store.add_documents(text_chunks)
            logger.info(f"{len(text_chunks)} chunks de texto adicionados à coleção '{self.collection_name}'.")
        except Exception as e:
            logger.error(f"Erro ao processar e adicionar documentos ao banco vetorial: {e}")
            raise

    def answer(self, question: str) -> str:
        """Recebe uma pergunta e retorna uma resposta."""
        if not question:
            return "Por favor, insira uma pergunta."
        
        try:
            logger.info(f"Processando pergunta: {question}")
            return self.rag_chain.invoke(question)
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta."