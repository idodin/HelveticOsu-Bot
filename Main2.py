#!/usr/bin/env python3

# Discord-py
import discord
from discord.ext import commands
import asyncio

# Other utilities
import os, sys

# Parse config file
from config import parser


#Extension List
startup = ["osu",  "update"]

config = parser.Parser()

bot=commands.Bot(command_prefix='?')

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as {} ({})'.format(bot.user.name, bot.user.id))

@bot.command()
@asyncio.coroutine
def load(extension_name: str):
    """
    Load a specific extension. Extension list = ["osu", "moderation", "update"]
    """
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        yield from bot.say("```{}: {}\n```".format(type(e).__name__,str(e)))
        return
    yield from bot.say("{} loaded succesfully.".format(extension_name))

@bot.command()
@asyncio.coroutine
def unload(extension_name: str):
    """
    Unload a specific extension. Extension list = ["osu", "moderation", "update"]
    """
    bot.unload_extension(extension_name)
    yield from bot.say("{} unloaded.".format(extension_name))

@bot.command(pass_context=True)
@asyncio.coroutine
def restart():
    yield from bot.say("Bye everyone! I'll be right back, woof~!")
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == "__main__":
    for extension in startup:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Couldn\'t load extension {}\n{}: {}'.format(extension, type(e).__name__,e))
    
    bot.run(config.discordkey)
