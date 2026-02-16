import ollama
from typing import Dict, Any

class MeetingSummarizer:
    def __init__(self, model: str = 'llama3.2:3b'):
        """Initialize Ollama-based meeting summarizer.
        
        Args:
            model: Ollama model to use for summarization
        """
        self.model = model
        self.summary_styles = self._get_summary_styles()
    
    def _get_summary_styles(self) -> Dict[str, Dict[str, str]]:
        """Define different summary styles with their prompts and descriptions"""
        return {
            "Executive Summary": {
                "description": "High-level overview for executives and stakeholders",
                "max_length": 600,
                "prompt_template": """Meeting Transcript:
{transcript}

Create an EXECUTIVE SUMMARY in this format:

**EXECUTIVE OVERVIEW**
• Brief meeting purpose and key outcomes

**KEY DECISIONS MADE**
• Major decision point 1
• Major decision point 2

**ACTION ITEMS & OWNERSHIP**
• [Name]: [Task] by [Date]
• [Name]: [Task] by [Date]

**STRATEGIC IMPLICATIONS**
• Impact on business/project goals
• Resource requirements or changes needed

**NEXT MEETING/FOLLOW-UP**
• Date and purpose of next meeting
• What needs to be prepared"""
            },
            
            "Detailed Meeting Notes": {
                "description": "Comprehensive notes capturing all discussion points",
                "max_length": 1000,
                "prompt_template": """Meeting Transcript:
{transcript}

Create DETAILED MEETING NOTES in this format:

**ATTENDEES & ROLES**
• List key participants if mentioned

**DISCUSSION HIGHLIGHTS**
• Main point discussed 1
• Main point discussed 2
• Important questions raised

**DECISIONS & AGREEMENTS**
• Decision made 1 with rationale
• Decision made 2 with rationale

**ACTION ITEMS**
• [Owner]: [Detailed task] - Due: [Date]
• [Owner]: [Detailed task] - Due: [Date]

**OPEN ISSUES**
• Unresolved item 1
• Unresolved item 2

**RESOURCES NEEDED**
• Budget/tools/people required"""
            },
            
            "Action-Focused": {
                "description": "Emphasis on tasks, deadlines, and next steps",
                "max_length": 400,
                "prompt_template": """Meeting Transcript:
{transcript}

Create an ACTION-FOCUSED summary:

**IMMEDIATE ACTIONS (This Week)**
• [Owner]: [Task] by [Day]
• [Owner]: [Task] by [Day]

**SHORT-TERM ACTIONS (Next 2 Weeks)**  
• [Owner]: [Task] by [Date]
• [Owner]: [Task] by [Date]

**DECISIONS REQUIRING ACTION**
• Decision → Action needed → Owner

**BLOCKERS TO RESOLVE**
• Issue → Who will resolve → When

**FOLLOW-UP SCHEDULE**
• Next check-in date and agenda items"""
            },
            
            "Creative Brief": {
                "description": "Creative and engaging summary with key insights",
                "max_length": 500,
                "prompt_template": """Meeting Transcript:
{transcript}

Create a CREATIVE SUMMARY:

**🎯 MEETING PURPOSE**
Brief purpose and main goal

**💡 KEY INSIGHTS**
• Most important insight or breakthrough
• Surprising discovery or learning

**🚀 MOMENTUM BUILDERS**
• What's driving progress forward
• Exciting opportunities identified  

**🔄 ACTION LOOP**
• Who → Does What → By When → Result Expected

**⚠️ WATCH OUT FOR**
• Potential challenges or risks ahead

**🎉 CELEBRATION WORTHY**
• Achievement or milestone to recognize"""
            },
            
            "Technical Summary": {
                "description": "Technical meetings with focus on specifications and requirements",
                "max_length": 700,
                "prompt_template": """Meeting Transcript:
{transcript}

Create a TECHNICAL SUMMARY:

**TECHNICAL REQUIREMENTS**
• Requirement 1 with specifications
• Requirement 2 with specifications

**ARCHITECTURE/DESIGN DECISIONS**
• Design choice 1 → Rationale
• Design choice 2 → Rationale

**IMPLEMENTATION TASKS**
• [Dev]: [Technical task] - Priority: High/Medium/Low
• [Dev]: [Technical task] - Priority: High/Medium/Low

**DEPENDENCIES & BLOCKERS**
• External dependency → Impact → Timeline
• Technical blocker → Resolution plan

**TESTING & VALIDATION**
• Testing approach decided
• Success criteria defined

**TECHNICAL RISKS**
• Risk → Mitigation strategy → Owner"""
            }
        }
    
    def get_available_styles(self) -> Dict[str, str]:
        """Get available summary styles with descriptions"""
        return {style: info["description"] for style, info in self.summary_styles.items()}
    
    def summarize(self, transcript: str, style: str = "Executive Summary", custom_prompt: str = None) -> str:
        """Generate structured meeting summary from transcript.
        
        Args:
            transcript: Full meeting transcript text
            style: Summary style to use
            custom_prompt: Custom prompt template (overrides style)
            
        Returns:
            Structured summary based on selected style or custom prompt
        """
        print(f"🤖 Summarizing with {self.model} using '{style}' style...")
        
        if custom_prompt:
            # Use custom prompt
            print("🎨 Using custom prompt template...")
            prompt = custom_prompt.format(transcript=transcript[:4000])
            max_tokens = 800
        elif style in self.summary_styles:
            # Use predefined style
            style_info = self.summary_styles[style]
            prompt = style_info["prompt_template"].format(transcript=transcript[:4000])
            max_tokens = style_info["max_length"]
        else:
            # Fallback to default
            return self._default_summary(transcript)
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.1,  # Low temperature for consistent formatting
                    'num_predict': max_tokens
                }
            )
            
            summary = response['response']
            print("✅ Summary generation complete")
            return summary
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _default_summary(self, transcript: str) -> str:
        """Fallback default summary"""
        return self.summarize(transcript, "Executive Summary")