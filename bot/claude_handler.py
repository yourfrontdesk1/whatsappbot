import anthropic
from typing import List, Dict, Optional


DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


class ClaudeHandler:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    def build_system_prompt(
        self,
        business: Dict,
        knowledge_base: List[Dict],
        services: List[Dict],
        operating_hours: List[Dict]
    ) -> str:
        """Build a dynamic system prompt from database content"""

        prompt_parts = []

        # Business identity
        prompt_parts.append(f"You are the AI assistant for {business['name']}.")
        if business.get('bot_tone'):
            prompt_parts.append(f"\nTONE & STYLE:\n{business['bot_tone']}")

        # Contact info
        contact_lines = ["\nLOCATION & CONTACT:"]
        if business.get('address'):
            contact_lines.append(f"- Address: {business['address']}")
        if business.get('phone'):
            contact_lines.append(f"- Phone: {business['phone']}")
        if business.get('email'):
            contact_lines.append(f"- Email: {business['email']}")
        if business.get('website'):
            contact_lines.append(f"- Website: {business['website']}")
        if len(contact_lines) > 1:
            prompt_parts.append('\n'.join(contact_lines))

        # Operating hours
        if operating_hours:
            hours_lines = ["\nOPERATING HOURS:"]
            for h in operating_hours:
                day = DAY_NAMES[h['day_of_week']]
                if h.get('is_closed'):
                    hours_lines.append(f"- {day}: CLOSED")
                else:
                    label = f" ({h['label']})" if h.get('label') else ""
                    hours_lines.append(f"- {day}: {h['open_time']} - {h['close_time']}{label}")
            prompt_parts.append('\n'.join(hours_lines))

        # Services
        if services:
            services_lines = ["\nSERVICES:"]
            current_category = None
            for s in services:
                cat = s.get('category', 'General')
                if cat != current_category:
                    current_category = cat
                    services_lines.append(f"\n{cat}:")

                price_str = ""
                if s.get('price_from') and s.get('price_to'):
                    currency = s.get('currency', 'GBP')
                    symbol = '£' if currency == 'GBP' else '€' if currency == 'EUR' else '$'
                    if s['price_from'] == s['price_to']:
                        price_str = f" ({symbol}{s['price_from']})"
                    else:
                        price_str = f" ({symbol}{s['price_from']}-{symbol}{s['price_to']})"
                elif s.get('price_from'):
                    currency = s.get('currency', 'GBP')
                    symbol = '£' if currency == 'GBP' else '€' if currency == 'EUR' else '$'
                    price_str = f" (from {symbol}{s['price_from']})"

                duration_str = f" - {s['duration_minutes']} min" if s.get('duration_minutes') else ""
                desc_str = f": {s['description']}" if s.get('description') else ""
                services_lines.append(f"  - {s['name']}{price_str}{duration_str}{desc_str}")

            prompt_parts.append('\n'.join(services_lines))

        # Knowledge base / FAQs
        if knowledge_base:
            kb_lines = ["\nKNOWLEDGE BASE:"]
            current_category = None
            for entry in knowledge_base:
                cat = entry.get('category', 'General')
                if cat != current_category:
                    current_category = cat
                    kb_lines.append(f"\n[{cat}]")
                kb_lines.append(f"Q: {entry['question']}")
                kb_lines.append(f"A: {entry['answer']}\n")
            prompt_parts.append('\n'.join(kb_lines))

        # Standard instructions
        prompt_parts.append("""
RESPONSE GUIDELINES:
- Keep responses concise and suited for WhatsApp
- Use emojis sparingly
- Always offer to help with bookings or transfer to staff
- End with: "Anything else I can help with?"

BOOKING PROCESS:
When someone wants to book:
1. Ask for: Name, preferred service, date, time
2. Confirm details
3. Tell them their request has been noted and the team will confirm availability

ESCALATION:
Transfer to human staff if:
- Medical questions
- Complaints
- Complex booking issues
- Payment problems""")

        if business.get('phone'):
            prompt_parts.append(f"\nFor urgent matters, direct customers to call: {business['phone']}")

        return '\n'.join(prompt_parts)

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict] = None,
        intent: str = None,
        business: Dict = None,
        knowledge_base: List[Dict] = None,
        services: List[Dict] = None,
        operating_hours: List[Dict] = None
    ) -> str:
        """Generate AI response using Claude with dynamic business context"""

        # Build system prompt from DB data or use fallback
        if business:
            system_prompt = self.build_system_prompt(
                business=business,
                knowledge_base=knowledge_base or [],
                services=services or [],
                operating_hours=operating_hours or []
            )
        else:
            system_prompt = "You are a helpful WhatsApp assistant. Be concise."

        # Enhance based on intent
        if intent == 'booking':
            system_prompt += "\n\nUSER IS TRYING TO BOOK. Collect: name, service, date, time."
        elif intent == 'hours':
            system_prompt += "\n\nUSER ASKING ABOUT HOURS. Provide full schedule clearly."

        # Build messages array
        messages = []
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg['role'],
                    "content": msg['message_text']
                })

        messages.append({
            "role": "user",
            "content": user_message
        })

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text

        except Exception as e:
            print(f"Claude API error: {e}")
            fallback = business.get('fallback_message') if business else None
            return fallback or (
                "I apologize, I'm having trouble right now. "
                "Please call us for immediate assistance."
            )
