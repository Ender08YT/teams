import nextcord
import discord
from nextcord.ext import commands
from nextcord import Interaction, ButtonStyle, Guild
from nextcord.ui import Button, View
import aiosqlite
import asyncio
from easy_pil import *
from PIL import Image, ImageDraw, ImageFont
from re import search
from cooldowns import CallableOnCooldown
import os
from dotenv import load_dotenv
from nextcord.utils import get
from random import choice
from discord import app_commands
from typing import List, Literal
from pathlib import Path
from typing import Optional
import time


intents = nextcord.Intents.all()
intents.members = True

# RANK INTEGERS
# 3: Owner
# 2: Manager
# 1: Member
OWNER_RANK_ID = 3
MANAGER_RANK_ID = 2
MEMBER_RANK_ID = 1
rank_dict = {MEMBER_RANK_ID: "Member", MANAGER_RANK_ID: "Manager", OWNER_RANK_ID: "Owner"}
bot = commands.Bot(intents=intents)
dotenv_path = Path("G:\Downloads\TeamsTesting\secrets.env")
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv('TOKEN')

class PageChanger(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(label='⇦ Previous Page', style=nextcord.ButtonStyle.red)
    async def previous(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        global team_count
        async with bot.db.cursor() as cursor:
            self.value = "last"
            await cursor.execute("SELECT name, team_id FROM teams WHERE guild_id = ?", (ctx.guild.id,))
            data = await cursor.fetchall()
            team_list = []
            for table in data:
                await cursor.execute("SELECT user_id FROM members WHERE team_id = ?", (table[1]))
                members = await cursor.fetchall()
                memcount = len(members)
                team_list.append((table[0],memcount))
            try:
                team_count
            except:
                print("nooo")
                team_count = 20
            current_list = []
            team_count -= 20
            if team_count < 0:
                team_count += 20
                return await ctx.send(f"You're on the first page!", ephemeral=True)
            countmax = team_count + 10
            while team_count < countmax:
                try:
                    current_list.append(team_list[team_count])
                    team_count += 1
                    print(team_count, team_list[team_count])
                except:
                    break
            await list_teams(current_list, ctx, None, "edit", countmax/10)
    
    @nextcord.ui.button(label='Next Page ⇨', style=nextcord.ButtonStyle.green)
    async def next(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        global team_count
        async with bot.db.cursor() as cursor:
            self.value = "next"
            await cursor.execute("SELECT name, team_id FROM teams WHERE guild_id = ?", (ctx.guild.id,))
            data = await cursor.fetchall()
            team_list = []
            for table in data:
                await cursor.execute("SELECT user_id FROM members WHERE team_id = ?", (table[1]))
                members = await cursor.fetchall()
                memcount = len(members)
                team_list.append((table[0],memcount))
            try:
                team_count
            except:
                print("nooo")
                team_count = 10
            try:
                print(team_count, team_list[team_count])
            except:
                return await ctx.send(f"You're on the last page!", ephemeral=True)
            current_list = []
            countmax = team_count + 10
            while team_count < countmax:
                try:
                    current_list.append(team_list[team_count])
                    team_count += 1
                    print(team_count, team_list[team_count])
                except:
                    team_count = countmax
                    break
            await list_teams(current_list, ctx, None, "edit",countmax/10)

async def list_teams(lst,ctx,view,msgtype,page):
    if msgtype == "new":
        em = nextcord.Embed(
            title="All Teams\n", color=nextcord.Color(int("777777", 16)))

        for table in lst:
            name = table[0]
            memcount = table[1]
            em.add_field(name=name,
                            value=f"Members: {memcount}​", inline=False)
        em.add_field(name="\n",
                     value=f"Page {page}", inline=False)
        if view == None:
            return await ctx.send(embed=em)
        return await ctx.send(embed=em, view=view)
    msg = ctx.message
    em = nextcord.Embed(
    title=f"All teams:\n", color=nextcord.Color(int("777777", 16)))

    for table in lst:
        name = table[0]
        memcount = table[1]
        em.add_field(name=name,
                            value=f"Members: {memcount}​", inline=False)
    em.add_field(name="\n",
                 value=f"Page {int(page)}", inline=False)
    if view == None:
        return await msg.edit(embed=em)
    return await ctx.edit(embed=em, view=view)

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    server_count = len(bot.guilds)
    print(f'{bot.user.name} is now online in {server_count} server(s)')
    setattr(bot, "db", await aiosqlite.connect("teams.db"))
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS teams (team_id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING NOT NULL, color STRING, image STRING, points INTEGER, category_id INTEGER, role_id INTEGER, channel_id INTEGER, voice_channel_id INTEGER, owner_id INTEGER, guild_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS members (user_id INTEGER, guild_id INTEGER, team_id INTEGER, rank_id INTEGER, team_join_date INTEGER, FOREIGN KEY (team_id) REFERENCES teams(team_id))")
        await cursor.execute("CREATE TABLE IF NOT EXISTS serversettings (guild_id INTEGER, join_toggle INTEGER, max_members INTEGER, team_channel_id INTEGER, required_role_id INTEGER)")
    guilds = bot.guilds
    server_count = len(guilds)
    gnamelist = []

    for guild in guilds:
        gentry = []
        gentry.append(guild.name)
        gentry.append(guild.member_count)
        gnamelist.append(gentry)
    gnamelist.sort(key=lambda guild: guild[1], reverse=True)
    for guild in gnamelist:
        print(f"Name: {guild[0]}, Members: {guild[1]}")
    mem_count = len(bot.users)
    print(f'{bot.user.name} is now online in {server_count} server(s)')
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.competing, name=f"{server_count} servers with {mem_count} members!"))
@bot.event
async def on_member_join(member):
    await check_member_for_data(member)
@bot.event
async def on_member_remove(member):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT rank_id FROM members WHERE user_id = ? AND guild_id = ?", (member.id, member.guild.id))
        rank = await cursor.fetchone()
        if rank[0] != OWNER_RANK_ID:
            print("jarvis, show me this guy's balls")
            await cursor.execute("DELETE FROM members WHERE user_id = ? AND guild_id = ?", (member.id, member.guild.id))
            return await bot.db.commit()
        print("let him cook")
        try:
            await cursor.execute("SELECT team_id FROM members WHERE user_id = ?", (member.id,))
            team_id = await cursor.fetchone()
            await cursor.execute("SELECT channel_id, voice_channel_id, category_id, role_id, name FROM teams WHERE team_id = ?", (team_id[0],))
            data = await cursor.fetchall(); data = data[0]
            print(data)
            # Deletes channel
            channel = member.guild.get_channel(data[0])
            if channel != None:
                await channel.delete()
            # Deletes VC
            vchannel = member.guild.get_channel(data[1])
            if vchannel != None:
                await vchannel.delete()
            # Deletes category
            category = member.guild.get_channel(data[2])
            if category != None:
                await category.delete()
            # Deletes role
            role = member.guild.get_role(data[3])
            if role != None:
                await role.delete()
            # Updates teams.db
            await cursor.execute("DELETE FROM teams WHERE team_id = ?", (team_id[0],))
            await cursor.execute("SELECT team_channel_id FROM serversettings WHERE guild_id = ?", (member.guild.id,))
            team_channel_id = await cursor.fetchone()
            if team_channel_id[0] == -1:
                return await member.guild.system_channel.send(f"\"{data[4]}\" has been deleted.", ephemeral=False)
            channel = member.guild.get_channel(team_channel_id[0])
            await channel.send(f"\"{data[4]}\" has been deleted.")
            await cursor.execute("DELETE FROM members WHERE user_id = ? AND guild_id = ?", (member.id, member.guild.id))
            return await bot.db.commit()
        except:
            print("jarvis, show me this guy's nuts")
            await cursor.execute("DELETE FROM members WHERE user_id = ? AND guild_id = ?", (member.id, member.guild.id))
            return await bot.db.commit()
async def check_for_data(ctx: nextcord.Interaction):
    if type(ctx) == nextcord.Message:
        if ctx.author.bot:
            return
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT team_id, rank_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.author.id, ctx.guild.id,))
            data = await cursor.fetchone()

            if not data:
                await cursor.execute("INSERT INTO members (user_id, guild_id, team_id, rank_id, team_join_date) VALUES (?, ?, ?, ?, ?)", (ctx.author.id, ctx.guild.id, 0, 1, None))

            try:

                team = data[0]
                rank = data[1]

                if str(team) == "None" or str(rank) == "None":
                    await cursor.execute("UPDATE members SET team_id = ?, rank_id = ? WHERE user_id = ? AND guild_id = ?", (0, 1, ctx.author.id, ctx.guild.id,))
            except TypeError:
                await cursor.execute("UPDATE members SET team_id = ?, rank_id = ? WHERE user_id = ? AND guild_id = ?", (0, 1, ctx.author.id, ctx.guild.id,))
        await bot.db.commit()
    else:
        if ctx.user.bot:
            return
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT team_id, rank_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
            data = await cursor.fetchone()

            if not data:
                await cursor.execute("INSERT INTO members (user_id, guild_id, team_id, rank_id, team_join_date) VALUES (?, ?, ?, ?, ?)", (ctx.user.id, ctx.guild.id, 0, 1, None))

            try:

                team = data[0]
                rank_id = data[1]

                if str(team) == "None" or str(rank_id) == "None":
                    await cursor.execute("UPDATE members SET team_id = ?, rank_id = ? WHERE user_id = ? AND guild_id = ?", (0, 1, ctx.user.id, ctx.guild.id,))
            except TypeError:
                await cursor.execute("UPDATE members SET team_id = ?, rank_id = ? WHERE user_id = ? AND guild_id = ?", (0, 1, ctx.user.id, ctx.guild.id,))
        await bot.db.commit()

