import ollama
from typing import Dict, Any

class MeetingSummarizer:
    def __init__(self, model: str = 'llama3.2:3b'):
        """Initialize Ollama-based meeting summarizer.
        
        Args:
            model: Ollama model to use for summarization
        """
        self.model = model
    
    def summarize(self, transcript: str) -> str:
        """Generate structured meeting summary from transcript.
        
        Args:
            transcript: Full meeting transcript text
            
        Returns:
            Structured summary with key decisions, action items, next steps, risks
        """
        print(f"🤖 Summarizing with {self.model}...")
        
        # Limit transcript length to avoid token limits
        limited_transcript = transcript[:4000]
        
        prompt = f"""Meeting Transcript:
{limited_transcript}

Output ONLY in this exact format:

**KEY DECISIONS**
• Decision point 1
• Decision point 2

**ACTION ITEMS** 
• [Name]: [Specific task] by [deadline]
• [Name]: [Specific task] by [deadline]

**NEXT STEPS**
• Next immediate action needed
• Follow-up required

**KEY RISKS**
• Potential risk or concern identified
• Another risk that needs attention"""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.1,  # Low temperature for consistent formatting
                    'num_predict': 600   # Limit response length
                }
            )
            
            summary = response['response']
            print("✅ Summary generation complete")
            return summary
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"