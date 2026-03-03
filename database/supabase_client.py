from supabase import create_client, Client
from typing import List, Dict, Optional


class SupabaseDB:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    # ==========================================
    # BUSINESS LOOKUP
    # ==========================================

    def get_business_by_whatsapp(self, whatsapp_number: str) -> Optional[Dict]:
        """Look up business by WhatsApp number"""
        try:
            result = self.client.table('businesses') \
                .select('*') \
                .eq('whatsapp_number', whatsapp_number) \
                .eq('is_active', True) \
                .single() \
                .execute()
            return result.data
        except Exception as e:
            print(f"Business lookup error: {e}")
            return None

    def get_business_by_id(self, business_id: str) -> Optional[Dict]:
        """Get business by ID"""
        try:
            result = self.client.table('businesses') \
                .select('*') \
                .eq('id', business_id) \
                .single() \
                .execute()
            return result.data
        except Exception as e:
            print(f"Business lookup error: {e}")
            return None

    def get_all_businesses(self) -> List[Dict]:
        """Get all businesses"""
        try:
            result = self.client.table('businesses') \
                .select('*') \
                .order('name') \
                .execute()
            return result.data or []
        except Exception as e:
            print(f"Business list error: {e}")
            return []

    def create_business(self, data: Dict) -> Optional[Dict]:
        """Create a new business"""
        try:
            result = self.client.table('businesses').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Business create error: {e}")
            return None

    def update_business(self, business_id: str, data: Dict) -> bool:
        """Update business details"""
        try:
            self.client.table('businesses') \
                .update(data) \
                .eq('id', business_id) \
                .execute()
            return True
        except Exception as e:
            print(f"Business update error: {e}")
            return False

    # ==========================================
    # KNOWLEDGE BASE
    # ==========================================

    def get_knowledge_base(self, business_id: str, category: str = None) -> List[Dict]:
        """Get knowledge base entries for a business"""
        try:
            query = self.client.table('knowledge_base') \
                .select('*') \
                .eq('business_id', business_id) \
                .eq('is_active', True) \
                .order('sort_order')

            if category:
                query = query.eq('category', category)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"KB fetch error: {e}")
            return []

    def get_all_knowledge_base(self, business_id: str) -> List[Dict]:
        """Get all KB entries including inactive (for admin)"""
        try:
            result = self.client.table('knowledge_base') \
                .select('*') \
                .eq('business_id', business_id) \
                .order('category') \
                .order('sort_order') \
                .execute()
            return result.data or []
        except Exception as e:
            print(f"KB fetch error: {e}")
            return []

    def create_kb_entry(self, data: Dict) -> Optional[Dict]:
        """Create knowledge base entry"""
        try:
            result = self.client.table('knowledge_base').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"KB create error: {e}")
            return None

    def update_kb_entry(self, entry_id: str, data: Dict) -> bool:
        """Update knowledge base entry"""
        try:
            data['updated_at'] = 'now()'
            self.client.table('knowledge_base') \
                .update(data) \
                .eq('id', entry_id) \
                .execute()
            return True
        except Exception as e:
            print(f"KB update error: {e}")
            return False

    def delete_kb_entry(self, entry_id: str) -> bool:
        """Delete knowledge base entry"""
        try:
            self.client.table('knowledge_base') \
                .delete() \
                .eq('id', entry_id) \
                .execute()
            return True
        except Exception as e:
            print(f"KB delete error: {e}")
            return False

    # ==========================================
    # SERVICES
    # ==========================================

    def get_services(self, business_id: str, category: str = None) -> List[Dict]:
        """Get services for a business"""
        try:
            query = self.client.table('services') \
                .select('*') \
                .eq('business_id', business_id) \
                .eq('is_active', True) \
                .order('sort_order')

            if category:
                query = query.eq('category', category)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Services fetch error: {e}")
            return []

    def get_all_services(self, business_id: str) -> List[Dict]:
        """Get all services including inactive (for admin)"""
        try:
            result = self.client.table('services') \
                .select('*') \
                .eq('business_id', business_id) \
                .order('category') \
                .order('sort_order') \
                .execute()
            return result.data or []
        except Exception as e:
            print(f"Services fetch error: {e}")
            return []

    def create_service(self, data: Dict) -> Optional[Dict]:
        """Create a service"""
        try:
            result = self.client.table('services').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Service create error: {e}")
            return None

    def update_service(self, service_id: str, data: Dict) -> bool:
        """Update a service"""
        try:
            self.client.table('services') \
                .update(data) \
                .eq('id', service_id) \
                .execute()
            return True
        except Exception as e:
            print(f"Service update error: {e}")
            return False

    def delete_service(self, service_id: str) -> bool:
        """Delete a service"""
        try:
            self.client.table('services') \
                .delete() \
                .eq('id', service_id) \
                .execute()
            return True
        except Exception as e:
            print(f"Service delete error: {e}")
            return False

    # ==========================================
    # OPERATING HOURS
    # ==========================================

    def get_operating_hours(self, business_id: str) -> List[Dict]:
        """Get operating hours for a business"""
        try:
            result = self.client.table('operating_hours') \
                .select('*') \
                .eq('business_id', business_id) \
                .order('day_of_week') \
                .execute()
            return result.data or []
        except Exception as e:
            print(f"Hours fetch error: {e}")
            return []

    def set_operating_hours(self, business_id: str, hours: List[Dict]) -> bool:
        """Replace all operating hours for a business"""
        try:
            # Delete existing hours
            self.client.table('operating_hours') \
                .delete() \
                .eq('business_id', business_id) \
                .execute()

            # Insert new hours
            for h in hours:
                h['business_id'] = business_id
            if hours:
                self.client.table('operating_hours').insert(hours).execute()
            return True
        except Exception as e:
            print(f"Hours update error: {e}")
            return False

    # ==========================================
    # ADMIN USERS
    # ==========================================

    def get_admin_by_email(self, email: str) -> Optional[Dict]:
        """Get admin user by email"""
        try:
            result = self.client.table('admin_users') \
                .select('*') \
                .eq('email', email) \
                .eq('is_active', True) \
                .single() \
                .execute()
            return result.data
        except Exception as e:
            print(f"Admin lookup error: {e}")
            return None

    def create_admin_user(self, data: Dict) -> Optional[Dict]:
        """Create admin user"""
        try:
            result = self.client.table('admin_users').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Admin create error: {e}")
            return None

    # ==========================================
    # MESSAGES (multi-tenant)
    # ==========================================

    def save_message(self, phone: str, text: str, role: str, intent: str = None, business_id: str = None):
        """Save message to database"""
        try:
            data = {
                'phone_number': phone,
                'message_text': text,
                'role': role,
            }
            if intent:
                data['intent'] = intent
            if business_id:
                data['business_id'] = business_id
            self.client.table('whatsapp_messages').insert(data).execute()
        except Exception as e:
            print(f"DB save error: {e}")

    def get_conversation_history(self, phone: str, limit: int = 5, business_id: str = None) -> List[Dict]:
        """Get recent conversation history"""
        try:
            query = self.client.table('whatsapp_messages') \
                .select('*') \
                .eq('phone_number', phone) \
                .order('created_at', desc=True) \
                .limit(limit)

            if business_id:
                query = query.eq('business_id', business_id)

            result = query.execute()
            return list(reversed(result.data)) if result.data else []
        except Exception as e:
            print(f"DB fetch error: {e}")
            return []

    # ==========================================
    # BOOKINGS (multi-tenant)
    # ==========================================

    def create_booking_request(self, phone: str, message: str, business_id: str = None):
        """Create booking request"""
        try:
            data = {
                'phone_number': phone,
                'notes': message,
                'status': 'pending'
            }
            if business_id:
                data['business_id'] = business_id
            self.client.table('bookings').insert(data).execute()
        except Exception as e:
            print(f"Booking save error: {e}")

    def get_bookings(self, business_id: str, status: str = None) -> List[Dict]:
        """Get bookings for a business"""
        try:
            query = self.client.table('bookings') \
                .select('*') \
                .eq('business_id', business_id) \
                .order('created_at', desc=True)

            if status:
                query = query.eq('status', status)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Bookings fetch error: {e}")
            return []

    def update_booking(self, booking_id: str, data: Dict) -> bool:
        """Update a booking"""
        try:
            self.client.table('bookings') \
                .update(data) \
                .eq('id', booking_id) \
                .execute()
            return True
        except Exception as e:
            print(f"Booking update error: {e}")
            return False

    # ==========================================
    # ANALYTICS
    # ==========================================

    def get_analytics(self, business_id: str, days: int = 30) -> List[Dict]:
        """Get analytics for a business"""
        try:
            result = self.client.table('bot_analytics') \
                .select('*') \
                .eq('business_id', business_id) \
                .order('date', desc=True) \
                .limit(days) \
                .execute()
            return result.data or []
        except Exception as e:
            print(f"Analytics fetch error: {e}")
            return []

    def get_message_stats(self, business_id: str) -> Dict:
        """Get message statistics for a business"""
        try:
            messages = self.client.table('whatsapp_messages') \
                .select('phone_number, role', count='exact') \
                .eq('business_id', business_id) \
                .execute()

            total = messages.count or 0

            # Get unique users
            users = self.client.table('whatsapp_messages') \
                .select('phone_number') \
                .eq('business_id', business_id) \
                .eq('role', 'user') \
                .execute()

            unique_phones = set()
            if users.data:
                for msg in users.data:
                    unique_phones.add(msg['phone_number'])

            return {
                'total_messages': total,
                'unique_users': len(unique_phones)
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return {'total_messages': 0, 'unique_users': 0}
