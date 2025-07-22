import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import pytz
import re
from utils.translation_buttons import TranslationView

class Matches(commands.Cog):
    """Match scheduling and management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="match", description="⚔️ من ضد من؟ - سهل جداً!")
    @app_commands.describe(
        team1="الفريق الأول (منشن اللاعبين)",
        team2="الفريق الثاني (منشن اللاعبين)", 
        day="يوم كم من الشهر؟ (مثل: 25)",
        time="الوقت (مثل: 8:30 PM أو 20:30)"
    )
    async def create_match(self, interaction: discord.Interaction, team1: str, team2: str, day: int, time: str):
        """Create a match: team vs team on specific day and time"""
        try:
            # Parse both teams
            team1_ids = self._parse_participants(team1, interaction.guild)
            team2_ids = self._parse_participants(team2, interaction.guild)
            
            if not team1_ids:
                embed = self.bot.embed_builder.create_error_embed(
                    "❌ الفريق الأول فارغ! منشن اللاعبين مثل: @player1 @player2",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
                
            if not team2_ids:
                embed = self.bot.embed_builder.create_error_embed(
                    "❌ الفريق الثاني فارغ! منشن اللاعبين مثل: @player1 @player2",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Parse day and time
            match_datetime = self._parse_day_and_time(day, time)
            if not match_datetime:
                embed = self.bot.embed_builder.create_error_embed(
                    "❌ اليوم أو الوقت غير صحيح! جرب: يوم 25 والوقت 8:30 PM",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Check if time is in the future
            if match_datetime <= datetime.now(pytz.UTC):
                embed = self.bot.embed_builder.create_error_embed(
                    "❌ Match time must be in the future!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Combine both teams
            all_participants = list(team1_ids) + list(team2_ids)
            
            # Create match data with team vs team format
            match_data = {
                'title': f"فريق ضد فريق",
                'description': f"الفريق الأول: {team1}\nالفريق الثاني: {team2}",
                'time': match_datetime.isoformat(),
                'creator_id': interaction.user.id,
                'participants': all_participants,
                'team1': list(team1_ids),
                'team2': list(team2_ids),
                'team1_mentions': team1,
                'team2_mentions': team2,
                'created_at': datetime.now(pytz.UTC).isoformat(),
                'reminded_10': False,
                'reminded_3': False
            }
            
            # Save match to database
            match_id = self.bot.database.create_match(interaction.guild.id, match_data)
            
            # Get guild language setting
            language = self.bot.database.get_guild_setting(interaction.guild.id, 'language', 'en')
            
            # Create match embed
            embed = self.bot.embed_builder.create_match_embed(match_data, match_id, language)
            
            await interaction.response.send_message(embed=embed)
            
            # Send DM notifications to participants
            await self._send_match_notifications(interaction.guild, match_data, all_participants, language)
            
            # Log in bot activity channel if set
            activity_channel_id = self.bot.database.get_guild_setting(interaction.guild.id, 'bot_activity_channel')
            if activity_channel_id:
                activity_channel = interaction.guild.get_channel(activity_channel_id)
                if activity_channel:
                    log_embed = discord.Embed(
                        title="🤖 Bot Activity",
                        description=f"Match created: **فريق ضد فريق**\nCreator: {interaction.user.mention}\nTeam 1: {team1}\nTeam 2: {team2}",
                        color=0x5865f2,
                        timestamp=datetime.utcnow()
                    )
                    await activity_channel.send(embed=log_embed)
                    
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to create match: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="matches", description="📋 See all matches")
    async def list_matches(self, interaction: discord.Interaction):
        """List all current matches in the server"""
        try:
            matches = self.bot.database.get_guild_matches(interaction.guild.id)
            
            if not matches:
                embed = discord.Embed(
                    title="📅 Current Matches",
                    description="No matches scheduled.",
                    color=0x5865f2,
                    timestamp=datetime.utcnow()
                )
            else:
                embed = discord.Embed(
                    title="📅 Current Matches",
                    description=f"Found {len(matches)} scheduled matches:",
                    color=0x5865f2,
                    timestamp=datetime.utcnow()
                )
                
                # Sort matches by time
                sorted_matches = sorted(matches.items(), key=lambda x: x[1]['time'])
                
                for i, (match_id, match_data) in enumerate(sorted_matches[:10], 1):  # Show max 10 matches
                    match_time = datetime.fromisoformat(match_data['time'])
                    creator = interaction.guild.get_member(match_data['creator_id'])
                    creator_name = creator.mention if creator else f"<@{match_data['creator_id']}>"
                    
                    participant_count = len(match_data['participants'])
                    time_str = f"<t:{int(match_time.timestamp())}:R>"
                    
                    embed.add_field(
                        name=f"`#{i}` {match_data['title']}",
                        value=f"**Time:** {time_str}\n**Creator:** {creator_name}\n**Participants:** {participant_count}",
                        inline=True
                    )
                
                if len(matches) > 10:
                    embed.set_footer(text=f"Showing 10 of {len(matches)} matches")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to list matches: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="end_match", description="End a match by number")
    @app_commands.describe(match_number="Match number from /list_matches")
    async def end_match(self, interaction: discord.Interaction, match_number: int):
        """End a match by its number from the list"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.manage_events:
                embed = self.bot.embed_builder.create_error_embed(
                    "You don't have permission to end matches!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            matches = self.bot.database.get_guild_matches(interaction.guild.id)
            
            if not matches:
                embed = self.bot.embed_builder.create_error_embed(
                    "No matches found to end!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Sort matches by time to get the correct order
            sorted_matches = sorted(matches.items(), key=lambda x: x[1]['time'])
            
            if not 1 <= match_number <= len(sorted_matches):
                embed = self.bot.embed_builder.create_error_embed(
                    f"Invalid match number! Must be between 1 and {len(sorted_matches)}",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Get the match to end
            match_id, match_data = sorted_matches[match_number - 1]
            
            # Check if user is the creator or has admin permissions
            if match_data['creator_id'] != interaction.user.id and not interaction.user.guild_permissions.administrator:
                embed = self.bot.embed_builder.create_error_embed(
                    "You can only end matches you created!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Remove the match
            self.bot.database.remove_match(interaction.guild.id, match_id)
            
            # Create success embed
            embed = discord.Embed(
                title="✅ Match Ended",
                description=f"**Match:** {match_data['title']}\n**Ended by:** {interaction.user.mention}",
                color=0x4CAF50,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to end match: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="cancel_match", description="Cancel a match by number")
    @app_commands.describe(match_number="Match number from /list_matches")
    async def cancel_match(self, interaction: discord.Interaction, match_number: int):
        """Cancel a match and notify participants"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.manage_events:
                embed = self.bot.embed_builder.create_error_embed(
                    "You don't have permission to cancel matches!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            matches = self.bot.database.get_guild_matches(interaction.guild.id)
            
            if not matches:
                embed = self.bot.embed_builder.create_error_embed(
                    "No matches found to cancel!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Sort matches by time to get the correct order
            sorted_matches = sorted(matches.items(), key=lambda x: x[1]['time'])
            
            if not 1 <= match_number <= len(sorted_matches):
                embed = self.bot.embed_builder.create_error_embed(
                    f"Invalid match number! Must be between 1 and {len(sorted_matches)}",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Get the match to cancel
            match_id, match_data = sorted_matches[match_number - 1]
            
            # Check if user is the creator or has admin permissions
            if match_data['creator_id'] != interaction.user.id and not interaction.user.guild_permissions.administrator:
                embed = self.bot.embed_builder.create_error_embed(
                    "You can only cancel matches you created!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Get guild language setting
            language = self.bot.database.get_guild_setting(interaction.guild.id, 'language', 'en')
            
            # Notify participants about cancellation
            await self._send_cancellation_notifications(interaction.guild, match_data, language)
            
            # Remove the match
            self.bot.database.remove_match(interaction.guild.id, match_id)
            
            # Create success embed
            embed = discord.Embed(
                title="❌ Match Cancelled",
                description=f"**Match:** {match_data['title']}\n**Cancelled by:** {interaction.user.mention}\n**Participants notified:** {len(match_data['participants'])}",
                color=0xf44336,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to cancel match: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _parse_participants(self, participants_str, guild):
        """Parse participant mentions and role mentions"""
        participant_ids = set()
        
        # Find user mentions
        user_matches = re.findall(r'<@!?(\d+)>', participants_str)
        for user_id in user_matches:
            member = guild.get_member(int(user_id))
            if member:
                participant_ids.add(member.id)
        
        # Find role mentions
        role_matches = re.findall(r'<@&(\d+)>', participants_str)
        for role_id in role_matches:
            role = guild.get_role(int(role_id))
            if role:
                for member in role.members:
                    participant_ids.add(member.id)
        
        return participant_ids
    
    def _parse_day_and_time(self, day, time_str):
        """Parse day (1-31) and time string into datetime"""
        try:
            from datetime import datetime, date
            import calendar
            
            # Validate day
            if day < 1 or day > 31:
                return None
                
            # Get current date
            now = datetime.now()
            current_year = now.year
            current_month = now.month
            
            # Check if day exists in current month
            try:
                match_date = date(current_year, current_month, day)
            except ValueError:
                # Day doesn't exist in current month, try next month
                if current_month == 12:
                    next_month = 1
                    next_year = current_year + 1
                else:
                    next_month = current_month + 1
                    next_year = current_year
                    
                try:
                    match_date = date(next_year, next_month, day)
                except ValueError:
                    return None
            
            # If day is in the past this month, use next month
            if match_date <= now.date():
                if current_month == 12:
                    next_month = 1
                    next_year = current_year + 1
                else:
                    next_month = current_month + 1
                    next_year = current_year
                    
                try:
                    match_date = date(next_year, next_month, day)
                except ValueError:
                    return None
            
            # Parse time
            time_formats = [
                '%H:%M',        # 20:30
                '%I:%M %p',     # 8:30 PM
                '%I %p',        # 8 PM
                '%H'            # 20
            ]
            
            parsed_time = None
            for fmt in time_formats:
                try:
                    parsed_time = datetime.strptime(time_str, fmt).time()
                    break
                except ValueError:
                    continue
            
            if not parsed_time:
                # Try to parse common formats
                time_lower = time_str.lower()
                if 'pm' in time_lower or 'am' in time_lower:
                    # Extract number and convert
                    import re
                    numbers = re.findall(r'\d+', time_str)
                    if numbers:
                        hour = int(numbers[0])
                        minute = int(numbers[1]) if len(numbers) > 1 else 0
                        if 'pm' in time_lower and hour != 12:
                            hour += 12
                        elif 'am' in time_lower and hour == 12:
                            hour = 0
                        try:
                            parsed_time = datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
                        except ValueError:
                            return None
                else:
                    return None
            
            # Combine date and time
            match_datetime = datetime.combine(match_date, parsed_time)
            return pytz.UTC.localize(match_datetime)
            
        except Exception as e:
            print(f"Error parsing day and time: {e}")
            return None
    
    def _parse_time(self, time_str):
        """Parse various time formats"""
        try:
            # Handle relative times like "today 8:30 PM"
            if 'today' in time_str.lower():
                time_part = time_str.lower().replace('today', '').strip()
                today = datetime.now()
                
                # Try to parse time part
                time_formats = ['%I:%M %p', '%H:%M', '%I %p']
                for fmt in time_formats:
                    try:
                        parsed_time = datetime.strptime(time_part, fmt).time()
                        result = datetime.combine(today.date(), parsed_time)
                        return pytz.UTC.localize(result) if result.tzinfo is None else result
                    except ValueError:
                        continue
            
            # Handle absolute datetime formats
            formats = [
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d %I:%M %p',
                '%d/%m/%Y %H:%M',
                '%d/%m/%Y %I:%M %p',
                '%m/%d/%Y %H:%M',
                '%m/%d/%Y %I:%M %p'
            ]
            
            for fmt in formats:
                try:
                    result = datetime.strptime(time_str, fmt)
                    return pytz.UTC.localize(result) if result.tzinfo is None else result
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error parsing time: {e}")
            return None
    
    async def _send_match_notifications(self, guild, match_data, participant_ids, language):
        """Send DM notifications to match participants"""
        try:
            for user_id in participant_ids:
                try:
                    member = guild.get_member(user_id)
                    if member:
                        embed = self.bot.embed_builder.create_match_notification_embed(match_data, language)
                        view = TranslationView(embed, match_data, language)
                        
                        await member.send(embed=embed, view=view)
                        
                except Exception as e:
                    print(f"Failed to send notification to user {user_id}: {e}")
                    
        except Exception as e:
            print(f"Error sending match notifications: {e}")
    
    async def _send_cancellation_notifications(self, guild, match_data, language):
        """Send DM notifications about match cancellation"""
        try:
            for user_id in match_data['participants']:
                try:
                    member = guild.get_member(user_id)
                    if member:
                        embed = self.bot.embed_builder.create_cancellation_embed(match_data, language)
                        view = TranslationView(embed, match_data, language)
                        
                        await member.send(embed=embed, view=view)
                        
                except Exception as e:
                    print(f"Failed to send cancellation notification to user {user_id}: {e}")
                    
        except Exception as e:
            print(f"Error sending cancellation notifications: {e}")



async def setup(bot):
    await bot.add_cog(Matches(bot))
