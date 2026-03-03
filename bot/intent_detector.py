def detect_intent(message: str) -> str:
    """Simple keyword-based intent detection"""

    message_lower = message.lower()

    # Booking keywords
    if any(word in message_lower for word in [
        'book', 'appointment', 'reserve', 'schedule', 'session'
    ]):
        return 'booking'

    # Hours keywords
    if any(word in message_lower for word in [
        'open', 'close', 'hours', 'time', 'when'
    ]):
        return 'hours'

    # Pricing keywords
    if any(word in message_lower for word in [
        'price', 'cost', 'how much', 'membership', 'fee'
    ]):
        return 'pricing'

    # Service info
    if any(word in message_lower for word in [
        'cryotherapy', 'massage', 'gym', 'pool', 'sauna'
    ]):
        return 'service_info'

    # General inquiry
    return 'general'
