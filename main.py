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
import datetime
import platform as pl
import aiohttp, asyncio
import dateutil.parser, spotipy, json, time, sys, os
from spotipy.oauth2 import SpotifyClientCredentials


bot = commands.Bot(
    command_prefix = "s.",
    intents        = discord.Intents.all()
)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id = cfg.SP_ID, 
    client_secret = cfg.SP_SRC)
)


@bot.event
async def on_ready():
    global _s_time
    _s_time = time.time()
    print(dt.now().strftime(fcs.TimeFormat.DEFAULT), bot.user, "on ready")


@bot.command(name="reboot", description="only admin")
async def exit_(inter):
    if not int(inter.author.id) in cfg.ADMINS:
        return await inter.send("You are NOT admin. You can't use this.", ephemeral=True)    
    
    _e_time = time.time() - _s_time
    
    d, h, m, s = fcs.get_time(_e_time)

    e = discord.Embed(
        title = "System reboot soon",
        color = cfg.SPFB
    )

    
    e.add_field(
        name  = "Operating time",
        value = f"**{d}** Days **{h}:{m}:{s}**",
        inline=False)

    with open("reboot.py", "w") as f:
        f.write("import os\n")
        f.write("os.system('nohup python main.py')")

    e.add_field(name  = "Successful created FILE",
                value = f"{f'{os.sep}'.join((f'{os.getcwd()}{os.sep}reboot.py').split(os.sep)[-2:])}")

    await inter.send(embed=e)
    os.system("python reboot.py")
    sys.exit()


@bot.command(name="exit", description="only admin")
async def exit_(inter):
    if not int(inter.author.id) in cfg.ADMINS:
        return await inter.send("You are NOT admin. You can't use this.", ephemeral=True)    
    
    _e_time = time.time() - _s_time
    t_data = datetime.timedelta(seconds=_e_time)
    
    e = discord.Embed(
        title = "System exit soon",
        color = cfg.SPFB
    )
    
    d, h, m, s = fcs.get_time(time.time() - _s_time)

    e.add_field(
        name  = "Operating time",
        value = f"**{d}** Days **{h}:{m}:{s}**",
        inline=False)

    await inter.send(embed=e)
    sys.exit()


@commands.guild_only()
@bot.user_command(name="account")
async def accountdetails(inter:discord.Interaction, user:discord.Member):
    e = discord.Embed(color=cfg.SPFB).set_author(icon_url = user.display_avatar, name=user)
    e.add_field(
        name = "Created Account", 
        value = f"> {dts.format_timestamp(user.created_at.timestamp(), TimestampType.RELATIVE)}")
    
    e.add_field(
        name = "Joined Server",   
        value = f"> {dts.format_timestamp(user.joined_at.timestamp(),  TimestampType.RELATIVE)}")
    
    await inter.response.send_message(embed = e, ephemeral=True)



@bot.slash_command(name="about", description="About this bot")
async def about(inter:discord.Interaction):
    user = bot.get_user(1039780426564239431)
    embed= discord.Embed(
        title       = "About this bot", 
        description = "For All of Spotify Lover and My friends!", 
        color       = cfg.SPFB)
    
    embed.add_field(
        name= "Users"  , 
        value= "> Servers: **%s**\n> Members: **%s**" % (
            len(bot.guilds), 
            sum([guild.member_count - 1 for guild in bot.guilds])))
    
    u = pl.uname()

    plat =  f"> OS: **{(u.system)}** (*{u.release}*)\n"
    plat += f"> Lang: **Python** (*{pl.python_version()}*)"

    embed.add_field(
        name  = "PlatForm",
        value = plat
    )

    embed.add_field(
        name= "Support", 
        value= f"> Deveroper: %s\n> Source: [Github.com](%s)\n> Our server: ~~[gg./](%s)~~" %(
            user.mention, 
           "https://github.com/wuliao97/Spotify-Discord-bot", 
           "https://discord.gg/"))

    await inter.response.send_message(embed = embed)



@bot.slash_command(name="status", description="check the bot")
async def bot_status(inter:discord.Interaction):

    e = discord.Embed(
        title = "Bot Status",
        color = cfg.SPFB
    )

    d, h, m, s = fcs.get_time(time.time() - _s_time)
        
    e.add_field(
        name  = "Operating time",
        value = f"**{d}** Days **{h}:{m}:{s}**",
        inline=False)

    e.add_field(name  = "Ping", value = f"**{round(bot.latency * 1000)}** ms")

    await inter.response.send_message(embed=e)


