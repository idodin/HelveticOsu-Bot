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

# for DB
import sqlite3

# update to osu api key
KEY = ""

# update to database path
DB_PATH = "./Members.db"

bot = commands.Bot(command_prefix='!')

mode_list = {
    "0"     :       "osu!",
    "1"     :       "Taiko",
    "2"     :       "Catch the Beat",
    "3"     :       "osu!mania"
    }

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as {0} ({1})'.format(bot.user.name, bot.user.id))

@bot.command(pass_context=True)
@asyncio.coroutine
def add(ctx, arg1: str, arg2: str):
    modrole = discord.utils.find(lambda r: r.name == 'Mods', ctx.message.server.roles)
    if modrole in ctx.message.author.roles:
        parameters = {"k" : KEY, "u" : arg2}
        response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
        if not response.json():
            yield from bot.send_message(ctx.message.channel, "Please ensure that you have used the command in the following syntax: \n `!add @user [osu user id]`")
        else:
            data = response.json()[0]
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            osumembers = c.execute('SELECT Username FROM Members WHERE OsuID = ?', (data["user_id"],)).fetchall()
            discordmembers = c.execute('SELECT Username FROM Members WHERE UserID = ?', (ctx.message.mentions[0].id,)).fetchall()
            if not osumembers and not discordmembers:
                if ctx.message.mentions[0].display_name != data["username"]:
                    yield from bot.change_nickname(ctx.message.author, data["username"])
                c.execute('INSERT INTO Members (UserID, Username, OsuID) VALUES (?, ?, ?)', (ctx.message.mentions[0].id, data["username"], data["user_id"]))
                conn.commit()
                conn.close()
                yield from bot.send_message(ctx.message.channel, "Entry created for `%s`." % (ctx.message.mentions[0].display_name))
            else:
                conn.close()
                yield from bot.send_message(ctx.message.channel, "User already found in database. If username is not updated in database, please use the `!update` command.")
    else:
        yield from bot.send_message(ctx.message.channel, "You do not have sufficient priviledges to execute this command.")

@bot.command(pass_context=True)
@asyncio.coroutine
def qadd(ctx, arg1: str):
    modrole = discord.utils.find(lambda r: r.name == 'Mods', ctx.message.server.roles)
    if modrole in ctx.message.author.roles:
        parameters = {"k": KEY, "u": ctx.message.mentions[0].display_name}
        response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
        if not response.json():
            yield from bot.send_message(ctx.message.channel, "No osu! user with the name `%s`." % (ctx.message.mentions[0].display_name))
        else:
            data = response.json()[0]
            conn =sqlite3.connect(DB_PATH)
            c = conn.cursor()
            osumembers = c.execute('SELECT Username FROM Members WHERE OsuID = ?', (data["user_id"],)).fetchall()
            discordmembers = c.execute('SELECT Username FROM Members where UserID = ?', (ctx.message.mentions[0].id,)).fetchall()
            if not osumembers and not discordmembers:
                c.execute('INSERT INTO Members (UserID, Username, OsuID) VALUES (?, ?, ?)', (ctx.message.mentions[0].id, data["username"], data["user_id"]))
                conn.commit()
                conn.close()
                yield from bot.send_message(ctx.message.channel, "Entry created for `%s`." % (ctx.message.mentions[0].display_name))
            else:
                yield from bot.send_message(ctx.message.channel, "Entry already found for the requested osu! profile or discord ID.")
    else:
        yield from bot.send_message(ctx.message.channel, "You do not have sufficient priviledges to execute this command.")

@bot.command(pass_context=True)
@asyncio.coroutine
def getchannel(ctx):
    print(ctx.message.channel.name)
    print(ctx.message.channel.name=="arrival")

@bot.command(pass_context=True)
@asyncio.coroutine
def getroles(ctx):
    member_role = discord.utils.find(lambda r: r.name == 'Members', ctx.message.server.roles)
    print(member_role.name)
    print(member_role.id)
    
@bot.command(pass_context=True)
@asyncio.coroutine
def hi(ctx):
    yield from bot.send_message(ctx.message.channel, "wassup fam")
    
