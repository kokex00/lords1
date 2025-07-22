import json
import os
from datetime import datetime
from typing import Dict, Any, List
import uuid

class Database:
    """Simple JSON-based database for bot data"""
    
    def __init__(self):
        self.data_dir = "data"
        self.matches_file = os.path.join(self.data_dir, "matches.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.warnings_file = os.path.join(self.data_dir, "warnings.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data files
        self._init_file(self.matches_file, {})
        self._init_file(self.settings_file, {})
        self._init_file(self.warnings_file, {})
    
    def _init_file(self, filepath: str, default_data: dict):
        """Initialize a JSON file if it doesn't exist"""
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
    
    def _load_json(self, filepath: str) -> dict:
        """Load JSON data from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, filepath: str, data: dict):
        """Save JSON data to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to {filepath}: {e}")
    
    # Match Management
    def create_match(self, guild_id: int, match_data: dict) -> str:
        """Create a new match and return its ID"""
        matches = self._load_json(self.matches_file)
        guild_str = str(guild_id)
        
        if guild_str not in matches:
            matches[guild_str] = {}
        
        match_id = str(uuid.uuid4())[:8]  # Short UUID
        matches[guild_str][match_id] = match_data
        
        self._save_json(self.matches_file, matches)
        return match_id
    
    def get_guild_matches(self, guild_id: int) -> dict:
        """Get all matches for a guild"""
        matches = self._load_json(self.matches_file)
        return matches.get(str(guild_id), {})
    
    def get_all_matches(self) -> dict:
        """Get all matches across all guilds"""
        return self._load_json(self.matches_file)
    
    def update_match(self, guild_id: int, match_id: str, match_data: dict):
        """Update match data"""
        matches = self._load_json(self.matches_file)
        guild_str = str(guild_id)
        
        if guild_str in matches and match_id in matches[guild_str]:
            matches[guild_str][match_id] = match_data
            self._save_json(self.matches_file, matches)
    
    def remove_match(self, guild_id: int, match_id: str):
        """Remove a match"""
        matches = self._load_json(self.matches_file)
        guild_str = str(guild_id)
        
        if guild_str in matches and match_id in matches[guild_str]:
            del matches[guild_str][match_id]
            self._save_json(self.matches_file, matches)
    
    # Guild Settings
    def initialize_guild(self, guild_id: int):
        """Initialize default settings for a new guild"""
        settings = self._load_json(self.settings_file)
        guild_str = str(guild_id)
        
        if guild_str not in settings:
            settings[guild_str] = {
                'language': 'en',
                'mod_log_channel': None,
                'bot_activity_channel': None,
                'match_channel': None,
                'created_at': datetime.utcnow().isoformat()
            }
            self._save_json(self.settings_file, settings)
    
    def get_guild_settings(self, guild_id: int) -> dict:
        """Get all settings for a guild"""
        settings = self._load_json(self.settings_file)
        guild_str = str(guild_id)
        
        if guild_str not in settings:
            self.initialize_guild(guild_id)
            return self.get_guild_settings(guild_id)
        
        return settings[guild_str]
    
    def get_guild_setting(self, guild_id: int, key: str, default=None):
        """Get a specific setting for a guild"""
        settings = self.get_guild_settings(guild_id)
        return settings.get(key, default)
    
    def set_guild_setting(self, guild_id: int, key: str, value):
        """Set a specific setting for a guild"""
        settings = self._load_json(self.settings_file)
        guild_str = str(guild_id)
        
        if guild_str not in settings:
            self.initialize_guild(guild_id)
            settings = self._load_json(self.settings_file)
        
        settings[guild_str][key] = value
        self._save_json(self.settings_file, settings)
    
    # Warning System
    def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> str:
        """Add a warning for a user"""
        warnings = self._load_json(self.warnings_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        if guild_str not in warnings:
            warnings[guild_str] = {}
        
        if user_str not in warnings[guild_str]:
            warnings[guild_str][user_str] = []
        
        warning_id = str(len(warnings[guild_str][user_str]) + 1)
        warning_data = {
            'id': warning_id,
            'moderator_id': moderator_id,
            'reason': reason,
            'timestamp': datetime.utcnow().timestamp()
        }
        
        warnings[guild_str][user_str].append(warning_data)
        self._save_json(self.warnings_file, warnings)
        
        return warning_id
    
    def get_user_warnings(self, guild_id: int, user_id: int) -> List[dict]:
        """Get all warnings for a user"""
        warnings = self._load_json(self.warnings_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        return warnings.get(guild_str, {}).get(user_str, [])
    
    def remove_warning(self, guild_id: int, user_id: int, warning_id: str):
        """Remove a specific warning"""
        warnings = self._load_json(self.warnings_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        if guild_str in warnings and user_str in warnings[guild_str]:
            warnings[guild_str][user_str] = [
                w for w in warnings[guild_str][user_str] 
                if w['id'] != warning_id
            ]
            self._save_json(self.warnings_file, warnings)
    
    # Utility Methods
    def cleanup_old_matches(self):
        """Remove matches older than 24 hours"""
        matches = self._load_json(self.matches_file)
        current_time = datetime.utcnow()
        
        for guild_id, guild_matches in matches.items():
            for match_id, match_data in list(guild_matches.items()):
                match_time = datetime.fromisoformat(match_data['time'])
                if (current_time - match_time).total_seconds() > 86400:  # 24 hours
                    del guild_matches[match_id]
        
        self._save_json(self.matches_file, matches)
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        matches = self._load_json(self.matches_file)
        settings = self._load_json(self.settings_file)
        warnings = self._load_json(self.warnings_file)
        
        total_matches = sum(len(guild_matches) for guild_matches in matches.values())
        total_guilds = len(settings)
        total_warnings = sum(
            sum(len(user_warnings) for user_warnings in guild_warnings.values())
            for guild_warnings in warnings.values()
        )
        
        return {
            'guilds': total_guilds,
            'matches': total_matches,
            'warnings': total_warnings
        }
