import requests
import time
import os
from datetime import datetime

class UptimeMonitor:
    """Simple uptime monitoring for the Discord bot"""
    
    def __init__(self, url="http://localhost:5000"):
        self.url = url
        self.log_file = "uptime.log"
        
    def ping_server(self):
        """Ping the keep-alive server"""
        try:
            response = requests.get(f"{self.url}/health", timeout=30)
            if response.status_code == 200:
                self.log_status("✅ Bot is online")
                return True
            else:
                self.log_status(f"⚠️ Bot responded with status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_status(f"❌ Bot is offline: {str(e)}")
            return False
    
    def log_status(self, message):
        """Log status with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # Write to log file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except:
            pass  # Silent fail if can't write to file
    
    def monitor_uptime(self, interval=300):  # Check every 5 minutes
        """Continuously monitor bot uptime"""
        self.log_status("🔍 Starting uptime monitoring...")
        
        while True:
            try:
                self.ping_server()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.log_status("🛑 Uptime monitoring stopped")
                break
            except Exception as e:
                self.log_status(f"⚠️ Monitor error: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    monitor = UptimeMonitor()
    
    # You can run this script separately to monitor your bot
    # python uptime_monitor.py
    monitor.monitor_uptime()