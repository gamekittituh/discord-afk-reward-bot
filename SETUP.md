# Discord AFK Reward Bot - Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Bot Token**
   - Copy `.env.example` to `.env`
   - Replace `your_discord_bot_token_here` with your actual Discord bot token
   ```bash
   cp .env.example .env
   # Edit .env file with your token
   ```

3. **Run the Bot**
   ```bash
   python bot.py
   ```

## Features

### Commands
- `!afk [message]` - Set AFK status with optional custom message
- `!exp` - Show your current EXP and rank information
- `!rank` - Show your current rank details
- `!top` - Display EXP leaderboard (top 10 users)

### Automatic Features
- **AFK Detection**: When you send a message after being AFK, you'll automatically receive EXP based on your AFK duration
- **Mention Notifications**: When someone mentions an AFK user, the bot will notify the channel with their AFK message and duration

## Configuration

### Rank System (`rank_config.json`)
The bot uses a configurable rank system with the following default ranks:
- **Newbie** (0+ EXP) - Gray
- **Regular** (100+ EXP) - Blue  
- **Active** (500+ EXP) - Green
- **Veteran** (1,500+ EXP) - Orange
- **Expert** (3,000+ EXP) - Red
- **Master** (5,000+ EXP) - Purple
- **Legend** (10,000+ EXP) - Gold

### EXP Rates
- **Base Rate**: 1 EXP per minute of AFK time
- **Maximum per Session**: 100 EXP (prevents abuse from extremely long AFK periods)

### Data Storage
- **afk.json**: Stores AFK status and user EXP data
- Future-proofed for database migration

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable the following bot permissions:
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands (optional, for future expansion)
6. Invite the bot to your server with these permissions

## Example Usage

```
User: !afk Going to lunch, back in 30 minutes
Bot: 😴 AFK Status Set
     User is now AFK
     Message: Going to lunch, back in 30 minutes

[30 minutes later]
User: I'm back!
Bot: 🎉 Welcome back!
     You were AFK for 30 minutes
     EXP Earned: +30 EXP
     Total EXP: 130 EXP
     Current Rank: Regular

User: !exp
Bot: 📊 Your EXP Status
     Current EXP: 130 EXP
     Current Rank: Regular
     Next Rank: Active (370 EXP needed)

User: !top
Bot: 🏆 EXP Leaderboard - Top 10
     🥇 #1 User1: 2500 EXP • Veteran
     🥈 #2 User2: 1800 EXP • Veteran  
     🥉 #3 User3: 600 EXP • Active
     ...
```

## Notes

- AFK time is calculated from when you set the status until you send your next message
- Mentioning AFK users will show their status without removing their AFK state
- Only the AFK user themselves can remove their AFK status by sending a message
- EXP rewards are calculated based on total AFK duration, capped at 100 EXP per session