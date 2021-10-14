#!/bin/python3
import discord
import re
import asyncio
import requests
from random import choice
from time import time
from discord.ext import commands
from configparser import ConfigParser
from discord_components import *

parser = ConfigParser()
parser.read('config.ini')


async def send_webhook(avatar_url, message, name, channel):
    hooks = await channel.webhooks()
    if not hooks or 'lovense' not in [hook.name for hook in hooks]:
        new_hook = await channel.create_webhook(name="lovense")
        data = {'content': message,
                'username': str(name),
                'avatar_url': str(avatar_url)}
        requests.post(new_hook.url, data=data)
        return
    for hook in hooks:
        if hook.name == 'lovense':
            data = {'content': message,
                    'username': str(name),
                    'avatar_url': str(avatar_url)}
            requests.post(hook.url, data=data)
            return


class Raffle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DiscordComponents(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        lovense_link = re.findall(r'https://c.lovense.com/c/\w\w\w\w\w\w', message.content)
        if lovense_link == []:
            return
        else:
            await message.delete()
            lovense_channel = message.guild.get_channel(parser.getint('channels', 'lovense'))
            n = await lovense_channel.send(f"{message.author.mention}")
            raffle_request_embed = discord.Embed(title='Do you want to raffle your lovense link.', colour=0xF21D92)

            m = await lovense_channel.send(embed=raffle_request_embed, components=[[Button(style=ButtonStyle.green, label='Yes'),
                                                                                    Button(style=ButtonStyle.red, label='No')]])

            try:
                def check(res):
                    return message.author == res.user
                response = await self.bot.wait_for('Button_click', timeout=60, check=check)

                if response.component.label == 'Yes':
                    await n.delete()
                    await m.delete()
                    o = await lovense_channel.send(f"<@&{parser.getint('roles', 'lovense')}>")
                    raffle_embed = discord.Embed(title="It's raffle time.",
                                                 description=f"Who is the lucky one to win {message.author.mention}'s lovense link\nreact with ✅ to get a chance to win.\n> time remaining: <t:{str(time() + 60)[:10]}:R>",
                                                 colour=0xF21D92)
                    raffle_embed.set_thumbnail(url=message.author.avatar_url)
                    box = await lovense_channel.send(embed=raffle_embed)
                    await box.add_reaction('✅')

                    await asyncio.sleep(60)
                    box = await lovense_channel.fetch_message(box.id)
                    users = await box.reactions[0].users().flatten()
                    try:
                        users.pop(users.index(self.bot.user))
                        users.pop(users.index(message.author))
                    except ValueError:
                        pass

                    if users == []:
                        await o.delete()
                        await box.delete()
                        await send_webhook(message.author.avatar_url, message.content, message.author.nick or message.author.name, lovense_channel)
                    else:
                        winner = choice(users)
                        raffle_win_embed = discord.Embed(title='Lovense link winner is',
                                                         description=f"{winner.mention} has won the raffle. The link will now be sent via DMs.",
                                                         colour=0xF21D92)
                        raffle_win_embed.set_thumbnail(url=message.author.avatar_url)
                        await box.edit(embed=raffle_win_embed)

                        raffle_DM_embed = discord.Embed(title='You Won the lovense link',
                                                        description=f"Congratulations! You won {message.author.mention}'s lovense link. Have fun!\n> {lovense_link[0]}",
                                                        colour=0xF21D92)

                        await winner.send(embed=raffle_DM_embed)

                elif response.component.label == 'No':
                    await n.delete()
                    await m.delete()
                    await send_webhook(message.author.avatar_url, message.content, message.author.nick or message.author.name, lovense_channel)

            except asyncio.TimeoutError:
                await n.delete()
                await m.delete()
                await send_webhook(message.author.avatar_url, message.content, message.author.nick or message.author.name, lovense_channel)


def setup(bot):
    bot.add_cog(Raffle(bot))
