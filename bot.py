import discord
from discord.ext import commands
import database
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    # Render assigns a dynamic port
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    database.setup_db()
    keep_alive() 
    print(f'Logged in as {bot.user}')

@bot.command()
async def add(ctx, *, task: str):
    database.add_task(ctx.author.id, task)
    await ctx.send(f"✅ Added: {task}")

@bot.command()
async def list(ctx):
    tasks = database.get_tasks(ctx.author.id)
    if not tasks:
        return await ctx.send("Your list is empty!")
    
    response = "**Your To-Do List:**\n"
    for task_id, task in tasks:
        response += f"`{task_id}`: {task}\n"
    await ctx.send(response)

@bot.command()
async def done(ctx, task_id: int):
    database.remove_task(task_id)
    await ctx.send(f"🗑️ Removed task `{task_id}`")

# Fetch token from Render's Environment Variables
TOKEN = os.environ.get('DISCORD_TOKEN')

if __name__ == "__main__":
    bot.run(TOKEN)