#!/usr/bin/env python3

from twitchio.ext import commands
import data
import argparse


class Bot(commands.Bot):

    def __init__(self, token):
        super().__init__(token=token, prefix='<unused>')

        # Default channel settings
        self.data = data.Data({
            'prefix': '!'
        })

    # todo: Allow users change advanced settings (like resetting the prefix) from the bot channel's chat

    async def event_ready(self):
        print(f'Logged in as "{self.nick}"\n')
        if self.nick not in self.data.channel_list():
            self.data.channel_add(self.nick)
        await bot.join_channels(self.data.channel_list())

    async def event_message(self, message):
        if message.echo:
            return

        channel = message.channel
        prefix = self.data.channel_setting(channel.name, 'prefix')
        if not message.content.startswith(prefix) or len(message.content) - len(prefix) < 1:
            return

        cmd = message.content.split(' ')[0][len(prefix):]
        args = message.content.strip().split(' ')[1:]
        privileged = message.author.is_mod or channel.name == message.author.name

        # keep up to date with changes to the tree below!
        internal_commands = ['botcommands', 'botjoin']
        internal_commands_privileged = ['botprefix', 'addcmd', 'removecmd', 'botleave']
        if cmd in internal_commands_privileged and not privileged:
            return

        # Don't forget to update the internal_commands lists with changes made below!
        if cmd == 'botcommands':
            cmdlist = self.data.command_list(channel.name) + internal_commands
            if privileged:
                cmdlist += internal_commands_privileged
            cmdlist = [f'{prefix}{cmd}' for cmd in cmdlist]
            await channel.send(f'Available commands: {", ".join(cmdlist)}')
        elif cmd == 'botjoin':
            await channel.send('Thank you for adding me to your channel!'
                               f' My prefix will be "{self.data.default_channel_data["settings"]["prefix"]}".')
            self.data.channel_add(message.author.name)
            await self.join_channels([message.author.name])

            # This whole damn message doesn't send because the author.send function doesn't work. >:(
            await message.author.send("Hello! Thanks again for adding me."
                                      " Send !bothelp in your channel's chat for more info."
                                      " Small reminder:"
                                      " while chat restrictions are enabled,"
                                      " I cannot talk in your chat unless you make me a moderator."
                                      " I won't (and can't) change anything or ban anyone though!")
        elif cmd == 'botprefix':
            self.data.channel_setting(channel.name, 'prefix', args[0])
            await channel.send(f'Prefix is now set to "{args[0]}"')
        elif cmd == 'addcmd':
            exists = args[0] in self.data.command_list(channel.name)
            self.data.command_add(channel.name, args[0], {
                'type': 'echo',
                'text': ' '.join(args[1:])
            })
            await channel.send(f'Command {"modified" if exists else "added"}: {prefix}{args[0]}')
        elif cmd == 'removecmd':
            if args[0] in self.data.command_list(channel.name):
                self.data.command_remove(channel.name, args[0])
                await channel.send(f'Command removed: {prefix}{args[0]}')
            else:
                await channel.send(f'Command not found: {prefix}{args[0]}')
        elif cmd == 'botleave':
            if not message.author.channel == channel:
                return
            # await channel.send('Thank you for letting me be part of your channel, it was a pleasure! Goodbye.')
            await channel.send(
                "I can't leave channels yet due to this bug: https://github.com/TwitchIO/TwitchIO/issues/206")
            await channel.send("You can change my prefix to something unobtrusive instead.")
        else:
            if cmd in self.data.command_list(channel.name):
                command = self.data.command_get(channel.name, cmd)
                if command['type'] == 'echo':
                    await channel.send(command['text'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("token", help="Oauth token for Twitch authentication")
    args = parser.parse_args()
    bot = Bot(args.token)
    bot.run()
