# YouTube Video Text Extractor and Q&A Generator

This project is a Streamlit-based web application that extracts text from YouTube videos and automatically generates questions and answers in multiple languages. It's perfect for creating study materials or flashcards for language learning and educational purposes.

## Features

- Extract text content from YouTube videos
- Generate questions and answers in multiple languages:
  - German
  - English
  - Spanish
  - French
  - Italian
  - Portuguese
- Export results to CSV format (compatible with Anki flashcards)
- User-friendly web interface
- Support for video transcription

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
cd extractvideotext
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run st.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

3. In the web interface:
   - Paste a YouTube video URL
   - Select your desired target language for Q&A generation
   - Click "Process Video"
   - Download the generated CSV file when processing is complete

## Project Structure

- `st.py`: Main Streamlit web application
- `extract.py`: Core functionality for video text extraction and Q&A generation
- `requirements.txt`: Project dependencies

## Dependencies

- streamlit: Web application framework
- langchain-community: Language model tools and utilities
- langchain-core: Core language processing functionality
- langchain-ollama: Language model integration
- crewai: AI agent framework
- youtube-dl: YouTube video processing
- pytube: YouTube video handling

## Notes

- The application requires an internet connection to access YouTube videos
- Processing time may vary depending on video length and complexity
- Generated Q&A pairs are saved in CSV format with semicolon (;) as the delimiter

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your chosen license]