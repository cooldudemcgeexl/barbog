
import logging
import os
import discord
import re
import openai
from discord import user
from discord.ext import commands
from openai.api_resources import engine

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
OPENAI_MODEL_ID = os.getenv("OPENAI_MODEL_ID")


logging.basicConfig(
    handlers=[logging.FileHandler('botlog.log', 'a', 'utf-8')],
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] - %(message)s')
logger = logging.getLogger()

enabled = False

bot = commands.Bot(command_prefix='$')

def generate_openai_message(user_prompt: str) -> str:
    bot_response = openai.Completion.create(
        model=OPENAI_MODEL_ID,
        prompt=user_prompt,
        temperature=0.7,
        max_tokens=128,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )  
    return bot_response.choices[0].text



@bot.command(name='toggle', help= 'Toggles text generation')
async def toggle_sending(ctx):
    global enabled
    enabled = not enabled
    await ctx.send(f"Barbog {'enabled' if enabled else 'disabled'}.")
    return

@bot.event
async def on_ready():
    print(f"Connected as {bot.user}")
    return

@bot.event
async def on_message(message: discord.message.Message):
    if message.author == bot.user:
        logger.info(f"Message sent in channel ({message.channel.name}) on server ({message.channel.guild.name}): {message.content}\n") 
        return

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        id_regex = f"(?:<@!{bot.user.id}>)(.*)"
        prompt_search = re.search(id_regex, message.content)
        if prompt_search is not None:
            user_prompt = prompt_search.group(1)
        else:
            user_prompt = ""
        
        await message.channel.send(generate_openai_message(user_prompt))
        return

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
