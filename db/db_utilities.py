import discord

import sqlite3

import requests
import json
import os, sys

class Db_Utilities():

    def __init__(self, db_path: str, osukey: str):
        self.db_path=db_path
        self.osukey = osukey
        self.displayupdate = None

    def add(self, member, osuID = None):
        # Checks if the user's discordID is already recorded
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if self.discordExists(member):
            #tries to update displayname
            displayupdate = self.updateDisplay(member)
            osuID = c.execute('SELECT OsuID FROM Members WHERE Username = ?', (member.display_name,)).fetchall()
            print(osuID[0][0])
            if(displayupdate):
                if(osuID) and self.displayClash(member, osuID[0][0]):
                    return 0
                self.displayupdate = displayupdate
                return  1
        #no osuID passed to function
        if osuID == None:
            clash = self.displayClash(member)
            response = requests.get("https://osu.ppy.sh/api/get_user", params={"k" : self.osukey, "u" : member.display_name})
            print(response.json())
            if not response.json():
                return -1
            data = response.json()[0]
            osuID = data["user_id"]
        else:
            clash = self.displayClash(member, osuID)
        if clash: 
            return 0
        c.execute('INSERT INTO Members (UserID, Username, OsuID) VALUES (?, ?, ?)', (member.id, member.display_name, osuID,))
        conn.commit()
        conn.close()
        self.displayupdate = self.updateDisplay(member)
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
    def displayClash(self, member = None, osuID = None):
        # Check whether to use name or id to search API (based on arguments passed).
        if osuID == None and member == None:
            return False
        elif osuID == None:
            name = member.display_name
        else:
            name = osuID
        parameters = {"k" : self.osukey, "u" : name}
        response = requests.get("https://osu.ppy.sh/api/get_user", params=parameters)
        #nothing returned, so user doesn't exist
        if not response.json():
            return False
        else:
            data=response.json()[0]
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        clashid = c.execute('SELECT UserID FROM Members WHERE OsuID = ?', (data["user_id"],)).fetchall()
        if clashid:
            if(str(clashid[0][0]) == member.id):
                print("id same")
                clashid = False
        clashname = c.execute('SELECT UserID FROM Members WHERE Username = ?', (data["username"],)).fetchall()
        if clashname:
            if(str(clashname[0][0]) == member.id):
                print("name same")
                clashname= False
        if clashid or clashname:
            return True
        else:
            return False
