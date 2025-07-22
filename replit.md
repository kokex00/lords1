# Overview

This is a comprehensive Discord bot designed for server management and match scheduling. The bot provides complete moderation tools, advanced match creation and management features, and multi-language support (English, Arabic, Portuguese). It's built using the discord.py library with a modular cog-based architecture and is currently operational and deployed.

**Current Status:** ✅ **FULLY OPERATIONAL** - Bot is connected to Discord with 21 slash commands
**Latest Updates (July 21, 2025):**
- ✅ Fixed translation system - now shows translations as separate messages without deleting originals
- ✅ Completely redesigned match creation: simple "team vs team" format with day/time selection
- ✅ New `/match` command format: team1, team2, day (1-31), time (8:30 PM format)
- ✅ Enhanced team display with colored team sections (🔴 Team 1 vs 🔵 Team 2)
- ✅ Added translation buttons in private messages (🇺🇸 🇸🇦 🇧🇷) for all languages
- ✅ Bot status shows "Made by kokex" as requested
- ✅ Added useful server commands: server_info, user_info, create_channel, poll
- ✅ Smart date parsing: automatically handles month transitions and past dates
- ✅ All embeds now include "Made by kokex | LORDS Bot" footer

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Architecture
- **Framework**: discord.py with the commands extension
- **Architecture Pattern**: Modular cog-based system
- **Data Storage**: JSON file-based database (simple flat files)
- **Language Support**: Multi-language translations (EN, AR, PT)
- **Command System**: Hybrid approach supporting both slash commands and traditional prefix commands

## Key Design Decisions
1. **JSON Database**: Chosen for simplicity and ease of deployment without external database dependencies
2. **Cog System**: Separates functionality into logical modules for better maintainability
3. **Multi-timezone Support**: Built-in support for GMT, Mecca time, and Portuguese timezone
4. **Embed-based UI**: Consistent visual presentation using Discord embeds

# Key Components

## Bot Core (`main.py`)
- Main bot class extending `commands.Bot`
- Handles bot initialization, cog loading, and background tasks
- Manages global bot state and core functionality

## Cogs (Command Modules)
- **Moderation (`cogs/moderation.py`)**: User management (kick, ban, mute, warnings)
- **Matches (`cogs/matches.py`)**: Match scheduling and management system
- **Settings (`cogs/settings.py`)**: Server configuration and channel management
- **General (`cogs/general.py`)**: General purpose commands and help system

## Utility Classes
- **Database (`utils/database.py`)**: JSON-based data persistence layer
- **Translations (`utils/translations.py`)**: Multi-language support and timezone handling
- **EmbedBuilder (`utils/embeds.py`)**: Consistent embed creation and formatting

# Data Flow

## Match Creation Process
1. User executes `/create_match` slash command
2. System validates permissions and parses input parameters
3. Participants are extracted from mentions (users/roles)
4. Match time is parsed and validated against current time
5. Match data is stored in JSON database
6. Private messages sent to all participants in their language
7. Background task schedules reminders (10 minutes and 3 minutes before)

## Moderation Actions
1. Moderator executes moderation command
2. Permission validation against user roles
3. Action logged to designated moderation channel
4. Target user receives private message notification
5. Action recorded in warnings database (if applicable)

# External Dependencies

## Discord.py Framework
- **Purpose**: Core Discord API interaction
- **Features Used**: Slash commands, embeds, member management, background tasks

## Python Standard Library
- **datetime/pytz**: Timezone handling and time parsing
- **json**: Data serialization for file-based storage
- **asyncio**: Asynchronous task management
- **re**: Regular expression parsing for time formats

## No External Database
- System uses JSON files for data persistence
- Files stored in `/data` directory (matches.json, settings.json, warnings.json)

# Deployment Strategy

## File Structure
```
/
├── main.py (bot entry point)
├── cogs/ (command modules)
├── utils/ (utility classes)
├── data/ (JSON data files)
└── attached_assets/ (requirements document)
```

## Configuration Requirements
- Discord bot token (environment variable)
- Appropriate bot permissions in Discord Developer Portal
- File system write access for JSON database

## Runtime Features
- Automatic cog loading on startup
- Background task management for match reminders
- Graceful error handling for missing permissions
- Multi-language DM notifications

## Scalability Considerations
- JSON database suitable for small to medium servers
- Can be migrated to proper database (PostgreSQL) for larger deployments
- Modular cog system allows easy feature additions
- Translation system supports adding new languages

## Bot Permissions Required
- Send Messages
- Use Slash Commands
- Manage Messages
- Kick Members
- Ban Members
- Timeout Members
- Read Message History
- Send Messages in Threads