import os
import wave
import json
import re
from vosk import Model, KaldiRecognizer

class VoskTranscriber:
    def __init__(self, model_path: str = "model"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path '{model_path}' does not exist.")
        self.model = Model(model_path)

    def _clean_text(self, text: str) -> str:
        """Clean text to remove invalid Unicode characters and surrogates"""
        if not text:
            return ""
        
        try:
            # Remove or replace surrogate characters
            cleaned = text.encode('utf-8', errors='ignore').decode('utf-8')
            # Remove control characters except newlines and tabs
            cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
            # Normalize whitespace
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return cleaned
        except Exception as e:
            print(f"Warning: Text cleaning failed: {e}")
            # Fallback: keep only ASCII characters
            return ''.join(char for char in text if ord(char) < 128).strip()

    def transcribe(self, audio_file_path: str) -> str:
        """Standard transcription without timestamps"""
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file '{audio_file_path}' does not exist.")

        # Only accept WAV files
        if not audio_file_path.lower().endswith(".wav"):
            raise ValueError("Only WAV files are supported. Please convert your audio/video file to WAV format using an online converter or audio editing software.")

        wav_file_path = audio_file_path

        # Check if the WAV file needs conversion to mono PCM
        converted_file_path = None
        try:
            with wave.open(wav_file_path, "rb") as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    # Need to convert to mono PCM
                    converted_file_path = wav_file_path.rsplit(".", 1)[0] + "_converted.wav"
                    self._convert_to_mono_pcm(wav_file_path, converted_file_path)
                    wav_file_path = converted_file_path
        except Exception as e:
            raise RuntimeError(f"Failed to process WAV file: {e}")

        try:
            with wave.open(wav_file_path, "rb") as wf:
                rec = KaldiRecognizer(self.model, wf.getframerate())
                transcript_parts = []

                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        try:
                            result = rec.Result()
                            result_dict = json.loads(result)
                            if 'text' in result_dict and result_dict['text'].strip():
                                clean_text = self._clean_text(result_dict['text'])
                                if clean_text:
                                    transcript_parts.append(clean_text)
                        except (json.JSONDecodeError, UnicodeError) as e:
                            print(f"Warning: Skipping invalid result: {e}")
                            continue

                # Get the final result
                try:
                    final_result = rec.FinalResult()
                    final_result_dict = json.loads(final_result)
                    if 'text' in final_result_dict and final_result_dict['text'].strip():
                        clean_text = self._clean_text(final_result_dict['text'])
                        if clean_text:
                            transcript_parts.append(clean_text)
                except (json.JSONDecodeError, UnicodeError) as e:
                    print(f"Warning: Final result parsing failed: {e}")

                # Join and clean the final transcript
                final_transcript = " ".join(transcript_parts).strip()
                return self._clean_text(final_transcript)
        finally:
            # Clean up converted file if it was created
            if converted_file_path and os.path.exists(converted_file_path):
                os.remove(converted_file_path)

    def transcribe_with_timestamps(self, audio_file_path: str) -> dict:
        """Transcription with word-level timestamps"""
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file '{audio_file_path}' does not exist.")

        if not audio_file_path.lower().endswith(".wav"):
            raise ValueError("Only WAV files are supported.")

        wav_file_path = audio_file_path
        converted_file_path = None
        
        try:
            with wave.open(wav_file_path, "rb") as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    converted_file_path = wav_file_path.rsplit(".", 1)[0] + "_converted.wav"
                    self._convert_to_mono_pcm(wav_file_path, converted_file_path)
                    wav_file_path = converted_file_path
        except Exception as e:
            raise RuntimeError(f"Failed to process WAV file: {e}")

        try:
            with wave.open(wav_file_path, "rb") as wf:
                # Enable word-level timestamps
                rec = KaldiRecognizer(self.model, wf.getframerate())
                rec.SetWords(True)
                
                timestamped_words = []
                transcript_segments = []
                current_segment = []
                current_start_time = 0

                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    
                    if rec.AcceptWaveform(data):
                        try:
                            result = rec.Result()
                            result_dict = json.loads(result)
                            
                            if 'result' in result_dict:
                                words = result_dict['result']
                                for word_info in words:
                                    clean_word = self._clean_text(word_info.get('word', ''))
                                    if clean_word:  # Only add non-empty words
                                        timestamped_words.append({
                                            'word': clean_word,
                                            'start': word_info.get('start', 0),
                                            'end': word_info.get('end', 0),
                                            'confidence': word_info.get('conf', 1.0)
                                        })
                                        current_segment.append(clean_word)
                                
                                if current_segment:
                                    segment_text = ' '.join(current_segment)
                                    transcript_segments.append({
                                        'text': self._clean_text(segment_text),
                                        'start': current_start_time,
                                        'end': timestamped_words[-1]['end'] if timestamped_words else current_start_time,
                                        'words': len(current_segment)
                                    })
                                    current_segment = []
                                    current_start_time = timestamped_words[-1]['end'] if timestamped_words else current_start_time
                        except (json.JSONDecodeError, UnicodeError, KeyError) as e:
                            print(f"Warning: Skipping invalid timestamped result: {e}")
                            continue

                # Get final result
                try:
                    final_result = rec.FinalResult()
                    final_result_dict = json.loads(final_result)
                    
                    if 'result' in final_result_dict:
                        words = final_result_dict['result']
                        for word_info in words:
                            clean_word = self._clean_text(word_info.get('word', ''))
                            if clean_word:
                                timestamped_words.append({
                                    'word': clean_word,
                                    'start': word_info.get('start', 0),
                                    'end': word_info.get('end', 0),
                                    'confidence': word_info.get('conf', 1.0)
                                })
                except (json.JSONDecodeError, UnicodeError, KeyError) as e:
                    print(f"Warning: Final timestamped result parsing failed: {e}")

                # Generate formatted transcript with timestamps
                formatted_transcript = self._format_timestamped_transcript(timestamped_words)
                full_text = ' '.join([w['word'] for w in timestamped_words])
                clean_full_text = self._clean_text(full_text)

                return {
                    'full_transcript': clean_full_text,
                    'timestamped_transcript': formatted_transcript,
                    'timestamped_words': timestamped_words,
                    'segments': transcript_segments,
                    'total_duration': timestamped_words[-1]['end'] if timestamped_words else 0
                }
                
        finally:
            if converted_file_path and os.path.exists(converted_file_path):
                os.remove(converted_file_path)

    def _format_timestamped_transcript(self, timestamped_words: list, words_per_line: int = 10) -> str:
        """Format timestamped words into readable transcript with time markers"""
        if not timestamped_words:
            return ""
            
        formatted_lines = []
        current_line_words = []
        current_line_start = None
        
        for i, word_info in enumerate(timestamped_words):
            if current_line_start is None:
                current_line_start = word_info['start']
            
            current_line_words.append(word_info['word'])
            
            # Add line break every N words or at natural pauses
            if len(current_line_words) >= words_per_line or (
                i < len(timestamped_words) - 1 and 
                timestamped_words[i + 1]['start'] - word_info['end'] > 1.0  # 1 second pause
            ):
                line_end_time = word_info['end']
                start_timestamp = self._format_timestamp(current_line_start)
                end_timestamp = self._format_timestamp(line_end_time)
                
                line_text = ' '.join(current_line_words)
                formatted_lines.append(f"[{start_timestamp} - {end_timestamp}] {line_text}")
                
                current_line_words = []
                current_line_start = None
        
        # Add remaining words
        if current_line_words:
            line_end_time = timestamped_words[-1]['end']
            start_timestamp = self._format_timestamp(current_line_start or 0)
            end_timestamp = self._format_timestamp(line_end_time)
            
            line_text = ' '.join(current_line_words)
            formatted_lines.append(f"[{start_timestamp} - {end_timestamp}] {line_text}")
        
        return '\n'.join(formatted_lines)

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file '{audio_file_path}' does not exist.")

        # Only accept WAV files
        if not audio_file_path.lower().endswith(".wav"):
            raise ValueError("Only WAV files are supported. Please convert your audio/video file to WAV format using an online converter or audio editing software.")

        wav_file_path = audio_file_path

        # Check if the WAV file needs conversion to mono PCM
        converted_file_path = None
        try:
            with wave.open(wav_file_path, "rb") as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    # Need to convert to mono PCM
                    converted_file_path = wav_file_path.rsplit(".", 1)[0] + "_converted.wav"
                    self._convert_to_mono_pcm(wav_file_path, converted_file_path)
                    wav_file_path = converted_file_path
        except Exception as e:
            raise RuntimeError(f"Failed to process WAV file: {e}")

        try:
            with wave.open(wav_file_path, "rb") as wf:
                rec = KaldiRecognizer(self.model, wf.getframerate())
                transcript_parts = []

                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        result = rec.Result()
                        result_dict = json.loads(result)
                        if 'text' in result_dict:
                            transcript_parts.append(result_dict['text'])

                # Get the final result
                final_result = rec.FinalResult()
                final_result_dict = json.loads(final_result)
                if 'text' in final_result_dict:
                    transcript_parts.append(final_result_dict['text'])

            return ' '.join(transcript_parts)
        finally:
            # Clean up converted file if created
            if converted_file_path and os.path.exists(converted_file_path):
                try:
                    os.remove(converted_file_path)
                except:
                    pass  # Ignore cleanup errors

    def _convert_to_mono_pcm(self, input_path: str, output_path: str):
        """Convert WAV file to mono PCM format"""
        with wave.open(input_path, "rb") as input_wav:
            # Get input parameters
            channels = input_wav.getnchannels()
            sample_width = input_wav.getsampwidth()
            framerate = input_wav.getframerate()
            frames = input_wav.readframes(input_wav.getnframes())

            # Convert to mono if stereo
            if channels == 2:
                import struct
                # Convert stereo to mono by averaging channels
                fmt = '<' + ('h' * (len(frames) // 2))
                samples = list(struct.unpack(fmt, frames))
                mono_samples = []
                for i in range(0, len(samples), 2):
                    mono_samples.append((samples[i] + samples[i+1]) // 2)
                frames = struct.pack('<' + ('h' * len(mono_samples)), *mono_samples)
                channels = 1

            # Write converted file
            with wave.open(output_path, "wb") as output_wav:
                output_wav.setnchannels(channels)
                output_wav.setsampwidth(2)  # 16-bit PCM
                output_wav.setframerate(framerate)
                output_wav.writeframes(frames)

# Example usage
if __name__ == "__main__":
    transcriber = VoskTranscriber()
    transcription = transcriber.transcribe("path_to_audio_file.wav")
    print(transcription)