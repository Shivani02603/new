"""
Speaker diarization module for identifying different speakers in audio files.
Uses a combination of silence detection and speaker change detection.
"""

import json
import wave
import numpy as np
from typing import List, Dict, Tuple
import vosk
from pathlib import Path


class SpeakerDiarizer:
    def __init__(self, model_path: str):
        """
        Initialize speaker diarization with Vosk model
        Args:
            model_path: Path to Vosk model directory
        """
        self.model = vosk.Model(model_path)
        self.rec = vosk.KaldiRecognizer(self.model, 16000)
        self.rec.SetWords(True)  # Enable word-level timestamps
    
    def detect_speaker_changes(self, audio_file: str, min_segment_duration: float = 3.0) -> List[Dict]:
        """
        Detect speaker changes in audio file using silence and energy analysis
        Args:
            audio_file: Path to WAV audio file
            min_segment_duration: Minimum duration for a speaker segment in seconds
        Returns:
            List of speaker segments with timestamps
        """
        # Read audio file
        wf = wave.open(audio_file, 'rb')
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise ValueError("Audio file must be WAV format mono PCM 16kHz")
        
        # Process audio in chunks
        segments = []
        current_speaker = 1
        segment_start = 0.0
        last_speaker_change = 0.0
        
        chunk_size = 4000  # 0.25 seconds at 16kHz
        audio_data = []
        
        while True:
            data = wf.readframes(chunk_size)
            if len(data) == 0:
                break
                
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())
                if result.get('text', '').strip():
                    # Get word-level timing information
                    words = result.get('result', [])
                    if words:
                        segment_end = words[-1].get('end', 0)
                        
                        # Simple speaker change detection based on silence gaps
                        silence_duration = segment_end - last_speaker_change
                        
                        # If there's a significant pause, assume speaker change
                        if silence_duration > 2.0 and (segment_end - segment_start) > min_segment_duration:
                            segments.append({
                                'speaker': f'Speaker {current_speaker}',
                                'start_time': segment_start,
                                'end_time': segment_end,
                                'duration': segment_end - segment_start,
                                'text': self._extract_text_for_segment(words, segment_start, segment_end)
                            })
                            
                            current_speaker += 1
                            segment_start = segment_end
                        
                        last_speaker_change = segment_end
        
        # Add final segment
        final_result = json.loads(self.rec.FinalResult())
        if final_result.get('text', '').strip():
            final_end = last_speaker_change + 1.0  # Estimate final end time
            segments.append({
                'speaker': f'Speaker {current_speaker}',
                'start_time': segment_start,
                'end_time': final_end,
                'duration': final_end - segment_start,
                'text': final_result['text']
            })
        
        wf.close()
        return segments
    
    def _extract_text_for_segment(self, words: List[Dict], start_time: float, end_time: float) -> str:
        """Extract text for a specific time segment"""
        segment_words = []
        for word in words:
            if start_time <= word.get('start', 0) <= end_time:
                segment_words.append(word.get('word', ''))
        return ' '.join(segment_words)
    
    def transcribe_with_speakers(self, audio_file: str) -> Dict:
        """
        Transcribe audio with speaker identification
        Args:
            audio_file: Path to WAV audio file
        Returns:
            Dictionary with full transcript and speaker segments
        """
        try:
            segments = self.detect_speaker_changes(audio_file)
            
            # Create full transcript with speaker labels
            full_transcript = ""
            speaker_count = len(set(seg['speaker'] for seg in segments))
            
            for segment in segments:
                timestamp_start = self._format_timestamp(segment['start_time'])
                timestamp_end = self._format_timestamp(segment['end_time'])
                
                full_transcript += f"\n[{timestamp_start} - {timestamp_end}] {segment['speaker']}:\n"
                full_transcript += f"{segment['text']}\n"
            
            return {
                'full_transcript': full_transcript.strip(),
                'segments': segments,
                'speaker_count': speaker_count,
                'total_duration': segments[-1]['end_time'] if segments else 0
            }
            
        except Exception as e:
            # Fallback to regular transcription if speaker detection fails
            return self._fallback_transcription(audio_file, str(e))
    
    def _fallback_transcription(self, audio_file: str, error_msg: str) -> Dict:
        """Fallback to regular transcription without speaker detection"""
        wf = wave.open(audio_file, 'rb')
        
        transcript = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())
                transcript += result.get('text', '') + " "
        
        final_result = json.loads(self.rec.FinalResult())
        transcript += final_result.get('text', '')
        
        wf.close()
        
        return {
            'full_transcript': f"[Single Speaker - Diarization Failed: {error_msg}]\n\n{transcript.strip()}",
            'segments': [{
                'speaker': 'Speaker 1 (Unknown)',
                'start_time': 0,
                'end_time': 0,
                'duration': 0,
                'text': transcript.strip()
            }],
            'speaker_count': 1,
            'total_duration': 0,
            'warning': f"Speaker diarization failed: {error_msg}"
        }
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


