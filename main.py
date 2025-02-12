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
intents = nextcord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents)
dotenv_path = Path("G:\Downloads\Teams\secrets.env")
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv('TOKEN')
all_teams = ("sample team")

@bot.event
async def on_ready():
    global all_teams
    server_count = len(bot.guilds)
    print(f'{bot.user.name} is now online in {server_count} server(s)')
    setattr(bot, "db", await aiosqlite.connect("teams.db"))
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS teams (user INTEGER, guild INTEGER, team STRING, rank STRING, role INTEGER, teamcolor STRING, channel INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS serversettings (guild INTEGER, jointoggle INTEGER, maxmembers INTEGER, teamchannel INTEGER)")

async def check_for_data(ctx: nextcord.Interaction):
    if type(ctx) == nextcord.Message:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (ctx.author.id, ctx.guild.id,))
            team = await cursor.fetchone()
            await cursor.execute("SELECT rank FROM teams WHERE user = ? AND guild = ?", (ctx.author.id, ctx.guild.id,))
            rank = await cursor.fetchone()

            if not team or not rank:
                await cursor.execute("INSERT INTO teams (team, rank, user, guild, role) VALUES (?, ?, ?, ?, ?)", ("Unaffiliated", "Member", ctx.author.id, ctx.guild.id, ctx.guild.default_role.id))

            try:

                team = team[0]
                rank = rank[0]

                if str(team) == "None" or str(rank) == "None":
                    await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", ctx.author.id, ctx.guild.id,))
                    await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", ctx.author.id, ctx.guild.id,))

            except TypeError:
                await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", ctx.author.id, ctx.guild.id,))
                await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", ctx.author.id, ctx.guild.id,))
        await bot.db.commit()
    else:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
            team = await cursor.fetchone()
            await cursor.execute("SELECT rank FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
            rank = await cursor.fetchone()

            if not team or not rank:
                await cursor.execute("INSERT INTO teams (team, rank, user, guild, role) VALUES (?, ?, ?, ?, ?)", ("Unaffiliated", "Member", ctx.user.id, ctx.guild.id, ctx.guild.default_role.id))

            try:

                team = team[0]
                rank = rank[0]

                if str(team) == "None" or str(rank) == "None":
                    await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", ctx.user.id, ctx.guild.id,))
                    await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", ctx.user.id, ctx.guild.id,))

            except TypeError:
                await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", ctx.user.id, ctx.guild.id,))
                await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", ctx.user.id, ctx.guild.id,))
        await bot.db.commit()

async def check_member_for_data(ctx: nextcord.Interaction, member: nextcord.Member):
    if type(ctx) == nextcord.Message:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (member.id, ctx.guild.id,))
            team = await cursor.fetchone()
            await cursor.execute("SELECT rank FROM teams WHERE user = ? AND guild = ?", (member.id, ctx.guild.id,))
            rank = await cursor.fetchone()

            if not team or not rank:
                await cursor.execute("INSERT INTO teams (team, rank, user, guild, role) VALUES (?, ?, ?, ?, ?)", ("Unaffiliated", "Member", member.id, ctx.guild.id, ctx.guild.default_role.id))

            try:

                team = team[0]
                rank = rank[0]

                if str(team) == "None" or str(rank) == "None":
                    await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", member.id, ctx.guild.id,))
                    await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", member.id, ctx.guild.id,))

            except TypeError:
                await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", member.id, ctx.guild.id,))
                await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", member.id, ctx.guild.id,))
        await bot.db.commit()
    else:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (member.id, ctx.guild.id,))
            team = await cursor.fetchone()
            await cursor.execute("SELECT rank FROM teams WHERE user = ? AND guild = ?", (member.id, ctx.guild.id,))
            rank = await cursor.fetchone()

            if not team or not rank:
                await cursor.execute("INSERT INTO teams (team, rank, user, guild, role) VALUES (?, ?, ?, ?, ?)", ("Unaffiliated", "Member", member.id, ctx.guild.id, ctx.guild.default_role.id))

            try:

                team = team[0]
                rank = rank[0]

                if str(team) == "None" or str(rank) == "None":
                    await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", member.id, ctx.guild.id,))
                    await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", member.id, ctx.guild.id,))

            except TypeError:
                await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", member.id, ctx.guild.id,))
                await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", member.id, ctx.guild.id,))
        await bot.db.commit()

