import pysqlite3 
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
import re
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from crewai import Agent, Task, Crew, Process
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Initialize Grok model via Groq API
llm = ChatGroq(
    groq_api_key=st.secrets.get("GROQ_API_KEY", "your-api-key-here"),
    model_name="llama3-70b-8192"  # This is Groq's implementation of Llama 3, similar to Grok
)

# Configuração da página
st.set_page_config(
    page_title="Extrator de Texto de Vídeos",
    page_icon="🎥",
    layout="wide"
)

# Título e descrição
st.title("Extrator de Texto de Vídeos do YouTube")
st.write("Esta ferramenta extrai o texto de vídeos do YouTube e gera perguntas e respostas no idioma escolhido.")

# Input do usuário
youtube_url = st.text_input("Cole o link do vídeo do YouTube aqui:", placeholder="https://www.youtube.com/watch?v=...")

# Seleção do idioma
languages = {
    "Alemão": "alemão",
    "Inglês": "inglês",
    "Espanhol": "espanhol",
    "Francês": "francês",
    "Italiano": "italiano",
    "Português": "português"
}
selected_language = st.selectbox("Escolha o idioma para as perguntas e respostas:", list(languages.keys()), index=5)

# Botão de processamento
if st.button("Processar Vídeo"):
    if youtube_url:
        try:
            with st.spinner("Processando o vídeo..."):
                # Extract video ID from URL
                video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
                if not video_id_match:
                    st.error("URL do YouTube inválida. Por favor, verifique o link e tente novamente.")
                    st.stop()
                
                video_id = video_id_match.group(1)
                
                # Try to get transcript using langchain's YoutubeLoader
                try:
                    video_loader = YoutubeLoader.from_youtube_url(youtube_url, language=["pt"])
                    infos = video_loader.load()
                    
                    if not infos:
                        raise IndexError("Não foi possível carregar a transcrição com o YoutubeLoader")
                    
                    transcricao = infos[0].page_content
                    
                except (IndexError, Exception) as e:
                    st.info("Usando método alternativo para obter a transcrição...")
                    
                    # Fallback: Use youtube_transcript_api directly
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
                        transcricao = " ".join([item['text'] for item in transcript_list])
                        
                        if not transcricao:
                            st.error("Não foi possível extrair a transcrição do vídeo.")
                            st.stop()
                            
                    except (TranscriptsDisabled, NoTranscriptFound) as e:
                        st.error(f"Este vídeo não possui legendas disponíveis: {str(e)}")
                        st.stop()
                    except Exception as e:
                        st.error(f"Erro ao obter a transcrição: {str(e)}")
                        st.stop()
                
                # Display a preview of the transcript
                st.subheader("Prévia da Transcrição:")
                st.write(transcricao[:500] + "..." if len(transcricao) > 500 else transcricao)
                
                # Configurar o agente
                researcher = Agent(
                    role="Professor",
                    goal="Criar perguntas e respostas",
                    llm=llm,  # Use Grok
                    verbose=True,
                    backstory=(
                        "Como professor, eu devo:"
                        f"- Criar perguntas e respostas em {languages[selected_language]} bem explicadas para criação de cards baseado na entrada: {transcricao}"
                        f"-Traduzir as perguntas e respostas de português para {languages[selected_language]}"
                        "- Colocar essas perguntas e respostas em um arquivo CSV nas colunas Pergunta e Resposta, com ponto e virgula como separador"
                    )
                )

                # Configurar a tarefa
                resume_strategy_task = Task(
                    description=(
                        f"Criar um CSV de perguntas e respostas para o aplicativo Anki em {languages[selected_language]}"
                    ),
                    expected_output=(
                        f"Um CSV bem formatado em {languages[selected_language]} com as colunas Pergunta e Resposta, com ponto e virgula como separador"
                    ),
                    agent=researcher,
                    output_file="output.csv",
                )

                # Criar e executar o crew
                job_application_crew = Crew(
                    agents=[researcher],
                    tasks=[resume_strategy_task],
                    verbose=True
                )

                result = job_application_crew.kickoff()

                # Oferecer o download do arquivo
                with open("output.csv", "r", encoding="utf-8") as file:
                    csv_content = file.read()
                    
                st.success("Processamento concluído!")
                st.download_button(
                    label="Baixar arquivo CSV",
                    data=csv_content,
                    file_name="perguntas_respostas.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"Ocorreu um erro durante o processamento: {str(e)}")
    else:
        st.warning("Por favor, insira um link do YouTube válido.")

# Instruções adicionais
st.markdown("""
### Como usar:
1. Cole o link do vídeo do YouTube
2. Selecione o idioma desejado para as perguntas e respostas
3. Clique em "Processar Vídeo"
4. Aguarde o processamento
5. Faça o download do arquivo CSV gerado
""")

