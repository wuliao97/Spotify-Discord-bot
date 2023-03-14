"""Config and Funcs"""
import config as cfg

import discord
from discord.ui import *
from discord.ext import commands
from discord_timestamps.formats import TimestampType

import datetime



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



class SpotifySelect(discord.ui.Select):
    def __init__(self, placeholder: str, options: list[discord.SelectOption], disabled: bool = False):
        super().__init__(placeholder=placeholder, options=options, disabled=disabled)

    async def callback(self, inter:discord.Interaction):
        song = self.values[0]
        await inter.response.send_message(song)


class SpotifySelectView(discord.ui.View):
    def __init__(self, placeholder, option, url,timeout: float = 180, disable_on_timeout: bool = True):
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.add_item(SpotifySelect(placeholder=placeholder, options=option))
        self.add_item(Button(label="URL", url=url, emoji=cfg.SP_EMOJI))



class SpotifyButtonS(discord.ui.View):
    def __init__(self, mode = "default", url = None | list):
        super().__init__()

        labels = []

        if mode == "default" and len(url) == 1:
            labels.extend(["Jump"])
            
        elif mode == "urls":
            labels.extend(["Song", "Album", "Artist"])
            
        for i, label in zip(url, labels):
            self.add_item(Button(label=label, url=i, emoji=cfg.SP_EMOJI))




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
        return (
            False, 
            discord.Embed(description=f"{user.mention} is not listening to Spotify!", color=cfg.SPFW), 
            None
        )


def data_sort(title:str, album:str) -> str:
    title = title.translate(str.maketrans({"[":"(", ")":")"}))
    title = title[:17] + "..." if len(title) > 17 else title
    album = album[:15] + "..." if len(album) > 15 else album

    return title, album



def spotify_extract(id)->list[str]:
    result = cfg.sp.track(id)
    
    song_url = result['external_urls']['spotify']
    album_url = result['album']['external_urls']['spotify']
    artist_url = result['artists'][0]['external_urls']['spotify']

    return [song_url, album_url, artist_url]



def sand_symbol(literal, symble="*", count = 1):
    return (symble * count) + str(literal) + (symble * count)

SS = sand_symbol



def time_func(PLACE:str = "JST"):
    data = datetime.datetime.now()
    data = datetime.datetime.astimezone(datetime.timezone(datetime.timedelta(hours=+9))) if PLACE =="JST" else datetime.datetime.utcnow()
    return data.timestamp()



def format_timestamp(timestamp,
    time_s_type:TimestampType = TimestampType.SHORT_TIME) -> str:
        
    if isinstance(timestamp, int):
        int_timestamp = timestamp
    elif isinstance(timestamp, float):
        int_timestamp = int(timestamp)

    return f'<t:{int_timestamp}{time_s_type.value}>'



def get_time(sec):
    td = datetime.timedelta(seconds=sec)
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    return td.days, h, m, s
