import streamlit as st
import os
from rag_pipeline import RAGPipeline
from config import config

@st.cache_resource
def get_pipeline():
    """Cria e retorna uma única instância do RAGPipeline (cached)."""
    return RAGPipeline()

def main():
    st.set_page_config(page_title="Pipeline RAG", page_icon="🤖")
    st.title("🤖 Pipeline RAG com Streamlit")

    # Instancia a RAGPipeline com tratamento de erro inicial
    try:
        pipeline = get_pipeline()
    except Exception as e:
        st.error(f"Erro crítico ao iniciar o sistema: {e}")
        st.info("Verifique se o arquivo .env está configurado corretamente.")
        return

    st.sidebar.title("📂 Upload de Documentos")
    
    # Lista de formatos suportados
    supported_formats = ['txt', 'pdf', 'md', 'docx', 'html', 'csv', 'xlsx', 'xls', 'mp3', 'wav', 'm4a', 'mp4', 'avi', 'mov']
    
    st.sidebar.info(f"**Formatos suportados:**\n\n"
                    f"📄 Documentos: TXT, PDF, MD, DOCX, HTML\n\n"
                    f"📊 Dados: CSV, XLSX\n\n"
                    f"🎵 Áudio: MP3, WAV, M4A\n\n"
                    f"🎬 Vídeo: MP4, AVI, MOV\n\n"
                    f"⚠️ Limite: {config.MAX_FILE_SIZE_MB}MB por arquivo")
    
    uploaded_files = st.sidebar.file_uploader(
        "Faça o upload de seus documentos aqui", 
        accept_multiple_files=True,
        type=supported_formats
    )

    if uploaded_files:
        file_paths = []
        # Garante que o diretório 'data' exista usando a config
        os.makedirs(config.DATA_DIR, exist_ok=True)
        
        # Valida tamanho dos arquivos
        max_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
        
        for uploaded_file in uploaded_files:
            # Verifica tamanho do arquivo
            if uploaded_file.size > max_size_bytes:
                st.sidebar.warning(f"⚠️ Arquivo {uploaded_file.name} excede o limite de {config.MAX_FILE_SIZE_MB}MB e foi ignorado.")
                continue
            
            file_path = os.path.join(config.DATA_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)
        
        if file_paths:
            st.sidebar.success(f"{len(file_paths)} documento(s) salvo(s) temporariamente.")

            if st.sidebar.button("Processar Documentos"):
                with st.spinner("Processando documentos e gerando embeddings..."):
                    try:
                        pipeline.add_documents(file_paths)
                        st.sidebar.success("✅ Documentos processados e indexados com sucesso!")
                    except Exception as e:
                        st.sidebar.error(f"Erro ao processar documentos: {e}")

    st.divider()
    st.header("💬 Faça uma pergunta")
    question = st.text_input("Sobre o que você quer saber?")

    if st.button("Obter Resposta", type="primary"):
        if not question:
            st.warning("⚠️ Por favor, digite uma pergunta.")
        else:
            with st.spinner("🧠 Pensando na resposta..."):
                answer = pipeline.answer(question)
                st.success("Resposta:")
                st.markdown(answer)

if __name__ == "__main__":
    main()
