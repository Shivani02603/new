import streamlit as st
import os
import requests
import zipfile
from pathlib import Path
from src.transcriber.vosk_transcriber import VoskTranscriber
from src.transcriber.speaker_diarizer import SimpleSpeakerDiarizer
from src.summarizer import MeetingSummarizer

# Language configuration
LANGUAGE_MODELS = {
    "English": {
        "model_path": "model",
        "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        "size": "1.8GB"
    },
    "Hindi": {
        "model_path": "model_hindi",
        "url": "https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip",
        "size": "42MB"
    },
    "Marathi": {
        "model_path": "model_marathi",
        "url": "https://alphacephei.com/vosk/models/vosk-model-mr-0.1.zip",
        "size": "38MB"
    },
    "Tamil": {
        "model_path": "model_tamil",
        "url": "https://alphacephei.com/vosk/models/vosk-model-ta-0.1.zip",
        "size": "45MB"
    },
    "Bengali": {
        "model_path": "model_bengali",
        "url": "https://alphacephei.com/vosk/models/vosk-model-bn-0.1.zip",
        "size": "52MB"
    }
}

def download_model(language):
    """Download and extract a language model"""
    model_info = LANGUAGE_MODELS[language]
    model_path = Path(model_info["model_path"])
    
    if model_path.exists():
        return True
        
    st.info(f"📥 Downloading {language} model ({model_info['size']})...")
    
    try:
        # Download the model
        response = requests.get(model_info["url"], stream=True)
        response.raise_for_status()
        
        zip_path = f"temp_{language.lower()}_model.zip"
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the model
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the model folder name inside the zip
            model_folder = zip_ref.namelist()[0].split('/')[0]
            zip_ref.extractall('.')
            
        # Rename to expected model path
        extracted_path = Path(model_folder)
        if extracted_path.exists():
            extracted_path.rename(model_path)
            
        # Clean up zip file
        os.remove(zip_path)
        
        st.success(f"✅ {language} model downloaded successfully!")
        return True
        
    except Exception as e:
        st.error(f"❌ Failed to download {language} model: {e}")
        return False

st.title("🎙️ Meeting Summary Writer")
st.markdown("### Multi-language AI-powered transcription and summarization")

# Language status check
available_languages = []
for lang, config in LANGUAGE_MODELS.items():
    if Path(config["model_path"]).exists():
        available_languages.append(f"✅ {lang}")
    else:
        available_languages.append(f"⬇️ {lang} (Download needed - {config['size']})")

with st.expander("🌍 Language Models Status"):
    for status in available_languages:
        st.text(status)
    st.markdown("""
    **Supported Languages:**
    - **English**: General purpose, works with most English accents
    - **Hindi**: Optimized for Hindi speech recognition  
    - **Marathi**: Native Marathi language support
    - **Tamil**: Tamil language recognition
    - **Bengali**: Bengali/Bangla language support
    """)

# Language selection
language = st.selectbox(
    "🌍 Select Language Model",
    list(LANGUAGE_MODELS.keys()),
    help="Choose the language model for transcription. Models will be downloaded automatically if needed."
)

# Auto-download model if not exists
model_config = LANGUAGE_MODELS[language]
model_path = model_config["model_path"]

if not Path(model_path).exists():
    st.warning(f"⚠️ {language} model not found!")
    if st.button(f"📥 Download {language} Model ({model_config['size']})"):
        with st.spinner(f"Downloading {language} model..."):
            if download_model(language):
                st.experimental_rerun()
    st.stop()
else:
    st.success(f"✅ {language} model ready!")

# Speaker Diarization Option
use_speaker_diarization = st.checkbox(
    "👥 Enable Speaker Diarization",
    help="Identify different speakers in the audio. Best for meetings with 2-4 people."
)

