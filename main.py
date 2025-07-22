import discord
from discord.ext import commands, tasks
import asyncio
import os
import json
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any

# Import our custom modules
from utils.database import Database
from utils.translations import Translations
from utils.embeds import EmbedBuilder
from keep_alive import keep_alive

# Define bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        self.database = Database()
        self.translations = Translations()
        self.embed_builder = EmbedBuilder()
        
    async def setup_hook(self):
        """Load all cogs and start background tasks"""
        # Load cogs
        cogs = ['cogs.moderation', 'cogs.matches', 'cogs.settings', 'cogs.general']
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")
        
        # Start background tasks
        self.match_reminder_task.start()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Bot ready event"""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status with creator info
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="LORDS BOT | Made by kokex | /help"
            )
        )
    
    async def on_guild_join(self, guild):
        """Initialize settings when joining a new guild"""
        self.database.initialize_guild(guild.id)
        print(f"Joined new guild: {guild.name} ({guild.id})")
    
    @tasks.loop(minutes=1)
    async def match_reminder_task(self):
        """Check for matches that need reminders"""
        try:
            current_time = datetime.now(pytz.UTC)
            matches = self.database.get_all_matches()
            
            for guild_id, guild_matches in matches.items():
                guild = self.get_guild(int(guild_id))
                if not guild:
                    continue
                
                for match_id, match_data in list(guild_matches.items()):
                    match_time = datetime.fromisoformat(match_data['time'])
                    time_diff = match_time - current_time
                    
                    # 10 minute reminder
                    if 9 <= time_diff.total_seconds() / 60 <= 11 and not match_data.get('reminded_10', False):
                        await self.send_match_reminder(guild, match_data, 10)
                        match_data['reminded_10'] = True
                        self.database.update_match(guild_id, match_id, match_data)
                    
                    # 3 minute reminder
                    elif 2 <= time_diff.total_seconds() / 60 <= 4 and not match_data.get('reminded_3', False):
                        await self.send_match_reminder(guild, match_data, 3)
                        match_data['reminded_3'] = True
                        self.database.update_match(guild_id, match_id, match_data)
                    
                    # Remove expired matches
                    elif time_diff.total_seconds() < -3600:  # 1 hour after match time
                        self.database.remove_match(guild_id, match_id)
                        
        except Exception as e:
            print(f"Error in match reminder task: {e}")
    
    async def send_match_reminder(self, guild, match_data, minutes):
        """Send reminder to match participants"""
        try:
            language = self.database.get_guild_setting(guild.id, 'language', 'en')
            
            # Create reminder embed
            embed = self.embed_builder.create_match_reminder_embed(match_data, minutes, language)
            
            # Send to participants
            for user_id in match_data['participants']:
                try:
                    user = guild.get_member(user_id)
                    if user:
                        view = TranslationView(match_data, language)
                        await user.send(embed=embed, view=view)
                except Exception as e:
                    print(f"Failed to send reminder to user {user_id}: {e}")
                    
        except Exception as e:
            print(f"Error sending match reminder: {e}")

class TranslationView(discord.ui.View):
    """View with translation buttons for DMs"""
    
    def __init__(self, match_data, current_language):
        super().__init__(timeout=None)
        self.match_data = match_data
        self.current_language = current_language
        
        # Add translation buttons
        if current_language != 'en':
            self.add_item(TranslationButton('🇺🇸', 'en', 'English'))
        if current_language != 'ar':
            self.add_item(TranslationButton('🇸🇦', 'ar', 'العربية'))
        if current_language != 'pt':
            self.add_item(TranslationButton('🇧🇷', 'pt', 'Português'))

class TranslationButton(discord.ui.Button):
    """Button for translating messages"""
    
    def __init__(self, emoji, language, label):
        super().__init__(emoji=emoji, label=label, style=discord.ButtonStyle.secondary)
        self.language = language
        
    async def callback(self, interaction: discord.Interaction):
        """Show translation as a separate message without deleting original"""
        try:
            bot = interaction.client
            embed_builder = bot.embed_builder
            
            # Get match data from view
            view = self.view
            match_data = view.match_data
            
            # Create new embed in selected language
            embed = embed_builder.create_match_reminder_embed(match_data, 0, self.language)
            
            # Add translation indicator to title
            if embed.title:
                embed.title = f"[{self.label}] {embed.title}"
            
            # Send as follow-up message instead of editing original
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"Translation error: {e}", ephemeral=True)

# Initialize and run the bot
async def main():
    # Start keep-alive server
    keep_alive()
    
    bot = DiscordBot()
    
    # Get token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not found!")
        return
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
