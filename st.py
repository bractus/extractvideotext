import pysqlite3 
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
from langchain_community.document_loaders import YoutubeLoader
from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from crewai import Agent, Task, Crew, Process

os.environ["OPENAI_MODEL_NAME"] = 'gpt-4o-mini'

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
                # Carregar o vídeo
                video_loader = YoutubeLoader.from_youtube_url(youtube_url, language=["pt"])
                infos = video_loader.load()
                transcricao = infos[0].page_content

                # Configurar o agente
                researcher = Agent(
                    role="Professor",
                    goal="Criar perguntas e respostas",
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

