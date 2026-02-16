import streamlit as st
from src.transcriber.vosk_transcriber import VoskTranscriber
from src.summarizer import MeetingSummarizer
from pathlib import Path

st.title("Meeting Summary Writer")

st.info("📢 **Language Support**: Currently using English model. For Hindi audio, download a Hindi Vosk model.")
st.markdown("""
**To use Hindi transcription:**
1. Download Hindi model from: https://alphacephei.com/vosk/models
2. Extract it to a folder named `model_hindi` in this directory  
3. Update the code to use the Hindi model

**Current setup works best with English audio.**
""")

# Language selection
language = st.selectbox(
    "Select Language Model",
    ["English", "Hindi"],
    help="Choose the language model for transcription. Make sure you have downloaded the Hindi model if selecting Hindi."
)

model_path = "model" if language == "English" else "model_hindi"

uploaded_file = st.file_uploader("Upload a WAV audio file", type=["wav"])

st.info("📝 **Note**: Only WAV files are supported. If you have MP4, MP3, or other formats, please convert them to WAV using:")
st.markdown("""- Online converters like [CloudConvert](https://cloudconvert.com/mp4-to-wav) or [OnlineConvert](https://audio.online-convert.com/convert-to-wav)
- Audio software like Audacity (free)
- VLC Media Player (File → Convert/Save)""")
model_size = st.selectbox("Select Whisper model size", ["tiny", "base", "small", "medium", "large"], index=1)

if uploaded_file is not None:
    st.write("### File uploaded:", uploaded_file.name)
    
    # Save uploaded file temporarily
    temp_file = Path("temp_" + uploaded_file.name)
    with open(temp_file, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Transcribe
    st.write("### Step 1: Transcribing audio...")
    try:
        transcriber = VoskTranscriber(model_path)
        transcript = transcriber.transcribe(str(temp_file))
    except FileNotFoundError as e:
        if "model_hindi" in str(e):
            st.error("🇮🇳 Hindi model not found! Please follow the setup instructions in HINDI_SETUP.md to download the Hindi model.")
            st.stop()
        else:
            st.error(f"Model error: {e}")
            st.stop()
    except Exception as e:
        st.error(f"Transcription error: {e}")
        st.stop()
    
    if not transcript or not transcript.strip():
        st.error("⚠️ Transcription failed or returned empty results. This could be because:")
        st.markdown("""- The audio quality is poor
- The language doesn't match the model (current model supports English)
- The audio file is corrupted or too short
- For Hindi audio, you need a Hindi Vosk model""")
        st.stop()
    else:
        st.write("### Transcript:")
        st.text_area("Transcript", transcript, height=300)
        
        st.info("👁️ **Please review the transcript above**. If it looks incorrect, try using the correct language model or check audio quality.")
        
        # Summarize
        st.write("### Step 2: Generating summary...")
        summarizer = MeetingSummarizer()
        summary = summarizer.summarize(transcript)
        
        st.write("### Summary:")
        st.text_area("Summary", summary, height=300)
        
        # Save results
        transcript_file = temp_file.parent / (temp_file.stem + "_transcript.txt")
        summary_file = temp_file.parent / (temp_file.stem + "_summary.md")
        
        transcript_file.write_text(transcript, encoding='utf-8')
        summary_file.write_text(summary, encoding='utf-8')
        
        st.success("Files saved:")
        st.write(f"Transcript: {transcript_file}")
        st.write(f"Summary: {summary_file}")