#!/usr/bin/python3

import discord
import requests
from bs4 import BeautifulSoup



class Disc_Utilities():
    def __init__(self):
        self.gamemodes = {
            "0"     :       "osu!",
            "1"     :       "Taiko",
            "2"     :       "Catch the Beat",
            "3"     :       "osu!mania"
            }
        self.revgamemodes = {
            "osu"   :       "0",
            "taiko" :       "1",
            "ctb"   :       "2",
            "mania" :       "3"
            }
    def embedDict(self, embed: discord.embeds.Embed, dictionary: dict):
        for key in dictionary:
            if "PP" in key or "Performance Points" in key:
                embed.add_field(name=key, value="`%s`"%(dictionary[key]))
            else:
                embed.add_field(name=key, value=dictionary[key])
        return embed

    def embedAvatar(self, embed: discord.embeds.Embed, user_id: str):
        url = "https://osu.ppy.sh/u/%s" % (user_id)
        r=requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        r.close()

        img_html = soup.find("div", class_="avatar-holder")
        try:
            img_tag = img_html.contents[0]
            img_url="https:%s" %(img_tag["src"])
            embed.set_thumbnail(url=img_url)
        except:
            pass

        return embed

    
