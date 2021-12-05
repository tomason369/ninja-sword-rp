import os
import discord
import asyncio
import json

from discord_slash import SlashCommand
from webserver import keep_alive
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle
from discord import Color
from datetime import datetime
from itertools import cycle

def get_prefix(bot, message):
    with open("prefix.json", "r") as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


status = cycle(["Jsem ručně dělaný", "Když neodpovím napiš $help"])
bot_name = "NINJA SWORD RP"
bot_icon = "https://cdn.discordapp.com/icons/910290682634182716/d76b55e6f5ea7b6834a5f9bee5c389e3.webp?"
welcomeChannel = "910308486557102143"


bot = commands.Bot(command_prefix=get_prefix)
slash = SlashCommand(bot, sync_commands=True)

#info
@bot.command(help="zde je info o botovi", aliases=["i"])
async def info(ctx):
    embed = discord.Embed(title="info",
                          description="info o botovy",
                          timestamp=datetime.utcnow())

    embed.set_author(name=bot_name, icon_url=bot_icon)
    embed.add_field(name="tvůrce tohoto bota",
                    value="toma_son#0576",
                    inline=True)
    embed.set_thumbnail(url=bot_icon)

    await ctx.channel.purge(limit=1)
    await ctx.send(
        embed=embed,
        components=[
            Button(
                style=ButtonStyle.URL,
                label="Yt kanál",
                url="https://www.youtube.com/channel/UCFwKU_i7nmc31FHc8koMURw"),
            Button(
                style=ButtonStyle.URL,
                label="Pozvi mě", 
                url= "https://discord.com/api/oauth2/authorize?client_id=910418225433567232&permissions=8&scope=bot%20applications.commands")
        ])

#clear
@bot.command(help="maže zprávy", aliases=["c"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amout: int):
    await ctx.channel.purge(limit=amout + 1)
    await ctx.send(f"Vymazal jsem {amout} zpráv")
    await asyncio.sleep(2)
    await ctx.channel.purge(limit=1)

#kick
@bot.command(help="vyhazuje lidi", aliases=["k"])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.channel.purge(limit=1)
    await ctx.send(
        f"Hráč {member.name} byl vyhozen za *{reason}* nechovejte se jako on prosím abych to nemusel opakovat děkuju"
    )

#ban
@bot.command(help="banuje lidi", aliases=["b"])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.channel.purge(limit=1)
    await ctx.send(
        f"Hráč {member.name} byl zabanován za *{reason}* nechovejte se jako on prosím abych to nemusel opakovat děkuju"
    )

#change prefix
@bot.command(help="změní ti prefix na tomto servevru",
             aliases=["changeprefix"])
async def chp(ctx, prefix):
    with open("prefix.json") as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open("prefix.json", "w") as f:
        json.dump(prefixes, f, indent=4)

    await ctx.channel.purge(limit=1)
    await ctx.send(f"Změnil jsem prefix na `{prefix}`")

#/ping
@slash.slash(description="Ping bota")
async def ping(ctx):
    await ctx.send(f"Bot ping je: {round(bot.latency * 1000)}ms")


@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


@bot.event
async def on_ready():
    print("bot is ready")
    change_status.start()
    DiscordComponents(bot)

#error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply(
            "nejspíš jsi napsal špatně command napiš **$help** aby si zjistil co jsi napsal špatně"
        )
    
    if isinstance(error, commands.MissingPermissions):
        perms = "".join(error.missing_perms)
        perms_formatted = f"{perms[0].upper()}{perms[1:]}"
        await ctx.reply(f"Potřebuješ tyto permise: {perms_formatted}")

    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.reply("Nedostatečný argument napiš **$help (command)**")

    if isinstance(error, commands.BadArgument):
      await ctx.reply("Špatný argument napiš **$help (command)**")


@bot.event
async def on_guild_join(guild):
    with open("prefix.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "$"

    with open("prefix.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@bot.event
async def on_guild_remove(guild):
    with open("prefix.json", "r") as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open("prefix.json", "w") as f:
        json.dump(prefixes, f, indent=4)

#welcome message
@bot.event
async def on_member_join(member):

    welcomeEmbed = discord.Embed(
        title="Novej member!!!!",
        description=
        f"Zdravím tě {member.name},vítej na našem Role Play serveru a doufám, že si užiješ spoustu srandy"
    )
    welcomeEmbed.set_image(url=member.icon_url)

    await bot.get_channel(welcomeChannel).send(embed=welcomeEmbed)

token = os.environ['token']

keep_alive()
bot.run(token)