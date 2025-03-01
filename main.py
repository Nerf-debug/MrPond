import discord
from discord.ext import commands
import sqlite3
import os

# Load token from environment variables
TOKEN = os.getenv("TOKEN")

# Bot prefix
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Connect to SQLite database
conn = sqlite3.connect("donations.db")
cursor = conn.cursor()

# Create donations table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS donations (
    user_id INTEGER PRIMARY KEY,
    total_donation INTEGER
)''')
conn.commit()

# Function to parse shorthand notation
def parse_donation(amount: str):
    amount = amount.lower()
    if "b" in amount:
        return int(float(amount.replace("b", "")) * 1_000_000_000)
    elif "m" in amount:
        return int(float(amount.replace("m", "")) * 1_000_000)
    elif "k" in amount:
        return int(float(amount.replace("k", "")) * 1_000)
    return int(amount)

# Add donation command
@bot.command()
async def add(ctx, member: discord.Member, amount: str):
    try:
        donation_amount = parse_donation(amount)

        cursor.execute("SELECT total_donation FROM donations WHERE user_id = ?", (member.id,))
        result = cursor.fetchone()

        if result:
            new_total = result[0] + donation_amount
            cursor.execute("UPDATE donations SET total_donation = ? WHERE user_id = ?", (new_total, member.id))
        else:
            new_total = donation_amount
            cursor.execute("INSERT INTO donations (user_id, total_donation) VALUES (?, ?)", (member.id, new_total))

        conn.commit()

        embed = discord.Embed(title="Donation Added", color=discord.Color.green())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Added Amount", value=f"{amount}", inline=False)
        embed.add_field(name="Total Donation", value=f"{new_total:,}", inline=False)
        embed.set_footer(text="Thank you for your contribution! 🎉")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Error: {e}")

# Check donation balance command
@bot.command()
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author

    cursor.execute("SELECT total_donation FROM donations WHERE user_id = ?", (member.id,))
    result = cursor.fetchone()

    total_donation = result[0] if result else 0

    embed = discord.Embed(title="Donation Balance", color=discord.Color.blue())
    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(name="Total Donation", value=f"{total_donation:,}", inline=False)
    embed.set_footer(text="Keep donating to reach milestones! 💰")

    await ctx.send(embed=embed)

# Run bot
bot.run(TOKEN)