async def check_server_for_data(ctx: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT guild FROM serversettings WHERE guild = ?", (ctx.guild.id,))
        guild = await cursor.fetchone()
        print(guild)
        if not guild:
            await cursor.execute("INSERT INTO serversettings (guild, jointoggle, maxmembers, teamchannel) VALUES (?, ?, ?, ?)", (ctx.guild.id, 0, -1, -1,))
    await bot.db.commit()

class DelPrompt(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Yes', style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        async with bot.db.cursor() as cursor:
            # Deletes channel
            await cursor.execute("SELECT channel FROM teams WHERE guild = ? AND user = ?", (ctx.guild.id, ctx.user.id))
            channel = await cursor.fetchone()
            channel = ctx.guild.get_channel(channel[0])
            await channel.delete()
            # Deletes VC
            await cursor.execute("SELECT vchannel FROM teams WHERE guild = ? AND user = ?", (ctx.guild.id, ctx.user.id))
            vchannel = await cursor.fetchone()
            vchannel = ctx.guild.get_channel(vchannel[0])
            await vchannel.delete()
            # Deletes category
            await cursor.execute("SELECT category FROM teams WHERE guild = ? AND user = ?", (ctx.guild.id, ctx.user.id))
            category = await cursor.fetchone()
            category = ctx.guild.get_channel(category[0])
            await category.delete()
            # Deletes role
            await cursor.execute("SELECT role FROM teams WHERE guild = ? AND user = ?", (ctx.guild.id, ctx.user.id))
            role = await cursor.fetchone()
            role = ctx.guild.get_role(role[0])
            await role.delete()
            # Updates teams.db
            await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET role = ? WHERE user = ? AND guild = ?", (ctx.guild.default_role.id, ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET channel = ? WHERE user = ? AND guild = ?", (ctx.guild.system_channel.id, ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET vchannel = ? WHERE user = ? AND guild = ?", (ctx.guild.system_channel.id, ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", ctx.user.id, ctx.guild.id,))
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
async def on_message(ctx):
    global all_teams
    async with bot.db.cursor() as cursor:
        await check_for_data(ctx=ctx)
        await cursor.execute("SELECT team FROM teams WHERE guild = ?", (ctx.guild.id,))
        all_teams = await cursor.fetchall()
    await bot.process_commands(ctx)

def hex_to_rgb(value):
    value = value.lstrip('#').rstrip(";")
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))




@bot.slash_command()
async def team(interaction: nextcord.Interaction):
    pass

