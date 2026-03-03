from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from bot.claude_handler import ClaudeHandler
from bot.whatsapp_client import WhatsApp360Dialog
from database.supabase_client import SupabaseDB
from bot.intent_detector import detect_intent

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-me-in-production')

# Initialize components
claude = ClaudeHandler(os.getenv('ANTHROPIC_API_KEY'))
whatsapp = WhatsApp360Dialog(os.getenv('DIALOG_360_API_KEY'))
db = SupabaseDB(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Register admin panel
from admin.routes import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')


@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages from 360dialog"""

    data = request.json

    # Extract message details
    if 'messages' in data and len(data['messages']) > 0:
        message = data['messages'][0]

        phone_number = message.get('from')
        text = message.get('text', {}).get('body', '')
        message_id = message.get('id')

        if not text:  # Skip media/location messages for now
            return jsonify({'status': 'ok'})

        # Look up which business this WhatsApp number belongs to
        # The 'to' field or the webhook config determines the business
        to_number = data.get('contacts', [{}])[0].get('wa_id', '')
        business = db.get_business_by_whatsapp(to_number)

        if not business:
            # Fallback: try to find any active business (single-tenant mode)
            businesses = db.get_all_businesses()
            business = businesses[0] if businesses else None

        business_id = business['id'] if business else None

        # Detect intent
        intent = detect_intent(text)

        # Get conversation history
        history = db.get_conversation_history(phone_number, limit=5, business_id=business_id)

        # Get business knowledge from DB
        knowledge_base = db.get_knowledge_base(business_id) if business_id else []
        services = db.get_services(business_id) if business_id else []
        operating_hours = db.get_operating_hours(business_id) if business_id else []

        # Generate AI response with dynamic business context
        response_text = claude.generate_response(
            user_message=text,
            conversation_history=history,
            intent=intent,
            business=business,
            knowledge_base=knowledge_base,
            services=services,
            operating_hours=operating_hours
        )

        # Save messages
        db.save_message(phone_number, text, 'user', intent, business_id)
        db.save_message(phone_number, response_text, 'assistant', business_id=business_id)

        # If booking intent, save to bookings table
        if intent == 'booking':
            db.create_booking_request(phone_number, text, business_id)

        # Send response via WhatsApp
        whatsapp.send_message(phone_number, response_text)

        return jsonify({'status': 'ok'})

    return jsonify({'status': 'no_message'})


@app.route('/webhook/status', methods=['POST'])
def status_webhook():
    """Handle message status updates"""
    return jsonify({'status': 'ok'})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'WhatsApp Bot Platform'
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
