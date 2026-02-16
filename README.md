# Meeting Summary Writer 🎙️→📋

**Transform meeting recordings into actionable summaries in minutes**

Convert audio files (MP3, WAV, M4A) → structured summaries with key decisions, action items, next steps, and risks.

- **🎙️ Whisper**: State-of-the-art speech recognition 
- **🤖 Ollama + Llama3.2**: Local AI summarization (no cloud costs)
- **⚡ Fast**: 25 minutes setup → production ready
- **🔒 Private**: Everything runs locally on your machine

## Quick Start

### 1. Install Ollama & Model
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download Llama model (3B params = laptop-friendly)  
ollama pull llama3.2:3b

# Start Ollama server (keep running in Terminal 1)
ollama serve
```

### 2. Install Python Dependencies
```bash
# Terminal 2
cd meeting-summary-writer
pip install -r requirements.txt
```

### 3. Process Your First Meeting
```bash
# Convert meeting audio → summary
python -m src.main your_meeting.mp3

# Check setup
python -m src.main check-setup
```

## Usage Examples

```bash
# Basic usage
python -m src.main sales_call.mp3

# Use larger Whisper model for better accuracy
python -m src.main --model-size medium important_meeting.wav

# Custom output directory
python -m src.main --output-dir ./summaries team_standup.m4a
```

## Output Files

```
📁 project/
├── your_meeting_transcript.txt    # Full raw transcript
├── your_meeting_summary.md        # Structured summary
└── meeting-summary-writer/        # This tool
```

**Sample Summary Output:**
```markdown
# Meeting Summary: sales_call

**KEY DECISIONS**
• Approved Q1 budget increase of 15%
• Moving to weekly client check-ins

**ACTION ITEMS**
• Ravi: Prepare Q1 budget report by Friday  
• Priya: Schedule demo with ProspectCorp by Wednesday

**NEXT STEPS**
• Follow up on vendor contracts
• Review pricing strategy for new market

**KEY RISKS**
• Vendor delay could impact March launch
• Competition launching similar product in Q2
```

## Project Structure

```
meeting-summary-writer/
├── src/
│   ├── main.py              # CLI entrypoint
│   ├── transcriber.py       # Whisper integration  
│   ├── summarizer.py        # Ollama + prompt engineering
│   └── utils/              # Helper functions
├── requirements.txt        # Python dependencies
├── .env.example           # Configuration template
└── README.md             # This file
```

## Hardware Requirements

- **RAM**: 8GB minimum (16GB recommended)
- **CPU**: Any modern Intel/AMD/Apple Silicon
- **Storage**: 5GB free space
- **Internet**: Only for initial setup (then 100% offline)

## Troubleshooting

**Ollama not found?**
```bash
ollama serve
```

**Model not available?**  
```bash
ollama pull llama3.2:3b
```

**Large audio files failing?**
- Use `--model-size small` for faster processing
- Break long recordings into smaller chunks

## Advanced Usage

**Batch Processing:**
```bash
# Process multiple files
for file in *.mp3; do
    python -m src.main "$file"
done
```

**Custom Prompts:** Edit `src/summarizer.py` to customize summary format.

## Contributing

This tool is production-ready for Indore SMEs doing daily standups and client calls. Perfect for teams wanting instant action items without cloud dependencies.