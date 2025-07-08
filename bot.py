import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PREFIX = os.getenv('BOT_PREFIX', '!')

# File paths
AFK_DATA_FILE = 'afk.json'
RANK_CONFIG_FILE = 'rank_config.json'

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

def load_afk_data():
    """Load AFK and EXP data from JSON file"""
    try:
        with open(AFK_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"afk_users": {}, "user_exp": {}}

def save_afk_data(data):
    """Save AFK and EXP data to JSON file"""
    try:
        with open(AFK_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving AFK data: {e}")

def load_rank_config():
    """Load rank configuration from JSON file"""
    try:
        with open(RANK_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"ranks": [], "exp_rate": {"base_per_minute": 1, "max_per_session": 100}}

def calculate_exp_reward(afk_duration_minutes):
    """Calculate EXP reward based on AFK duration"""
    rank_config = load_rank_config()
    base_rate = rank_config.get('exp_rate', {}).get('base_per_minute', 1)
    max_reward = rank_config.get('exp_rate', {}).get('max_per_session', 100)
    
    # Calculate base reward (1 EXP per minute)
    exp_reward = int(afk_duration_minutes * base_rate)
    
    # Cap the reward at maximum per session
    return min(exp_reward, max_reward)

def get_user_rank(user_exp):
    """Get user's current rank based on EXP"""
    rank_config = load_rank_config()
    ranks = rank_config.get('ranks', [])
    
    # Sort ranks by min_exp in descending order to find the highest qualifying rank
    sorted_ranks = sorted(ranks, key=lambda r: r.get('min_exp', 0), reverse=True)
    
    for rank in sorted_ranks:
        if user_exp >= rank.get('min_exp', 0):
            return rank
    
    # Return the lowest rank if no rank qualifies
    return sorted_ranks[-1] if sorted_ranks else {"name": "Unranked", "min_exp": 0, "color": "#95a5a6"}

def format_duration(seconds):
    """Format duration in a human-readable way"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if minutes > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours != 1 else ''}"

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready to serve in {len(bot.guilds)} guild(s)')

@bot.event
async def on_message(message):
    """Handle all incoming messages"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Load data
    data = load_afk_data()
    afk_users = data.get('afk_users', {})
    user_exp = data.get('user_exp', {})
    user_id = str(message.author.id)
    
    # Check if user was AFK and is now active
    if user_id in afk_users:
        afk_info = afk_users[user_id]
        afk_start_time = datetime.fromisoformat(afk_info['timestamp'])
        current_time = datetime.now(timezone.utc)
        
        # Calculate AFK duration
        afk_duration = current_time - afk_start_time
        afk_duration_seconds = afk_duration.total_seconds()
        afk_duration_minutes = afk_duration_seconds / 60
        
        # Calculate EXP reward
        exp_reward = calculate_exp_reward(afk_duration_minutes)
        
        # Update user's EXP
        if user_id not in user_exp:
            user_exp[user_id] = 0
        user_exp[user_id] += exp_reward
        
        # Remove user from AFK list
        del afk_users[user_id]
        
        # Save updated data
        data['afk_users'] = afk_users
        data['user_exp'] = user_exp
        save_afk_data(data)
        
        # Create welcome back embed
        embed = discord.Embed(
            title="🎉 Welcome back!",
            description=f"You were AFK for {format_duration(afk_duration_seconds)}",
            color=discord.Color.green()
        )
        embed.add_field(name="EXP Earned", value=f"+{exp_reward} EXP", inline=True)
        embed.add_field(name="Total EXP", value=f"{user_exp[user_id]} EXP", inline=True)
        
        # Get user's current rank
        rank = get_user_rank(user_exp[user_id])
        embed.add_field(name="Current Rank", value=rank['name'], inline=True)
        
        await message.channel.send(embed=embed)
    
    # Check for mentions of AFK users
    if message.mentions:
        for mentioned_user in message.mentions:
            mentioned_user_id = str(mentioned_user.id)
            if mentioned_user_id in afk_users:
                afk_info = afk_users[mentioned_user_id]
                afk_message = afk_info.get('message', 'No message set')
                afk_start_time = datetime.fromisoformat(afk_info['timestamp'])
                current_time = datetime.now(timezone.utc)
                afk_duration = current_time - afk_start_time
                
                embed = discord.Embed(
                    title="🔕 User is AFK",
                    description=f"{mentioned_user.display_name} is currently AFK",
                    color=discord.Color.orange()
                )
                embed.add_field(name="AFK Message", value=afk_message, inline=False)
                embed.add_field(name="AFK Duration", value=format_duration(afk_duration.total_seconds()), inline=True)
                
                await message.channel.send(embed=embed)
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='afk')
async def set_afk(ctx, *, message="No message set"):
    """Set AFK status with optional message"""
    data = load_afk_data()
    afk_users = data.get('afk_users', {})
    user_id = str(ctx.author.id)
    
    # Set user as AFK
    afk_users[user_id] = {
        'message': message,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'user_name': ctx.author.display_name
    }
    
    # Save data
    data['afk_users'] = afk_users
    save_afk_data(data)
    
    # Send confirmation
    embed = discord.Embed(
        title="😴 AFK Status Set",
        description=f"{ctx.author.display_name} is now AFK",
        color=discord.Color.blue()
    )
    embed.add_field(name="Message", value=message, inline=False)
    embed.add_field(name="Started", value=f"<t:{int(datetime.now(timezone.utc).timestamp())}:R>", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='exp')
