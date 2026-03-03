-- ============================================
-- MULTI-TENANT WHATSAPP BOT SCHEMA
-- ============================================

-- Businesses table (multi-tenant core)
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    whatsapp_number TEXT UNIQUE NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    website TEXT,
    timezone TEXT DEFAULT 'Europe/Gibraltar',
    welcome_message TEXT DEFAULT 'Hello! How can I help you today?',
    fallback_message TEXT DEFAULT 'I apologize, I''m having trouble right now. Please call us for immediate assistance.',
    bot_tone TEXT DEFAULT 'Professional but warm and welcoming. Concise responses suited for WhatsApp.',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_businesses_whatsapp ON businesses(whatsapp_number);
CREATE INDEX idx_businesses_slug ON businesses(slug);

-- Admin users for the dashboard
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'staff' CHECK (role IN ('owner', 'admin', 'staff')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_business ON admin_users(business_id);

-- Knowledge base (FAQs and general info)
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT[],
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_kb_business ON knowledge_base(business_id);
CREATE INDEX idx_kb_category ON knowledge_base(category);

-- Services offered by each business
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    price_from DECIMAL(10,2),
    price_to DECIMAL(10,2),
    currency TEXT DEFAULT 'GBP',
    duration_minutes INTEGER,
    is_bookable BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_services_business ON services(business_id);

-- Operating hours per business
CREATE TABLE operating_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    label TEXT,
    is_closed BOOLEAN DEFAULT false
);

CREATE INDEX idx_hours_business ON operating_hours(business_id);

-- Messages table (now multi-tenant)
CREATE TABLE whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    message_text TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    intent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_phone ON whatsapp_messages(phone_number);
CREATE INDEX idx_messages_created ON whatsapp_messages(created_at DESC);
CREATE INDEX idx_messages_business ON whatsapp_messages(business_id);

-- Bookings table (now multi-tenant)
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    customer_name TEXT,
    service TEXT,
    preferred_date TEXT,
    preferred_time TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bookings_phone ON bookings(phone_number);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_business ON bookings(business_id);

-- Analytics table (now multi-tenant)
CREATE TABLE bot_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_messages INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    booking_requests INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_analytics_date ON bot_analytics(date DESC);
CREATE INDEX idx_analytics_business ON bot_analytics(business_id);