@bot.event
@asyncio.coroutine
def on_message(message):
    # TO-DO: add dicts for game mode and approval status
    content = message.content
    s_index = content.find("osu.ppy.sh/s/")
    b_index = content.find("osu.ppy.sh/b/")
    u_index = content.find("osu.ppy.sh/u/")
    if message.channel.name != "arrival":
        if s_index == -1 and b_index == -1 and u_index == -1:
            yield from bot.process_commands(message)
            return
        
        # get beatmap id off of s formatted links
        elif s_index != -1 and b_index == -1 and u_index == -1:
            
            # grabs beatmapset_id from link, link length = 13
            beatmapset_id = content[s_index+13:]
            parameters = {"k": KEY, "s": beatmapset_id}
            response = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameters)
            data = response.json()[0]

            # parse beatmap thumbnail img url
            url = "https://osu.ppy.sh/s/%s" % (beatmapset_id)
            r=requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            r.close()
            img_tag = soup.find("img", class_="bmt") #finds img tag with bmt class
            img_url="https:%s" %(img_tag["src"]) #get src argument from img tag
            
            beatmap_info=discord.Embed(title="Beatmap Info for:", description="**%s - %s (mapped by %s)**" % (data["artist"], data["title"], data["creator"]), color=0xC54B5E)
            beatmap_info.set_thumbnail(url=img_url)
            beatmap_info.add_field(name="Difficulty Name", value="`%s`" % (data["version"]), inline=True)
            beatmap_info.add_field(name="Star Rating", value="`%s`"%(data["difficultyrating"][0:3]), inline=True)
            beatmap_info.add_field(name="BPM", value="`%s`"%(data["bpm"]), inline=True)
            beatmap_info.add_field(name="Circle Size", value="`%s`" % (data["diff_size"]), inline=True)
            beatmap_info.add_field(name="Overall Difficulty", value="`%s`" %(data["diff_overall"]), inline=True)
            beatmap_info.add_field(name="Approach Rate", value="`%s`" % (data["diff_approach"]), inline=True)
            beatmap_info.add_field(name="HP Drain", value="`%s`" % (data["diff_drain"]), inline=True)
            beatmap_info.add_field(name="Drain Time", value="`%s`" % (data["hit_length"]), inline=True)
            
            yield from bot.send_message(message.channel, embed=beatmap_info)
            
        # get beatmap id off of b formatted links    
        elif s_index == -1 and b_index !=-1 and u_index == -1:
            beatmap_id = content[b_index+13:b_index+19]
            parameters = {"k": KEY, "b": beatmap_id}
            response = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameters)
            data = response.json()[0]

            url = "https://osu.ppy.sh/b/%s" % (beatmap_id)
            r=requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            r.close()
            img_tag = soup.find("img", class_="bmt") #finds img tag with bmt class
            img_url="https:%s" % (img_tag["src"]) #get src argument from img tag
            
            beatmap_info=discord.Embed(title="Beatmap Info for:", description="**%s - %s (mapped by %s)**" % (data["artist"], data["title"], data["creator"]), color=0xC54B5E)
            beatmap_info.set_thumbnail(url=img_url)
            beatmap_info.add_field(name="Difficulty Name", value="`%s`" % (data["version"]), inline=True)
            beatmap_info.add_field(name="Star Rating", value="`%s`"%(data["difficultyrating"][0:3]), inline=True)
            beatmap_info.add_field(name="BPM", value="`%s`"%(data["bpm"]), inline=True)
            beatmap_info.add_field(name="Circle Size", value="`%s`" % (data["diff_size"]), inline=True)
            beatmap_info.add_field(name="Overall Difficulty", value="`%s`" %(data["diff_overall"]), inline=True)
            beatmap_info.add_field(name="Approach Rate", value="`%s`" % (data["diff_approach"]), inline=True)
            beatmap_info.add_field(name="HP Drain", value="`%s`" % (data["diff_drain"]), inline=True)
            beatmap_info.add_field(name="Drain Time", value="`%s`" % (data["hit_length"]), inline=True)
            
            yield from bot.send_message(message.channel, embed=beatmap_info)
        yield from bot.process_commands(message)
    # only in arrival channel
    else:
        if u_index != -1 and message.author.id != bot.user.id:
            print(u_index)
            user_input = content[u_index+13:]
            # strip usual characters that follow user link
            user_string = user_input.split()
            user_string = user_string[0].split('`')
            user_string = user_string[0].split(')')
            user_string = user_string[0].split(']')
            print(user_string[0])
            # check link for user-id format
            if not user_string[0].isdigit():
                yield from bot.send_message(message.channel, "Please use user-id links (ie: https://osu.ppy.sh/u/124493)")
                return
            else:
                # get user info from osu api
                parameters = {"k": KEY, "u": user_string[0]}
                response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters, verify=False)
                # not found
                if not response.json():
                    yield from bot.send_message(message.channel, "Error: the user id `%s` does not exist" % (user_string[0]))
                else:
                    data = response.json()[0]
                    username = data["username"]
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    if not c.execute('SELECT * FROM Members where UserID=?', (message.author.id,)).fetchall() and not c.execute('SELECT * FROM Members where OsuID=?', (data["user_id"],)).fetchall():
                        if message.author.name != username:
                            yield from bot.change_nickname(message.author, username)
                        c.execute('INSERT INTO Members (UserID, Username, OsuID) VALUES (?, ?, ?)', (message.author.id, message.author.name, data["user_id"]))
                        conn.commit()
                        conn.close()
                        yield from bot.add_roles(message.author, (discord.utils.find(lambda r: r.name == 'Members', message.server.roles)))# searches for and assigns Members role
                    else:
                        yield from bot.send_message(message.channel, "Either osu! profile or discord profile has already been registered. Please wait to be manually verified by a moderator.")
                        yield from bot.send_message(discord.utils.find(lambda c: c.name == 'team', message.server.channels), "User error in registering. Check #arrival") # searches for and sends toteams channel
            yield from bot.process_commands(message)
        else:
            yield from bot.process_commands(message)
    yield from bot.process_commands(message)  

