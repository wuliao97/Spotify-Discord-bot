"""Config and Funcs"""
import config as cfg

import discord
from discord.ui import *
from discord.commands import Option
from discord.ext import commands, tasks
import discord_timestamps as dts
from discord_timestamps.formats import TimestampType
import os, re, io, sys,json
import spotipy, logging, requests, datetime, asyncio
import datetime as dt
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont



"""Userfull Timeformat for strftime"""
class TimeFormat:
    DEFAULT = "%Y/%m/%d (%a) %H:%M:%S" #2023/01/01 (Sun) 01:00:00
    ONE     = "%Y/%m/%d (%a) %H:%M"    #2023/01/01 (Sun) 01:00
    TWO     = "%Y/%m/%d %H:%M:%S"      #2023/01/01 01:00:00
    THREE   = "%Y/%m/%d %H:%M"         #2023/01/01 01:00

    FOUR    = "%m/%d (%a) %H:%M:%S"    #01/01 (Sun) 01:00:00
    FIVE    = "%m/%d (%a) %H:%M"       #01/01 (Sun) 01:00 
    SIX     = "%m/%d %H:%M:%S"         #01/01 01:00:00
    SEVEN   = "%m/%d %H:%M"            #01/01 01:00

    EIGHT   = "%H:%M:%S"               #01:00:00
    NINE    = "%H:%M"                  #01:00



"""For Spotify, send a Song URL"""
class SpotifyView(discord.ui.View):
    def __init__(self, spotify, ephemeral:bool):
        super().__init__()
        self.sp = spotify
        self.ephemeral = ephemeral

    @discord.ui.button(label="URL", style=discord.ButtonStyle.green, emoji=cfg.SP_EMOJI)
    async def callback(self, button:discord.Button, interaction:discord.Interaction):
        button.disabled=True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(self.sp.track_url, ephemeral=self.ephemeral)



class SpotifySelect(discord.ui.Select):
    def __init__(self, placeholder: str, options: list[discord.SelectOption], disabled: bool = False, max_values=None):
        super().__init__(placeholder=placeholder, options=options, disabled=disabled, max_values=max_values)

    async def callback(self, inter:discord.Interaction):
        song = self.values
        self.disabled = True
        msg = await inter.response.send_message(song)




class SpotifySelectView(discord.ui.View):
    def __init__(self, placeholder, option, max, timeout: float = 180, disable_on_timeout: bool = True):
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.add_item(SpotifySelect(placeholder=placeholder, options=option, max_values=max))



def is_dev():
    def checking(inter:discord.Interaction | commands.context.Context):
        return int(inter.author.id) in cfg.ADMINS
    return commands.check(checking)



def spotify(interact:discord.Interaction, user:discord.Member):
    user = user if user else interact.user

    if material:= next((activity for activity in user.activities if isinstance(activity, discord.Spotify)), None):

        artists = material.artists
        artists = ", ".join(artists) if isinstance(artists, list) else material.artist
        artists = str(artists).translate(str.maketrans({"[":"", "]":"", "'":""}))

        return True, material, artists
    else:
        return False, discord.Embed(description=f"{user.mention} is not listening to Spotify!", color=cfg.SPF), None



def sand_symbol(literal, symble="*", count = 1):
    return (symble * count) + str(literal) + (symble * count)

SS = sand_symbol

def time_func(PLACE:str = "JST"):
    data = dt.datetime.now()
    data = dt.datetime.astimezone(dt.timezone(dt.timedelta(hours=+9))) if PLACE =="JST" else dt.datetime.utcnow()
    return data.timestamp()



def format_timestamp(timestamp,
    time_s_type:TimestampType = TimestampType.SHORT_TIME,
) -> str:

    if isinstance(timestamp, int):
        int_timestamp = timestamp
    elif isinstance(timestamp, float):
        int_timestamp = int(timestamp)

    return f'<t:{int_timestamp}{time_s_type.value}>'