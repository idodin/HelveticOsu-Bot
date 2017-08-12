#!/usr/bin/env python3

# required for discord.py
import discord
from discord.ext import commands
import asyncio

# required for URL access, parsing and osu! API
import requests
from bs4 import BeautifulSoup
import json

# other utilities used
import re, os, sys, random, math, time

# update to osu api key
key = " "

bot = commands.Bot(command_prefix='!')

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as {0} ({1})'.format(bot.user.name, bot.user.id))

@bot.command(pass_context=True)
@asyncio.coroutine
def user(ctx, *, arg1: str):
    parameters = {"k": key, "u": arg1}
    # get username, country, country rank, total pp, playcount and ranked score
    response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
    data = response.json()[0]
    # get beatmap id and pp value for top play
    parameters = {"k": key, "u": data["user_id"]}
    userbest = requests.get("https://osu.ppy.sh/api/get_user_best", params=parameters)
    bestinfo = userbest.json()[0]
    # get artist, title, and creator of top play map
    parameters = {"k" : key, "b" : bestinfo["beatmap_id"]}
    bestscore = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameters)
    bestscore_info = bestscore.json()[0]

    # put to sleep so it doesn't double post
    # TO-DO: Change output to embed
    time.sleep(2)
    output_list = (data["username"], data["country"], data["pp_country_rank"], data["pp_raw"], data["accuracy"][0:5], data["playcount"], bestscore_info["artist"], bestscore_info["title"], bestscore_info["creator"], bestinfo["pp"])
    yield from bot.send_message(ctx.message.channel, "**User data for %s (%s #%s): \n**Performance Points: `%s` \nHit Accuracy: `%s%%` \nPlaycount: `%s` \nTop Score: `%s - %s (mapped by %s) [%s pp]`" % output_list)
    
bot.run(os.environ.get("DISCORD_TOKEN"))
