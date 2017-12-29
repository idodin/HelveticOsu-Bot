#!/usr/bin/python3

import configparser


class Parser():
    def __init__(self):
        self.configfile = 'C:/Users/Imad/Documents/GitHub/HelveticOsu-Bot/config/config.ini'
        config = configparser.ConfigParser()
        config.read(self.configfile)
        self.osukey = config['API']['Key']
        self.discordkey = config['Discord']['Key']
        list = config['Discord']['Mod Roles'].split(",")
        for i in range (0,2):
            list[i] = list[i].lstrip()
        self.modroles = list
        self.db_path = config['DB']['Path']

