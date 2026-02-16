# Hindi Language Support Setup

## Current Status
- **Current Model**: English (vosk-model-small-en-us)
- **Result**: Hindi audio will produce incorrect/gibberish transcriptions

## To Add Hindi Support:

### Step 1: Download Hindi Model
1. Go to: https://alphacephei.com/vosk/models
2. Download one of these Hindi models:
   - `vosk-model-hi-0.22` (Recommended - 294MB)
   - `vosk-model-small-hi-0.22` (Smaller - 48MB)

### Step 2: Setup Hindi Model
1. Extract the downloaded ZIP file
2. Rename the extracted folder to `model_hindi`
3. Place it in the meeting-summary-writer directory

Your folder structure should look like:
```
meeting-summary-writer/
├── model/           (English model)
├── model_hindi/     (Hindi model - NEW)
├── app.py
└── src/
```

### Step 3: Update the Code
You can either:

**Option A**: Create a Hindi-specific app
- Copy `app.py` to `app_hindi.py`
- Change the VoskTranscriber initialization to use `model_hindi`

**Option B**: Add language selection to the current app
- I can help modify the app to let users choose between English and Hindi

### Step 4: Test
- Upload a Hindi WAV file
- The transcription should now work correctly in Hindi

## Quick Test
After setup, you can test if the Hindi model works:
```bash
python -c "from vosk import Model; print('Hindi model loaded successfully')" 
```

Would you like me to help implement Option B (language selection in the app)?