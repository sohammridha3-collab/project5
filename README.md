# 🎬 AI Video Assistant & Meeting Intelligence

An end-to-end intelligent assistant that transcribes videos and audio files, generates structured executive summaries, extracts key decisions and action items, and lets you chat with your meetings using Retrieval-Augmented Generation (RAG).

---

## ✨ Features

- **Multilingual Audio Transcription**: Supports English using OpenAI Whisper and Hinglish/Indian languages via Sarvam AI.
- **Smart Summarization**: Generates titles and concise executive summaries powered by Mistral AI.
- **Automated Insights**:
  - ✅ **Action Items**: Extracts actionable tasks and assignees.
  - 🔑 **Key Decisions**: Highlights critical agreements and conclusions.
  - ❓ **Open Questions**: Surfaces unanswered queries from the meeting.
- **Interactive RAG Chat**: Chat with your meeting recording using ChromaDB vector search and LangChain.
- **Modern Streamlit UI**: User-friendly web interface for uploading files or pasting video URLs.

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM & Extraction**: [Mistral AI](https://mistral.ai/) (`mistral-small-latest`) via LangChain
- **Speech-to-Text**: [OpenAI Whisper](https://github.com/openai/whisper) & [Sarvam AI](https://www.sarvam.ai/)
- **Embeddings & Vector Database**: HuggingFace (`all-MiniLM-L6-v2`) & [ChromaDB](https://www.trychroma.com/)
- **Audio Processing**: PyDub, yt-dlp

---

## 📁 Project Structure

```plaintext
project5/
├── core/
│   ├── extractor.py        # Action items & decision extraction
│   ├── rag_engine.py       # RAG pipeline for conversational Q&A
│   ├── summarizer.py       # Title & meeting summarization
│   ├── transcriber.py      # Whisper and Sarvam transcription engines
│   └── vector_store.py     # Chroma vector database & embeddings
├── utils/
│   └── audio_processor.py  # Audio extraction and chunking
├── app.py                  # Streamlit web application
├── main.py                 # CLI pipeline entry point
├── test.py                 # Pipeline test runner
├── Requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sohammridha3-collab/project5.git
cd project5
```

### 2. Create and Activate a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r Requirements.txt
```

> **Note**: Audio processing requires `ffmpeg` installed on your system PATH.

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Add your API keys inside `.env`:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
```

---

## 🖥️ Usage

### Run Streamlit Web Application

```bash
streamlit run app.py
```

### Run FastAPI Backend Server

```bash
python api.py
```
> Server will boot up and display clickable local server and Swagger API documentation links (`http://127.0.0.1:8000/docs`).

### Run via Command-Line Interface (CLI)

```bash
python main.py
```

---

## 📜 License

This project is licensed under the MIT License - feel free to modify and adapt it for your own use.
