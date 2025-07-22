import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

class Moderation(commands.Cog):
    """Moderation commands for server management"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="kick", description="👢 Remove someone from server")
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for the kick"
    )
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Kick a member from the server"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.kick_members:
                embed = self.bot.embed_builder.create_error_embed(
                    self.bot.translations.get_text('no_permission', 'en'),
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Check if trying to kick a higher role
            if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
                embed = self.bot.embed_builder.create_error_embed(
                    "You cannot kick someone with a higher or equal role!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Send DM to user before kicking
            try:
                dm_embed = discord.Embed(
                    title="🦶 You have been kicked",
                    description=f"**Server:** {interaction.guild.name}\n**Reason:** {reason}",
                    color=0xff6b6b,
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            # Kick the member
            await member.kick(reason=f"Kicked by {interaction.user} | {reason}")
            
            # Create success embed
            embed = discord.Embed(
                title="✅ Member Kicked",
                description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**Moderator:** {interaction.user.mention}",
                color=0x4CAF50,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log to moderation channel if set
            log_channel_id = self.bot.database.get_guild_setting(interaction.guild.id, 'mod_log_channel')
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                    
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to kick member: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(
        member="The member to ban",
        reason="Reason for the ban",
        delete_days="Days of messages to delete (0-7)"
    )
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided", delete_days: int = 0):
        """Ban a member from the server"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.ban_members:
                embed = self.bot.embed_builder.create_error_embed(
                    "You don't have permission to ban members!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Check if trying to ban a higher role
            if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
                embed = self.bot.embed_builder.create_error_embed(
                    "You cannot ban someone with a higher or equal role!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Validate delete_days
            if not 0 <= delete_days <= 7:
                embed = self.bot.embed_builder.create_error_embed(
                    "Delete days must be between 0 and 7!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Send DM to user before banning
            try:
                dm_embed = discord.Embed(
                    title="🔨 You have been banned",
                    description=f"**Server:** {interaction.guild.name}\n**Reason:** {reason}",
                    color=0xff4757,
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            # Ban the member
            await member.ban(reason=f"Banned by {interaction.user} | {reason}", delete_message_days=delete_days)
            
            # Create success embed
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**Moderator:** {interaction.user.mention}\n**Messages Deleted:** {delete_days} days",
                color=0xff4757,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log to moderation channel if set
            log_channel_id = self.bot.database.get_guild_setting(interaction.guild.id, 'mod_log_channel')
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                    
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to ban member: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="mute", description="Timeout a member")
    @app_commands.describe(
        member="The member to timeout",
        duration="Duration in minutes",
        reason="Reason for the timeout"
    )
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
        """Timeout a member"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.moderate_members:
                embed = self.bot.embed_builder.create_error_embed(
                    "You don't have permission to timeout members!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Check if trying to timeout a higher role
            if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
                embed = self.bot.embed_builder.create_error_embed(
                    "You cannot timeout someone with a higher or equal role!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Validate duration (Discord allows max 28 days = 40320 minutes)
            if not 1 <= duration <= 40320:
                embed = self.bot.embed_builder.create_error_embed(
                    "Duration must be between 1 minute and 28 days (40320 minutes)!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Calculate timeout until time
            timeout_until = datetime.utcnow() + timedelta(minutes=duration)
            
            # Send DM to user before timing out
            try:
                dm_embed = discord.Embed(
                    title="🔇 You have been timed out",
                    description=f"**Server:** {interaction.guild.name}\n**Duration:** {duration} minutes\n**Reason:** {reason}",
                    color=0xffa502,
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            # Timeout the member
            await member.timeout(timeout_until, reason=f"Timed out by {interaction.user} | {reason}")
            
            # Create success embed
            embed = discord.Embed(
                title="🔇 Member Timed Out",
                description=f"**Member:** {member.mention}\n**Duration:** {duration} minutes\n**Reason:** {reason}\n**Moderator:** {interaction.user.mention}\n**Expires:** <t:{int(timeout_until.timestamp())}:R>",
                color=0xffa502,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log to moderation channel if set
            log_channel_id = self.bot.database.get_guild_setting(interaction.guild.id, 'mod_log_channel')
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                    
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to timeout member: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(
        member="The member to warn",
        reason="Reason for the warning"
    )
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Warn a member"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.kick_members:
                embed = self.bot.embed_builder.create_error_embed(
                    "You don't have permission to warn members!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Add warning to database
            warning_id = self.bot.database.add_warning(
                interaction.guild.id,
                member.id,
                interaction.user.id,
                reason
            )
            
            # Get total warnings for user
            warnings = self.bot.database.get_user_warnings(interaction.guild.id, member.id)
            warning_count = len(warnings)
            
            # Send DM to user
            try:
                dm_embed = discord.Embed(
                    title="⚠️ You have been warned",
                    description=f"**Server:** {interaction.guild.name}\n**Reason:** {reason}\n**Total Warnings:** {warning_count}",
                    color=0xff9f43,
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            # Create success embed
            embed = discord.Embed(
                title="⚠️ Member Warned",
                description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**Moderator:** {interaction.user.mention}\n**Warning ID:** `{warning_id}`\n**Total Warnings:** {warning_count}",
                color=0xff9f43,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log to moderation channel if set
            log_channel_id = self.bot.database.get_guild_setting(interaction.guild.id, 'mod_log_channel')
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                    
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to warn member: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="warnings", description="View warnings for a member")
    @app_commands.describe(member="The member whose warnings to view")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        """View warnings for a member"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.kick_members:
                embed = self.bot.embed_builder.create_error_embed(
                    "You don't have permission to view warnings!",
                    interaction.user
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            warnings = self.bot.database.get_user_warnings(interaction.guild.id, member.id)
            
            if not warnings:
                embed = discord.Embed(
                    title="📋 Warnings",
                    description=f"{member.mention} has no warnings.",
                    color=0x4CAF50,
                    timestamp=datetime.utcnow()
                )
            else:
                embed = discord.Embed(
                    title="📋 Warnings",
                    description=f"**Member:** {member.mention}\n**Total Warnings:** {len(warnings)}",
                    color=0xff9f43,
                    timestamp=datetime.utcnow()
                )
                
                # Add warning fields
                for i, warning in enumerate(warnings[-10:], 1):  # Show last 10 warnings
                    moderator = interaction.guild.get_member(warning['moderator_id'])
                    mod_name = moderator.mention if moderator else f"<@{warning['moderator_id']}>"
                    
                    embed.add_field(
                        name=f"Warning #{warning['id']}",
                        value=f"**Reason:** {warning['reason']}\n**Moderator:** {mod_name}\n**Date:** <t:{int(warning['timestamp'])}:R>",
                        inline=False
                    )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.create_error_embed(f"Failed to get warnings: {e}", interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