@bot.command(pass_context=True)
@asyncio.coroutine
def restart(ctx):
    yield from bot.send_message(ctx.message.channel, "Ciao doods brb")
    python = sys.executable
    os.execl(python, python, *sys.argv)
    yield from bot.send_message(ctx.message.channel, "I'm back boiss")

@bot.command(pass_context=True)
@asyncio.coroutine
def sw(ctx):
    yield from bot.send_message(ctx.message.channel, "This is why Zhuriel doesn't do software...")
    yield from bot.delete_message(ctx.message)

#TO-DO see if "gateway" method works better (ie. subsequent, non-nested if statements)
@bot.command(pass_context=True)
@asyncio.coroutine
def update(ctx, arg1: str):
    modrole = discord.utils.find(lambda r: r.name == 'Mods', ctx.message.server.roles)
    print(modrole)
    #checks if executor is mod
    if modrole in ctx.message.author.roles:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        print('Checking for entry')
        if not ctx.message.mentions:
            yield from bot.send_message(ctx.message.channel, "Please ensure that you are mentioning the user you are trying to update the database entry for: \n `!update @user`")
            return
        username = c.execute('SELECT Username FROM Members where UserID=?', (ctx.message.mentions[0].id,)).fetchall()
        conn.commit()
        conn.close()
        #no userid entry in database
        if not username:
            yield from bot.send_message(ctx.message.channel, "No entry found for `%s`. Please use !add command." % (ctx.message.mentions[0].display_name))
        # userid entry in database
        else:
            print("Entry found for %s" % (ctx.message.mentions[0].display_name))
            conn=sqlite3.connect(DB_PATH)
            c=conn.cursor()
            osu_id = c.execute('SELECT OsuID FROM Members where UserID=?', (ctx.message.mentions[0].id,)).fetchall()
            conn.commit()
            parameters = {"k": KEY, "u": osu_id[0][0]}
            response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
            print(response.json())
            data = response.json()[0]
            # osu username matches display name
            if data["username"] == ctx.message.mentions[0].display_name:
                print("osu! username = display name")
                # database username != osu username
                if username[0][0] != data["username"]:
                    c.execute('UPDATE Members SET Username = ? WHERE UserID = ?', (data["username"], ctx.message.mentions[0].id))
                    conn.commit()
                    print("Entry updated")
                    yield from bot.send_message(ctx.message.channel, "Entry updated for `%s`." % (ctx.message.mentions[0].display_name))
                    conn.close()
                else:
                    yield from bot.send_message(ctx.message.channel, "The user `%s's` information is already up to date." % (ctx.message.mentions[0].display_name))
                    conn.close()
            # osu username doesn't match display name   
            elif data["username"] != ctx.message.mentions[0].display_name:
                oldname = ctx.message.mentions[0].display_name
                print("osu! username != displayname")
                yield from bot.change_nickname(ctx.message.mentions[0], data["username"])
                # odatabase username != osu username
                if username[0][0] != data["username"]:
                    c.execute('UPDATE Members SET Username = ? WHERE UserID = ?', (data["username"], ctx.message.mentions[0].id))
                    conn.commit()
                    print("Entry updated")
                    conn.close()
                    yield from bot.send_message(ctx.message.channel, "Entry and display name updated for `%s`." % (oldname))
                elif username[0][0] == data["username"]:
                    yield from bot.send_message(ctx.message.channel, "The user `%s's` display name has been changed to `%s`." % (oldname, ctx.message.mentions[0].display_name))
    else:
        yield from bot.send_message(ctx.message.channel, "You do not have sufficient priviledges to execute this command.")

