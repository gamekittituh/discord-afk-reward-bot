import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# File paths
AFK_DATA_FILE = 'afk.json'
RANK_CONFIG_FILE = 'rank_config.json'

# Load data files
def load_afk_data():
    """Load AFK user data from JSON file"""
    try:
        with open(AFK_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}}

def save_afk_data(data):
    """Save AFK user data to JSON file"""
    with open(AFK_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_rank_config():
    """Load rank configuration from JSON file"""
    try:
        with open(RANK_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"ranks": [], "exp_per_minute": 1}

# Initialize data
afk_data = load_afk_data()
rank_config = load_rank_config()

def get_user_data(user_id):
    """Get user data, create if doesn't exist"""
    user_id_str = str(user_id)
    if user_id_str not in afk_data["users"]:
        afk_data["users"][user_id_str] = {
            "username": "",
            "exp": 0,
            "total_afk_time": 0,
            "afk_sessions": 0,
            "last_afk_start": None,
            "last_afk_end": None,
            "is_afk": False,
            "afk_message": ""
        }
    return afk_data["users"][user_id_str]

def get_user_rank(exp):
    """Get user rank based on EXP"""
    for rank in rank_config["ranks"]:
        if rank["min_exp"] <= exp <= rank["max_exp"]:
            return rank
    return rank_config["ranks"][-1]  # Return highest rank if EXP exceeds all ranges

def calculate_exp_from_afk_time(afk_minutes):
    """Calculate EXP based on AFK time in minutes"""
    exp_per_minute = rank_config.get("exp_per_minute", 1)
    return int(afk_minutes * exp_per_minute)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return
    
    user_data = get_user_data(message.author.id)
    
    # Check if user is returning from AFK
    if user_data["is_afk"] and user_data["last_afk_start"]:
        # Calculate AFK duration
        afk_start = datetime.fromisoformat(user_data["last_afk_start"])
        afk_end = datetime.now(timezone.utc)
        afk_duration = afk_end - afk_start
        afk_minutes = afk_duration.total_seconds() / 60
        
        # Calculate and award EXP
        exp_gained = calculate_exp_from_afk_time(afk_minutes)
        user_data["exp"] += exp_gained
        user_data["total_afk_time"] += afk_duration.total_seconds()
        user_data["last_afk_end"] = afk_end.isoformat()
        user_data["is_afk"] = False
        user_data["username"] = str(message.author)
        
        # Save data
        save_afk_data(afk_data)
        
        # Get rank info
        current_rank = get_user_rank(user_data["exp"])
        
        # Send welcome back message
        embed = discord.Embed(
            title="🎉 ยินดีต้อนรับกลับ!",
            description=f"คุณได้รับ **{exp_gained} EXP** จากการ AFK เป็นเวลา {int(afk_minutes)} นาที",
            color=int(current_rank["color"].replace("#", ""), 16)
        )
        embed.add_field(
            name="📊 สถิติปัจจุบัน",
            value=f"**EXP:** {user_data['exp']}\n**แรงค์:** {current_rank['name']}",
            inline=True
        )
        embed.set_footer(text=f"เวลา AFK: {int(afk_minutes)} นาที")
        
        await message.channel.send(embed=embed)
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='afk')
async def set_afk(ctx, *, message=""):
    """Set AFK status with optional message"""
    user_data = get_user_data(ctx.author.id)
    
    # Check if already AFK
    if user_data["is_afk"]:
        await ctx.send("❌ คุณอยู่ในสถานะ AFK อยู่แล้ว!")
        return
    
    # Set AFK status
    user_data["is_afk"] = True
    user_data["afk_message"] = message
    user_data["last_afk_start"] = datetime.now(timezone.utc).isoformat()
    user_data["afk_sessions"] += 1
    user_data["username"] = str(ctx.author)
    
    # Save data
    save_afk_data(afk_data)
    
    # Create embed
    embed = discord.Embed(
        title="😴 ตั้งสถานะ AFK",
        description=f"**{ctx.author.display_name}** ได้ตั้งสถานะ AFK",
        color=0x87CEEB
    )
    
    if message:
        embed.add_field(name="💭 ข้อความ", value=message, inline=False)
    
    embed.add_field(
        name="ℹ️ ข้อมูล",
        value="พิมพ์ข้อความใดก็ได้เพื่อกลับจากสถานะ AFK และรับ EXP",
        inline=False
    )
    embed.set_footer(text=f"เริ่มต้น AFK: {datetime.now().strftime('%H:%M:%S')}")
    
    await ctx.send(embed=embed)

