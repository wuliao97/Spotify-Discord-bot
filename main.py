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
import datetime as dt
import platform as pl
import dateutil.parser, spotipy, urllib, time, sys, os


bot = commands.Bot(
    command_prefix = "s.",
    intents        = discord.Intents.all()
)



@bot.event
async def on_ready():
    global _s_time
    _s_time = time.time()
    print(dt.datetime.now().strftime(fcs.TimeFormat.DEFAULT), bot.user, "on ready")


@bot.command(name="reboot", description="only admin")
async def exit_(inter):
    if not int(inter.author.id) in cfg.ADMINS:
        return await inter.send("You are NOT admin. You can't use this.", ephemeral = True)    
    
    d, h, m, s = fcs.get_time(time.time() - _s_time)

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
    e = discord.Embed(color = cfg.SPFB).set_author(icon_url = user.display_avatar, name=user)
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
    embed = discord.Embed(
        title       = "About this bot", 
        description = "For All of Spotify Lover and My friends!", 
        color       = cfg.SPFB)
    
    embed.add_field(
        name= "Users"  , 
        value= "> Servers: **%s**\n> Members: **%s**" % (
            len(bot.guilds), 
            sum([guild.member_count - 1 for guild in bot.guilds])
        ))
    
    u = pl.uname()

    plat =  f"> OS: **{(u.system)}** (*{u.release}*)\n"
    plat += f"> Lang: **Python** (*{pl.python_version()}*)"

    embed.add_field(
        name  = "Platform",
        value = plat
    )

    embed.add_field(
        name= "Support", 
        value= "> Deveroper: %s\n> Source: [Github.com](%s)\n> Our server: ||[DC Link](%s)||" %(
            user.mention, 
           "https://github.com/wuliao97/Spotify-Discord-bot", 
           "https://discord.gg/enni"))

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
        e.set_image(url=server_avatar)
        e.set_thumbnail(url=avatar)
    
    await inter.response.send_message(embed=e)



@bot.slash_command(name="banner", description="ユーザープロフィールからバナーを取得。もしあれば。")
async def send_banner_user(inter:discord.Interaction, user:discord.Member = None):
    user = await bot.fetch_user(user.id if user else inter.user.id)
        
    e = discord.Embed(color = cfg.SPFB)

    if (user.banner):
        e.description = f"{user.mention}'s Banner\n\n> [URL]({user.banner.url})", 
        e.set_image(url = user.banner.url)
    
        await inter.response.send_message(embed = e)
    
    else:
        e.description = user.name + " **haven't a Banner**. Go away."
        await inter.response.send_message(embed = e, ephemeral = True)