async def show_exp(ctx):
    """Show user's current EXP"""
    data = load_afk_data()
    user_exp = data.get('user_exp', {})
    user_id = str(ctx.author.id)
    
    current_exp = user_exp.get(user_id, 0)
    rank = get_user_rank(current_exp)
    
    embed = discord.Embed(
        title="📊 Your EXP Status",
        color=int(rank['color'][1:], 16)  # Convert hex color to int
    )
    embed.add_field(name="Current EXP", value=f"{current_exp} EXP", inline=True)
    embed.add_field(name="Current Rank", value=rank['name'], inline=True)
    
    # Find next rank
    rank_config = load_rank_config()
    ranks = sorted(rank_config.get('ranks', []), key=lambda r: r.get('min_exp', 0))
    next_rank = None
    for r in ranks:
        if r.get('min_exp', 0) > current_exp:
            next_rank = r
            break
    
    if next_rank:
        exp_needed = next_rank['min_exp'] - current_exp
        embed.add_field(name="Next Rank", value=f"{next_rank['name']} ({exp_needed} EXP needed)", inline=False)
    else:
        embed.add_field(name="Status", value="🏆 Maximum rank achieved!", inline=False)
    
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command(name='rank')
async def show_rank(ctx):
    """Show user's current rank"""
    data = load_afk_data()
    user_exp = data.get('user_exp', {})
    user_id = str(ctx.author.id)
    
    current_exp = user_exp.get(user_id, 0)
    rank = get_user_rank(current_exp)
    
    embed = discord.Embed(
        title="🎖️ Your Current Rank",
        color=int(rank['color'][1:], 16)
    )
    embed.add_field(name="Rank", value=rank['name'], inline=True)
    embed.add_field(name="EXP", value=f"{current_exp} EXP", inline=True)
    embed.add_field(name="Required EXP", value=f"{rank['min_exp']} EXP", inline=True)
    
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command(name='top')
async def show_leaderboard(ctx):
    """Show EXP leaderboard for top 10 users"""
    data = load_afk_data()
    user_exp = data.get('user_exp', {})
    
    if not user_exp:
        embed = discord.Embed(
            title="📋 EXP Leaderboard",
            description="No users have earned EXP yet!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return
    
    # Sort users by EXP (descending)
    sorted_users = sorted(user_exp.items(), key=lambda x: x[1], reverse=True)[:10]
    
    embed = discord.Embed(
        title="🏆 EXP Leaderboard - Top 10",
        color=discord.Color.gold()
    )
    
    for i, (user_id, exp) in enumerate(sorted_users, 1):
        try:
            user = bot.get_user(int(user_id))
            user_name = user.display_name if user else f"Unknown User ({user_id})"
            rank = get_user_rank(exp)
            
            # Medal emojis for top 3
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "
            
            embed.add_field(
                name=f"{medal}#{i} {user_name}",
                value=f"{exp} EXP • {rank['name']}",
                inline=False
            )
        except Exception as e:
            print(f"Error processing user {user_id}: {e}")
            continue
    
    embed.set_footer(text=f"Total users: {len(user_exp)}")
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param.name}")
    else:
        print(f"Command error: {error}")
        await ctx.send("❌ An error occurred while processing the command.")

# Run the bot
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
        exit(1)
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("Error: Invalid Discord token!")
    except Exception as e:
        print(f"Error starting bot: {e}")