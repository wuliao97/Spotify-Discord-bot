"""Config and Funcs"""
import config as cfg
import funcs as fcs

"""Libraries for Discord"""
import discord
from discord.ext import commands
from discord.commands import Option
from discord.ui import *

"""Usefull Other Libraries"""
from discord_timestamps.formats import TimestampType
import discord_timestamps as dts
from datetime import datetime as dt
import aiohttp, asyncio
import dateutil.parser, spotipy, json, time, os
from spotipy.oauth2 import SpotifyClientCredentials


bot = commands.Bot(
    intents=discord.Intents.all()
)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id = cfg.SP_ID, 
    client_secret = cfg.SP_SRC)
)


@bot.event
async def on_ready():
    print(dt.now().strftime(fcs.TimeFormat.DEFAULT), bot.user, "on ready")



@bot.user_command(name="account")
async def accountdetails(
    inter:discord.Interaction, 
    user :discord.Member):

    e = discord.Embed(color=cfg.SPB).set_author(icon_url = user.display_avatar, name=user)
    e.add_field(name = "Created Account", value = f"> {dts.format_timestamp(user.created_at.timestamp(), TimestampType.RELATIVE)}")
    e.add_field(name = "Joined Server",   value = f"> {dts.format_timestamp(user.joined_at.timestamp(),  TimestampType.RELATIVE)}")
    await inter.response.send_message(embed=e, ephemeral=True)



@bot.slash_command(name="about", description="About this bot")
async def about(inter:discord.Interaction):

    user = bot.get_user(1039780426564239431)
    embed= discord.Embed(
        title       = "About this bot", 
        description = "For All of Spotify Lover and My friends!", 
        color       = cfg.SPB)
    embed.add_field(name= "Users"  ,value= "> Servers: **%s**\n> Members: **%s**" % (len(bot.guilds), sum([guild.member_count - 1 for guild in bot.guilds])))
    embed.add_field(name= "Support",  value= f"> Deveroper: %s\n> Source: ~~[Github.com](%s)~~\n> Our server: ~~[gg./](%s)~~" % (user.mention, "https://github.com/Ennuilw/", "https://discord.gg/"))

    await inter.response.send_message(embed=embed)



@bot.slash_command(name="avatar", description="アイコンを取得")
async def send_user_avatar(
    inter:discord.Interaction,
    user :discord.Member = None):

    user = user if user else inter.user
    avatar = user.avatar.url

    e = discord.Embed(
        description = "%s's Avatar\n\n> **[URL](%s)**" % (user.mention, avatar),
        color       = cfg.FAV)

    if (avatar == (server_avatar:=user.display_avatar.url)):
        e.set_image(url = avatar)
    else:
        e.description += f"\n> **[Server URL]({server_avatar})**"
        e.set_image(url = server_avatar).set_thumbnail(url=avatar)
    await inter.response.send_message(embed=e)


@bot.slash_command(name="banner", description="ユーザープロフィールからバナーを取得。もしあれば。")
async def send_banner_user(
    inter:discord.Interaction,
    user :discord.Member = None):

    user = await bot.fetch_user(user.id if user else inter.user.id)
    if (user.banner):
        e = discord.Embed(
            description = f"{user.mention}'s Banner\n\n> [URL]({user.banner.url})", 
            color= cfg.FAV)
        e.set_image(url=user.banner.url)
        await inter.response.send_message(embed=e)
    else:
        await inter.response.send_message("%s haven't a Banner. Go away." % user.name, ephemeral=True)



@bot.slash_command(name="userinfo", description="ユーザー情報を送信")
async def send_user_info(
    inter:discord.Interaction,
    user :discord.Member = None):

    user = user if user else inter.user
    status = str(user.status)
    s_icon = "🟢" if status == "online" else "🟡" if status == "idle" else "🔴" if status == "dnd" else "⚫"
    
    embed = discord.Embed(
        description = "ID: **%s**\nStatus: **`%s %s`**" % (user.id, s_icon, status),
        color       = cfg.FAV
    ).set_footer(text="and other info: '/avatar', '/banner' | banner is User profile only!")
    embed.set_thumbnail(url = user.display_avatar)

    if (user.name == user.display_name):
        embed.add_field(name="Name",      value= f"> {user}")
        embed.add_field(name="Bot?",      value= f"> {'Yes' if user.bot else 'No'}")
    else:
        embed.add_field(name= "Name"    , value= f"> {user}")
        embed.add_field(name= "Nickname", value= f"> {user.display_name}")
    
    if len(user.roles) >= 1:
        new_role = ([r.mention for r in user.roles][1:])
        embed.add_field(
            name  = f"Roles [ {len(user.roles)-1} ]", 
            value = f"> {' '.join(new_role[::-1])}", 
            inline= False)

    embed.add_field(name="Created Account", value=f"> {dts.format_timestamp(user.created_at.timestamp(), TimestampType.RELATIVE)}")
    embed.add_field(name="Joined Server",   value=f"> {dts.format_timestamp(user.joined_at.timestamp() , TimestampType.RELATIVE)}")
    
    user_ = await bot.fetch_user(user.id)
    if (user_.banner.url):
        embed.set_image(url=user_.banner.url)

    await inter.response.send_message(embed=embed)