@bot.command(name='exp', aliases=['rank'])
async def check_exp(ctx, user: discord.Member = None):
    """Check EXP and rank of user"""
    target_user = user or ctx.author
    user_data = get_user_data(target_user.id)
    current_rank = get_user_rank(user_data["exp"])
    
    # Find next rank
    next_rank = None
    for rank in rank_config["ranks"]:
        if rank["min_exp"] > user_data["exp"]:
            next_rank = rank
            break
    
    embed = discord.Embed(
        title=f"📊 สถิติของ {target_user.display_name}",
        color=int(current_rank["color"].replace("#", ""), 16)
    )
    
    embed.add_field(
        name="🏆 แรงค์ปัจจุบัน",
        value=f"**{current_rank['name']}**",
        inline=True
    )
    
    embed.add_field(
        name="⭐ EXP",
        value=f"**{user_data['exp']}**",
        inline=True
    )
    
    if next_rank:
        exp_needed = next_rank["min_exp"] - user_data["exp"]
        embed.add_field(
            name="🎯 แรงค์ถัดไป",
            value=f"**{next_rank['name']}**\n(ต้องการ {exp_needed} EXP)",
            inline=True
        )
    
    embed.add_field(
        name="📈 สถิติ AFK",
        value=f"**เซสชั่น:** {user_data['afk_sessions']}\n**เวลารวม:** {int(user_data['total_afk_time']/60)} นาที",
        inline=False
    )
    
    if user_data["is_afk"]:
        embed.add_field(
            name="😴 สถานะ",
            value=f"**AFK** - {user_data['afk_message']}" if user_data['afk_message'] else "**AFK**",
            inline=False
        )
    
    embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command(name='top', aliases=['leaderboard'])
async def show_leaderboard(ctx, limit: int = 10):
    """Show top users by EXP"""
    if limit > 20:
        limit = 20
    
    # Sort users by EXP
    sorted_users = sorted(
        afk_data["users"].items(),
        key=lambda x: x[1]["exp"],
        reverse=True
    )[:limit]
    
    if not sorted_users:
        await ctx.send("❌ ไม่มีข้อมูลผู้ใช้!")
        return
    
    embed = discord.Embed(
        title="🏆 อันดับ EXP สูงสุด",
        description=f"แสดง {len(sorted_users)} อันดับแรก",
        color=0xFFD700
    )
    
    leaderboard_text = ""
    for i, (user_id, user_data) in enumerate(sorted_users, 1):
        rank_info = get_user_rank(user_data["exp"])
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        # Try to get user from Discord
        try:
            discord_user = bot.get_user(int(user_id))
            username = discord_user.display_name if discord_user else user_data.get("username", "Unknown User")
        except:
            username = user_data.get("username", "Unknown User")
        
        leaderboard_text += f"{medal} **{username}**\n"
        leaderboard_text += f"    {rank_info['name']} - {user_data['exp']} EXP\n\n"
    
    embed.description = leaderboard_text
    embed.set_footer(text=f"ใช้คำสั่ง !exp เพื่อดูสถิติของตัวเอง")
    
    await ctx.send(embed=embed)

@bot.event
async def on_message_delete(message):
    """Handle message deletion for AFK mentions"""
    pass

@bot.event
async def on_message_edit(before, after):
    """Handle message edits"""
    pass

# Handle mentions of AFK users
@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return
    
    user_data = get_user_data(message.author.id)
    
    # Check if user is returning from AFK (same logic as before)
    if user_data["is_afk"] and user_data["last_afk_start"]:
        afk_start = datetime.fromisoformat(user_data["last_afk_start"])
        afk_end = datetime.now(timezone.utc)
        afk_duration = afk_end - afk_start
        afk_minutes = afk_duration.total_seconds() / 60
        
        exp_gained = calculate_exp_from_afk_time(afk_minutes)
        user_data["exp"] += exp_gained
        user_data["total_afk_time"] += afk_duration.total_seconds()
        user_data["last_afk_end"] = afk_end.isoformat()
        user_data["is_afk"] = False
        user_data["username"] = str(message.author)
        
        save_afk_data(afk_data)
        
        current_rank = get_user_rank(user_data["exp"])
        
        embed = discord.Embed(
            title="🎉 ยินดีต้อนรับกลับ!",
            description=f"คุณได้รับ **{exp_gained} EXP** จากการ AFK เป็นเวลา {int(afk_minutes)} นาที",
            color=int(current_rank["color"].replace("#", ""), 16)
        )
        embed.add_field(
            name="📊 สถิติปัจจุบัน",
            value=f"**EXP:** {user_data['exp']}\n**แรงค์:** {current_rank['name']}",
            inline=True
        )
        embed.set_footer(text=f"เวลา AFK: {int(afk_minutes)} นาที")
        
        await message.channel.send(embed=embed)
    
    # Check for mentions of AFK users
    if message.mentions:
        for mentioned_user in message.mentions:
            mentioned_data = get_user_data(mentioned_user.id)
            if mentioned_data["is_afk"]:
                afk_msg = f" - {mentioned_data['afk_message']}" if mentioned_data['afk_message'] else ""
                
                embed = discord.Embed(
                    title="😴 ผู้ใช้กำลัง AFK",
                    description=f"**{mentioned_user.display_name}** กำลัง AFK{afk_msg}",
                    color=0x87CEEB
                )
                
                if mentioned_data["last_afk_start"]:
                    afk_start = datetime.fromisoformat(mentioned_data["last_afk_start"])
                    afk_duration = datetime.now(timezone.utc) - afk_start
                    afk_minutes = int(afk_duration.total_seconds() / 60)
                    embed.set_footer(text=f"AFK มาแล้ว {afk_minutes} นาที")
                
                await message.channel.send(embed=embed)
    
    # Process commands
    await bot.process_commands(message)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ ข้อมูลไม่ครบ: {error}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ ข้อมูลไม่ถูกต้อง: {error}")
    else:
        print(f"Error: {error}")
        await ctx.send("❌ เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ ไม่พบ DISCORD_TOKEN ใน environment variables")
        print("กรุณาสร้างไฟล์ .env และใส่ DISCORD_TOKEN=your_bot_token")
    else:
        bot.run(token)