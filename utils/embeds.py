import discord
from datetime import datetime
from typing import Dict, Any, Optional

class EmbedBuilder:
    """Utility class for creating consistent embeds"""
    
    def __init__(self):
        self.colors = {
            'success': 0x4CAF50,
            'error': 0xf44336,
            'warning': 0xffa502,
            'info': 0x5865f2,
            'match': 0x9b59b6,
            'moderation': 0xe74c3c
        }
    
    def create_error_embed(self, message: str, user: discord.User) -> discord.Embed:
        """Create a standardized error embed"""
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=self.colors['error'],
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Requested by {user.display_name}", icon_url=user.display_avatar.url)
        return embed
    
    def create_success_embed(self, title: str, message: str, user: discord.User) -> discord.Embed:
        """Create a standardized success embed"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=message,
            color=self.colors['success'],
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Requested by {user.display_name}", icon_url=user.display_avatar.url)
        return embed
    
    def create_match_embed(self, match_data: Dict[str, Any], match_id: str, language: str) -> discord.Embed:
        """Create a match information embed"""
        from utils.translations import Translations
        translations = Translations()
        
        title = translations.get_text('match_created', language)
        
        embed = discord.Embed(
            title=f"⚔️ {title}",
            description=f"**{match_data['title']}**",
            color=self.colors['match'],
            timestamp=datetime.utcnow()
        )
        
        # Match time
        match_time = datetime.fromisoformat(match_data['time'])
        formatted_time = translations.format_time_for_language(match_time, language)
        
        embed.add_field(
            name=f"🕒 {translations.get_text('match_time', language)}",
            value=f"{formatted_time}\n<t:{int(match_time.timestamp())}:R>",
            inline=False
        )
        
        # Teams (if available) or Participants
        if match_data.get('team1_mentions') and match_data.get('team2_mentions'):
            embed.add_field(
                name="🔴 الفريق الأول",
                value=match_data['team1_mentions'],
                inline=True
            )
            embed.add_field(
                name="🔵 الفريق الثاني", 
                value=match_data['team2_mentions'],
                inline=True
            )
            embed.add_field(
                name="\u200b",
                value="\u200b",
                inline=True
            )
        else:
            embed.add_field(
                name=f"👥 {translations.get_text('participants', language)}",
                value=f"{len(match_data['participants'])} members",
                inline=True
            )
        
        # Match ID
        embed.add_field(
            name="🆔 Match ID",
            value=f"`{match_id}`",
            inline=True
        )
        
        # Description if provided
        if match_data.get('description'):
            embed.add_field(
                name=f"📝 {translations.get_text('description', language)}",
                value=match_data['description'],
                inline=False
            )
        
        # Creator
        embed.add_field(
            name=f"👤 {translations.get_text('creator', language)}",
            value=f"<@{match_data['creator_id']}>",
            inline=True
        )
        
        # Visual separator
        embed.add_field(name="\u200b", value="─" * 30, inline=False)
        
        return embed
    
    def create_match_notification_embed(self, match_data: Dict[str, Any], language: str) -> discord.Embed:
        """Create a match notification embed for DMs"""
        from utils.translations import Translations
        translations = Translations()
        
        title = translations.get_text('join_match', language)
        
        embed = discord.Embed(
            title=f"⚔️ {title}",
            description=f"**{match_data['title']}**",
            color=self.colors['match'],
            timestamp=datetime.utcnow()
        )
        
        # Match time
        match_time = datetime.fromisoformat(match_data['time'])
        formatted_time = translations.format_time_for_language(match_time, language)
        
        embed.add_field(
            name=f"🕒 {translations.get_text('match_time', language)}",
            value=f"{formatted_time}\n<t:{int(match_time.timestamp())}:R>",
            inline=False
        )
        
        # Description if provided
        if match_data.get('description'):
            embed.add_field(
                name=f"📝 {translations.get_text('description', language)}",
                value=match_data['description'],
                inline=False
            )
        
        # Participants count
        embed.add_field(
            name=f"👥 {translations.get_text('participants', language)}",
            value=str(len(match_data['participants'])),
            inline=True
        )
        
        embed.set_footer(text=translations.get_text('match_info', language))
        
        return embed
    
    def create_cancellation_embed(self, match_data: Dict[str, Any], language: str) -> discord.Embed:
        """Create a match cancellation embed for DMs"""
        from utils.translations import Translations
        translations = Translations()
        
        title = translations.get_text('match_cancelled', language)
        
        embed = discord.Embed(
            title=f"❌ {title}",
            description=f"**{match_data['title']}**",
            color=0xf44336,
            timestamp=datetime.utcnow()
        )
        
        # Match time
        if match_data.get('time'):
            match_time = datetime.fromisoformat(match_data['time'])
            formatted_time = translations.format_time_for_language(match_time, language)
            
            embed.add_field(
                name=f"🕒 {translations.get_text('match_time', language)}",
                value=f"{formatted_time}\n<t:{int(match_time.timestamp())}:R>",
                inline=False
            )
        
        # Reason
        reason_text = translations.get_text('reason', language)
        embed.add_field(
            name=f"📝 {reason_text}",
            value="Match cancelled by administrator",
            inline=False
        )
        
        return embed
    
    def create_match_reminder_embed(self, match_data: Dict[str, Any], minutes: int, language: str) -> discord.Embed:
        """Create a match reminder embed"""
        from utils.translations import Translations
        translations = Translations()
        
        title = translations.get_text('match_reminder', language)
        
        embed = discord.Embed(
            title=f"⏰ {title}",
            description=f"**{match_data['title']}**\n\n{translations.get_text('match_in', language)} {minutes} {translations.get_text('minutes_before', language)}",
            color=self.colors['warning'],
            timestamp=datetime.utcnow()
        )
        
        # Match time
        match_time = datetime.fromisoformat(match_data['time'])
        formatted_time = translations.format_time_for_language(match_time, language)
        
        embed.add_field(
            name=f"🕒 {translations.get_text('match_time', language)}",
            value=f"{formatted_time}\n<t:{int(match_time.timestamp())}:R>",
            inline=False
        )
        
        # Description if provided
        if match_data.get('description'):
            embed.add_field(
                name=f"📝 {translations.get_text('description', language)}",
                value=match_data['description'],
                inline=False
            )
        
        return embed
    
    def create_cancellation_embed(self, match_data: Dict[str, Any], language: str) -> discord.Embed:
        """Create a match cancellation embed"""
        from utils.translations import Translations
        translations = Translations()
        
        title = translations.get_text('match_cancelled', language)
        
        embed = discord.Embed(
            title=f"❌ {title}",
            description=f"**{match_data['title']}**",
            color=self.colors['error'],
            timestamp=datetime.utcnow()
        )
        
        # Original match time
        match_time = datetime.fromisoformat(match_data['time'])
        formatted_time = translations.format_time_for_language(match_time, language)
        
        embed.add_field(
            name=f"🕒 {translations.get_text('match_time', language)}",
            value=formatted_time,
            inline=False
        )
        
        # Description if provided
        if match_data.get('description'):
            embed.add_field(
                name=f"📝 {translations.get_text('description', language)}",
                value=match_data['description'],
                inline=False
            )
        
        embed.set_footer(text="We apologize for any inconvenience caused.")
        
        return embed
    
    def create_moderation_embed(self, action: str, member: discord.Member, moderator: discord.User, reason: str) -> discord.Embed:
        """Create a moderation action embed"""
        action_emojis = {
            'kick': '🦶',
            'ban': '🔨',
            'mute': '🔇',
            'warn': '⚠️',
            'timeout': '⏰'
        }
        
        action_colors = {
            'kick': 0xff6b6b,
            'ban': 0xff4757,
            'mute': 0xffa502,
            'warn': 0xff9f43,
            'timeout': 0xffa502
        }
        
        emoji = action_emojis.get(action.lower(), '🛡️')
        color = action_colors.get(action.lower(), self.colors['moderation'])
        
        embed = discord.Embed(
            title=f"{emoji} Member {action.title()}",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Member", value=member.mention, inline=True)
        embed.add_field(name="👮 Moderator", value=moderator.mention, inline=True)
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        
        embed.set_footer(text=f"User ID: {member.id}")
        
        return embed
    
    def create_info_embed(self, title: str, description: str, fields: Optional[Dict[str, str]] = None) -> discord.Embed:
        """Create a general information embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=self.colors['info'],
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for name, value in fields.items():
                embed.add_field(name=name, value=value, inline=False)
        
        return embed
