import discord

import sqlite3

import requests
import json
import os, sys

class Db_Utilities():

    def __init__(self, db_path: str, osukey: str):
        self.db_path=db_path
        self.osukey = osukey
        self.displayname = None

    def add(self, member, osuID = None):
        if self.discordExists(member):
            displayname = self.updateDisplay(member) 
            if(displayname):
                self.displayname = displayname
                return  1
        if osuID == None:
            clash = self.displayClash(member)
            response = requests.get("https://osu.ppy.sh/api/get_user", params={"k" : self.osukey, "u" : member.display_name})
            data = response.json()[0]
            osuID = data["user_id"]
        else:
            clash = self.displayClash(osuID, member)
        if clash:
            return 0
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO Members (UserID, Username, OsuID) VALUES (?, ?, ?)', (member.id, member.display_name, osuID,))
        conn.commit()
        conn.close()
        self.displayname = self.updateDisplay(member)
        return 2

    # Function checks if a member's discordID exists in the database
    def discordExists(self, member):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        print(member.id)
        discordlist = c.execute('SELECT Username FROM Members WHERE UserID = ?', (member.id,)).fetchall()
        conn.close()
        if not discordlist:
            return False
        else:
            return True
        
    # Function attempts to update a member's display name in the database
    # - you probably want to force update their discord display name too
    def updateDisplay(self, member):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        osuID = c.execute('SELECT OsuID FROM Members WHERE UserID = ?', (member.id,)).fetchall()
        # No osu!ID on record - can't update
        if not osuID:
            conn.close()
            return False
        parameters = {"k" : self.osukey, "u" : osuID}
        response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
        # osu!ID doesn't exist on server - can't update
        if not response.json():
            conn.close()
            return False
        else:
            data = response.json()[0]
        c.execute('UPDATE Members SET Username = ? WHERE UserID = ?', (data["username"], member.id,))
        conn.commit()
        conn.close()
        return data["username"]

    # Function checks if a user's display name or userID clashes with a current user's display name.
    def displayClash(self, osuID = None, member = None):
        if osuID == None and member == None:
            return False
        elif member == None:
            name = osuID
        else:
            name = member.display_name
        parameters = {"k" : self.osukey, "u" : name}
        response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
        if not response.json():
            return False
        else:
            data=response.json()[0]
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        clash = c.execute('SELECT OsuID FROM Members WHERE Username = ?', (data["username"],)).fetchall()
        if not clash:
            return True
        else:
            return False
