from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Discord Bot Status</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                background: #2c2f33; 
                color: #ffffff; 
                margin: 0; 
                padding: 50px;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: #36393f;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            .status {
                font-size: 24px;
                color: #7289da;
                margin-bottom: 20px;
            }
            .online {
                color: #43b581;
            }
            .features {
                text-align: left;
                margin: 20px 0;
            }
            .feature {
                margin: 10px 0;
                padding: 10px;
                background: #2c2f33;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Discord Bot</h1>
            <div class="status online">✅ Bot is Online and Running</div>
            
            <div class="features">
                <h3>Available Features:</h3>
                <div class="feature">⚔️ Match Creation & Management</div>
                <div class="feature">🛡️ Moderation Tools (Kick, Ban, Mute, Warn)</div>
                <div class="feature">🌐 Multi-language Support (AR, EN, PT)</div>
                <div class="feature">⏰ Automatic Match Reminders</div>
                <div class="feature">📧 DM Notifications with Translation</div>
                <div class="feature">⚙️ Server Configuration</div>
            </div>
            
            <p>Use <code>/help</code> in Discord to see all available commands.</p>
            <p><small>Keep-alive service is running to maintain bot uptime.</small></p>
        </div>
    </body>
    </html>
    """

@app.route('/status')
def status():
    return {
        "status": "online",
        "bot": "Discord Server Management Bot",
        "features": [
            "Match Management",
            "Moderation Tools", 
            "Multi-language Support",
            "Auto Reminders",
            "Translation System"
        ]
    }

@app.route('/health')
def health():
    return {"status": "healthy", "service": "keep-alive"}

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print(f"Keep-alive server started on port 5000")