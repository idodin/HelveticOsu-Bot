#!/usr/bin/env python3

# Discord-py
import discord
from discord.ext import commands
import asyncio

# Other utilities
import os, sys

# Parse config file
from config import parser

# Utility for auto-add
from db import db_utilities as db

#Extension List
startup = ["osu",  "update"]

config = parser.Parser()
utility = db.Db_Utilities(config.db_path, config.osukey)

bot=commands.Bot(command_prefix='!')

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as {} ({})'.format(bot.user.name, bot.user.id))

@bot.command()
@commands.has_any_role(*config.modroles)
@asyncio.coroutine
def load(extension_name: str):
    """
    [Moderator Only] - Load a specific extension.
    Extension list = ["osu", "update"]
    Usage !load [extension]
    """
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        yield from bot.say("```{}: {}\n```".format(type(e).__name__,str(e)))
        return
    yield from bot.say("{} loaded succesfully.".format(extension_name))

@bot.command()
@commands.has_any_role(*config.modroles)
@asyncio.coroutine
def unload(extension_name: str):
    """
    [Moderator Only] - Unload a specific extension.
    Extension list = ["osu", "update"]
    Usage: !unload [extension]
    """
    bot.unload_extension(extension_name)
    yield from bot.say("{} unloaded.".format(extension_name))

@bot.command()
@asyncio.coroutine
def update():
    """
    [Moderator Only] - Update the bot by pulling from the git repository.
    Usage: !update
    """
    yield from bot.say("I'm evolving! Woof!~")
    os.system('git pull')

@bot.command(pass_context=True)
@commands.has_any_role(*config.modroles)
@asyncio.coroutine
def restart():
    """
    [Moderator Only] - Restart the bot.
    Usage: !restart
    """
    yield from bot.say("Bye everyone! I'll be right back, woof~!")
    python = sys.executable
    os.execl(python, python, *sys.argv)

@bot.command(pass_context=True)
@asyncio.coroutine
def woof():
    """
    Makes bot go woof!
    """
    yield from bot.say("Woof!")

@bot.event
@asyncio.coroutine
def on_message(message):
    if message.channel.name == "arrival":
        u_index = message.content.find("osu.ppy.sh/u/")
        if u_index != -1:
            user_input=message.content[u_index + 13:]
            user_string = user_input.split()
            user_string = user_string[0].split('`')
            user_string = user_string[0].split(')')
            user_string = user_string[0].split(']')
            if not user_string[0].isdigit():
                yield from bot.send_message(message.channel, "Please use user-id links (ie: https://osu.ppy.sh/u/124493)")
            else:
                status = utility.add(message.author, user_string[0])
                if(status == 2):
                    yield from bot.send_message(message.channel, "%s successfully added to the database." % (message.author.display_name))
                    yield from bot.change_nickname(message.author, utility.displayupdate)
                    if utility.usercountry == "CH":
                        yield from bot.add_roles(message.author, (discord.utils.find(lambda r: r.name == 'Members', message.server.roles)))# searches for and assigns Members role
                    else:
                        yield from bot.add_roles(message.author, (discord.utils.find(lambda r: r.name == 'Visitor', message.server.roles)))
                        yield from bot.add_roles(message.author, (discord.utils.find(lambda r: r.name == 'Members', message.server.roles)))
                elif(status == 1):
                    yield from bot.send_message(message.channel, "%s's entry has been successfully updated." % (message.author.display_name))
                    yield from bot.change_nickname(message.author, utility.displayupdate)
                    if utility.usercountry == "CH":
                        yield from bot.add_roles(message.author, (discord.utils.find(lambda r: r.name == 'Members', message.server.roles)))# searches for and assigns Members role
                    else:
                        yield from bot.add_roles(message.author, (discord.utils.find(lambda r: r.name == 'Visitor', message.server.roles)))
                        yield from bot.add_roles(message.author, (discord.utils.find(lambda r: r.name == 'Members', message.server.roles)))
                else:
                    yield from bot.send_message(message.channel, "Error in adding user. Please ensure user is not already in the database.")
                    yield from bot.send_message(discord.utils.find(lambda c: c.name == 'team', message.server.channels), "User error in registering. Check #arrival")
    yield from bot.process_commands(message)

if __name__ == "__main__":
    for extension in startup:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Couldn\'t load extension {}\n{}: {}'.format(extension, type(e).__name__,e))
    
    bot.run(config.discordkey)