#TO-DO see if "gateway" method works better (ie. subsequent, non-nested if statements)
@bot.command(pass_context=True)
@asyncio.coroutine
def updateall(ctx):
    print("command received")
    modrole = discord.utils.find(lambda r: r.name == 'Mods', ctx.message.server.roles)
    print(modrole)
    #checks if executor is mod
    if modrole in ctx.message.author.roles:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for member in ctx.message.server.members:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            print("Member Username is: %s \n Member ID is: %s" % (member.display_name, member.id))
            username = c.execute('SELECT Username FROM Members where UserID=?', (member.id,)).fetchall()
            conn.commit()
            conn.close()
            #no userid entry in database
            if not username:
                yield from bot.send_message(ctx.message.channel, "No entry found for `%s`. Please use !add command." % (member.display_name))
            # userid entry in database
            else:
                print("Entry found for %s" % (member.display_name))
                conn=sqlite3.connect(DB_PATH)
                c=conn.cursor()
                osu_id = c.execute('SELECT OsuID FROM Members where UserID=?', (member.id,)).fetchall()
                conn.commit()
                parameters = {"k": KEY, "u": osu_id[0][0]}
                response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters, verify=False)
                print(response.json())
                data = response.json()[0]
                # osu username matches display name
                if data["username"] == member.display_name:
                    print("osu! username = display name")
                    # database username != osu username
                    if username[0][0] != data["username"]:
                        c.execute('UPDATE Members SET Username = ? WHERE UserID = ?', (data["username"], member.id))
                        conn.commit()
                        print("Entry updated")
                        yield from bot.send_message(ctx.message.channel, "Entry updated for `%s`." % (member.display_name))
                        conn.close()
                    else:
                        yield from bot.send_message(ctx.message.channel, "The user `%s's` information is already up to date." % (member.display_name))
                        conn.close()
                # osu username doesn't match display name   
                elif data["username"] != member.display_name:
                    oldname = member.display_name
                    print("osu! username != displayname")
                    yield from bot.change_nickname(member, data["username"])
                    # odatabase username != osu username
                    if username[0][0] != data["username"]:
                        c.execute('UPDATE Members SET Username = ? WHERE UserID = ?', (data["username"], member.id))
                        conn.commit()
                        print("Entry updated")
                        conn.close()
                        yield from bot.send_message(ctx.message.channel, "Entry and display name updated for `%s`." % (oldname))
                    elif username[0][0] == data["username"]:
                        yield from bot.send_message(ctx.message.channel, "The user `%s's` display name has been changed to `%s`." % (oldname, member.display_name))
    else:
        yield from bot.send_message(ctx.message.channel, "You do not have sufficient priviledges to execute this command.")
            
            
@bot.command(pass_context=True)
@asyncio.coroutine
@commands.cooldown(1, 10)
def user(ctx, *, arg1: str):
    print("%s attempted to execute %s on %s" %(ctx.message.author, ctx.command, time.ctime()))
    list = []
    i = 0
    for key in range(0,4):
        parameters = {"k": KEY, "u": arg1, "m": key}
        response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
        if not response.json():
            user_info = discord.Embed(title="User info for %s" % (arg1) , description = " ", color=0xC54B5E)
            user_info.add_field(name = "Error:", value = "`No user found by the name %s`" % (arg1))
            print("CommandError: No User Found")
            yield from bot.send_message(ctx.message.channel, embed=user_info)
            return
        else:
            data = response.json()[0]
            list.append(data["pp_rank"])
            i += 1
    print(list)
    minelement = int(list[0])
    minindex = 0
    for i in range (0,4):
        if int(list[i]) < minelement:
            print("yes" + str(i))
            minelement = int(list[i])
            minindex = i
            continue
        else:
            continue
        
    print('minindex = ' + str(minindex))
    parameters = {"k": KEY, "u": arg1, "m": minindex}
    response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
    data = response.json()[0]
    # get beatmap id and pp value for top play
    parameters = {"k": KEY, "u": data["user_id"], "m": minindex}
    userbest = requests.get("https://osu.ppy.sh/api/get_user_best", params=parameters)
    bestinfo = userbest.json()[0]
    # get artist, title, and creator of top play map
    parameters = {"k" : KEY, "b" : bestinfo["beatmap_id"]}
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
    user_info.add_field(name="Mode", value="%s"%(mode_list[str(minindex)]))
    user_info.add_field(name="Performance Points", value="`%s`"%(data["pp_raw"]))
    user_info.add_field(name="Accuracy", value="`%s`"%(data["accuracy"][0:5]))
    user_info.add_field(name="Top Rank", value=top_score)
    yield from bot.send_message(ctx.message.channel, embed=user_info)
    print("Command Success")
        
bot.run(os.environ.get("DISCORD_TOKEN"))