async def check_member_for_data(member: nextcord.Member):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team_id, rank_id FROM members WHERE user_id = ? AND guild_id = ?", (member.id, member.guild.id,))
        data = await cursor.fetchone()
        if not data:
            await cursor.execute("INSERT INTO members (user_id, guild_id, team_id, rank_id, team_join_date) VALUES (?, ?, ?, ?, ?)", (member.id, member.guild.id, 0, 1, None))

        try:

            team = data[0]
            rank_id = data[1]

            if str(team) == "None" or str(rank_id) == "None":
                await cursor.execute("UPDATE members SET team_id = ?, rank_id = ? WHERE user_id = ? AND guild_id = ?", (0, 1, member.id, member.guild.id,))
        except TypeError:
            await cursor.execute("UPDATE members SET team_id = ?, rank_id = ? WHERE user_id = ? AND guild_id = ?", (0, 1, member.id, member.guild.id,))
    await bot.db.commit()
    

async def check_server_for_data(ctx: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT guild_id FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
        guild = await cursor.fetchone()
        print(guild)
        if not guild:
            await cursor.execute("INSERT INTO serversettings (guild_id, join_toggle, max_members, team_channel_id, required_role_id) VALUES (?, ?, ?, ?, ?)", (ctx.guild.id, 0, -1, -1, -1))
    await bot.db.commit()

class DelPrompt(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Yes', style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT team_id FROM members WHERE user_id = ?", (ctx.user.id,))
            team_id = await cursor.fetchone()
            await cursor.execute("SELECT channel_id, voice_channel_id, category_id, role_id FROM teams WHERE team_id = ?", (team_id[0],))
            data = await cursor.fetchall(); data = data[0]
            print(data)
            # Deletes channel
            channel = ctx.guild.get_channel(data[0])
            if channel != None:
                await channel.delete()
            # Deletes VC
            vchannel = ctx.guild.get_channel(data[1])
            if vchannel != None:
                await vchannel.delete()
            # Deletes category
            category = ctx.guild.get_channel(data[2])
            if category != None:
                await category.delete()
            # Deletes role
            role = ctx.guild.get_role(data[3])
            if role != None:
                await role.delete()
            # Updates teams.db
            await cursor.execute("UPDATE members SET team_id = ?, rank_id = ? WHERE user_id = ? AND guild_id = ?", (0, 1, ctx.user.id, ctx.guild.id,))
            await cursor.execute("DELETE FROM teams WHERE team_id = ?", (team_id[0],))
            await bot.db.commit()
            self.value = True
            self.stop()

    @nextcord.ui.button(label='No', style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        self.value = False
        self.stop()


class TraPrompt(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Yes', style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        async with bot.db.cursor() as cursor:
            self.value = True
            self.stop()

    @nextcord.ui.button(label='No', style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        self.value = False
        self.stop()


@bot.event
async def on_message(message): 
    await check_for_data(ctx=message)

def hex_to_rgb(value):
    value = value.lstrip('#').rstrip(";")
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


@bot.slash_command()
async def team(interaction: nextcord.Interaction):
    pass


@team.subcommand(description="Create a new team!")
async def create(ctx: nextcord.Interaction, name: str = nextcord.SlashOption(description="Enter your team's name:"), color: str = nextcord.SlashOption(description="Enter a valid hex code for your team's color (e.g. #FFFFFF):")):
    await check_for_data(ctx=ctx)
    await check_server_for_data(ctx=ctx)
    await ctx.response.defer()
    match = search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
    if match:
        async with bot.db.cursor() as cursor:
            if len(name) > 20:
                return await ctx.send("This team's name is too long! Keep team names under 15 characters.", ephemeral=True)
            await cursor.execute("SELECT name FROM teams WHERE guild_id = ?", (ctx.guild.id,))
            data = await cursor.fetchall()
            nametuple = (name,)
            if nametuple in data:
                return await ctx.send("This team already exists! Try using /team join instead.", ephemeral=True)
            await cursor.execute("SELECT team_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
            team_id = await cursor.fetchone()
            if team_id[0] != 0:
                await cursor.execute("SELECT name FROM teams WHERE team_id = ?", (team_id[0],))
                team = await cursor.fetchone()
                return await ctx.send(f"You're already in this team: {team[0]}. Try using /team leave first.", ephemeral=True)
            role = await ctx.guild.create_role(name=name, color=nextcord.Color(int(color.strip("#"), 16)), mentionable=True, hoist=True)
            await ctx.user.add_roles(role)
            overwrites = {
                ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                role: nextcord.PermissionOverwrite(read_messages=True),
                ctx.guild.get_member(1132561711493288040): nextcord.PermissionOverwrite(read_messages=True)
            }
            category = await ctx.guild.create_category(name=name, overwrites=overwrites)
            channel = await ctx.guild.create_text_channel(name=name + "-chat", overwrites=overwrites, category=category)
            voice_channel = await ctx.guild.create_voice_channel(name=name + "-chat", overwrites=overwrites, category=category)
            await cursor.execute("INSERT INTO teams (name, color, points, category_id, role_id, channel_id, voice_channel_id, owner_id, guild_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, color, 0, category.id, role.id, channel.id, voice_channel.id, ctx.user.id, ctx.guild.id))
            await cursor.execute("SELECT LAST_INSERT_ROWID()")
            team_id = await cursor.fetchone()
            unix_time = int(time.time())
            print(unix_time)
            await cursor.execute("UPDATE members SET team_id = ?, team_join_date = ?, rank_id = ? WHERE user_id = ? AND guild_id = ?", (team_id[0], unix_time, OWNER_RANK_ID, ctx.user.id, ctx.guild.id))
            await bot.db.commit()
            await check_server_for_data(ctx)
            await cursor.execute("SELECT team_channel_id FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
            team_channel_id = await cursor.fetchone()
            if team_channel_id[0] == -1:
                return await ctx.send(f"{role.mention} ({name}) has been created by {ctx.user.mention}.", ephemeral=False)
            channel = ctx.guild.get_channel(team_channel_id[0])
            await channel.send(f"{role.mention} ({name}) has been created by {ctx.user.mention}.")
            return await ctx.send("Team succesfully created!", ephemeral=True)
    else:
        await ctx.send("That's not a valid hex code.", ephemeral=True)




@team.subcommand(description="join a team")
async def join(ctx: nextcord.Interaction, name: str = nextcord.SlashOption(description="Enter the name of the team you want to join:")):
        
        await check_for_data(ctx=ctx)
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT join_toggle FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
            jointoggle = await cursor.fetchone()
            if jointoggle[0] == 0:
                return await ctx.send("Joining is disabled on this server.", ephemeral=True)            
            await cursor.execute("SELECT team_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
            mem_team_id = await cursor.fetchone()
            if mem_team_id[0] != 0:
                await cursor.execute("SELECT name FROM teams WHERE team_id = ?", (team_id[0],))
                team = await cursor.fetchone()
                return await ctx.send(f"You're already in this team: {team[0]}. Try using /team leave first.", ephemeral=True)
            await cursor.execute("SELECT team_id FROM teams WHERE name LIKE ? AND guild_id = ?", (name, ctx.guild.id))
            team_id = await cursor.fetchone()
            if team_id:
                await cursor.execute("SELECT role_id FROM teams WHERE team_id = ? AND guild_id = ?", (team_id[0], ctx.guild.id,))
                role_id = await cursor.fetchone()
                role = ctx.guild.get_role(role_id[0])
                await ctx.user.add_roles(role)
                unix_time = int(time.time())
                await cursor.execute("UPDATE members SET team_id = ?, team_join_date = ? WHERE user_id = ? AND guild_id = ?", (team_id[0], unix_time, ctx.user.id, ctx.guild.id,))
                await bot.db.commit()
                await cursor.execute("SELECT team_channel_id FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
                team_channel_id = await cursor.fetchone()
                await cursor.execute("SELECT name FROM teams WHERE team_id = ?", (team_id[0],))
                team_name = await cursor.fetchone()
                if team_channel_id[0] == -1:
                    return await ctx.send(f"{ctx.user.mention} has joined {role.mention} ({team_name[0]}).", ephemeral=False)
                channel = ctx.guild.get_channel(team_channel_id[0])
                await channel.send(f"{ctx.user.mention} has joined {role.mention} ({team_name[0]})!")
                return await ctx.send(f"Successfully joined {role.mention} ({team_name[0]})!", ephemeral=True)
            else:
                return await ctx.send("This team doesn't exist! Try using /team create instead.", ephemeral=True)
            
@join.on_autocomplete('name')
async def members_autocompletion(ctx: nextcord.Interaction, team: str):
    async with bot.db.cursor() as cursor:
        choices = await fetch_choices(ctx.guild.id)
        print(choices)
        await ctx.response.send_autocomplete(choices)


@team.subcommand(description="Add someone to a team")
async def add(ctx: nextcord.Interaction, member: nextcord.Member):
        await check_for_data(ctx=ctx)
        await check_member_for_data(member)
        await ctx.response.defer()
        async with bot.db.cursor() as cursor:            
            await cursor.execute("SELECT team_id FROM members WHERE user_id = ? AND guild_id = ?", (member.id, ctx.guild.id,))
            mem_team = await cursor.fetchone()
            if mem_team[0] != 0:
                return await ctx.send("This member is already in a team! Don't be a thief.", ephemeral=True)
            await cursor.execute("SELECT team_id, rank_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
            data = await cursor.fetchone()
            if data[0] == 0:
                return await ctx.send("You're not even in a team! Try using /team create first.", ephemeral=True)
            if data[1] != OWNER_RANK_ID:
                return await ctx.send("Only a team's owner can add members to a team.", ephemeral=True)
            await cursor.execute("SELECT max_members FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
            maxmembers = await cursor.fetchone()
            if maxmembers[0] != -1:
                await cursor.execute("SELECT user_id FROM members WHERE team_id = ?", (data[0],))
                members = await cursor.fetchall()
                if members:
                    count = 0
                    for table in data:
                        count += 1
                if count >= maxmembers[0]:
                    return await ctx.send(f"Your team is already at max capacity! Max members on this server is {maxmembers[0]}.", ephemeral=True)
            await cursor.execute("SELECT role_id FROM teams WHERE team_id = ?", (data[0],))
            role_id = await cursor.fetchone()
            role = ctx.guild.get_role(role_id[0])
            await member.add_roles(role)
            unix_time = int(time.time())
            await cursor.execute("UPDATE members SET team_id = ?, team_join_date = ? WHERE user_id = ? AND guild_id = ?", (data[0], unix_time, member.id, ctx.guild.id,))
            await bot.db.commit()
            await cursor.execute("SELECT team_channel_id FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
            team_channel_id = await cursor.fetchone()
            await cursor.execute("SELECT name FROM teams WHERE team_id = ?", (data[0],))
            team_name = await cursor.fetchone()
            if team_channel_id[0] == -1:
                return await ctx.send(f"{member.mention} has been added to {role.mention} ({team_name[0]}).", ephemeral=False)
            channel = ctx.guild.get_channel(team_channel_id[0])
            await channel.send(f"{member.mention} has been added to {role.mention} ({team_name[0]}).")
            return await ctx.send("Member succesfully added.", ephemeral=True)

@team.subcommand(description="Transfer ownership of your team")
async def transfer(ctx: nextcord.Interaction, member: nextcord.Member):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team_id, rank_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
        team_id, rank_id = await cursor.fetchone()
        if team_id == 0:
            return await ctx.send("You're not in any teams!", ephemeral=True)
        if rank_id != OWNER_RANK_ID:
            return await ctx.send("You can't transfer ownership if you aren't the owner.", ephemeral=True)
        await cursor.execute("SELECT team_id FROM members WHERE user_id = ? AND guild_id = ?", (member.id, ctx.guild.id,))
        mem_team_id = await cursor.fetchone()
        if mem_team_id[0] != team_id:
            return await ctx.send("You can't transfer ownership to someone who isn't on your team.", ephemeral=True)
        await cursor.execute("SELECT name FROM teams WHERE team_id = ?", (team_id,))
        name = await cursor.fetchone()
        view = TraPrompt()
        await ctx.send(f"Are you sure you would like to transfer ownership of {name[0]} to {member}?", ephemeral=True, view=view)
        await view.wait()
        if view.value is None:
            return
        elif view.value:
            await cursor.execute("UPDATE teams SET owner_id = ? WHERE team_id = ?", (member.id, team_id,))
            await cursor.execute("UPDATE members SET rank_id = ? WHERE user_id = ? AND guild_id = ?", (OWNER_RANK_ID, member.id, ctx.guild.id,))
            await cursor.execute("UPDATE members SET rank_id = ? WHERE user_id = ? AND guild_id = ?", (MEMBER_RANK_ID, ctx.user.id, ctx.guild.id,))
            await bot.db.commit()
            return await ctx.send(f"Successfully transferred ownership to {member}.", ephemeral=True)
        else:
            return await ctx.send("Transfer request canceled.", ephemeral=True)           
        
@team.subcommand(description="Leave your current team")
async def leave(ctx: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team_id, rank_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
        data = await cursor.fetchone()
        await cursor.execute("SELECT name FROM teams WHERE team_id = ?", (data[0],))
        team_name = await cursor.fetchone()
        if data[0] == 0:
            return await ctx.send("You're not in any teams!", ephemeral=True)
        if data[1] == OWNER_RANK_ID:
            await cursor.execute("SELECT user_id FROM members WHERE team_id = ? AND guild_id = ?", (data[0], ctx.guild.id,))
            member_list = await cursor.fetchall()
            if len(member_list) > 1:
                return await ctx.send("You can't leave a team with members that you're the owner of! Try transferring ownership first.", ephemeral=True)
            else:
                print(data[0])
                await cursor.execute("SELECT name FROM teams WHERE team_id = ?", (data[0],))
                team_name = await cursor.fetchone()
                print(team_name)
                view = DelPrompt()
                await ctx.send(f"Are you sure you would like to leave {team_name[0]}? This will delete the team!", ephemeral=True, view=view)
                await view.wait()
                if view.value is None:
                    return
                elif view.value:
                    await cursor.execute("SELECT team_channel_id FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
                    team_channel_id = await cursor.fetchone()
                    if team_channel_id[0] == -1:
                        return await ctx.send(f"\"{team_name[0]}\" has been disbanded!", ephemeral=False)
                    channel = ctx.guild.get_channel(team_channel_id[0])
                    await channel.send(f"\"{team_name[0]}\" has been disbanded!")
                    return await ctx.send(f"Successfully deleted {team_name[0]}", ephemeral=True)
                else:
                    return await ctx.send("Deletion request canceled.", ephemeral=True)

        await cursor.execute("SELECT role_id FROM teams WHERE team_id = ?", (data[0],))
        role_id = await cursor.fetchone()
        role = ctx.guild.get_role(role_id[0])
        await ctx.user.remove_roles(role)
        await cursor.execute("UPDATE members SET team_id = ?, rank_id = ? WHERE user_id = ? AND guild_id = ?", (0, MEMBER_RANK_ID, ctx.user.id, ctx.guild.id,))
        await bot.db.commit()
        await cursor.execute("SELECT team_channel_id FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
        team_channel_id = await cursor.fetchone()
        if team_channel_id[0] == -1:
            return await ctx.send(f"{ctx.user.mention} has left {role.mention} ({team_name[0]}).", ephemeral=False)
        channel = ctx.guild.get_channel(team_channel_id[0])
        await channel.send(f"{ctx.user.mention} has left {role.mention} ({team_name[0]}).")
        return await ctx.send(f"Succesfully left {role.mention} ({team_name[0]}).", ephemeral=True)

@team.subcommand(description="Remove someone from your team")
async def remove(ctx: nextcord.Interaction, member:nextcord.Member):
    await check_for_data(ctx=ctx)
    await check_member_for_data(member)
    if member.id == ctx.user.id:
            return await ctx.send("You can't remove *yourself* from a team -- try /team leave instead.", ephemeral=True)            
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team_id, rank_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
        data = await cursor.fetchone()
        if data[0] == 0:
            return await ctx.send("You're not even in a team! Nice try, though.", ephemeral=True)
        if data[1] != OWNER_RANK_ID:
            return await ctx.send("Only a team's owner can remove members from a team.", ephemeral=True)
        await cursor.execute("SELECT team_id FROM members WHERE user_id = ? AND guild_id = ?", (member.id, ctx.guild.id,))
        mem_team_id = await cursor.fetchone()
        if mem_team_id[0] != data[0]:
            return await ctx.send("This member isn't even on your team!", ephemeral=True)        

        await cursor.execute("SELECT role_id FROM teams WHERE team_id = ?", (data[0],))
        role_id = await cursor.fetchone()
        role = ctx.guild.get_role(role_id[0])
        await member.remove_roles(role)
        await cursor.execute("UPDATE members SET team_id = ?, rank_id = ?, team_join_date = ? WHERE user_id = ? AND guild_id = ?", (0, MEMBER_RANK_ID, None, member.id, ctx.guild.id,))
        await bot.db.commit()
        await cursor.execute("SELECT team_channel_id FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
        team_channel_id = await cursor.fetchone()
        await cursor.execute("SELECT name FROM teams WHERE team_id = ?", (data[0],))
        team_name = await cursor.fetchone()
        if team_channel_id[0] == -1:
            return await ctx.send(f"{member.mention} has been removed from {role.mention} ({team_name[0]}).", ephemeral=False)
        channel = ctx.guild.get_channel(team_channel_id[0])
        await channel.send(f"{member.mention} has been removed from {role.mention} ({team_name[0]}).")
        return await ctx.send("Member succesfully removed.", ephemeral=True)

@team.subcommand(description="Lists all the members on the entered team (or your team if nothing is entered)")
async def members(ctx: nextcord.Interaction, team: Optional[str] = nextcord.SlashOption('team')):
    await check_for_data(ctx=ctx)
    await ctx.response.defer()
    team_found = False
    async with bot.db.cursor() as cursor:
        if team == None:
            await cursor.execute("SELECT team_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
        else:
            await cursor.execute("SELECT team_id FROM teams WHERE name LIKE ? AND guild_id = ?", (team, ctx.guild.id))
        team_id = await cursor.fetchone()
        try:
            team_id = team_id[0]
        except:
            return await ctx.send("Team not found! ¯\_(ツ)_/¯", ephemeral=True)
        if team_id == 0:
            team = "Unaffiliated"
            await cursor.execute("SELECT user_id, rank_id FROM members WHERE team_id = ? AND guild_id = ?", (team_id, ctx.guild.id,))
            data = await cursor.fetchall()
            if data:
                em = nextcord.Embed(title=f"Unaffiliated Members:")
                count = 0
                for table in data:
                    count += 1
                    user = ctx.guild.get_member(table[0])
                    rank = rank_dict[table[1]]
                    em.add_field(name=f"{count}. {user.name}",
                        value=f"{rank}", inline=False)
                return await ctx.send(embed=em)
            return await ctx.send("no members/all members are in a team ¯\_(ツ)_/¯", ephemeral=True)
        
        await cursor.execute("SELECT color, name FROM teams WHERE team_id = ?", (team_id,))
        teamdata = await cursor.fetchone()
        try:
            teamcolor = teamdata[0]
        except:
            teamcolor = "#5865F2"
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT user_id, rank_id FROM members WHERE team_id = ? ORDER BY rank_id DESC", (team_id,))
            data = await cursor.fetchall()
            print(data)
            if data:
                em = nextcord.Embed(title=f"Members of {teamdata[1]}:", color=nextcord.Color(int(teamcolor.strip("#"), 16)))
                count = 0
                for table in data:
                    count += 1
                    print(table)
                    try:
                        user = ctx.guild.get_member(table[0])
                        print(user)
                        rank = rank_dict[table[1]]
                        em.add_field(name=f"{count}. {user.name}",
                                    value=f"{rank}", inline=False)
                    except:
                        print("fuck")
                        em.add_field(name=f"{count}. N/A",
                                    value="N/A", inline=False)
                return await ctx.send(embed = em)
            
@members.on_autocomplete('team')
async def members_autocompletion(ctx: nextcord.Interaction, team: str):
    async with bot.db.cursor() as cursor:
        choices = await fetch_choices(ctx.guild.id)
        if not team:
            return await ctx.response.send_autocomplete(choices[:25]) # Show the first 25 if no input
        filtered_options = [option for option in choices if team.lower() in option.lower()]
        await ctx.response.send_autocomplete(filtered_options[:25])


async def fetch_choices(guild_id):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT name FROM teams WHERE guild_id = ?", (guild_id,))
        teams = await cursor.fetchall()
        items = []
        for team in teams:
            if not (team[0] in items):
                items.append(team[0])
        return items

@team.subcommand(description="Lists all teams on the server")
async def list(ctx: nextcord.Interaction):
    global team_count
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT name, team_id FROM teams WHERE guild_id = ?", (ctx.guild.id,))
        data = await cursor.fetchall()
        team_names = []
        team_list = []
        current_teams = []
        if data:
            em = nextcord.Embed(title="All Teams:", color=nextcord.Color(int("AE02D0", 16)))
        for table in data:
                await cursor.execute("SELECT user_id FROM members WHERE team_id = ?", (table[1],))
                members = await cursor.fetchall()
                memcount = len(members)
                team_names.append(table[0])
                team_list.append((table[0],memcount))
        if len(team_list) <= 10:
            return await list_teams(team_list, ctx, None, "new", 1)
        view = PageChanger()
        team_count = 0
        current_list = []
        while team_count < 10:
            current_list.append(team_list[team_count])
            team_count += 1
            print(team_count, team_list[team_count])
        return await list_teams(current_list, ctx, view, "new",1)


@team.subcommand(description="Change your team color!")
async def color(ctx: nextcord.Interaction, color: str = nextcord.SlashOption(description="Enter a valid hex code (e.g. #FFFFFF): ")):
    async with bot.db.cursor() as cursor:
        await check_for_data(ctx=ctx)
        await cursor.execute("SELECT rank_id, team_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
        rank_id, team_id = await cursor.fetchone()
        if rank_id > MEMBER_RANK_ID:
            match = search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
            if match:
                await cursor.execute("UPDATE teams SET color = ? WHERE team_id = ?", (color, team_id,))
                await bot.db.commit()
                await cursor.execute("SELECT role_id FROM teams WHERE team_id = ?", (team_id,))
                role_id = await cursor.fetchone()
                role = ctx.guild.get_role(role_id[0])
                await role.edit(color=nextcord.Color(int(color.strip("#"), 16)))
                await ctx.send("Team color updated!")
            else:
                await ctx.send("That's not a valid hex code.", ephemeral=True)
        else:
            await ctx.send("This command is restricted to team managers.", ephemeral=True)

@team.subcommand(description="Change your team name!")
async def rename(ctx: nextcord.Interaction, name: str = nextcord.SlashOption(description="Enter a new name for your team: ")):
    async with bot.db.cursor() as cursor:
        await check_for_data(ctx=ctx)
        await cursor.execute("SELECT rank_id, team_id FROM members WHERE user_id = ? AND guild_id = ?", (ctx.user.id, ctx.guild.id,))
        rank_id, team_id = await cursor.fetchone()
        if rank_id > MEMBER_RANK_ID:
            await cursor.execute("SELECT name FROM teams WHERE guild_id = ?", (ctx.guild.id,))
            data = await cursor.fetchall()
            nametuple = (name,)
            if nametuple in data:
                return await ctx.send("There's already a team with this name!", ephemeral=True)
            await cursor.execute("SELECT role_id, channel_id, voice_channel_id, category_id, name FROM teams WHERE team_id = ?", (team_id,))
            data = await cursor.fetchall()
            data = data[0]
            print(data)
            
            role = ctx.guild.get_role(data[0])
            channel = ctx.guild.get_channel(data[1])
            vchannel = ctx.guild.get_channel(data[2])
            category = nextcord.utils.get(ctx.guild.categories, id=data[3])
            await role.edit(name=name)
            await channel.edit(name=name + "-chat")
            await vchannel.edit(name=name + "-chat")
            await category.edit(name=name)
            await cursor.execute("UPDATE teams SET name = ? WHERE team_id = ?", (name, team_id))
            await bot.db.commit()
            await ctx.send("Team name updated!")
        else:
            return await ctx.send("This command is restricted to team managers.", ephemeral=True)

@bot.slash_command(description="[ADMIN] Delete another team.", default_member_permissions = 8)
async def delteam(ctx: nextcord.Interaction, team: str = nextcord.SlashOption('team') ):       
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team_id FROM teams WHERE name LIKE ? AND guild_id = ?", (team, ctx.guild.id))
        team_id = await cursor.fetchone()
        await cursor.execute("SELECT channel_id, voice_channel_id, category_id, role_id FROM teams WHERE team_id = ?", (team_id[0],))
        data = await cursor.fetchall(); data = data[0]
        print(data)
        # Deletes channel
        channel = ctx.guild.get_channel(data[0])
        if channel != None:
            await channel.delete()
        # Deletes VC
        vchannel = ctx.guild.get_channel(data[1])
        if vchannel != None:
            await vchannel.delete()
        # Deletes category
        category = ctx.guild.get_channel(data[2])
        if category != None:
            await category.delete()
        # Deletes role
        role = ctx.guild.get_role(data[3])
        if role != None:
            await role.delete()
        # Updates teams.db
        await cursor.execute("UPDATE members SET team_id = ?, rank_id = ?, team_join_date = ? WHERE team_id = ? AND guild_id = ?", (0, MEMBER_RANK_ID, None, team_id[0], ctx.guild.id))
        await cursor.execute("DELETE FROM teams WHERE team_id = ?", (team_id[0],))
        await bot.db.commit()
        await cursor.execute("SELECT team_channel_id FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
        team_channel_id = await cursor.fetchone()
        if team_channel_id[0] == -1:
            return await ctx.send(f"\"{team}\" has been deleted.", ephemeral=False)
        channel = ctx.guild.get_channel(team_channel_id[0])
        await channel.send(f"\"{team}\" has been deleted.")
        return await ctx.send(f"Successfully deleted {team}.", ephemeral=True)
    

@delteam.on_autocomplete('team')
async def members_autocompletion(ctx: nextcord.Interaction, team: str):
    async with bot.db.cursor() as cursor:
        choices = await fetch_choices(ctx.guild.id)
        if not team:
            return await ctx.response.send_autocomplete(choices[:25]) # Show the first 25 if no input
        filtered_options = [option for option in choices if team.lower() in option.lower()]
        await ctx.response.send_autocomplete(filtered_options[:25])

# @bot.slash_command(description="[ADMIN] Reset a member's internal data (CAN BREAK TEAMS; BE CAREFUL).", default_member_permissions = 8)
# async def memreset(ctx: nextcord.Interaction, member: nextcord.Member):       
#     async with bot.db.cursor() as cursor:       
#         await cursor.execute("SELECT rank FROM teams WHERE guild = ? AND user = ?", (ctx.guild.id, member.id,))
#         rank = await cursor.fetchone()
#         if rank[0] == "Owner":
#             await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (member.id, ctx.guild.id,))
#             team = await cursor.fetchone()
#             await cursor.execute("SELECT user, rank FROM teams WHERE team = ? AND guild = ?", (team[0], ctx.guild.id,))
#             data = await cursor.fetchall()
#             print(data)
#             if len(data) > 1:
#                 return await ctx.send("This member owns a team with other members. Doing this would be a mistake.", ephemeral=True)
#         await cursor.execute("UPDATE teams SET role = ? WHERE user = ? AND guild = ?", (ctx.guild.default_role.id, member.id, ctx.guild.id,))
#         await cursor.execute("UPDATE teams SET channel = ? WHERE user = ? AND guild = ?", (ctx.guild.system_channel.id, member.id, ctx.guild.id,))
#         await cursor.execute("UPDATE teams SET vchannel = ? WHERE user = ? AND guild = ?", (ctx.guild.system_channel.id, member.id, ctx.guild.id,))
#         await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", member.id, ctx.guild.id,))
#         await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", member.id, ctx.guild.id,))
#         return await ctx.send(f"Successfully reset {member.name}.", ephemeral=True)

@bot.slash_command(description="[ADMIN] Toggle whether members can join teams, or if they have to be added.", default_member_permissions = 8)
async def join_toggle(ctx: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await check_server_for_data(ctx)
        print("bit")
        await cursor.execute("SELECT join_toggle FROM serversettings WHERE guild_id = ?", (ctx.guild.id,))
        join_toggle = await cursor.fetchone()
        if join_toggle[0] == 0:
            await cursor.execute("UPDATE serversettings SET join_toggle = ? WHERE guild_id = ?", (1, ctx.guild.id,))
            await bot.db.commit()
            print("ch")
            return await ctx.send("Joining has been enabled.", ephemeral=True)
            
        if join_toggle[0] == 1:
            await cursor.execute("UPDATE serversettings SET join_toggle = ? WHERE guild_id = ?", (0, ctx.guild.id,))
            await bot.db.commit()
            print("coin")
            return await ctx.send("Joining has been disabled.", ephemeral=True)
            
@bot.slash_command(description="[ADMIN] Set the channel for transactions (-1 to set to where the command is ran)", default_member_permissions = 8)
async def team_channel(ctx: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await check_server_for_data(ctx)
        channel = ctx.channel
        await cursor.execute("UPDATE serversettings SET team_channel_id =? WHERE guild_id = ?", (channel.id, ctx.guild.id,))      
        await bot.db.commit()
        return await ctx.send(f"Transaction channel set to {channel.mention}.", ephemeral=True)      

@bot.slash_command(description="[ADMIN] Set the maximum number of members that can be on a team (-1 to disable) ", default_member_permissions = 8)
async def maxmembers(ctx: nextcord.Interaction, max: int = nextcord.SlashOption(description="Max amount of members that can be on a team (-1 to disable maximum): ")):
    async with bot.db.cursor() as cursor:
        await check_server_for_data(ctx)
        await cursor.execute("UPDATE serversettings SET max_members =? WHERE guild_id = ?", (max, ctx.guild.id,))      
        await bot.db.commit()
        return await ctx.send(f"Maximum members set to {max}.", ephemeral=True) 

bot.run(TOKEN)
