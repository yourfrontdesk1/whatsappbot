import os
from dotenv import load_dotenv

load_dotenv()

# 360dialog
DIALOG_360_API_KEY = os.getenv('DIALOG_360_API_KEY')

# Anthropic
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# App
FLASK_ENV = os.getenv('FLASK_ENV', 'production')
PORT = int(os.getenv('PORT', 5000))
