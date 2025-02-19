ChatGPT backend Discord Chatbot with DB backend that can be reloaded based on time or conversation. 

# Setup

You need a OpenAI and Discord APP API key. 

https://discord.com/developers/docs/intro

https://platform.openai.com/docs/overview

Invite the APP from discord applications dashboard to the discord server you want to use. (usually a url link invite - then you pick the server from your own logged in)

Create a channel in the discord server called "gupp_chat", this is where it will respond. 

On main computer/server that will run this code, export keys to ENV vars OPENAPI_KEY and DISCORD_KEY

export OPENAPI_KEY=xxxxxxxxx

export DISCORD_KEY=xxxxxxxxx

# Run format

"python3 discord_main.py"

# Commands

"!<name_of_conversation>" to change to new or existing chat thread

"gupp stats" to see current convo

"list conv" to see all existing conversations

