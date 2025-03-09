import os
import io
from langchain_community.document_loaders import YoutubeLoader
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# video_loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=HDNxFiRrfVY",
#                                               language = ["en"])

video_loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=Iw6gm-e-vIg&ab_channel=JerryStrazzeri",
                                              language = ["pt"])

infos = video_loader.load()
transcricao = infos[0].page_content

from crewai import Agent, Task, Crew, Process

import os

language = "alemão"

# Initialize Claude Sonnet
llm = ChatAnthropic(
    anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key-here"),
    model="claude-3-sonnet-20240229"
)

# Agent 1: Researcher
researcher = Agent(
    role="Professor",
    goal="Criar perguntas e respostas",
    llm=llm,  # Use Claude Sonnet
    verbose=True,
    backstory=(
        "Como professor, eu devo:"
        f"- Criar perguntas e respostas em {language} bem explicadas para criação de cards baseado na entrada: {transcricao}"
       f"-Traduzir as perguntas e respostas de português para {language}"
        "- Colocar essas perguntas e respostas em um arquivo CSV nas colunas Pergunta e Resposta, com ponto e virgula como separador"
    )
) 