# Timestamped Transcript Option
use_timestamped_transcript = st.checkbox(
    "⏰ Enable Timestamped Transcript",
    help="Show precise timestamps for each word/phrase in the transcript."
)

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
    st.write("### 🎧 Step 1: Transcribing audio...")
    progress_bar = st.progress(0)
    progress_bar.progress(25, text="Loading model...")
    
    try:
        if use_speaker_diarization:
            # Use speaker diarization
            st.info("\ud83d\udc65 Using speaker diarization - this may take longer...")
            diarizer = SimpleSpeakerDiarizer(model_path)
            progress_bar.progress(50, text="Analyzing speakers and audio...")
            
            result = diarizer.transcribe_with_speakers(str(temp_file))
            transcript = result['full_transcript']
            speaker_count = result.get('speaker_count', 1)
            timestamped_data = None
            
            progress_bar.progress(100, text="Speaker analysis complete!")
            
            # Show speaker info
            st.info(f"\ud83d\udc65 Detected {speaker_count} speaker(s) in the audio")
            
        elif use_timestamped_transcript:
            # Use timestamped transcription
            st.info("⏰ Creating timestamped transcript - this may take longer...")
            transcriber = VoskTranscriber(model_path)
            progress_bar.progress(50, text="Processing timestamps...")
            
            timestamped_data = transcriber.transcribe_with_timestamps(str(temp_file))
            transcript = timestamped_data['full_transcript']
            
            progress_bar.progress(100, text="Timestamp analysis complete!")
            st.info(f"⏰ Generated timestamps for {len(timestamped_data.get('timestamped_words', []))} words")
            
        else:
            # Regular transcription without speaker diarization or timestamps
            transcriber = VoskTranscriber(model_path)
            progress_bar.progress(50, text="Processing audio...")
            transcript = transcriber.transcribe(str(temp_file))
            timestamped_data = None
            progress_bar.progress(100, text="Transcription complete!")
            
    except FileNotFoundError as e:
        st.error(f"❌ Model error: {language} model not found at {model_path}")
        st.info("Try clicking the download button above to get the model.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Transcription error: {e}")
        st.stop()
    
    if not transcript or not transcript.strip():
        st.error("⚠️ Transcription failed or returned empty results. This could be because:")
        st.markdown(f"""
        - The audio quality is poor or too noisy
        - The language doesn't match the selected model ({language})
        - The audio file is corrupted or too short (minimum 3 seconds recommended)
        - The speaker is too far from the microphone
        
        **Try:**
        - Selecting the correct language model
        - Using a different audio file
        - Improving audio quality
        """)
        st.stop()
    else:
        st.write("### 📝 Transcript:")
        
        # Search and Highlight Feature
        with st.expander("🔍 Search & Highlight in Transcript"):
            search_term = st.text_input(
                "Enter keyword to search and highlight:",
                placeholder="e.g., meeting, project, deadline"
            )
            
            if search_term:
                # Count occurrences
                search_count = transcript.lower().count(search_term.lower())
                if search_count > 0:
                    st.success(f"🎯 Found '{search_term}' {search_count} time(s) in transcript")
                    
                    # Highlight the search term
                    highlighted_transcript = transcript
                    import re
                    
                    # Case-insensitive highlighting
                    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
                    highlighted_transcript = pattern.sub(
                        lambda m: f"**:red[{m.group()}]**", 
                        transcript
                    )
                    
                    st.markdown("**Transcript with highlighted search results:**")
                    st.markdown(highlighted_transcript)
                    
                    # Show context around matches
                    st.markdown("**Search Results Context:**")
                    matches = list(pattern.finditer(transcript))
                    for i, match in enumerate(matches[:5]):  # Show first 5 matches
                        start_pos = max(0, match.start() - 50)
                        end_pos = min(len(transcript), match.end() + 50)
                        context = transcript[start_pos:end_pos]
                        
                        # Highlight in context
                        context_highlighted = pattern.sub(
                            lambda m: f"**:red[{m.group()}]**", 
                            context
                        )
                        
                        st.markdown(f"**Match {i+1}:** ...{context_highlighted}...")
                        
                else:
                    st.warning(f"🔍 No matches found for '{search_term}'")
                    st.info("Try searching for different keywords or check spelling.")
        
        # Regular transcript display
        st.text_area(
            "Full Transcript", 
            transcript, 
            height=300,
            help="The complete transcription of your audio file"
        )
        
        # Timestamped transcript display (if available)
        if timestamped_data:
            with st.expander("⏰ Timestamped Transcript Details"):
                st.markdown("**Formatted transcript with time markers:**")
                st.text_area(
                    "Timestamped Transcript",
                    timestamped_data['timestamped_transcript'],
                    height=400,
                    help="Transcript with precise timestamps for each segment"
                )
                
                # Show statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Words", len(timestamped_data.get('timestamped_words', [])))
                with col2:
                    st.metric("Duration", f"{timestamped_data.get('total_duration', 0):.1f}s")
                with col3:
                    avg_confidence = sum(w.get('confidence', 1.0) for w in timestamped_data.get('timestamped_words', [])) / max(len(timestamped_data.get('timestamped_words', [])), 1)
                    st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                
                # Word-level details (first 50 words)
                if timestamped_data.get('timestamped_words'):
                    st.markdown("**Word-level timing (first 50 words):**")
                    word_data = []
                    for word_info in timestamped_data['timestamped_words'][:50]:
                        word_data.append({
                            'Word': word_info['word'],
                            'Start': f"{word_info['start']:.2f}s",
                            'End': f"{word_info['end']:.2f}s",
                            'Confidence': f"{word_info.get('confidence', 1.0):.2f}"
                        })
                    
                    import pandas as pd
                    df = pd.DataFrame(word_data)
                    st.dataframe(df, use_container_width=True)
                    
                    if len(timestamped_data['timestamped_words']) > 50:
                        st.info(f"Showing first 50 words out of {len(timestamped_data['timestamped_words'])} total words")
        
        st.info("👁️ **Please review the transcript above**. If it looks incorrect, try using the correct language model or check audio quality.")
        
        # Summarize
        st.write("### 🤖 Step 2: Generating AI summary...")
        
        # Custom Summarization Options
        with st.expander("🎯 Customize Summary Style"):
            summarizer = MeetingSummarizer()
            available_styles = summarizer.get_available_styles()
            
            summary_style = st.selectbox(
                "Choose Summary Style:",
                options=list(available_styles.keys()),
                help="Select the type of summary that best fits your needs"
            )
            
            # Show style description
            st.info(f"📝 {available_styles[summary_style]}")
            
            # Custom prompt option
            use_custom_prompt = st.checkbox(
                "🎨 Use Custom Prompt",
                help="Create your own summary template"
            )
            
            custom_prompt = None
            if use_custom_prompt:
                st.markdown("**Custom Prompt Template:**")
                st.markdown("Use `{transcript}` as placeholder for the meeting transcript.")
                
                custom_prompt = st.text_area(
                    "Enter your custom prompt:",
                    value="""Meeting Transcript:
{transcript}

Create a custom summary with:

**SECTION 1**
• Your custom point 1
• Your custom point 2

**SECTION 2**  
• Another custom section""",
                    height=200,
                    help="Design your own summary format. Use {transcript} placeholder."
                )
                
                if custom_prompt and "{transcript}" not in custom_prompt:
                    st.warning("⚠️ Your custom prompt should include {transcript} placeholder!")
        
        # Generate summary with selected options
        with st.spinner("🤖 AI is analyzing the transcript..."):
            if use_custom_prompt and custom_prompt and "{transcript}" in custom_prompt:
                summary = summarizer.summarize(transcript, custom_prompt=custom_prompt)
                st.success(f"✨ Generated custom summary!")
            else:
                summary = summarizer.summarize(transcript, style=summary_style)
                st.success(f"✨ Generated {summary_style.lower()} summary!")
        
        st.write("### ✨ Summary:")
        st.text_area("AI-Generated Summary", summary, height=300)
        
        # Save results
        transcript_file = temp_file.parent / (temp_file.stem + "_transcript.txt")
        summary_file = temp_file.parent / (temp_file.stem + "_summary.md")
        
        try:
            # Clean text before saving to prevent encoding issues
            clean_transcript = transcript.encode('utf-8', errors='ignore').decode('utf-8')
            clean_summary = summary.encode('utf-8', errors='ignore').decode('utf-8')
            
            transcript_file.write_text(clean_transcript, encoding='utf-8')
            summary_file.write_text(clean_summary, encoding='utf-8')
            
            st.success("Files saved:")
            st.write(f"Transcript: {transcript_file}")
            st.write(f"Summary: {summary_file}")
        except Exception as e:
            st.warning(f"⚠️ File saving failed: {e}")
            st.info("Files were not saved to disk, but you can copy the content above.")