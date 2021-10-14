#!/bin/python3

import discord
import os
from discord.ext import commands
from discord_components import *


bot = commands.Bot(command_prefix=['&'], case_insensitive=True, intents=discord.Intents.all())
bot.remove_command('help')

# Getting discord bot token from environment variable
TOKEN = os.environ['LOVE']

# Loading Cogs and changing presence when the bot is online


@bot.event
async def on_ready():
    DiscordComponents(bot)
    for filename in os.listdir('./Cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f"Cogs.{filename[:-3]}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="lovense links"))
    print("lovense is ready and online...")


if __name__ == '__main__':
    bot.run(TOKEN)
