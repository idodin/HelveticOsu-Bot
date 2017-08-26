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
key = ""

bot = commands.Bot(command_prefix='!')

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as {0} ({1})'.format(bot.user.name, bot.user.id))
    
@bot.command(pass_context=True)
@asyncio.coroutine
def hi(ctx):
    yield from bot.send_message(ctx.message.channel, "wassup fam")
    
@bot.event
@asyncio.coroutine
def on_message(message):
    content = message.content
    s_index = content.find("osu.ppy.sh/s/")
    b_index = content.find("osu.ppy.sh/b/")
    if s_index == -1 and b_index == -1:
        yield from bot.process_commands(message)
        return
    
    # get beatmap id off of s formatted links
    elif s_index != -1 and b_index == -1:
        # grabs beatmapset_id from link, link length = 13
        beatmapset_id = content[s_index+13:]
        print(beatmapset_id)
        parameters = {"k": key, "s": beatmapset_id}
        response = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameters)
        print(response.json())
        data = response.json()[0]
        output_list = (data["artist"], data["title"], data["creator"], data["difficultyrating"][0:3])
        # TO-DO: Change output to embed
        yield from bot.send_message(message.channel, "%s - %s - %s - %s" % output_list)
        
    # get beatmap id off of b formatted links    
    elif s_index == -1 and b_index !=-1:
        beatmap_id = content[b_index+13:b_index+19]
        print(beatmap_id)
        parameters = {"k": key, "b": beatmap_id}
        response = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameters)
        print("JSON")
        print(response.json())
        data = response.json()[0]
        output_list = (data["artist"], data["title"], data["creator"], data["difficultyrating"][0:3])
        yield from bot.send_message(message.channel, "%s - %s - %s - %s" % output_list)
    yield from bot.process_commands(message)

@bot.command(pass_context=True)
@asyncio.coroutine
def restart(ctx):
    yield from bot.send_message(ctx.message.channel, "Ciao doods brb")
    python = sys.executable
    os.execl(python, python, *sys.argv)
        
@bot.command(pass_context=True)
@asyncio.coroutine
@commands.cooldown(1, 10)
def user(ctx, *, arg1: str):
    parameters = {"k": key, "u": arg1}
    print("%s attempted to execute %s on %s" %(ctx.message.author, ctx.command, time.ctime()))
    # get username, country, country rank, total pp, playcount and ranked score
    response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
    
    # json empty if user not found...
    if not response.json():
        user_info = discord.Embed(title="User info for %s" % (arg1) , description = " ", color=0xC54B5E)
        user_info.add_field(name = "Error:", value = "`No user found by the name %s`" % (arg1))
        print("CommandError: No User Found")
        yield from bot.send_message(ctx.message.channel, embed=user_info)
    else:
        data = response.json()[0]
        # get beatmap id and pp value for top play
        parameters = {"k": key, "u": data["user_id"]}
        userbest = requests.get("https://osu.ppy.sh/api/get_user_best", params=parameters)
        bestinfo = userbest.json()[0]
        # get artist, title, and creator of top play map
        parameters = {"k" : key, "b" : bestinfo["beatmap_id"]}
        bestscore = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameters)
        bestscore_info = bestscore.json()[0]
        
        url = "https://osu.ppy.sh/u/%s" % (data["user_id"])
        r=requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        r.close()
        # parse avatar image url
        img_html = soup.find("div", class_="avatar-holder") #finds avatar-holder class
        img_tag = img_html.contents[0] #gets 1st element from avatar-holder class array (img tag)
        img_url="https:%s" %(img_tag["src"]) #get src argument from img tag
        
        top_score="`%s - %s (mapped by %s) [%s pp]`" % (bestscore_info["artist"], bestscore_info["title"], bestscore_info["creator"], bestinfo["pp"][0:3])
        user_info = discord.Embed(title='User info for %s' % (data["username"]), description='# %s (%s - # %s)' % (data["pp_rank"],data["country"], data["pp_country_rank"]), color=0xC54B5E)
        user_info.set_thumbnail(url=img_url)
        user_info.add_field(name="Performance Points", value="`%s`"%(data["pp_raw"]))
        user_info.add_field(name="Accuracy", value="`%s`"%(data["accuracy"][0:5]))
        user_info.add_field(name="Top Rank", value=top_score)
        yield from bot.send_message(ctx.message.channel, embed=user_info)
        print("Command Success")
        
bot.run(os.environ.get("DISCORD_TOKEN"))
