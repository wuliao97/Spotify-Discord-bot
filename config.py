import os, json

with open(".\\config\\config.json") as f:
    CFG = json.load(f)


"""For bot"""
TOKEN = CFG["TOKEN"]

"""For Spotify"""
SP_ID    = CFG["SPOTIFY"]["CLIENT_ID"]
SP_SRC   = CFG["SPOTIFY"]["CLIENT_SECRET"]
SP_EMOJI = CFG["SPOTIFY"]["EMOJI"]
SP_JUMP_E= CFG["SPOTIFY"]["JUMP_EMOJI"]

"""For Verifing"""
ADMINS = CFG["ADMINS"]


"""Other"""
NOC = 0x2f3136
FAV = 0x6dc1d1
SPF = 0x1DB954
SPB = 191414