@bot.slash_command(name="userinfo", description="ユーザー情報を送信")
async def send_user_info(inter:discord.Interaction, user:discord.Member = None):
    user = user if user else inter.user
    status = str(user.status)
    s_icon = "🟢" if status == "online" else "🟡" if status == "idle" else "🔴" if status == "dnd" else "⚫"
        
    embed = discord.Embed(
        description = "ID: **%s**\nStatus: **`%s %s`**" % (user.id, s_icon, status),
        color       = cfg.SPFB
    )
    embed.set_footer(text="and other info: '/avatar', '/banner' | banner is User profile only!")
    embed.set_thumbnail(url = user.display_avatar)
    embed.add_field(name = "Name", value = f"> {user}")

    if (user.name == user.display_name):
        embed.add_field(name="Bot?",      value = f"> {'Yes' if user.bot else 'No'}")
    
        embed.add_field(name= "Nickname", value = f"> {user.display_name}")
    
    if len(user.roles) >= 1:
        new_role = ([r.mention for r in user.roles][1:])
        embed.add_field(
            name   = f"Roles ( {len(user.roles)-1} )", 
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
    guild                = inter.guild
    req                  = await bot.http.request(discord.http.Route("GET", "/guilds/" + str(guild.id)))
    tchannels, vchannels = len(guild.text_channels), len(guild.voice_channels)
    emojis   , emojis_g  = len(guild.emojis)       , sum([1 for e in guild.emojis if e.animated])
        
    embed = discord.Embed(
        title = guild.name,
        color = cfg.SPFB
    )

    embed.add_field(name = "Owner", value = guild.owner.mention)
    embed.add_field(name = "ID",    value = guild.id)
    embed.add_field(name = "Createion", value = f"{dts.format_timestamp(guild.created_at.timestamp(), TimestampType.RELATIVE)}")
        

    embed.add_field(name  = f"Members ({guild.member_count})", 
                    value = "**%s** User | **%s** Bot\n**%s** Online(user)" % (
                        user_ := sum(1 for user in guild.members if not user.bot),
                        guild.member_count - user_,
                        sum(1 for member in guild.members if member.status != discord.Status.offline and not member.bot)))

    embed.add_field(
        name= f"Channels ({tchannels + vchannels})", 
        value= "**%s** Text | **%s** Voice\n**%s** Category" % (
            tchannels,
            vchannels, 
            len(guild.categories)))
    
    embed.add_field(
        name = f"Emojis ({emojis})",
        value= "**%s** Static\n**%s** Animated\n**%s** Sticker" % (
            str(emojis - emojis_g), 
            str(emojis_g), 
            len(guild.stickers)))
    
    embed.add_field(
        name = "Role",
        value= "**%s** Count" % (len(guild.roles)))
    
    if (guild.premium_subscription_count > 0):
        embed.add_field(
            name  = f"Boost ({guild.premium_subscription_count})", 
            value = "**%s** Tier" % (guild.premium_tier))
    
    if (guild.icon):
        embed.set_thumbnail(url = guild.icon.url)

    if vanity:=req["vanity_url_code"]:
        embed.description = f"Vanity `{vanity}`"

    await inter.response.send_message(embed = embed)



@bot.slash_command(name="spotify-track", description="Get the Spotify music URL from user activities")
async def spotify_cmd(
    inter   :discord.Interaction, 
    user    :discord.Member = None, 
    me_only :Option(str, "Me only?", choices=["Yes", "No"]) = "No"
):
    flag, material, artists = fcs.spotify(inter, user)
    if (flag):
        await inter.response.send_message(
            content   = material.track_url,
            ephemeral = True if me_only == "Yes" else False)
        
    else:
        await inter.response.send_message(embed = material, ephemeral = True)



@bot.slash_command(name="spotify", description="Get the Spotify music info from user activities")
async def spotify_cmd(
    inter   :discord.Interaction, 
    user    :discord.Member = None, 
    me_only :Option(str, "Me only?", choices=["Yes", "No"]) = "No"
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
            view      = fcs.SpotifyButtonS(mode = "urls", url = fcs.spotify_extract(material.track_id)),
            ephemeral = True if me_only == "Yes" else False)
    else:
        await inter.response.send_message(embed=material, ephemeral=True)



@bot.slash_command(name="spotify-cover", description="Get the Spotify music cover(aka Jakect) from user activities")
async def spotify_cmd(
    inter   :discord.Interaction, 
    user    :discord.Member = None, 
    me_only :Option(str, "Display Me only?", choices=["Yes", "No"]) = "No"
):
    flag, material, artists = fcs.spotify(inter, user)
    if (flag):
        e = discord.Embed(
            title       = material.title,
            description = (f"Artists: **{artists}** Album: **{material.album}**"),
            color       = cfg.SPFW
            )
        e.set_image(url = material.album_cover_url)

        await inter.response.send_message(
            embed     = e,
            view      = fcs.SpotifyButtonS(mode = "urls", url = fcs.spotify_extract(material.track_id)),
            ephemeral =True if me_only == "Yes" else False)
    else:
        await inter.response.send_message(embed=material, ephemeral=True)



@bot.slash_command(name="spotify-search", description="SpotifyAPIを用いて楽曲を検索")
async def spotify_songs_search(
    inter:discord.Interaction,
    *, keyword, 
    limit:Option(int, "Search song Limit | Default: 5 max: 20") = 5
):
    result = cfg.sp.search(q = keyword, limit = limit if 20 >= limit else 20)
    sp_list = []
    for track in result['tracks']['items']:
        title, album = fcs.data_sort(track['name'], track['album']['name'])
        url = track['external_urls']['spotify']
        artist = track['artists'][0]['name']

        sp_list.append("%s **[%s](%s)** (%s) - **%s**" % (cfg.SP_JUMP_E, title, url, album, artist))

    await inter.response.send_message(
        embed = discord.Embed(
            description = "\n\n".join(sp_list), 
            color       = cfg.SPFW
        ).set_footer(text = "Layout: *Title* (Album) - *Artists*"),
        view = fcs.SpotifyButtonS(mode = "default", url = [f"https://open.spotify.com/search/{urllib.parse.quote((str(keyword)))}"]))


@bot.slash_command(name="spotify-search-select", description="Now coding...")
async def spotify_song_search_select(
    inter:discord.Interaction,
    *, keyword:str, 
    limit:Option(int, "Use to limit song search | Default:4, Max: 25") = 7
):
    result = cfg.sp.search(q=keyword, limit = limit if 25 >= limit else 25)
    select_option:list = []
    
    for track in result['tracks']['items']:
        select_option.append(discord.SelectOption(
            label = track["name"],
            value = track['external_urls']['spotify'],
            description = track["album"]["name"] + " : " + track["artists"][0]["name"]
        ))
    await inter.response.send_message(view = fcs.SpotifySelectView(
        placeholder = "Choose the song",
        option      = select_option,
        url = f"https://open.spotify.com/search/{urllib.parse.quote((str(keyword)))}")
    )



bot.run(cfg.TOKEN)
