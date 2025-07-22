import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class Settings(commands.Cog):
    """Server configuration and bot settings"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="set_channel", description="Set channels for bot functions")
    @app_commands.describe(
        function="Channel function",
        channel="Channel to set"
    )
    @app_commands.choices(function=[
        app_commands.Choice(name="Moderation Logs", value="mod_log_channel"),
        app_commands.Choice(name="Bot Activity", value="bot_activity_channel"),
        app_commands.Choice(name="Match Announcements", value="match_channel")
    ])
    async def set_channel(self, interaction: discord.Interaction, function: app_commands.Choice[str], channel: discord.TextChannel):
        """Set channels for various bot functions"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.administrator:
                embed = self.bot.embed_builder.create_error_embed(
                    "You need administrator permissions to configure channels!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Set the channel in database
            self.bot.database.set_guild_setting(interaction.guild.id, function.value, channel.id)
            
            # Create success embed
            embed = discord.Embed(
                title="✅ Channel Set",
                description=f"**Function:** {function.name}\n**Channel:** {channel.mention}",
                color=0x4CAF50,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log in bot activity channel
            if function.value != 'bot_activity_channel':  # Avoid infinite loop
                activity_channel_id = self.bot.database.get_guild_setting(interaction.guild.id, 'bot_activity_channel')
                if activity_channel_id:
                    activity_channel = interaction.guild.get_channel(activity_channel_id)
                    if activity_channel:
                        log_embed = discord.Embed(
                            title="🤖 Bot Activity",
                            description=f"Channel configured: {function.name} → {channel.mention}\nConfigured by: {interaction.user.mention}",
                            color=0x5865f2,
                            timestamp=datetime.utcnow()
                        )
                        await activity_channel.send(embed=log_embed)
                        
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to set channel: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="set_language", description="Set server language")
    @app_commands.describe(language="Server language")
    @app_commands.choices(language=[
        app_commands.Choice(name="English (GMT)", value="en"),
        app_commands.Choice(name="العربية (Mecca Time)", value="ar"),
        app_commands.Choice(name="Português", value="pt")
    ])
    async def set_language(self, interaction: discord.Interaction, language: app_commands.Choice[str]):
        """Set the default language for the server"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.administrator:
                embed = self.bot.embed_builder.create_error_embed(
                    "You need administrator permissions to change server language!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Set the language in database
            self.bot.database.set_guild_setting(interaction.guild.id, 'language', language.value)
            
            # Create success embed in the selected language
            if language.value == 'ar':
                embed = discord.Embed(
                    title="✅ تم تعديل اللغة",
                    description=f"**اللغة:** {language.name}\n**تم التعديل بواسطة:** {interaction.user.mention}",
                    color=0x4CAF50,
                    timestamp=datetime.utcnow()
                )
            elif language.value == 'pt':
                embed = discord.Embed(
                    title="✅ Idioma Definido",
                    description=f"**Idioma:** {language.name}\n**Definido por:** {interaction.user.mention}",
                    color=0x4CAF50,
                    timestamp=datetime.utcnow()
                )
            else:  # English
                embed = discord.Embed(
                    title="✅ Language Set",
                    description=f"**Language:** {language.name}\n**Set by:** {interaction.user.mention}",
                    color=0x4CAF50,
                    timestamp=datetime.utcnow()
                )
            
            await interaction.response.send_message(embed=embed)
            
            # Log in bot activity channel
            activity_channel_id = self.bot.database.get_guild_setting(interaction.guild.id, 'bot_activity_channel')
            if activity_channel_id:
                activity_channel = interaction.guild.get_channel(activity_channel_id)
                if activity_channel:
                    log_embed = discord.Embed(
                        title="🤖 Bot Activity",
                        description=f"Server language changed to: {language.name}\nChanged by: {interaction.user.mention}",
                        color=0x5865f2,
                        timestamp=datetime.utcnow()
                    )
                    await activity_channel.send(embed=log_embed)
                    
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to set language: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="settings", description="View current bot settings")
    async def settings(self, interaction: discord.Interaction):
        """Display current bot settings for the server"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.manage_guild:
                embed = self.bot.embed_builder.create_error_embed(
                    "You need manage server permissions to view bot settings!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Get current settings
            settings = self.bot.database.get_guild_settings(interaction.guild.id)
            
            embed = discord.Embed(
                title="⚙️ Bot Settings",
                description=f"Current settings for **{interaction.guild.name}**",
                color=0x5865f2,
                timestamp=datetime.utcnow()
            )
            
            # Language setting
            language_names = {'en': 'English (GMT)', 'ar': 'العربية (Mecca Time)', 'pt': 'Português'}
            current_lang = settings.get('language', 'en')
            embed.add_field(
                name="🌐 Language",
                value=language_names.get(current_lang, current_lang),
                inline=True
            )
            
            # Channel settings
            channel_settings = [
                ('mod_log_channel', 'Moderation Logs', '🛡️'),
                ('bot_activity_channel', 'Bot Activity', '🤖'),
                ('match_channel', 'Match Announcements', '⚔️')
            ]
            
            for setting_key, setting_name, emoji in channel_settings:
                channel_id = settings.get(setting_key)
                if channel_id:
                    channel = interaction.guild.get_channel(channel_id)
                    value = channel.mention if channel else "Channel not found"
                else:
                    value = "Not set"
                
                embed.add_field(
                    name=f"{emoji} {setting_name}",
                    value=value,
                    inline=True
                )
            
            # Statistics
            matches_count = len(self.bot.database.get_guild_matches(interaction.guild.id))
            embed.add_field(
                name="📊 Statistics",
                value=f"Active Matches: {matches_count}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to get settings: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="dm", description="💌 Send private message")
    @app_commands.describe(
        user="User to send message to",
        message="Message content",
        embed_title="Embed title (optional)",
        embed_color="Embed color (hex, e.g., #ff0000)"
    )
    async def send_dm(self, interaction: discord.Interaction, user: discord.Member, message: str, embed_title: str = None, embed_color: str = None):
        """Send a private message to a specific user"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.manage_messages:
                embed = self.bot.embed_builder.create_error_embed(
                    "You need manage messages permissions to send DMs!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Parse color if provided
            color = 0x5865f2  # Default color
            if embed_color:
                try:
                    if embed_color.startswith('#'):
                        color = int(embed_color[1:], 16)
                    else:
                        color = int(embed_color, 16)
                except ValueError:
                    color = 0x5865f2
            
            # Create DM embed
            if embed_title:
                dm_embed = discord.Embed(
                    title=embed_title,
                    description=message,
                    color=color,
                    timestamp=datetime.utcnow()
                )
                dm_embed.set_footer(
                    text=f"From {interaction.guild.name}",
                    icon_url=interaction.guild.icon.url if interaction.guild.icon else None
                )
            else:
                dm_embed = discord.Embed(
                    description=message,
                    color=color,
                    timestamp=datetime.utcnow()
                )
                dm_embed.set_footer(
                    text=f"Message from {interaction.guild.name}",
                    icon_url=interaction.guild.icon.url if interaction.guild.icon else None
                )
            
            # Get server language for translation buttons
            language = self.bot.database.get_guild_setting(interaction.guild.id, 'language', 'en')
            
            # Create view with translation buttons
            view = discord.ui.View(timeout=None)
            if language != 'en':
                view.add_item(TranslationButton('🇺🇸', 'en', 'English', message, embed_title, color))
            if language != 'ar':
                view.add_item(TranslationButton('🇸🇦', 'ar', 'العربية', message, embed_title, color))
            if language != 'pt':
                view.add_item(TranslationButton('🇧🇷', 'pt', 'Português', message, embed_title, color))
            
            # Send DM
            try:
                await user.send(embed=dm_embed, view=view)
                success = True
                error_msg = None
            except discord.Forbidden:
                success = False
                error_msg = "User has DMs disabled"
            except Exception as e:
                success = False
                error_msg = str(e)
            
            # Create response embed
            if success:
                response_embed = discord.Embed(
                    title="✅ Message Sent",
                    description=f"**Recipient:** {user.mention}\n**Message:** {message[:100]}{'...' if len(message) > 100 else ''}",
                    color=0x4CAF50,
                    timestamp=datetime.utcnow()
                )
            else:
                response_embed = discord.Embed(
                    title="❌ Message Failed",
                    description=f"**Recipient:** {user.mention}\n**Error:** {error_msg}",
                    color=0xf44336,
                    timestamp=datetime.utcnow()
                )
            
            await interaction.response.send_message(embed=response_embed)
            
            # Log in bot activity channel
            activity_channel_id = self.bot.database.get_guild_setting(interaction.guild.id, 'bot_activity_channel')
            if activity_channel_id:
                activity_channel = interaction.guild.get_channel(activity_channel_id)
                if activity_channel:
                    status = "✅ Sent" if success else "❌ Failed"
                    log_embed = discord.Embed(
                        title="🤖 Bot Activity",
                        description=f"DM {status}: {interaction.user.mention} → {user.mention}",
                        color=0x5865f2,
                        timestamp=datetime.utcnow()
                    )
                    await activity_channel.send(embed=log_embed)
                    
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to send DM: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class TranslationButton(discord.ui.Button):
    """Button for translating DM messages"""
    
    def __init__(self, emoji, language, label, original_message, embed_title, color):
        super().__init__(emoji=emoji, label=label, style=discord.ButtonStyle.secondary)
        self.language = language
        self.original_message = original_message
        self.embed_title = embed_title
        self.color = color
        
    async def callback(self, interaction: discord.Interaction):
        """Show translation in a separate message without deleting original"""
        try:
            # Simple translation mappings for basic messages
            translations = {
                'en': {
                    'hello': 'Hello',
                    'welcome': 'Welcome',
                    'message': 'Message',
                    'from': 'From'
                },
                'ar': {
                    'hello': 'مرحبا',
                    'welcome': 'أهلا وسهلا',
                    'message': 'رسالة',
                    'from': 'من'
                },
                'pt': {
                    'hello': 'Olá',
                    'welcome': 'Bem-vindo',
                    'message': 'Mensagem',
                    'from': 'De'
                }
            }
            
            # Simple translation (for demo - would use proper translation API in production)
            translated_message = self.original_message
            
            # Add language prefix to show it's translated
            if self.embed_title:
                title_prefix = f"[{self.label}] {self.embed_title}"
                translated_embed = discord.Embed(
                    title=title_prefix,
                    description=translated_message,
                    color=self.color,
                    timestamp=datetime.utcnow()
                )
            else:
                translated_embed = discord.Embed(
                    title=f"[{self.label}] Translation",
                    description=translated_message,
                    color=self.color,
                    timestamp=datetime.utcnow()
                )
            
            # Send as a follow-up message instead of editing the original
            await interaction.response.send_message(embed=translated_embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"Translation error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Settings(bot))
