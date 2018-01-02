#!/usr/bin/env python3

import discord
from discord.ext import commands
import asyncio

import sqlite3

import time

from db import db_utilities
from config import parser

config = parser.Parser()
modroles = config.modroles

class Update():
    """
    This extension contains commands that update and moderate the user database.
    """
    def __init__(self, bot):
        self.bot = bot
        self.config = config
        self.utility = db_utilities.Db_Utilities(self.config.db_path, self.config.osukey)
        
    @commands.command(pass_context = True)
    @commands.has_any_role(*config.modroles)
    @asyncio.coroutine
    def add(self, ctx):
        """
        [Moderator Only] - Add the mentioned user to the user database. Does not assign roles.
        Usage: !add @mention
        """
        try:
            status = self.utility.add(ctx.message.mentions[0])
            if(status == 2):
                yield from self.bot.say("%s successfully added to the database." % (ctx.message.mentions[0].display_name))
                yield from self.bot.change_nickname(ctx.message.mentions[0], self.utility.displayupdate)
            elif(status == 1):
                yield from self.bot.say("%s's entry has been successfully updated." % (ctx.message.mentions[0].display_name))
                yield from self.bot.change_nickname(ctx.message.mentions[0], self.utility.displayupdate)
            elif(status == -1):
                yield from self.bot.say("No osu user by the name %s and no OsuID on record for that discord user. Update username and try again." % (ctx.message.mentions[0].display_name))
            else:
                yield from self.bot.say("Error in adding '%s'. Please ensure '%s' is not already in the database." % (ctx.message.mentions[0].display_name, ctx.message.mentions[0].display_name))
        except IndexError:
            yield from self.bot.say("Error in adding user, ensure that you are mentioning the user.")

    @commands.command(pass_context = True)
    @commands.has_any_role(*config.modroles)
    @asyncio.coroutine
    def addall(self, ctx):
        """
        [Moderator Only] - Parses the member list, adding members to the database.
        Danger! This command takes a long time to work and often needs to be executed multiple times.
        Only use in #developer
        Usage: !addall
        """

        for member in ctx.message.server.members:
            status = self.utility.add(member)
            if(status == 2):
                yield from self.bot.say("%s successfully added to the database." % (member.display_name))
                yield from self.bot.change_nickname(member, self.utility.displayupdate)
            elif(status == 1):
                yield from self.bot.say("%s's entry has been successfully updated." % (member.display_name))
                yield from self.bot.change_nickname(member, self.utility.displayupdate)
            elif(status == -1):
                yield from self.bot.say("No osu user by the name %s and no OsuID on record for that discord user. Update username and try again." % (member.display_name))
            else:
                yield from self.bot.say("Error in adding '%s'. Please ensure '%s' is not already in the database." % (member.display_name, member.display_name))
            time.sleep(5)

    @commands.command()
    @commands.has_any_role(*config.modroles)
    @asyncio.coroutine
    def delete(self, arg1: str):
        """
        [Moderator Only] - Deletes the record associated with the specified OsuID Number
        Usage: !del [osuid]
        """
        try:
            conn = sqlite3.connect(self.config.db_path)
            c = conn.cursor()
            deleted = c.execute('SELECT Username FROM Members WHERE OsuID = ?', (arg1,)).fetchall()
            conn.commit()
        except Exception:
            yield from self.bot.say("Error in finding record to delete.")

        if len(deleted) > 1:
            yield from self.bot.say("More than one record found! Grrrrr~")
        if len(deleted) == 0:
            yield from self.bot.say("No records found to delete!")
        else:
            c.execute('DELETE FROM Members WHERE OsuID = ?', (arg1,)).fetchall()
            conn.commit()
            conn.close()
            yield from self.bot.say("Successfully deleted record for %s!" % (deleted[0]))

    @commands.command()
    @commands.has_any_role(*config.modroles)
    @asyncio.coroutine
    def listdb(self):
        conn = sqlite3.connect(self.config.db_path)
        c = conn.cursor()
        db=c.execute('SELECT UserID, OsuID, Username FROM Members').fetchall()
        message = "```Member DB: \n ---------------------------------------------------\n         DiscordID       OsuID        Username\n ---------------------------------------------------\n"
        for i in range(len(db)):
            if len(message + "[%d] %s - %s - %s \n" %(i, db[i][0], db[i][1], db[i][2])) > 1996:
                message = message + "```"
                yield from self.bot.say(message)
                message = "```[%d] %s - %s - %s \n" %(i, db[i][0], db[i][1], db[i][2])
            else:
                message = message + "[%d] %s - %s - %s \n" %(i, db[i][0], db[i][1], db[i][2])
        message = message + "```"
        yield from self.bot.say(message)
        conn.close()
        
            
def setup(bot):
    bot.add_cog(Update(bot))

