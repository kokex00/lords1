import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import platform

class General(commands.Cog):
    """General server and bot commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Show help information")
    async def help(self, interaction: discord.Interaction):
        """Display comprehensive help information"""
        try:
            embed = discord.Embed(
                title="🤖 Bot Help",
                description="Comprehensive server management and match scheduling bot",
                color=0x5865f2,
                timestamp=datetime.utcnow()
            )
            
            # Moderation Commands
            embed.add_field(
                name="🛡️ Moderation - Keep Order!",
                value=(
                    "`/kick` - Remove someone\n"
                    "`/ban` - Ban someone\n"
                    "`/mute` - Timeout someone\n"
                    "`/warn` - Give warning\n"
                    "`/warnings` - See warnings"
                ),
                inline=False
            )
            
            # Match Commands
            embed.add_field(
                name="⚔️ Matches - Super Easy!",
                value=(
                    "`/match` - Create a match (simple!)\n"
                    "`/matches` - See current matches\n"
                    "`/end_match` - End a match\n"
                    "`/cancel_match` - Cancel a match"
                ),
                inline=False
            )
            
            # Settings Commands  
            embed.add_field(
                name="⚙️ Settings - Easy Setup!",
                value=(
                    "`/set_channel` - Set bot channels\n"
                    "`/set_language` - Change language\n"
                    "`/settings` - View settings\n"
                    "`/dm` - Send private message"
                ),
                inline=False
            )
            
            # General Commands
            embed.add_field(
                name="📊 General",
                value=(
                    "`/serverinfo` - Server information\n"
                    "`/userinfo` - User information\n"
                    "`/ping` - Bot latency\n"
                    "`/help` - This help message"
                ),
                inline=False
            )
            
            # Features
            embed.add_field(
                name="✨ Quick Tips",
                value=(
                    "• Use `/match` to create a match easily\n"
                    "• Translation buttons preserve original messages\n"
                    "• Bot remembers your language settings\n"
                    "• All times automatically converted to your timezone"
                ),
                inline=False
            )
            
            embed.add_field(
                name="✨ Features",
                value=(
                    "• Multi-language support (EN/AR/PT)\n"
                    "• Automatic match reminders\n"
                    "• Translation buttons in DMs\n"
                    "• Timezone handling\n"
                    "• Comprehensive logging"
                ),
                inline=False
            )
            
            embed.set_footer(text="Use slash commands (/) to interact with the bot")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to show help: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="serverinfo", description="Display server information")
    async def serverinfo(self, interaction: discord.Interaction):
        """Display detailed server information"""
        try:
            guild = interaction.guild
            
            # Get various counts
            text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
            voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
            categories = len([c for c in guild.channels if isinstance(c, discord.CategoryChannel)])
            
            # Get member counts
            total_members = guild.member_count
            bots = len([m for m in guild.members if m.bot])
            humans = total_members - bots
            
            # Get boost info
            boost_level = guild.premium_tier
            boost_count = guild.premium_subscription_count or 0
            
            embed = discord.Embed(
                title=f"📊 {guild.name}",
                color=0x5865f2,
                timestamp=datetime.utcnow()
            )
            
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            # Basic Info
            embed.add_field(
                name="🆔 Basic Info",
                value=f"**ID:** `{guild.id}`\n**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}\n**Created:** <t:{int(guild.created_at.timestamp())}:R>",
                inline=True
            )
            
            # Member Info
            embed.add_field(
                name="👥 Members",
                value=f"**Total:** {total_members:,}\n**Humans:** {humans:,}\n**Bots:** {bots:,}",
                inline=True
            )
            
            # Channel Info
            embed.add_field(
                name="📁 Channels",
                value=f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Categories:** {categories}",
                inline=True
            )
            
            # Boost Info
            embed.add_field(
                name="⚡ Nitro Boost",
                value=f"**Level:** {boost_level}/3\n**Boosts:** {boost_count}\n**Features:** {len(guild.features)}",
                inline=True
            )
            
            # Role Info
            embed.add_field(
                name="🎭 Roles",
                value=f"**Total:** {len(guild.roles)}\n**Highest:** {guild.roles[-1].mention}",
                inline=True
            )
            
            # Security
            verification_levels = {
                discord.VerificationLevel.none: "None",
                discord.VerificationLevel.low: "Low",
                discord.VerificationLevel.medium: "Medium",
                discord.VerificationLevel.high: "High",
                discord.VerificationLevel.highest: "Highest"
            }
            
            embed.add_field(
                name="🔒 Security",
                value=f"**Verification:** {verification_levels.get(guild.verification_level, 'Unknown')}\n**2FA Required:** {'Yes' if guild.mfa_level else 'No'}",
                inline=True
            )
            
            if guild.description:
                embed.add_field(
                    name="📝 Description",
                    value=guild.description,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to get server info: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="userinfo", description="Display user information")
    @app_commands.describe(user="User to get information about (optional)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        """Display detailed user information"""
        try:
            if user is None:
                user = interaction.user
            
            embed = discord.Embed(
                title=f"👤 {user.display_name}",
                color=user.color if user.color != discord.Color.default() else 0x5865f2,
                timestamp=datetime.utcnow()
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            
            # Basic Info
            embed.add_field(
                name="🆔 Basic Info",
                value=f"**Username:** {user.name}\n**ID:** `{user.id}`\n**Bot:** {'Yes' if user.bot else 'No'}",
                inline=True
            )
            
            # Dates
            embed.add_field(
                name="📅 Dates",
                value=f"**Created:** <t:{int(user.created_at.timestamp())}:R>\n**Joined:** <t:{int(user.joined_at.timestamp())}:R>",
                inline=True
            )
            
            # Roles
            if len(user.roles) > 1:  # Exclude @everyone
                roles = [role.mention for role in user.roles[1:]]  # Skip @everyone
                role_list = ", ".join(roles[:5])  # Show first 5 roles
                if len(roles) > 5:
                    role_list += f" and {len(roles) - 5} more..."
            else:
                role_list = "None"
            
            embed.add_field(
                name=f"🎭 Roles ({len(user.roles) - 1})",
                value=role_list,
                inline=False
            )
            
            # Permissions
            key_perms = []
            if user.guild_permissions.administrator:
                key_perms.append("Administrator")
            elif user.guild_permissions.manage_guild:
                key_perms.append("Manage Server")
            elif user.guild_permissions.moderate_members:
                key_perms.append("Moderate Members")
            elif user.guild_permissions.manage_messages:
                key_perms.append("Manage Messages")
            
            if key_perms:
                embed.add_field(
                    name="🔑 Key Permissions",
                    value=", ".join(key_perms),
                    inline=True
                )
            
            # Status
            status_emojis = {
                discord.Status.online: "🟢 Online",
                discord.Status.idle: "🟡 Idle",
                discord.Status.dnd: "🔴 Do Not Disturb",
                discord.Status.offline: "⚫ Offline"
            }
            
            embed.add_field(
                name="📊 Status",
                value=status_emojis.get(user.status, "❓ Unknown"),
                inline=True
            )
            
            # Activity
            if user.activity:
                activity_type = {
                    discord.ActivityType.playing: "Playing",
                    discord.ActivityType.streaming: "Streaming",
                    discord.ActivityType.listening: "Listening to",
                    discord.ActivityType.watching: "Watching",
                    discord.ActivityType.custom: "Custom Status",
                    discord.ActivityType.competing: "Competing in"
                }.get(user.activity.type, "Activity")
                
                embed.add_field(
                    name="🎮 Activity",
                    value=f"{activity_type} {user.activity.name}",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to get user info: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Display bot latency information"""
        try:
            # Calculate latencies
            api_latency = round(self.bot.latency * 1000)
            
            embed = discord.Embed(
                title="🏓 Pong!",
                color=0x4CAF50 if api_latency < 100 else 0xffa502 if api_latency < 200 else 0xf44336,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📡 API Latency",
                value=f"`{api_latency}ms`",
                inline=True
            )
            
            # Bot info
            embed.add_field(
                name="🤖 Bot Info",
                value=f"**Guilds:** {len(self.bot.guilds)}\n**Python:** {platform.python_version()}\n**discord.py:** {discord.__version__}",
                inline=True
            )
            
            # Status indicator
            if api_latency < 100:
                status = "🟢 Excellent"
            elif api_latency < 200:
                status = "🟡 Good"
            elif api_latency < 300:
                status = "🟠 Fair"
            else:
                status = "🔴 Poor"
            
            embed.add_field(
                name="📊 Status",
                value=status,
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to get ping: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="server_info", description="📊 Show server information")
    async def server_info(self, interaction: discord.Interaction):
        """Display detailed server information"""
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"📊 {guild.name} Information",
            color=0x5865f2,
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="🆔 Server ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="📅 Created", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=True)
        
        embed.add_field(name="👥 Members", value=f"{guild.member_count}", inline=True)
        embed.add_field(name="📝 Text Channels", value=f"{len(guild.text_channels)}", inline=True)
        embed.add_field(name="🔊 Voice Channels", value=f"{len(guild.voice_channels)}", inline=True)
        
        embed.add_field(name="😀 Emojis", value=f"{len(guild.emojis)}", inline=True)
        embed.add_field(name="🎭 Roles", value=f"{len(guild.roles)}", inline=True)
        embed.add_field(name="⚡ Boost Level", value=f"{guild.premium_tier}", inline=True)
        
        if guild.description:
            embed.add_field(name="📖 Description", value=guild.description, inline=False)
            
        embed.set_footer(text="Made by kokex | LORDS Bot")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="user_info", description="👤 Show user information")
    @app_commands.describe(user="User to show info about")
    async def user_info(self, interaction: discord.Interaction, user: discord.Member = None):
        """Display detailed user information"""
        target = user or interaction.user
        
        embed = discord.Embed(
            title=f"👤 {target.display_name}",
            color=target.color,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(name="🏷️ Username", value=f"{target.name}", inline=True)
        embed.add_field(name="🆔 User ID", value=f"`{target.id}`", inline=True)
        embed.add_field(name="🤖 Bot", value="Yes" if target.bot else "No", inline=True)
        
        embed.add_field(name="📅 Account Created", value=f"<t:{int(target.created_at.timestamp())}:F>", inline=False)
        embed.add_field(name="📥 Joined Server", value=f"<t:{int(target.joined_at.timestamp())}:F>", inline=False)
        
        if target.premium_since:
            embed.add_field(name="💎 Boosting Since", value=f"<t:{int(target.premium_since.timestamp())}:F>", inline=False)
        
        if target.roles[1:]:  # Exclude @everyone
            roles = [role.mention for role in target.roles[1:][:10]]  # Show max 10 roles
            embed.add_field(name="🎭 Roles", value=" ".join(roles), inline=False)
        
        embed.set_footer(text="Made by kokex | LORDS Bot")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="create_channel", description="📋 Create a new text channel")
    @app_commands.describe(name="Channel name", topic="Channel topic (optional)")
    async def create_channel(self, interaction: discord.Interaction, name: str, topic: str = None):
        """Create a new text channel"""
        try:
            if not interaction.user.guild_permissions.manage_channels:
                embed = self.bot.embed_builder.create_error_embed(
                    "You don't have permission to create channels!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            channel = await interaction.guild.create_text_channel(name=name, topic=topic)
            
            embed = discord.Embed(
                title="✅ Channel Created",
                description=f"Successfully created {channel.mention}",
                color=0x4CAF50,
                timestamp=datetime.utcnow()
            )
            
            if topic:
                embed.add_field(name="📝 Topic", value=topic, inline=False)
            
            embed.set_footer(text="Made by kokex | LORDS Bot")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to create channel: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="poll", description="📊 Create a simple poll")
    @app_commands.describe(question="Poll question", option1="First option", option2="Second option", option3="Third option (optional)", option4="Fourth option (optional)")
    async def poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None):
        """Create a simple poll with reactions"""
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        
        embed = discord.Embed(
            title="📊 Poll",
            description=f"**{question}**",
            color=0x5865f2,
            timestamp=datetime.utcnow()
        )
        
        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        
        for i, option in enumerate(options):
            embed.add_field(name=f"{reactions[i]} Option {i+1}", value=option, inline=False)
        
        embed.set_footer(text=f"Poll by {interaction.user.display_name} | Made by kokex")
        
        await interaction.response.send_message(embed=embed)
        
        # Get the message and add reactions
        message = await interaction.original_response()
        for i in range(len(options)):
            await message.add_reaction(reactions[i])

async def setup(bot):
    await bot.add_cog(General(bot))
