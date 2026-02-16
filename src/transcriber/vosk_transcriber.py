import os
import wave
import json
from vosk import Model, KaldiRecognizer

class VoskTranscriber:
    def __init__(self, model_path: str = "model"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path '{model_path}' does not exist.")
        self.model = Model(model_path)

    def transcribe(self, audio_file_path: str) -> str:
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