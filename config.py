import os, json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


with open(f".{os.sep}config{os.sep}config.json") as f:
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
NOC  = 0x2f3136
FAV  = 0x6dc1d1
FAV2 = 191414

SPFW = 0x1DB954
SPFB = 0x191414


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id     = SP_ID, 
    client_secret = SP_SRC)
)