@team.subcommand(description="help me")
async def ohmygod(interaction: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await check_server_for_data(ctx=interaction)
        print('call me a good boy')

@team.subcommand(description="create a new team")
async def create(ctx: nextcord.Interaction, name: str = nextcord.SlashOption(description="Enter your team's name:"), color: str = nextcord.SlashOption(description="Enter a valid hex code for your team's color (e.g. #FFFFFF):")):
    await check_for_data(ctx=ctx)
    await ctx.response.defer()
    match = search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
    if match:
        async with bot.db.cursor() as cursor:
            if len(name) > 20:
                return await ctx.send("This team's name is too long! Keep team names under 15 characters.", ephemeral=True)
            await cursor.execute("SELECT team FROM teams WHERE guild = ?", (ctx.guild.id,))
            data = await cursor.fetchall()
            nametuple = (name,)
            if nametuple in data:
                return await ctx.send("This team already exists! Try using /team join instead.", ephemeral=True)
            await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
            team = await cursor.fetchone()
            if team[0] != "Unaffiliated":
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
            vchannel = await ctx.guild.create_voice_channel(name=name + "-chat", overwrites=overwrites, category=category)
            await cursor.execute("UPDATE teams SET role = ? WHERE user = ? AND guild = ?", (role.id, ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", (name, ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Owner", ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET teamcolor = ? WHERE user = ? AND guild = ?", (color, ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET channel = ? WHERE user = ? AND guild = ?", (channel.id, ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET vchannel = ? WHERE user = ? AND guild = ?", (vchannel.id, ctx.user.id, ctx.guild.id,))
            await cursor.execute("UPDATE teams SET category = ? WHERE user = ? AND guild = ?", (category.id, ctx.user.id, ctx.guild.id,))
            await bot.db.commit()
            await cursor.execute("SELECT teamchannel FROM serversettings WHERE guild = ?", (ctx.guild.id,))
            teamchannel = await cursor.fetchone()
            if teamchannel[0] == -1:
                return await ctx.send(f"{role.mention} ({name}) has been created by {ctx.user.mention}.", ephemeral=False)
            channel = ctx.guild.get_channel(teamchannel[0])
            await channel.send(f"{role.mention} ({name}) has been created by {ctx.user.mention}.")
            return await ctx.send("Team succesfully created!", ephemeral=True)
    else:
        await ctx.send("That's not a valid hex code.", ephemeral=True)




@team.subcommand(description="join a team")
async def join(ctx: nextcord.Interaction, name: str = nextcord.SlashOption(description="Enter the name of the team you want to join:")):
        
        await check_for_data(ctx=ctx)
        if name.lower() == "unaffiliated":
            return await ctx.send("That's not a team!", ephemeral=True)
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT jointoggle FROM serversettings WHERE guild = ?", (ctx.guild.id,))
            jointoggle = await cursor.fetchone()
            if jointoggle[0] == 0:
                return await ctx.send("Joining is disabled on this server.", ephemeral=True)            
            await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
            team = await cursor.fetchone()
            if team[0] != "Unaffiliated":
                return await ctx.send(f"You're already in this team: {team[0]}. Try using /team leave first.", ephemeral=True)
            await cursor.execute("SELECT team FROM teams WHERE guild = ?", (ctx.guild.id,))
            data = await cursor.fetchall()
            print()
            teamslower = [[(word.lower()) for word in element]
                                for element in data]
            count = 0
            print(teamslower)
            print(name.lower)
            for team in teamslower:
                if [name.lower()] == teamslower[count]:
                    team_found = True
                    print(teamslower[count])
                else:
                    count += 1
            if team_found:
                print(count)
                team = data[count][0]
                await cursor.execute("SELECT role FROM teams WHERE team = ? AND guild = ? AND rank = ?", (team, ctx.guild.id, "Owner"))
                role = await cursor.fetchone()
                role = ctx.guild.get_role(role[0])
                await ctx.user.add_roles(role)
                await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", (team, ctx.user.id, ctx.guild.id,))
                await bot.db.commit()
                await cursor.execute("SELECT teamchannel FROM serversettings WHERE guild = ?", (ctx.guild.id,))
                teamchannel = await cursor.fetchone()
                if teamchannel[0] == -1:
                    return await ctx.send(f"{ctx.user.mention} has joined {role.mention} ({data[count][0]}).", ephemeral=False)
                channel = ctx.guild.get_channel(teamchannel[0])
                await channel.send(f"{ctx.user.mention} has joined {role.mention} ({data[count][0]})!")
                return await ctx.send(f"Successfully joined {role.mention} ({data[count][0]})!", ephemeral=True)
            else:
                return await ctx.send("This team doesn't exist! Try using /team create instead.", ephemeral=True)
            
@join.on_autocomplete('name')
async def members_autocompletion(ctx: nextcord.Interaction, team: str):
    async with bot.db.cursor() as cursor:
        choices = await fetch_choices(ctx.guild.id)
        print(choices)
        choices.remove("Unaffiliated")
        await ctx.response.send_autocomplete(choices)


@team.subcommand(description="Add someone to a team")
async def add(ctx: nextcord.Interaction, member: nextcord.Member):
        await check_for_data(ctx=ctx)
        await check_member_for_data(ctx, member)
        async with bot.db.cursor() as cursor:            
            await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (member.id, ctx.guild.id,))
            mem_team = await cursor.fetchone()
            if mem_team[0] != "Unaffiliated":
                return await ctx.send("This member is already in a team! Don't be a thief.", ephemeral=True)
            await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
            team = await cursor.fetchone()
            if team[0] == "Unaffiliated":
                return await ctx.send("You're not even in a team! Try using /team create first.", ephemeral=True)
            await cursor.execute("SELECT rank FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
            rank = await cursor.fetchone()
            if rank[0] != "Owner":
                return await ctx.send("Only a team's owner can add members to a team.", ephemeral=True)
            await cursor.execute("SELECT maxmembers FROM serversettings WHERE guild = ?", (ctx.guild.id,))
            maxmembers = await cursor.fetchone()
            if maxmembers[0] != -1:
                await cursor.execute("SELECT user FROM teams WHERE team = ? AND guild = ?", (team[0], ctx.guild.id,))
                data = await cursor.fetchall()
                if data:
                    count = 0
                    for table in data:
                        count += 1
                if count >= maxmembers[0]:
                    return await ctx.send(f"Your team is already at max capacity! Max members on this server is {maxmembers[0]}.", ephemeral=True)
            await cursor.execute("SELECT role FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
            role = await cursor.fetchone()
            role = ctx.guild.get_role(role[0])
            await member.add_roles(role)
            await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", (team[0], member.id, ctx.guild.id,))
            await bot.db.commit()
            await cursor.execute("SELECT teamchannel FROM serversettings WHERE guild = ?", (ctx.guild.id,))
            teamchannel = await cursor.fetchone()
            if teamchannel[0] == -1:
                return await ctx.send(f"{member.mention} has been added to {role.mention} ({team[0]}).", ephemeral=False)
            channel = ctx.guild.get_channel(teamchannel[0])
            await channel.send(f"{member.mention} has been added to {role.mention} ({team[0]}).")
            return await ctx.send("Member succesfully added.", ephemeral=True)

@team.subcommand(description="Transfer ownership of your team")
async def transfer(ctx: nextcord.Interaction, member: nextcord.Member):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
        team = await cursor.fetchone()
        if team[0] == "Unaffiliated":
            return await ctx.send("You're not in any teams!", ephemeral=True)
        await cursor.execute("SELECT rank FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
        rank = await cursor.fetchone()
        if rank[0] == "Owner":
            await cursor.execute("SELECT user, rank FROM teams WHERE team = ? AND guild = ?", (team[0], ctx.guild.id,))
            data = await cursor.fetchall()
            if len(data) == 1:
                return await ctx.send("You can't transfer ownership if you're the only member!", ephemeral=True)
            else:
                await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (member.id, ctx.guild.id,))
                mem_team = await cursor.fetchone()
                if mem_team != team:
                    return await ctx.send("You can't transfer ownership to someone who isn't on your team.", ephemeral=True)
                view = TraPrompt()
                await ctx.send(f"Are you sure you would like to transfer ownership of {team[0]} to {member}?", ephemeral=True, view=view)
                await view.wait()
                if view.value is None:
                    return
                elif view.value:
                    await cursor.execute("SELECT teamcolor FROM teams WHERE team = ? AND guild = ? AND rank = ?", (team[0], ctx.guild.id, "Owner"))
                    color = await cursor.fetchone()
                    await cursor.execute("UPDATE teams SET teamcolor = ? WHERE user = ? AND guild = ?", (color[0], member.id, ctx.guild.id,))

                    await cursor.execute("SELECT channel FROM teams WHERE team = ? AND guild = ? AND rank = ?", (team[0], ctx.guild.id, "Owner"))
                    channel = await cursor.fetchone()
                    await cursor.execute("UPDATE teams SET channel = ? WHERE user = ? AND guild = ?", (channel[0], member.id, ctx.guild.id,))

                    await cursor.execute("SELECT vchannel FROM teams WHERE team = ? AND guild = ? AND rank = ?", (team[0], ctx.guild.id, "Owner"))
                    vchannel = await cursor.fetchone()
                    await cursor.execute("UPDATE teams SET vchannel = ? WHERE user = ? AND guild = ?", (vchannel[0], member.id, ctx.guild.id,))
                    
                    await cursor.execute("SELECT category FROM teams WHERE team = ? AND guild = ? AND rank = ?", (team[0], ctx.guild.id, "Owner"))
                    category = await cursor.fetchone()
                    await cursor.execute("UPDATE teams SET category = ? WHERE user = ? AND guild = ?", (category[0], member.id, ctx.guild.id,))

                    await cursor.execute("SELECT role FROM teams WHERE team = ? AND guild = ? AND rank = ?", (team[0], ctx.guild.id, "Owner"))
                    role = await cursor.fetchone()
                    await cursor.execute("UPDATE teams SET role = ? WHERE user = ? AND guild = ?", (role[0], member.id, ctx.guild.id,))

                    await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Owner", member.id, ctx.guild.id,))
                    await cursor.execute("UPDATE teams SET rank = ? WHERE user = ? AND guild = ?", ("Member", ctx.user.id, ctx.guild.id,)) 
                    await bot.db.commit()

                    return await ctx.send(f"Successfully transferred ownership to {member}.", ephemeral=True)
                else:
                    return await ctx.send("Transfer request canceled.", ephemeral=True)
        else:
            return await ctx.send("You can't transfer ownership if you aren't the owner.", ephemeral=True)
        
@team.subcommand(description="Leave your current team")
async def leave(ctx: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
        team = await cursor.fetchone()
        if team[0] == "Unaffiliated":
            return await ctx.send("You're not in any teams!", ephemeral=True)
        await cursor.execute("SELECT rank FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
        rank = await cursor.fetchone()
        if rank[0] == "Owner":
            await cursor.execute("SELECT user, rank FROM teams WHERE team = ? AND guild = ?", (team[0], ctx.guild.id,))
            data = await cursor.fetchall()
            if len(data) > 1:
                return await ctx.send("You can't leave a team with members that you're the owner of! Try transferring ownership first.", ephemeral=True)
            else:
                view = DelPrompt()
                await ctx.send(f"Are you sure you would like to leave {team[0]}? This will delete the team!", ephemeral=True, view=view)
                await view.wait()
                if view.value is None:
                    return
                elif view.value:
                    await cursor.execute("SELECT teamchannel FROM serversettings WHERE guild = ?", (ctx.guild.id,))
                    teamchannel = await cursor.fetchone()
                    if teamchannel[0] == -1:
                        return await ctx.send(f"{team[0]} has been disbanded!", ephemeral=False)
                    channel = ctx.guild.get_channel(teamchannel[0])
                    await channel.send(f"\"{team[0]}\" has been disbanded!")
                    return await ctx.send(f"Successfully deleted {team[0]}", ephemeral=True)
                else:
                    return await ctx.send("Deletion request canceled.", ephemeral=True)

        await cursor.execute("SELECT role FROM teams WHERE team = ? AND guild = ? AND rank = ?", (team[0], ctx.guild.id, "Owner"))
        role = await cursor.fetchone()
        role = ctx.guild.get_role(role[0])
        await ctx.user.remove_roles(role)
        await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", ctx.user.id, ctx.guild.id,))
        await cursor.execute("UPDATE teams SET role = ? WHERE user = ? AND guild = ?", (ctx.guild.default_role.id, ctx.user.id, ctx.guild.id,))
        await bot.db.commit()
        await cursor.execute("SELECT teamchannel FROM serversettings WHERE guild = ?", (ctx.guild.id,))
        teamchannel = await cursor.fetchone()
        if teamchannel[0] == -1:
            return await ctx.send(f"{ctx.user.mention} has left {role.mention} ({team[0]}).", ephemeral=False)
        channel = ctx.guild.get_channel(teamchannel[0])
        await channel.send(f"{ctx.user.mention} has left {role.mention} ({team[0]}).")
        return await ctx.send(f"Succesfully left {role.mention} ({team[0]}).", ephemeral=True)

@team.subcommand(description="Remove someone from your team")
async def remove(ctx: nextcord.Interaction, member:nextcord.Member):
    await check_for_data(ctx=ctx)
    await check_member_for_data(ctx, member)
    if member.id == ctx.user.id:
            return await ctx.send("You can't remove *yourself* from a team -- try /team leave instead.", ephemeral=True)            
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
        team = await cursor.fetchone()
        if team[0] == "Unaffiliated":
            return await ctx.send("You're not even in a team! Nice try, though.", ephemeral=True)
        await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (member.id, ctx.guild.id,))
        mem_team = await cursor.fetchone()
        if mem_team[0] != team[0]:
            return await ctx.send("This member isn't even on your team!", ephemeral=True)
        await cursor.execute("SELECT rank FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
        rank = await cursor.fetchone()
        if rank[0] != "Owner":
            return await ctx.send("Only a team's owner can remove members from a team.", ephemeral=True)

        await cursor.execute("SELECT role FROM teams WHERE team = ? AND guild = ? AND rank = ?", (team[0], ctx.guild.id, "Owner"))
        role = await cursor.fetchone()
        role = ctx.guild.get_role(role[0])
        await member.remove_roles(role)
        await cursor.execute("UPDATE teams SET team = ? WHERE user = ? AND guild = ?", ("Unaffiliated", member.id, ctx.guild.id,))
        await cursor.execute("UPDATE teams SET role = ? WHERE user = ? AND guild = ?", (ctx.guild.default_role.id, member.id, ctx.guild.id,))
        await bot.db.commit()
        await cursor.execute("SELECT teamchannel FROM serversettings WHERE guild = ?", (ctx.guild.id,))
        teamchannel = await cursor.fetchone()
        if teamchannel[0] == -1:
            return await ctx.send(f"{member.mention} has been removed from {role.mention} ({team[0]}).", ephemeral=False)
        channel = ctx.guild.get_channel(teamchannel[0])
        await channel.send(f"{member.mention} has been removed from {role.mention} ({team[0]}).")
        return await ctx.send("Member succesfully removed.", ephemeral=True)

@team.subcommand(description="Lists all the members on the entered team (or your team if nothing is entered)")
async def members(ctx: nextcord.Interaction, team: Optional[str] = nextcord.SlashOption('team')):
    await check_for_data(ctx=ctx)
    team_found = False
    async with bot.db.cursor() as cursor:
        if team == None:
            await cursor.execute("SELECT team FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
            team = await cursor.fetchone()
            team = team[0]
        if team.lower() == "unaffiliated":
            team = "Unaffiliated"
            await cursor.execute("SELECT user, rank FROM teams WHERE team = ? AND guild = ?", (team, ctx.guild.id,))
            data = await cursor.fetchall()
            if data:
                em = nextcord.Embed(title=f"Unaffiliated Members:")
                count = 0
                for table in data:
                    count += 1
                    user = ctx.guild.get_member(table[0])
                    rank = table[1]
                    em.add_field(name=f"{count}. {user.name}",
                        value=f"{rank}", inline=False)
                return await ctx.send(embed=em)
            return await ctx.send("no members/all members are in a team ¯\_(ツ)_/¯", ephemeral=True)
        
        await cursor.execute("SELECT team FROM teams WHERE guild = ?", (ctx.guild.id,))
        data = await cursor.fetchall()
        teamslower = [[(word.lower()) for word in element]
                      for element in data]
        count = 0
        print(teamslower)
        print(team.lower())
        for name in teamslower:
            if [team.lower()] == teamslower[count]:
                team_found = True
                print(teamslower[count])
            else:
                count += 1
        if not team_found:
            return await ctx.send("this team doesn't exist/it has no members ¯\_(ツ)_/¯", ephemeral=True)
        print(count)
        team = data[count][0]
        await cursor.execute("SELECT teamcolor FROM teams WHERE team = ? AND guild = ? AND rank = ?", (team, ctx.guild.id, "Owner"))
        teamcolor = await cursor.fetchone()
        try:
            teamcolor = teamcolor[0]
        except:
            teamcolor = "#5865F2"
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT user, rank FROM teams WHERE team = ? AND guild = ? ORDER BY rank DESC", (team, ctx.guild.id,))
            data = await cursor.fetchall()
            if data:
                em = nextcord.Embed(title=f"Members of {team}:", color=nextcord.Color(int(teamcolor.strip("#"), 16)))
                count = 0
                for table in data:
                    count += 1
                    user = ctx.guild.get_member(table[0])
                    rank = table[1]
                    em.add_field(name=f"{count}. {user.name}",
                                value=f"{rank}", inline=False)
                return await ctx.send(embed = em)
            
@members.on_autocomplete('team')
async def members_autocompletion(ctx: nextcord.Interaction, team: str):
    async with bot.db.cursor() as cursor:
        choices = await fetch_choices(ctx.guild.id)
        await ctx.response.send_autocomplete(choices)


async def fetch_choices(guild_id):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team FROM teams WHERE guild = ?", (guild_id,))
        teams = await cursor.fetchall()
        items = []
        for team in teams:
            if not (team[0] in items):
                items.append(team[0])
        return items

@team.subcommand(description="Lists all teams on the server")
async def list(ctx: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT team FROM teams WHERE guild = ?", (ctx.guild.id,))
        data = await cursor.fetchall()
        current_teams = []
        if data:
            em = nextcord.Embed(title="All Teams:", color=nextcord.Color(int("AE02D0", 16)))
            for table in data:
                if not table[0] in current_teams and table[0] != "Unaffiliated":
                    await cursor.execute("SELECT user FROM teams WHERE guild = ? AND team = ?", (ctx.guild.id, table[0]))
                    members = await cursor.fetchall()
                    memcount = len(members)
                    em.add_field(name=f"{table[0].title()}",
                        value=f"Members: {memcount}", inline=False)
                    current_teams.append(table[0])
                else:
                    pass
                current_teams.append(table[0])
            await cursor.execute("SELECT user FROM teams WHERE guild = ? AND team = ?", (ctx.guild.id, "Unaffiliated"))
            members = await cursor.fetchall()
            memcount = len(members)
            em.add_field(name='\u200b',
                            value=f"Unaffiliated Members: {memcount}", inline=False)
                
            return await ctx.send(embed=em)


@team.subcommand(description="Change your team color!")
async def color(ctx: nextcord.Interaction, color: str = nextcord.SlashOption(description="Enter a valid hex code (e.g. #FFFFFF): ")):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT rank FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))
        rank = await cursor.fetchone()
        if rank[0] == "Owner":
            match = search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
            if match:
                    await cursor.execute("UPDATE teams SET teamcolor = ? WHERE user = ? AND guild = ?", (color, ctx.user.id, ctx.guild.id,))
                    await bot.db.commit()
                    await cursor.execute("SELECT role FROM teams WHERE user = ? AND guild = ?", (ctx.user.id, ctx.guild.id,))

                    role = await cursor.fetchone()
                    role = ctx.guild.get_role(role[0])
                    await role.edit(color=nextcord.Color(int(color.strip("#"), 16)))
                    await ctx.send("Team color updated!")

            else:
                await ctx.send("That's not a valid hex code.", ephemeral=True)
        else:
            await ctx.send("Only a team's owner can run this command.", ephemeral=True)

@bot.slash_command(description="Toggle whether members can join teams, or if they have to be added.", default_member_permissions = 8)
async def jointoggle(ctx: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await check_server_for_data(ctx)
        print("bit")
        await cursor.execute("SELECT jointoggle FROM serversettings WHERE guild = ?", (ctx.guild.id,))
        jointoggle = await cursor.fetchone()
        if jointoggle[0] == 0:
            await cursor.execute("UPDATE serversettings SET jointoggle = ? WHERE guild = ?", (1, ctx.guild.id,))
            await bot.db.commit()
            print("ch")
            return await ctx.send("Joining has been enabled.", ephemeral=True)
            
        if jointoggle[0] == 1:
            await cursor.execute("UPDATE serversettings SET jointoggle = ? WHERE guild = ?", (0, ctx.guild.id,))
            await bot.db.commit()
            print("coin")
            return await ctx.send("Joining has been disabled.", ephemeral=True)
            
@bot.slash_command(description="Set the channel for transactions (-1 to set to where the command is ran)", default_member_permissions = 8)
async def teamchannel(ctx: nextcord.Interaction):
    async with bot.db.cursor() as cursor:
        await check_server_for_data(ctx)
        channel = ctx.channel
        await cursor.execute("UPDATE serversettings SET teamchannel =? WHERE guild = ?", (channel.id, ctx.guild.id,))      
        await bot.db.commit()
        return await ctx.send(f"Transaction channel set to {channel.mention}.", ephemeral=True)      

@bot.slash_command(description="Set the maximum number of members that can be on a team (-1 to disable) ", default_member_permissions = 8)
async def maxmembers(ctx: nextcord.Interaction, max: int = nextcord.SlashOption(description="Max amount of members that can be on a team (-1 to disable maximum): ")):
    async with bot.db.cursor() as cursor:
        await check_server_for_data(ctx)
        await cursor.execute("UPDATE serversettings SET maxmembers =? WHERE guild = ?", (max, ctx.guild.id,))      
        await bot.db.commit()
        return await ctx.send(f"Maximum members set to {max}.", ephemeral=True) 

bot.run(TOKEN)
