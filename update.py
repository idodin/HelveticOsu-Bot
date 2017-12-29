#!/usr/bin/env python3

import discord
from discord.ext import commands
import asyncio

from db import db_utilities
from config import parser

class Update():
    def __init__(self, bot):
        self.bot = bot
        self.parser = parser.Parser()
        self.utility = db_utilities.Db_Utilities(self.parser.db_path, self.parser.osukey)
        
    @commands.command(pass_context = True)
    @asyncio.coroutine
    def add(self, ctx):
        modroles = []
        for i in self.parser.modroles:
            modroles.append(discord.utils.find(lambda r: r.name == i, ctx.message.server.roles))
        if any(i in modroles for i in ctx.message.author.roles):
            try:
                status = self.utility.add(ctx.message.mentions[0])
                if(status == 2):
                    yield from self.bot.say("%s successfully added to the database." % (ctx.message.mentions[0].display_name))
                    yield from self.bot.change_nickname(ctx.message.mentions[0], self.utility.displayname)
                elif(status == 1):
                    yield from self.bot.say("%s's entry has been successfully updated." % (ctx.message.mentions[0].display_name))
                    yield from self.bot.change_nickname(ctx.message.mentions[0], self.utility.displayname)
                else:
                    yield from self.bot.say("Error in adding user. Please ensure user is not already in the database.")
            except IndexError:
                yield from self.bot.say("Error in adding user, ensure that you are mentioning the user.")
        else:
            yield from self.bot.say("You don't have sufficient priviledges to use this command.")
 
def setup(bot):
    bot.add_cog(Update(bot))

