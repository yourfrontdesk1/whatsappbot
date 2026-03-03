import anthropic
import os
from typing import List, Dict


class ClaudeHandler:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

        # Load system prompt
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'prompts',
            'system_prompt.txt'
        )
        with open(prompt_path, 'r') as f:
            self.system_prompt = f.read()

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict] = None,
        intent: str = None
    ) -> str:
        """Generate AI response using Claude"""

        # Build messages array
        messages = []

        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg['role'],
                    "content": msg['message_text']
                })

        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Enhance system prompt based on intent
        enhanced_prompt = self.system_prompt
        if intent == 'booking':
            enhanced_prompt += "\n\nUSER IS TRYING TO BOOK. Collect: name, service, date, time."
        elif intent == 'hours':
            enhanced_prompt += "\n\nUSER ASKING ABOUT HOURS. Provide full schedule clearly."

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=enhanced_prompt,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            print(f"Claude API error: {e}")
            return (
                "I apologize, I'm having trouble right now. "
                "Please call us at +350 56005388 for immediate assistance."
            )
