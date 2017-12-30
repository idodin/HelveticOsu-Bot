#!/usr/bin/env python3

import discord
from discord.ext import commands
import asyncio

from db import db_utilities
from config import parser

config = parser.Parser()
modroles = config.modroles

class Update():
    def __init__(self, bot):
        self.bot = bot
        self.config = config
        self.utility = db_utilities.Db_Utilities(self.config.db_path, self.config.osukey)
        
    @commands.command(pass_context = True)
    @commands.has_any_role(*config.modroles)
    @asyncio.coroutine
    def add(self, ctx):
        try:
            status = self.utility.add(ctx.message.mentions[0])
            print(ctx.message.mentions[0].id)
            if(status == 2):
                yield from self.bot.say("%s successfully added to the database." % (ctx.message.mentions[0].display_name))
                yield from self.bot.change_nickname(ctx.message.mentions[0], self.utility.displayname)
            elif(status == 1):
                yield from self.bot.say("%s's entry has been successfully updated." % (ctx.message.mentions[0].display_name))
                yield from self.bot.change_nickname(ctx.message.mentions[0], self.utility.displayname)
            elif(status == -1):
                yield from self.bot.say("No osu user by the name %s and no OsuID on record for that discord user. Update username and try again." % (ctx.message.mentions[0].display_name))
            else:
                yield from self.bot.say("Error in adding user. Please ensure user is not already in the database.")
        except IndexError:
            yield from self.bot.say("Error in adding user, ensure that you are mentioning the user.")
 
def setup(bot):
    bot.add_cog(Update(bot))

