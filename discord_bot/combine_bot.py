import os
import pickle
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

MUTE_DURATION = 5  # Duration that you will be muted for for insults (in seconds)

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Load the combined model
with open('../models/combine/combine_logistic_regression_model.pkl', 'rb') as model_file:
    classifier_combined = pickle.load(model_file)

# Load the TfidfVectorizer
with open('../models/combine/combine_tfidf_vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer_combined = pickle.load(vectorizer_file)

# Set up Discord client
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to mute a user for MUTE_DURATION seconds by removing the Basique role that allows them to chat
async def mute_user(user, guild):
    basique_role = discord.utils.get(guild.roles, name="Basique")
    if not basique_role:
        print("The Basique role does not exist in the server.")
        return

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

    await asyncio.sleep(MUTE_DURATION)

    try:
        await user.add_roles(basique_role)
        print(f"Re-added the Basique role to {user} after {MUTE_DURATION} seconds.")
    except discord.Forbidden:
        print("The bot does not have permission to add roles.")
    except discord.HTTPException as e:
        print(f"Failed to re-add Basique role to {user}: {e}")

# Function to classify text using the combined model
def classify_text(text):
    try:
        text_transformed = vectorizer_combined.transform([text])
        prediction = classifier_combined.predict(text_transformed)
        return prediction[0]
    except Exception as e:
        return f"Error in classification: {str(e)}"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_input = message.content.strip()

    classification_result = classify_text(user_input)
    print(f"Classification result: {classification_result}")

    if classification_result == 2:  # Insult
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

    elif classification_result == 1 and not user_input.startswith('!allow'):  # Sensitive data
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

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