@bot.slash_command(name="avatar", description="アイコンを取得")
async def send_user_avatar(inter:discord.Interaction, user:discord.Member = None):
    user   = user if user else inter.user
    avatar = user.avatar.url
    e = discord.Embed(
        description = "%s's Avatar\n\n> **[URL](%s)**" % (user.mention, avatar),
        color       = cfg.SPFB)

    if (avatar == (server_avatar := user.display_avatar.url)):
        e.set_image(url=avatar)
    else:
        e.description += f"\n> **[Server URL]({server_avatar})**"
        e.set_image(url=server_avatar).set_thumbnail(url=avatar)
    await inter.response.send_message(embed=e)



@bot.slash_command(name="banner", description="ユーザープロフィールからバナーを取得。もしあれば。")
async def send_banner_user(inter:discord.Interaction, user:discord.Member = None):
    user = await bot.fetch_user(user.id if user else inter.user.id)
    if (user.banner):
        e = discord.Embed(
            description = f"{user.mention}'s Banner\n\n> [URL]({user.banner.url})", 
            color= cfg.SPFB)
        e.set_image(url = user.banner.url)
        await inter.response.send_message(embed=e)
    else:
        await inter.response.send_message(user.name + " haven't a Banner. Go away.", ephemeral=True)



@bot.slash_command(name="userinfo", description="ユーザー情報を送信")
async def send_user_info(inter:discord.Interaction, user:discord.Member = None):
    user = user if user else inter.user
    status = str(user.status)
    s_icon = "🟢" if status == "online" else "🟡" if status == "idle" else "🔴" if status == "dnd" else "⚫"
    embed = discord.Embed(
        description = "ID: **%s**\nStatus: **`%s %s`**" % (user.id, s_icon, status),
        color       = cfg.SPFB
    ).set_footer(text="and other info: '/avatar', '/banner' | banner is User profile only!")
    embed.set_thumbnail(url = user.display_avatar)
    embed.add_field(name = "Name", value = f"> {user}")

    if (user.name == user.display_name):
        embed.add_field(name="Bot?",      value = f"> {'Yes' if user.bot else 'No'}")
    else:
        embed.add_field(name= "Nickname", value = f"> {user.display_name}")
    
    if len(user.roles) >= 1:
        new_role = ([r.mention for r in user.roles][1:])
        embed.add_field(
            name   = f"Roles [ {len(user.roles)-1} ]", 
            value  = f"> {' '.join(new_role[::-1])}", 
            inline = False)

    embed.add_field(
        name  = "Created Account", 
        value = f"> {dts.format_timestamp(user.created_at.timestamp(), TimestampType.RELATIVE)}")
    embed.add_field(
        name  = "Joined Server",   
        value = f"> {dts.format_timestamp(user.joined_at.timestamp() , TimestampType.RELATIVE)}")
    
    if (user_ := await bot.fetch_user(user.id)):
        if (user_.banner):
            embed.set_image(url = user_.banner.url)

    await inter.response.send_message(embed=embed)



@bot.slash_command(name="serverinfo", description="Get info about server")
async def send_server_info(inter:discord.Interaction):
    guild = inter.guild
    req   = await bot.http.request(discord.http.Route("GET", "/guilds/" + str(guild.id)))
    tchannels, vchannels = len(guild.text_channels), len(guild.voice_channels)
    emojis   , emojis_g  = len(guild.emojis)       , sum([1 for e in guild.emojis if e.animated])
    embed= discord.Embed(
        title = guild.name,
        color = cfg.SPFB
    ).set_footer(text = "S = Static, A = Animated")

    embed.add_field(name = "Owner",     value = guild.owner.mention)
    embed.add_field(name = "Server ID", value = guild.id)
    embed.add_field(name = "Createion", value = f"{dts.format_timestamp(guild.created_at.timestamp(), TimestampType.RELATIVE)}\n")

    embed.add_field(name = f"Members [{guild.member_count}]", value= "**%s** User | **%s** Bot\n**%s** Online(user)" % (
                user_:=sum(1 for user in guild.members if not user.bot),
                guild.member_count - user_,
                sum(1 for member in guild.members if member.status != discord.Status.offline and not member.bot)))

    embed.add_field(
        name= f"Channels [{tchannels + vchannels}]", 
        value= "**%s** Text | **%s** Voice\n**%s** Category" % (tchannels, vchannels, len(guild.categories)))
    
    embed.add_field(
        name = f"Emojis [{emojis}]", 
        value= "**%s** S | **%s** A\n**%s** Sticker" % (emojis - emojis_g, emojis_g, sum(guild.stickers)))

    if (boosts:=guild.premium_subscription_count > 0):
        embed.add_field(
            name = "Boost", value= "**%s** Count\n**%s** Tier" % (boosts, guild.premium_tier))
        
    embed.add_field(
        name = "Role", 
        value= "**%s** Count" % (len(guild.roles)))
    
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
            content   = material.track_url,
            ephemeral = me_only)
    else:
        await inter.response.send_message(embed=material, ephemeral=True)



