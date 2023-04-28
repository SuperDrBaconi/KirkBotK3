import random
import discord
import asyncio
import os
from discord.ext import commands, tasks
from configparser import ConfigParser
from pypresence import Presence 


ospath = os.path.abspath(os.getcwd())
info = ConfigParser()
config = ConfigParser()
info.read(rf'{ospath}/info.ini')
config.read(rf'{ospath}/config.ini')

command_prefix = config['BOTCONFIG']['prefix']
status = info['STATUS']['status']
activity = discord.Activity(name=status, type=discord.ActivityType.watching)
started_tasks = []

class setStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        # await taskLoop('loop')
        print('Status module online')
        while not self.bot.is_closed():
            activity = discord.Activity(name=status, type=discord.ActivityType.watching)
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            await asyncio.sleep(10)
            
            activity = discord.Activity(name=f'{command_prefix}help', type=discord.ActivityType.playing)
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            await asyncio.sleep(10)
            
            activity = discord.Activity(name=f'{command_prefix}help', type=discord.Game(name=f'{command_prefix}help'))
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            await asyncio.sleep(10)

    #commands
    @commands.has_permissions(administrator=True)
    @commands.group(name='botstatus', invoke_without_command=True)
    async def botstatus_base(self, ctx):
        await ctx.channel.send(f'current status is: {status}')
    
    @commands.has_permissions(administrator=True)
    @botstatus_base.command(name='set', invoke_without_command=False)
    async def setbotstatus(self, ctx, *, statusmessage):
        message = await ctx.send(f"[1️⃣ for watching]. [2️⃣ for listening to.]")
        await message.add_reaction('1️⃣')
        await message.add_reaction('2️⃣')

        check = lambda r, u: u == ctx.author and str(r.emoji) in "1️⃣2️⃣"
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=10)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            await ctx.message.delete()
            await message.edit(content="update cancelled, timed out.")
            return

        if str(reaction.emoji) == "1️⃣":
            activity = discord.Activity(name=statusmessage, type=discord.ActivityType.watching)
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            strstatus = 'Watching'

        elif str(reaction.emoji) == "2️⃣":
            activity = discord.Activity(name=statusmessage, type=discord.ActivityType.listening)
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            strstatus = 'Listening to'

        else:
            await message.edit(content="Update cancelled.")
            return
        
        info.set('STATUS', 'status', statusmessage)

        with open(rf'{ospath}/info.ini', 'w') as infofile:
            info.write(infofile)
        await message.edit(content=f'Updated Status to: {strstatus} {statusmessage}')
        await message.clear_reactions()
    
    @commands.command(aliases=["loop1"])
    async def loop_task_one(self, ctx, *, restinput):
        # await ctx.send("")
        # task_generator(ctx, restinput)
        await taskLoop(ctx, restinput)

async def setup(bot):
    await bot.add_cog(setStatus(bot))

async def say_1_loop(restinput):
    print(restinput)


async def say_2_loop():
    print('2')


def task_generator(ctx, restinput):
    t = tasks.loop(seconds=3)(say_1_loop)
    started_tasks.append(t)
    t.start(ctx, restinput) 

@tasks.loop(seconds=10)
async def taskLoop(ctx, something):

    print(something)

# async def change_presence(self):
#     print('Waiting to start change_presence')
#     await self.bot.wait_until_ready()
#     print('change_presence started')

#     statuses = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
#     while not self.bot.is_closed():
#         status = random.choice(statuses)
#         await self.bot.change_presence(activity=discord.Game(name=status))
#         await asyncio.sleep(10)