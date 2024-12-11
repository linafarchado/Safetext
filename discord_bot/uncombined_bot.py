import os
import pickle
import discord
from discord.ext import commands
from dotenv import load_dotenv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import asyncio

MUTE_DURATION = 5  # Duration in seconds

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Load the sensitive data model
with open('../models/sensitive/random_forest_model.pkl', 'rb') as model_file:
    classifier_sensitive = pickle.load(model_file)

# Load the TfidfVectorizer for sensitive data
with open('../models/sensitive/tfidf_vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer_sensitive = pickle.load(vectorizer_file)

# Load the insult detection model
with open('../models/insults/lg_insult.pkl', 'rb') as insult_model_file:
    classifier_insult = pickle.load(insult_model_file)

# Load the TfidfVectorizer for insult detection
with open('../models/insults/vector_insult.pkl', 'rb') as vectorizer_insult_file:
    vectorizer_insult = pickle.load(vectorizer_insult_file)

# Set up Discord client
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Temporary store for override approvals
override_requests = {}

async def mute_user(user, guild):
    # Fetch the Basique role
    basique_role = discord.utils.get(guild.roles, name="Basique")
    if not basique_role:
        print("The Basique role does not exist in the server.")
        return

    # Try to remove the Basique role from the user
    try:
        print(f"Removing the Basique role from {user} for {MUTE_DURATION} seconds.")
        await user.remove_roles(basique_role)
        print(f"Removed the Basique role from {user} for {MUTE_DURATION} seconds.")
    except discord.Forbidden:
        print("The bot does not have permission to remove roles.")
        return
    except discord.HTTPException as e:
        print(f"Failed to remove Basique role from {user}: {e}")
        return

    # Wait for the mute duration
    await asyncio.sleep(MUTE_DURATION)
    # Try to add the Basique role back to the user after the mute duration
    try:
        # Re-add the Basique role
        await user.add_roles(basique_role)
        print(f"Re-added the Basique role to {user} after {MUTE_DURATION} seconds.")
    except discord.Forbidden:
        print("The bot does not have permission to add roles.")
    except discord.HTTPException as e:
        print(f"Failed to re-add Basique role to {user}: {e}")
    
# Function to classify insults
def classify_insult(text):
    try:
        text_transformed = vectorizer_insult.transform([text])
        prediction = classifier_insult.predict(text_transformed)
        return prediction[0]
    except Exception as e:
        return f"Error in insult classification: {str(e)}"

# Function to classify sensitive data
def classify_sensitive(text):
    try:
        text_transformed = vectorizer_sensitive.transform([text])
        prediction = classifier_sensitive.predict(text_transformed)
        return prediction[0]
    except Exception as e:
        return f"Error in sensitive classification: {str(e)}"

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# Event when the bot receives a message
@bot.event
async def on_message(message):
    global override_requests

    # Ignore messages sent by the bot itself
    if message.author.bot:
        return

    user_input = message.content.strip()

    # Check if the message matches an override request
    if message.author.id in override_requests and user_input == override_requests[message.author.id]:
        del override_requests[message.author.id]
        await bot.process_commands(message)
        return

    # Step 1: Check for insults
    insult_result = classify_insult(user_input)
    print(insult_result)
    if insult_result == 1:
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, your message has been removed due to inappropriate language. "
                f"You have been temporarily muted for {MUTE_DURATION} seconds."
            )
            await mute_user(message.author, message.guild)
        except discord.Forbidden:
            await message.channel.send(
                f"{message.author.mention}, I tried to delete your message but lack the required permissions."
            )
        except discord.HTTPException as e:
            await message.channel.send(f"An error occurred while deleting the message: {str(e)}")
        return

    # Step 2: Check for sensitive data if no insult was detected
    sensitive_result = classify_sensitive(user_input)
    if sensitive_result == 1 and not user_input.startswith('!allow'):
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, your message has been removed because it contains sensitive data. "
                f"If you still want to post it, use `!allow <message>` (Do this at your own risk)."
            )
        
        except discord.Forbidden:
            await message.channel.send(
                f"{message.author.mention}, I tried to delete your message but lack the required permissions."
            )
        except discord.HTTPException as e:
            await message.channel.send(f"An error occurred while deleting the message: {str(e)}")
        return

    # Allow the bot to process other commands (if needed)
    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)