@bot.slash_command(name="spotify", description="Get the Spotify music info from user activities")
async def spotify_cmd(
    inter   :discord.Interaction, 
    user    :discord.Member = None, 
    me_only :Option(bool, "Me only?", choices=[True, False]) = False
):
    flag, material, artists = fcs.spotify(inter, user)
    if (flag):
        e = discord.Embed(color=cfg.SPFW).set_thumbnail(url=material.album_cover_url)
        e.add_field(
            name  = "Title", 
            value = f"```{material.title}```")
        e.add_field(
            name  = "Time", 
            value = f"```{dateutil.parser.parse(str(material.duration)).strftime('%M:%S')}```")
        e.add_field(
            name  = "Album", 
            value = f"```{material.album}```", inline=False)
        e.add_field(
            name  = "Artist(s)", 
            value = f"```{artists}```", inline=False)
        
        await inter.response.send_message(
            embed     = e,
            view      = fcs.SpotifyView(material, me_only),
            ephemeral = me_only)
    else:
        await inter.response.send_message(embed=material, ephemeral=True)



@bot.slash_command(name="spotify-cover", description="Get the Spotify music cover(aka Jakect) from user activities")
async def spotify_cmd(
    inter   :discord.Interaction, 
    user    :discord.Member = None, 
    me_only :Option(bool, "Me only?", choices=[True, False]) = False
):
    flag, material, artists = fcs.spotify(inter, user)
    if (flag):
        e = discord.Embed(color = cfg.SPFW).set_image(url = material.album_cover_url)
        await inter.response.send_message(
            embed     = e,
            view      = fcs.SpotifyView(material, me_only),
            ephemeral = me_only)
    else:
        await inter.response.send_message(embed=material, ephemeral=True)



@bot.slash_command(name="spotify-songs-search", description="SpotifyAPIを用いて楽曲を検索")
async def spotify_songs_search(
    inter:discord.Interaction,
    *, keyword, 
    limit:Option(int, "Search song Limit | Default: 4 max: 20") = 4):
    result = sp.search(q=keyword, limit=limit if 20 >= limit else 20)
    sp_list = []
    for track in result['tracks']['items']:
        song_title = track['name']

        song_title      = song_title.translate(str.maketrans({"[" : "(", "[" : ")"})) if "[" or "]" in song_title else song_title
        song_title      = str(song_title[:15] + "...") if len(song_title) > 15 else song_title
        song_album      = str(track['album']['name'][:13] + "...") if len(track['album']['name']) > 13 else track['album']['name']
    
        sp_list.append(f"{cfg.SP_JUMP_E} **[{song_title}]({track['external_urls']['spotify']})** - **{track['artists'][0]['name']}** : {song_album}")
    
    message = "\n\n".join(sp_list)
    keyword = __import__("urllib").parse.quote((str(keyword)))
    message += f"\n\n{cfg.SP_EMOJI} **[Jump to Spotify search engine](https://open.spotify.com/search/{keyword})**"

    await inter.response.send_message(
        embed=discord.Embed(
            description= message, 
            color      = cfg.SPFW
    ).set_footer(text="Layout: *Title* - *Artists* : Album"))


@bot.slash_command(name="spotify-song-search-select", description="Now coding...")
async def spotify_song_search_select(inter:discord.Interaction, *, keyword, limit:Option(int, "Use to limit song search | Default:4, Max: 10")=4):
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
