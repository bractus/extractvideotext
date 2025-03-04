import os
import io
from langchain_community.document_loaders import YoutubeLoader
from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# video_loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=HDNxFiRrfVY",
#                                               language = ["en"])

video_loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=Iw6gm-e-vIg&ab_channel=JerryStrazzeri",
                                              language = ["pt"])



infos = video_loader.load()
transcricao = infos[0].page_content

from crewai import Agent, Task, Crew,Process

import os
# from utils import get_openai_api_key, get_serper_api_key

language = "alemão"

os.environ["OPENAI_API_KEY"] = "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"
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4o-mini'
# os.environ["SERPER_API_KEY"] = "199ef3a2e3d3c53e48f5ab9063bd8c67121cce4a"#get_serper_api_key()

# from crewai_tools import (
#   FileReadTool,
#   ScrapeWebsiteTool,
#   MDXSearchTool,
#   SerperDevTool
# )

# scrape_tool = ScrapeWebsiteTool()
# read_resume = FileReadTool(file_path='./b.csv')
# semantic_search_resume = MDXSearchTool(mdx='./CairoRochaResume.pdf')

# Agent 1: Researcher
researcher = Agent(
    role="Professor",
    goal="Criar perguntas e respostas",
    # tools = [scrape_tool, search_tool, read_resume],
    verbose=True,
    backstory=(
        "Como professor, eu devo:"
        f"- Criar perguntas e respostas em {language} bem explicadas para criação de cards baseado na entrada: {transcricao}"
       f"-Traduzir as perguntas e respostas de português para {language}"
        "- Colocar essas perguntas e respostas em um arquivo CSV nas colunas Pergunta e Resposta, com ponto e virgula como separador"
    )
)

resume_strategy_task = Task(
    description=(
        f"Criar um CSV de perguntas e respostas para o aplicativo Anki em {language}"
    ),
    expected_output=(
        f"Um CSV bem formatado em {language} com as colunas Pergunta e Resposta, com ponto e virgula como separador"
    ),
    agent=researcher,
    output_file="output.csv",
)

job_application_crew = Crew(
    agents=[researcher],
    tasks=[resume_strategy_task],
    verbose=True
)

result = job_application_crew.kickoff()