from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import hashlib
import os

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

# Secret key for sessions
admin_bp.secret_key = os.getenv('SECRET_KEY', 'change-me-in-production')


def get_db():
    """Get database instance from app context"""
    from flask import current_app
    from database.supabase_client import SupabaseDB
    if not hasattr(current_app, '_db'):
        current_app._db = SupabaseDB(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
    return current_app._db


def hash_password(password: str) -> str:
    """Hash password with SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_user' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


# ==========================================
# AUTH
# ==========================================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        db = get_db()
        user = db.get_admin_by_email(email)

        if user and user['password_hash'] == hash_password(password):
            session['admin_user'] = {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'business_id': user['business_id'],
                'role': user['role']
            }
            return redirect(url_for('admin.dashboard'))

        flash('Invalid email or password', 'error')

    return render_template('login.html')


@admin_bp.route('/logout')
def logout():
    session.pop('admin_user', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    """First-time setup: create owner account and business"""
    db = get_db()

    # Check if any admin users exist
    businesses = db.get_all_businesses()
    if businesses:
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        # Create business
        business = db.create_business({
            'name': request.form.get('business_name'),
            'slug': request.form.get('business_name', '').lower().replace(' ', '-'),
            'whatsapp_number': request.form.get('whatsapp_number'),
            'phone': request.form.get('phone'),
            'email': request.form.get('business_email'),
            'address': request.form.get('address'),
        })

        if business:
            # Create owner account
            db.create_admin_user({
                'email': request.form.get('email'),
                'password_hash': hash_password(request.form.get('password')),
                'name': request.form.get('name'),
                'business_id': business['id'],
                'role': 'owner'
            })
            flash('Setup complete! Please log in.', 'success')
            return redirect(url_for('admin.login'))

        flash('Error creating business', 'error')

    return render_template('setup.html')


# ==========================================
# DASHBOARD
# ==========================================

@admin_bp.route('/')
@login_required
def dashboard():
    db = get_db()
    business_id = session['admin_user']['business_id']
    business = db.get_business_by_id(business_id)
    stats = db.get_message_stats(business_id)
    bookings = db.get_bookings(business_id, status='pending')

    return render_template('dashboard.html',
        business=business,
        stats=stats,
        pending_bookings=bookings[:10]
    )


# ==========================================
# KNOWLEDGE BASE
# ==========================================

@admin_bp.route('/knowledge')
@login_required
def knowledge_base():
    db = get_db()
    business_id = session['admin_user']['business_id']
    entries = db.get_all_knowledge_base(business_id)

    # Group by category
    categories = {}
    for entry in entries:
        cat = entry.get('category', 'General')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(entry)

    return render_template('knowledge_base.html', categories=categories)


@admin_bp.route('/knowledge/add', methods=['GET', 'POST'])
@login_required
def add_kb_entry():
    if request.method == 'POST':
        db = get_db()
        business_id = session['admin_user']['business_id']

        keywords_raw = request.form.get('keywords', '')
        keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()]

        db.create_kb_entry({
            'business_id': business_id,
            'category': request.form.get('category'),
            'question': request.form.get('question'),
            'answer': request.form.get('answer'),
            'keywords': keywords
        })
        flash('Knowledge base entry added', 'success')
        return redirect(url_for('admin.knowledge_base'))

    return render_template('kb_form.html', entry=None)


@admin_bp.route('/knowledge/edit/<entry_id>', methods=['GET', 'POST'])
@login_required
def edit_kb_entry(entry_id):
    db = get_db()

    if request.method == 'POST':
        keywords_raw = request.form.get('keywords', '')
        keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()]

        db.update_kb_entry(entry_id, {
            'category': request.form.get('category'),
            'question': request.form.get('question'),
            'answer': request.form.get('answer'),
            'keywords': keywords,
            'is_active': request.form.get('is_active') == 'on'
        })
        flash('Entry updated', 'success')
        return redirect(url_for('admin.knowledge_base'))

    # Get entry for editing
    business_id = session['admin_user']['business_id']
    entries = db.get_all_knowledge_base(business_id)
    entry = next((e for e in entries if e['id'] == entry_id), None)
    if not entry:
        flash('Entry not found', 'error')
        return redirect(url_for('admin.knowledge_base'))

    return render_template('kb_form.html', entry=entry)


@admin_bp.route('/knowledge/delete/<entry_id>', methods=['POST'])
@login_required
def delete_kb_entry(entry_id):
    db = get_db()
    db.delete_kb_entry(entry_id)
    flash('Entry deleted', 'success')
    return redirect(url_for('admin.knowledge_base'))


# ==========================================
# SERVICES
# ==========================================

@admin_bp.route('/services')
@login_required
def services():
    db = get_db()
    business_id = session['admin_user']['business_id']
    all_services = db.get_all_services(business_id)

    # Group by category
    categories = {}
    for svc in all_services:
        cat = svc.get('category', 'General')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(svc)

    return render_template('services.html', categories=categories)


@admin_bp.route('/services/add', methods=['GET', 'POST'])
@login_required
def add_service():
    if request.method == 'POST':
        db = get_db()
        business_id = session['admin_user']['business_id']

        price_from = request.form.get('price_from')
        price_to = request.form.get('price_to')
        duration = request.form.get('duration_minutes')

        db.create_service({
            'business_id': business_id,
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'price_from': float(price_from) if price_from else None,
            'price_to': float(price_to) if price_to else None,
            'currency': request.form.get('currency', 'GBP'),
            'duration_minutes': int(duration) if duration else None,
            'is_bookable': request.form.get('is_bookable') == 'on'
        })
        flash('Service added', 'success')
        return redirect(url_for('admin.services'))

    return render_template('service_form.html', service=None)


@admin_bp.route('/services/edit/<service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    db = get_db()

    if request.method == 'POST':
        price_from = request.form.get('price_from')
        price_to = request.form.get('price_to')
        duration = request.form.get('duration_minutes')

        db.update_service(service_id, {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'price_from': float(price_from) if price_from else None,
            'price_to': float(price_to) if price_to else None,
            'currency': request.form.get('currency', 'GBP'),
            'duration_minutes': int(duration) if duration else None,
            'is_bookable': request.form.get('is_bookable') == 'on',
            'is_active': request.form.get('is_active') == 'on'
        })
        flash('Service updated', 'success')
        return redirect(url_for('admin.services'))

    business_id = session['admin_user']['business_id']
    all_services = db.get_all_services(business_id)
    service = next((s for s in all_services if s['id'] == service_id), None)
    if not service:
        flash('Service not found', 'error')
        return redirect(url_for('admin.services'))

    return render_template('service_form.html', service=service)


@admin_bp.route('/services/delete/<service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    db = get_db()
    db.delete_service(service_id)
    flash('Service deleted', 'success')
    return redirect(url_for('admin.services'))


# ==========================================
# OPERATING HOURS
# ==========================================

@admin_bp.route('/hours', methods=['GET', 'POST'])
@login_required
def operating_hours():
    db = get_db()
    business_id = session['admin_user']['business_id']

    if request.method == 'POST':
        hours = []
        for day in range(7):
            is_closed = request.form.get(f'closed_{day}') == 'on'
            open_time = request.form.get(f'open_{day}', '09:00')
            close_time = request.form.get(f'close_{day}', '17:00')
            label = request.form.get(f'label_{day}', '')

            hours.append({
                'day_of_week': day,
                'open_time': open_time,
                'close_time': close_time,
                'label': label if label else None,
                'is_closed': is_closed
            })

        db.set_operating_hours(business_id, hours)
        flash('Operating hours updated', 'success')
        return redirect(url_for('admin.operating_hours'))

    hours = db.get_operating_hours(business_id)

    # Build a dict keyed by day_of_week for the template
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours_by_day = {}
    for day in range(7):
        existing = next((h for h in hours if h['day_of_week'] == day), None)
        hours_by_day[day] = {
            'name': day_names[day],
            'open_time': existing['open_time'] if existing else '09:00',
            'close_time': existing['close_time'] if existing else '17:00',
            'label': existing.get('label', '') if existing else '',
            'is_closed': existing.get('is_closed', False) if existing else False
        }

    return render_template('hours.html', hours_by_day=hours_by_day)


# ==========================================
# BUSINESS SETTINGS
# ==========================================

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    db = get_db()
    business_id = session['admin_user']['business_id']

    if request.method == 'POST':
        db.update_business(business_id, {
            'name': request.form.get('name'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'website': request.form.get('website'),
            'whatsapp_number': request.form.get('whatsapp_number'),
            'welcome_message': request.form.get('welcome_message'),
            'fallback_message': request.form.get('fallback_message'),
            'bot_tone': request.form.get('bot_tone'),
        })
        flash('Settings updated', 'success')
        return redirect(url_for('admin.settings'))

    business = db.get_business_by_id(business_id)
    return render_template('settings.html', business=business)


# ==========================================
# BOOKINGS
# ==========================================

@admin_bp.route('/bookings')
@login_required
def bookings():
    db = get_db()
    business_id = session['admin_user']['business_id']
    status_filter = request.args.get('status')
    all_bookings = db.get_bookings(business_id, status=status_filter)
    return render_template('bookings.html', bookings=all_bookings, current_status=status_filter)


@admin_bp.route('/bookings/<booking_id>/update', methods=['POST'])
@login_required
def update_booking(booking_id):
    db = get_db()
    new_status = request.form.get('status')
    db.update_booking(booking_id, {'status': new_status})
    flash(f'Booking {new_status}', 'success')
    return redirect(url_for('admin.bookings'))


# ==========================================
# CONVERSATIONS
# ==========================================

@admin_bp.route('/conversations')
@login_required
def conversations():
    db = get_db()
    business_id = session['admin_user']['business_id']
    stats = db.get_message_stats(business_id)
    return render_template('conversations.html', stats=stats)
