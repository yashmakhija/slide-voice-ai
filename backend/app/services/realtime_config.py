from typing import Any

from app.data.slides import get_slide_summaries


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "navigate_to_slide",
        "description": (
            "Navigate to a specific slide when the user asks about a topic. "
            "Use this when the user's question relates to content on a different slide."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "slide_id": {
                    "type": "integer",
                    "description": "The slide number to navigate to (1-5)",
                    "minimum": 1,
                    "maximum": 5,
                },
                "reason": {
                    "type": "string",
                    "description": "Brief reason for navigating to this slide",
                },
            },
            "required": ["slide_id"],
        },
    },
    {
        "type": "function",
        "name": "get_current_slide_info",
        "description": "Get information about the current slide being displayed.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "end_presentation",
        "description": (
            "End the presentation session. Call this when the user indicates they are done, "
            "says goodbye, thanks you, or declines to ask more questions after you offer."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "farewell_message": {
                    "type": "string",
                    "description": "A brief farewell message to say before ending",
                },
            },
            "required": [],
        },
    },
]


def build_system_prompt() -> str:
    """Build the system prompt with slide information."""
    slide_summaries = get_slide_summaries()

    return f"""You are an engaging AI presenter giving a presentation about Machine Learning.

## Your Slides
{slide_summaries}

## Your Behavior
1. When the presentation starts, introduce yourself and begin presenting the current slide
2. Speak naturally and conversationally, as if giving a live presentation
3. When users ask questions:
   - If the question relates to a different slide, use navigate_to_slide() to go there first
   - Then answer the question in context of that slide
4. Keep responses concise but informative (2-3 sentences typically)
5. Be enthusiastic and make the content accessible to beginners
6. On the last slide, after presenting, ask if they have questions or want to revisit anything
7. If the user says "no", "bye", "thanks", "that's all", or indicates they're done, call end_presentation() to end the session gracefully

## Navigation Rules
- If user asks about "types of ML" or "supervised/unsupervised" → Slide 2
- If user asks about "applications" or "examples" or "real world" → Slide 3
- If user asks about "training" or "how it learns" → Slide 4
- If user asks about "getting started" or "tools" or "how to begin" → Slide 5
- If user asks about "what is ML" or "definition" → Slide 1

## Voice Style
- Warm and friendly
- Clear explanations without jargon
- Use analogies when helpful
- Pause briefly between key points"""


def build_session_config() -> dict[str, Any]:
    """Build the complete session configuration for OpenAI Realtime API."""
    return {
        "modalities": ["text", "audio"],
        "instructions": build_system_prompt(),
        "voice": "alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "input_audio_transcription": {
            "model": "whisper-1",
        },
        "turn_detection": {
            "type": "server_vad",  # Server-side Voice Activity Detection
            "threshold": 0.5,  # Sensitivity (0.0-1.0)
            "prefix_padding_ms": 300,  # Audio to include before speech
            "silence_duration_ms": 500,  # Silence before end of turn
        },
        "tools": TOOLS,
        "tool_choice": "auto",  # Let AI decide when to use tools
        "temperature": 0.7,
    }
