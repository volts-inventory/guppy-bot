import discord
import core.chat_gpt as chat_gpt
import os
from datetime import datetime, timedelta

token = os.environ['DISCORD_KEY']
client = discord.Client(intents=discord.Intents.all())

current_handler = chat_gpt.Guppy()

CURRENT_TIME = datetime.now()
CURR_CONVO = "%s-%s-%s" % (CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.year)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global CURR_CONVO, CURRENT_TIME
    if message.channel.name == 'gupp_chat':
        
        if message.author == client.user:
            return
        
        if (datetime.now() - CURRENT_TIME) > timedelta(hours=24): 
            CURRENT_TIME = datetime.now()
            CURR_CONVO = "%s-%s-%s" % (CURRENT_TIME.month, CURRENT_TIME.day, CURRENT_TIME.year)
            try:
                await message.channel.send(f"New Day! Changed to topic: \"{CURR_CONVO}\"\nSet Smart Mode to False.")
            except Exception as e:
                await message.channel.send(e)


        if "!" == message.content[0]:
            CURR_CONVO = message.content[1:]
            try:
                await message.channel.send(f"Changed to topic: \"{CURR_CONVO}\"\nSet Smart Mode to False.")
            except Exception as e:
                await message.channel.send(e)
        
        elif "list conv" in str(message.content).lower():
            convos = current_handler.get_conversations(message.author.display_name)
            selection_string = "Here are the following open conversations:\n"
            for c in convos:
                selection_string += f"- {c} \n"
            await message.channel.send(selection_string)
        
        elif "gupp stats" in str(message.content).lower():
            try:
                await message.channel.send(f"Current Stats:\nCurr Convo: {CURR_CONVO}")
            except Exception as e:
                await message.channel.send(e)

        else:
            resp = str(current_handler.converse(f"{message.author.display_name}", CURR_CONVO, message.content))
            try:
                if len(resp) >= 1500:
                    paged_msgs = [resp[i:i+1500] for i in range(0, len(resp), 1500)]
                    for msg in paged_msgs:
                        await message.channel.send(f"{msg}")
                else:
                    await message.channel.send(f"{resp}")
            except Exception as e:
                await message.channel.send(e)

client.run(token)