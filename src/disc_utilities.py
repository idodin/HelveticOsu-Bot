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
        self.modlist = {
            "1"     :       "EZ",
            "2"     :       "NV",
            "3"     :       "HD",
            "4"     :       "HR",
            "5"     :       "SD",
            "6"     :       "DT",
            "7"     :       "RX",
            "8"     :       "HT",
            "9"     :       "NC",
            "10"    :       "FL",
            "11"    :       "AP",
            "12"    :       "SO",
            "13"    :       "AP",
            "14"    :       "PF",
            "15"    :       "4K",
            "16"    :       "5K",
            "17"    :       "6K",
            "18"    :       "7K",
            "19"    :       "8K",
            "20"    :       "KM",
            "21"    :       "FI",
            "22"    :       "Random",
            "23"    :       "Last Mod",
            "24"    :       "9K",
            "25"    :       "10K",
            "26"    :       "1K",
            "27"    :       "3K",
            "28"    :       "2K"
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

    def getModList(self, bitenum):
        list = []
        if bitenum & 1:
            list.append("No Fail")
        for i in range (1, 22):
            if (bitenum>>i) & 1:
                list.append(self.modlist[str(i)])
                # Exceptions
                if i == 9:
                    list.remove("DT")
                elif i == 13:
                    list.remove("AP")
                elif i==2:
                    list.remove("NV")
            else:
                continue
        string = ""
        for i in range (len(list)):
            string += list[i]
        return string.rstrip(',')

                
            

    
