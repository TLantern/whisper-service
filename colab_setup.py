#!/usr/bin/env python3
"""
Google Colab Setup for Whisper v3 Service
⚠️ WARNING: This is for testing only! Colab sessions timeout after 12-24 hours.
"""

# Run this in Google Colab Pro ($10/month) for testing

# 1. Install dependencies
"""
!pip install fastapi uvicorn openai-whisper torch torchaudio pydantic python-multipart pyngrok
!wget -q -O - https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar xvz -C /usr/local/bin
"""

# 2. Create the app (copy the app.py content from the main service)

# 3. Start service and ngrok tunnel
"""
import subprocess
import threading
import time
from pyngrok import ngrok

# Start service in background
def run_service():
    subprocess.run(["python", "app.py"])

service_thread = threading.Thread(target=run_service, daemon=True)
service_thread.start()
time.sleep(10)

# Create ngrok tunnel
public_url = ngrok.connect(8000)
print(f"🌐 Public URL: {public_url}")
print(f"📋 Set REMOTE_WHISPER_URL={public_url} in your main app")
"""

# ⚠️ LIMITATIONS:
# - Sessions timeout after 12-24 hours
# - Need to restart manually
# - Not reliable for production
# - Colab Pro costs $10/month anyway

# 💡 BETTER ALTERNATIVES:
# 1. Railway: $5-10/month (recommended)
# 2. Render: Free tier available
# 3. Fly.io: Very cheap
# 4. Heroku: $25/month (what we built earlier)
