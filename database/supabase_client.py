from supabase import create_client, Client
from typing import List, Dict


class SupabaseDB:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    def save_message(self, phone: str, text: str, role: str, intent: str = None):
        """Save message to database"""
        try:
            data = {
                'phone_number': phone,
                'message_text': text,
                'role': role,
            }
            if intent:
                data['intent'] = intent
            self.client.table('whatsapp_messages').insert(data).execute()
        except Exception as e:
            print(f"DB save error: {e}")

    def get_conversation_history(self, phone: str, limit: int = 5) -> List[Dict]:
        """Get recent conversation history"""
        try:
            result = self.client.table('whatsapp_messages') \
                .select('*') \
                .eq('phone_number', phone) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()

            # Reverse to get chronological order
            return list(reversed(result.data)) if result.data else []
        except Exception as e:
            print(f"DB fetch error: {e}")
            return []

    def create_booking_request(self, phone: str, message: str):
        """Create booking request"""
        try:
            self.client.table('bookings').insert({
                'phone_number': phone,
                'notes': message,
                'status': 'pending'
            }).execute()
        except Exception as e:
            print(f"Booking save error: {e}")
