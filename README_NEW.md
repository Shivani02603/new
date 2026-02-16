# Meeting Summary Writer 🎙️→📋

**Transform meeting recordings into actionable summaries locally and privately**

A complete audio transcription and summarization pipeline using Vosk (offline speech-to-text) and Ollama (local AI summarization).

## ✨ Features

- 🌍 **Multi-language Support**: English and Hindi transcription (expandable)
- 🔒 **100% Local & Private**: No cloud APIs, all processing on your machine
- 🎨 **Web Interface**: Clean Streamlit-based UI
- 🎯 **Smart Audio Processing**: Automatic format conversion and optimization
- 🤖 **AI Summarization**: Local LLM-powered intelligent summaries
- 📁 **Export Options**: Save transcripts and summaries locally

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Ollama installed and running locally
- Git (for cloning)

### Installation

1. **Clone and setup**
```bash
git clone https://github.com/yourusername/meeting-summary-writer.git
cd meeting-summary-writer
pip install -r requirements.txt
```

2. **Download language models**
- Models are not included in the repo due to size
- English model: Download and extract to `model/` folder  
- Hindi model: Download and extract to `model_hindi/` folder (optional)
- See `HINDI_SETUP.md` for detailed instructions

3. **Start services**
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start the app
streamlit run app.py
```

4. **Access the app**
- Open http://localhost:8501 in your browser
- Select language, upload WAV file, get results!

## 🎯 Usage

### Web Interface (Recommended)
1. Select language (English/Hindi)
2. Upload a WAV audio file
3. Review the transcript
4. Get AI-generated summary
5. Download results

### Command Line Interface
```bash
# Process a single file
python -m src.main transcribe your_audio.wav

# Check if everything is working
python -m src.main check-setup
```

## 📁 Project Structure

```
meeting-summary-writer/
├── app.py                     # Streamlit web application
├── src/
│   ├── main.py               # CLI entry point
│   ├── summarizer.py         # AI summarization logic
│   └── transcriber/
│       ├── __init__.py
│       └── vosk_transcriber.py  # Speech-to-text engine
├── model/                    # English Vosk model (download separately)
├── model_hindi/              # Hindi Vosk model (optional)
├── requirements.txt          # Python dependencies
├── HINDI_SETUP.md           # Language model setup guide
└── README.md               # This file
```

## 🔧 Technical Stack

- **Speech Recognition**: Vosk (offline, privacy-focused)
- **AI Summarization**: Ollama with Llama3.2:3b model
- **Web Interface**: Streamlit 
- **Audio Processing**: Python wave module with automatic format conversion
- **Language Support**: Modular architecture for easy language additions

## 🌟 Planned Features (v2.0)

- [ ] 🗣️ Speaker diarization (identify different speakers)
- [ ] ⏰ Timestamped transcripts
- [ ] 🔍 Search and highlight in transcripts  
- [ ] 🎨 Custom summarization styles (bullet points, executive summary, action items)
- [ ] 🌐 More languages (Marathi, Tamil, Bengali, Spanish, French)

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - Use freely for personal and commercial projects!

## ⚠️ Important Notes

- **Model Files**: Language models are not included due to size. Download separately.
- **Privacy**: All processing is local - no data leaves your machine
- **Performance**: Larger models = better accuracy but slower processing
- **Hardware**: Runs on CPU, GPU acceleration not required

## 🆘 Troubleshooting

**"Model not found" error**: Download language models as described in setup  
**Audio format error**: Convert your files to WAV format first  
**Ollama connection error**: Ensure `ollama serve` is running  
**Dependencies error**: Use Python 3.10+ and install requirements.txt  

---

**Made with ❤️ for privacy-conscious meeting documentation**