#!/usr/bin/python3

import discord
from discord.ext import commands
import asyncio
import requests
from bs4 import BeautifulSoup

from src import disc_utilities
from config import parser

class Osu():
    """
    This extension contains commands that parse and display information from the osu API and website.
    """
    def __init__(self, bot):
        self.bot = bot
        self.config = parser.Parser()
        self.utility = disc_utilities.Disc_Utilities()

    @commands.command(pass_context = True)
    @commands.cooldown(1, 10)
    @asyncio.coroutine
    def user(self, ctx, *, arg1: str):
        """
        Display profile information for the specified user.
        Usage: !user Im so mad bro
        Displays information for the mode on which the user has the highest global rank.
        Usage !user [osu | taiko | mania | ctb] Im so mad bro
        Displays information for the mode specified. 
        """
        
        mode = arg1.split(" ")[0]
        modelist = ['osu', 'taiko', 'mania', 'ctb']

        #Check whether mode was specified. Note if a user's username starts with one of the gamemodes, errors will occur.
        if mode in modelist: 
            arg = arg1.split(" ")[1]
            for i in range (2,len(arg1.split(" "))):
                arg = arg + " " + arg1.split(" ")[i]
            arg1 = arg
            minindex = self.utility.revgamemodes[mode]

        #Does user exist?
        parameters = {"k": self.config.osukey, "u": arg1}
        response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
        if not response.json():
            user_info = discord.Embed(title="User info for %s" % (arg1), description = " ", color=0xC54B5E)
            user_info.add_field(name = "Error:", value = "`No user found by the name %s`" % (arg1))
            yield from self.bot.send_message(ctx.message.channel, embed=user_info)
            return
        
        list = []

        #Check which mode highest ranked - if no mode specified.
        if not mode in modelist:
            
            for mode in range(0,4):
                parameters = {"k": self.config.osukey, "u": arg1, "m": mode}
                response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
                data = response.json()[0]
                list.append(data["pp_rank"])
                
            minelement = int(list[0])
            minindex = 0
            
            for i in range (0,4):
                if int(list[i]) < minelement and int(list[i]) > 0:
                    minelement = int(list[i])
                    minindex = i
            
        parameters = {"k": self.config.osukey, "u": arg1, "m": minindex}
        response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
        data = response.json()[0]
        
        # get beatmap id and pp value for top play
        parameters = {"k": self.config.osukey, "u": data["user_id"], "m": minindex}
        userbest = requests.get("https://osu.ppy.sh/api/get_user_best", params=parameters)
        bestinfo = userbest.json()[0]
        
        # get artist, title, and creator of top play map
        parameters = {"k" : self.config.osukey, "b" : bestinfo["beatmap_id"]}
        bestscore = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameters)
        bestscore_info = bestscore.json()[0]
        embed_fields = {
            "Mode"  :   self.utility.gamemodes[str(minindex)],
            "Performance Points"    :   data["pp_raw"],
            "Accuracy"  :   data["accuracy"][0:5],
            "Top Rank"  :   "`%s - %s (mapped by %s) [%s pp]`" % (bestscore_info["artist"], bestscore_info["title"], bestscore_info["creator"], bestinfo["pp"][0:6])
            }
        user_info = discord.Embed(title='User info for %s' % (data["username"]), description='# %s (%s - # %s)' % (data["pp_rank"],data["country"], data["pp_country_rank"]), color=0xC54B5E)
        user_info = self.utility.embedDict(user_info, embed_fields)
        user_info = self.utility.embedAvatar(user_info, data["user_id"])
        
        yield from self.bot.send_message(ctx.message.channel, embed=user_info)
    
def setup(bot):
    bot.add_cog(Osu(bot))