@bot.slash_command(name="serverinfo", description="Get info about server")
async def send_server_info(inter:discord.Interaction):
    guild = inter.guild
    req = await bot.http.request(discord.http.Route("GET", f"/guilds/{guild.id}"))
    tchannels, vchannels = len(guild.text_channels), len(guild.voice_channels)
    emojis, e_gif = len(guild.emojis), sum([1 for e in guild.emojis if e.animated])
        
    embed= discord.Embed(
        title = guild.name,
        color = cfg.NOC
    ).set_footer(text = "S = Static, A = Animated")

    embed.add_field(name = "Owner", value = guild.owner.mention)
    embed.add_field(name = "Server ID", value = guild.id)
    embed.add_field(name = "Createion", value =f"{dts.format_timestamp(guild.created_at.timestamp(), TimestampType.RELATIVE)}\n")

    embed.add_field(name = f"Members [{guild.member_count}]", 
        value= f"**{sum(1 for member in guild.members if not member.bot)}** User | **{sum(1 for member in guild.members if member.bot)}** Bot\n**{sum([1 for user in guild.members if user.status != discord.Status.offline])}** Online")
    
    embed.add_field(name= f"Channels [{tchannels + vchannels}]", 
            value= f"**{tchannels}** Text | **{vchannels}** Voice\n**{len(guild.categories)}** Category")
    
    embed.add_field(name = f"Emojis [{emojis}]", value= f"**{emojis - e_gif}** S | **{e_gif}** A\n**{sum(guild.stickers)}** Sticker")

    if (boosts:=guild.premium_subscription_count > 0):
        embed.add_field(name = "Boost", value= f"**{boosts}** Count\n**{guild.premium_tier}** Tier")
    embed.add_field(name = "Role", value= f"**{len(guild.roles)}** Count")
    
    if (guild.icon):
        embed.set_thumbnail(url = guild.icon.url)

    if vanity:=req["vanity_url_code"]:
        embed.description = f":link: **Vanity** `{vanity}`"

    await inter.response.send_message(embed=embed)



@bot.slash_command(name="spotify-track-url", description="Get the Spotify music URL from user activities")
async def spotify_cmd(
    inter   :discord.Interaction, 
    user    :discord.Member = None, 
    me_only :Option(bool, "Me only?", choices=[True, False]) = False
):
    flag, material, artists = fcs.spotify(inter, user)
    if (flag):
        await inter.response.send_message(
            content= material.track_url,
            ephemeral=me_only)
    else:
        await inter.response.send_message(embed=material, ephemeral=True)



@bot.slash_command(name="spotify-info", description="Get the Spotify music info from user activities")
async def spotify_cmd(
    inter   :discord.Interaction, 
    user    :discord.Member = None, 
    me_only :Option(bool, "Me only?", choices=[True, False]) = False
):
    flag, material, artists = fcs.spotify(inter, user)
    if (flag):
        e = discord.Embed(color=cfg.SPF).set_thumbnail(url=material.album_cover_url)
        e.add_field(name="Title", value=f"```{material.title}```").add_field(name="Time", value=f"```{dateutil.parser.parse(str(material.duration)).strftime('%M:%S')}```")
        e.add_field(name="Album", value=f"```{material.album}```", inline=False).add_field(name="Artist[s]", value=f"```{artists}```", inline=False)
        await inter.response.send_message(
            embed = e,
            view = fcs.SpotifyView(material, me_only),
            ephemeral=me_only)
    else:
        await inter.response.send_message(embed=material, ephemeral=True)



@bot.slash_command(name="spotify-songs-search", description="SpotifyAPIを用いて楽曲を検索")
async def spotify_songs_search(interaction:discord.Interaction, *, keyword, limit:Option(int, "Search song Limit | Default: 4 max: 20")=4):
    result = sp.search(q=keyword, limit=limit if 20 >= limit else 20)
    sp_list = []
    for track in result['tracks']['items']:
        song_url = track['external_urls']['spotify']
        song_title = track['name']
        if "[" and "]" in song_title:song_title = song_title.translate(str.maketrans({"[":"(", "[":")"}))
        if len(song_title) > 20:
            song_title = str(song_title[:15] + "... ")
        if len(track['album']['name']) > 15:repl_song_album = str(track['album']['name'][:15] + "...")
        else:repl_song_album=track['album']['name']
        sp_list.append(f"{cfg.SP_EMOJI} **[{song_title}]({song_url})** - **{track['artists'][0]['name']}** | {repl_song_album}")
    message = "\n\n".join(sp_list)

    keyword = __import__("urllib").parse.quote((str(keyword)))
    message += f"\n\n{cfg.SP_EMOJI} **[Jump to Spotify search engine](https://open.spotify.com/search/{keyword})**"
    await interaction.response.send_message(
        embed=discord.Embed(
            description= message, 
            color      = cfg.SPF
    ).set_footer(text="Layout: *Title* - *Artists* | Album"))


@bot.slash_command(name="spotify-song-search-new", description="Now coding...")
async def spotify_song_search_new(inter:discord.Interaction, *, keyword, limit:Option(int, "Use to limit song search | Default:4, Max: 10")=4):
    result = sp.search(q=keyword, limit=limit if 10 >= limit else 10)
    select_option:list = []
    for track in result['tracks']['items']:
        select_option.append(discord.SelectOption(
            label = track["name"],
            value = track['external_urls']['spotify'],
            description = track["album"]["name"] + " : " + track["artists"][0]["name"]
        ))
    await inter.response.send_message(view = fcs.SpotifySelectView(
        placeholder = "Choose the song",
        option      = select_option))




bot.run(cfg.TOKEN)