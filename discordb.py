import discord
from discord.ext import commands, tasks
from utilities.common_ut import send_msg, listen_recv
from utilities.client_ut import connect_to_server
import sys
intents = discord.Intents.all()


class UnfilteredBot(commands.Bot):
    """An overridden version of the Bot class that will listen to other bots."""

    async def process_commands(self, message):
        """Override process_commands to listen to bots."""
        ctx = await self.get_context(message)
        await self.invoke(ctx)


client = UnfilteredBot(intents=intents, command_prefix='!')
client.socket = None 

discord_bot_token = '' #the token of your discord bot that can be obtained at discord.com/developers/applications
channel_id = 1 #id of the discord channel you plan to use to communicate with the server


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    client.socket = connect_to_server('discordb.py')
    communicationLoop.start()


@client.command()
async def cmds(ctx):
    channel = client.get_channel(channel_id)
    embed = discord.Embed(title='Commands list',description='!processes - shows currently running processes\n!kill_server - kill server and all its subprocesses',colour=discord.Colour.purple())
    await channel.send(embed=embed)
    await ctx.message.delete()
    
@client.command()
async def processes(ctx):
    send_msg(client.socket, '#discord_get_processes!')
    await ctx.message.delete()

@client.command()
async def kill_server(ctx):
    send_msg(client.socket, '#kill_server!')
    channel = client.get_channel(channel_id)
    await channel.send('kill_server command launched')
    await ctx.message.delete()

@client.command()
async def start_process(ctx, arg):
    send_msg(client.socket, '#start;'+ arg +'!')
    await ctx.message.delete()

@client.command()
async def kill_process(ctx, arg):
    send_msg(client.socket, '#kill;'+ arg +'!')
    await ctx.message.delete()

@tasks.loop(seconds = 3) 
async def communicationLoop():
    if client.socket is not None and client.socket is not False:
        msg = listen_recv(client.socket)
        if type(msg) is str:
            if msg == 'kill':
                client.socket.close()
                sys.exit()
            else:
                channel = client.get_channel(channel_id)
                await channel.send(msg)
        elif msg == False:
            client.socket.close()
            sys.exit()

client.run(discord_bot_token)


