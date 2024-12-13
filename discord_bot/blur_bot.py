import os
import discord
from discord.ext import commands
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Load the trained model
MODEL_PATH = "../models/blur/saved_model"
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

# Create the NER pipeline
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# Function to mask detected PII in a message
def mask_pii(text):
    entities = ner_pipeline(text)
    sorted_entities = sorted(entities, key=lambda x: x['start'], reverse=True)
    
    for entity in sorted_entities:
        start, end = entity['start'], entity['end']
        label = entity['entity_group']
        text = text[:start] + f"[{label}]" + text[end:]
    
    return text

# Set up the Discord bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    original_text = message.content.strip()
    if original_text.startswith('!allow'):
        return
    masked_text = mask_pii(original_text)

    try:
        await message.delete()
        await message.channel.send(
            f"{message.author.mention}, your message has been processed: \n{masked_text}"
        )
    except discord.Forbidden:
        print("Bot lacks permissions to delete messages or post masked text.")
    except discord.HTTPException as e:
        print(f"HTTP Exception: {e}")

bot.run(DISCORD_TOKEN)