class SimpleSpeakerDiarizer:
    """
    Simplified speaker diarization that uses energy-based segmentation
    More reliable but less accurate than advanced methods
    """
    
    def __init__(self, model_path: str):
        self.model = vosk.Model(model_path)
    
    def transcribe_with_speakers(self, audio_file: str, energy_threshold: float = 0.3) -> Dict:
        """
        Simple speaker detection using energy levels and pauses
        """
        # Read and analyze audio
        wf = wave.open(audio_file, 'rb')
        frames = wf.readframes(wf.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.int16)
        
        # Calculate energy levels
        window_size = 16000  # 1 second windows
        energy_windows = []
        
        for i in range(0, len(audio_data), window_size):
            window = audio_data[i:i+window_size]
            energy = np.mean(window**2)
            energy_windows.append(energy)
        
        # Normalize energy
        max_energy = max(energy_windows) if energy_windows else 1
        normalized_energy = [e/max_energy for e in energy_windows]
        
        # Detect speaker changes based on energy changes
        speaker_changes = [0]  # Start with first speaker at time 0
        current_speaker_energy = normalized_energy[0] if normalized_energy else 0
        
        for i, energy in enumerate(normalized_energy[1:], 1):
            # If energy changes significantly, assume speaker change
            energy_change = abs(energy - current_speaker_energy)
            if energy_change > energy_threshold:
                speaker_changes.append(i)
                current_speaker_energy = energy
        
        wf.close()
        
        # Now transcribe with speaker segments
        rec = vosk.KaldiRecognizer(self.model, 16000)
        rec.SetWords(True)
        
        wf = wave.open(audio_file, 'rb')
        segments = []
        current_segment = 0
        current_speaker = 1
        transcript_parts = []
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
                
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get('text', '').strip()
                if text:
                    # Estimate time based on processed data
                    estimated_time = len(transcript_parts) * 0.25  # Rough estimate
                    
                    # Check if we should change speaker based on our energy analysis
                    time_window = int(estimated_time)
                    if time_window in speaker_changes and len(segments) > 0:
                        current_speaker += 1
                    
                    segments.append({
                        'speaker': f'Speaker {current_speaker}',
                        'text': text,
                        'estimated_time': estimated_time
                    })
                    transcript_parts.append(text)
        
        # Get final result
        final_result = json.loads(rec.FinalResult())
        if final_result.get('text', '').strip():
            segments.append({
                'speaker': f'Speaker {current_speaker}',
                'text': final_result['text'],
                'estimated_time': len(transcript_parts) * 0.25
            })
        
        wf.close()
        
        # Format final transcript
        full_transcript = ""
        current_speaker_name = ""
        current_speaker_text = []
        
        for segment in segments:
            if segment['speaker'] != current_speaker_name:
                # Finalize previous speaker
                if current_speaker_text:
                    full_transcript += f"{current_speaker_name}:\n{' '.join(current_speaker_text)}\n\n"
                
                # Start new speaker
                current_speaker_name = segment['speaker']
                current_speaker_text = [segment['text']]
            else:
                current_speaker_text.append(segment['text'])
        
        # Add final speaker
        if current_speaker_text:
            full_transcript += f"{current_speaker_name}:\n{' '.join(current_speaker_text)}"
        
        return {
            'full_transcript': full_transcript.strip(),
            'segments': segments,
            'speaker_count': current_speaker,
            'method': 'energy_based_simple'
        }