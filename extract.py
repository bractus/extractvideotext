import os
import io
import re
from langchain_community.document_loaders import YoutubeLoader
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from crewai import Agent, Task, Crew, Process

# Define the YouTube URL
youtube_url = "https://www.youtube.com/watch?v=Iw6gm-e-vIg&ab_channel=JerryStrazzeri"

# Extract video ID from URL
video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
if not video_id_match:
    print("URL do YouTube inválida. Por favor, verifique o link e tente novamente.")
    exit(1)

video_id = video_id_match.group(1)

# Try to get transcript using langchain's YoutubeLoader
try:
    video_loader = YoutubeLoader.from_youtube_url(youtube_url, language=["pt"])
    infos = video_loader.load()
    
    if not infos:
        raise IndexError("Não foi possível carregar a transcrição com o YoutubeLoader")
    
    transcricao = infos[0].page_content
    
except (IndexError, Exception) as e:
    print(f"Erro com YoutubeLoader: {str(e)}")
    print("Usando método alternativo para obter a transcrição...")
    
    # Fallback: Use youtube_transcript_api directly
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        transcricao = " ".join([item['text'] for item in transcript_list])
        
        if not transcricao:
            print("Não foi possível extrair a transcrição do vídeo.")
            exit(1)
            
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"Este vídeo não possui legendas disponíveis: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Erro ao obter a transcrição: {str(e)}")
        exit(1)

# Print a preview of the transcript
print("Prévia da Transcrição:")
print(transcricao[:500] + "..." if len(transcricao) > 500 else transcricao)

language = "alemão"

# Initialize Grok model via Groq API
llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY", "your-api-key-here"),
    model_name="llama3-70b-8192"  # This is Groq's implementation of Llama 3, similar to Grok
)

# Agent 1: Researcher
researcher = Agent(
    role="Professor",
    goal="Criar perguntas e respostas",
    llm=llm,  # Use Grok
    verbose=True,
    backstory=(
        "Como professor, eu devo:"
        f"- Criar perguntas e respostas em {language} bem explicadas para criação de cards baseado na entrada: {transcricao}"
       f"-Traduzir as perguntas e respostas de português para {language}"
        "- Colocar essas perguntas e respostas em um arquivo CSV nas colunas Pergunta e Resposta, com ponto e virgula como separador"
    )
) 