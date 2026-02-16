import typer
from rich import print
from pathlib import Path
from .transcriber.vosk_transcriber import VoskTranscriber
from .summarizer import MeetingSummarizer
import os

app = typer.Typer(help="Meeting Summary Writer - Convert audio recordings to structured summaries")

@app.command()
def summarize(
    audio_file: Path = typer.Argument(..., help="Path to audio file (MP3, WAV, M4A, etc.)"),
    output_dir: Path = typer.Option(None, help="Output directory (defaults to same as audio file)")
):
    """
    Convert meeting audio → transcript + structured summary
    
    Example: python -m src.main sales_call.mp3
    """
    
    # Validate input file
    if not audio_file.exists():
        print(f"❌ [red]Audio file not found: {audio_file}[/red]")
        raise typer.Exit(1)
    
    if not audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a', '.mp4', '.avi', '.mov']:
        print(f"⚠️ [yellow]Warning: {audio_file.suffix} may not be supported by Vosk[/yellow]")
    
    # Set output directory
    if output_dir is None:
        output_dir = audio_file.parent
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 [bold blue]Meeting Summary Writer[/bold blue]")
    print(f"📁 Input: {audio_file}")
    print(f"📁 Output: {output_dir}")
    
    try:
        print("\n🔧 [bold]Step 1: Initialize Transcriber[/bold]")
        # Step 1: Transcribe
        transcriber = VoskTranscriber()
        
        print("\n🔧 [bold]Step 2: Start Transcription[/bold]")
        transcript = transcriber.transcribe(str(audio_file))
        
        if not transcript or len(transcript.strip()) == 0:
            print("❌ [red]Empty transcript generated![/red]")
            raise typer.Exit(1)
        
        print(f"\n💾 [bold]Step 3: Save Transcript[/bold]")
        # Save transcript
        transcript_file = output_dir / f"{audio_file.stem}_transcript.txt"
        transcript_file.write_text(transcript, encoding='utf-8')
        print(f"💾 Saved: [blue]{transcript_file}[/blue]")
        
        print(f"\n🤖 [bold]Step 4: Generate Summary[/bold]")
        # Step 2: Summarize
        summarizer = MeetingSummarizer()
        summary = summarizer.summarize(transcript)
        
        print(f"\n💾 [bold]Step 5: Save Summary[/bold]") 
        # Save summary
        summary_file = output_dir / f"{audio_file.stem}_summary.md"
        summary_content = f"# Meeting Summary: {audio_file.stem}\n\n{summary}"
        summary_file.write_text(summary_content, encoding='utf-8')
        print(f"💾 Saved: [blue]{summary_file}[/blue]")
        
        print("\n🎉 [bold green]COMPLETE![/bold green]")
        print(f"✅ Transcript: [blue]{transcript_file.name}[/blue]")
        print(f"✅ Summary: [blue]{summary_file.name}[/blue]")
        
        # Preview summary
        print("\n--- 📋 [bold]SUMMARY PREVIEW[/bold] ---")
        print(summary)
        
    except KeyboardInterrupt:
        print("\n❌ [red]Operation cancelled by user[/red]")
        raise typer.Exit(1)
    except Exception as e:
        print(f"\n❌ [red]Error: {type(e).__name__}: {str(e)}[/red]")
        
        # Log the full traceback for debugging
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)

@app.command()
def check_setup():
    """Verify Ollama server and model availability."""
    print("🔍 Checking setup...")
    
    try:
        import ollama
        models = ollama.list()
        
        if any('llama3.2:3b' in str(model) for model in models['models']):
            print("✅ [green]Ollama server running[/green]")
            print("✅ [green]llama3.2:3b model available[/green]")
        else:
            print("❌ [red]llama3.2:3b model not found[/red]")
            print("💡 Run: [blue]ollama pull llama3.2:3b[/blue]")
    except Exception as e:
        print(f"❌ [red]Ollama server not available: {e}[/red]")
        print("💡 Run: [blue]ollama serve[/blue]")

if __name__ == "__main__":
    app()