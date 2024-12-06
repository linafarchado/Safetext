import os
import pickle
import discord
from discord.ext import commands
from dotenv import load_dotenv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Load the trained model
with open('exemple_model.pkl', 'rb') as model_file:
    classifier = pickle.load(model_file)

# Load the TfidfVectorizer used during training
with open('exemple_vectorize.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

# Set up Discord client
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to classify text
def classify_text(text):
    try:
        # Transform the text using the same TfidfVectorizer
        text_transformed = vectorizer.transform([text])  # Shape it into a 2D array

        # Predict the class of the transformed text
        prediction = classifier.predict(text_transformed)

        return prediction[0]  # Return the predicted class

    except Exception as e:
        return f"Error in classification: {str(e)}"

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# Temporary store for override approvals
override_requests = {}

# Command to allow a specific message to be posted
@bot.command(name="allow")
async def allow_message(ctx, *, message: str):
    global override_requests

    # Save the user's approved message in the override_requests dictionary
    override_requests[ctx.author.id] = message

    await ctx.send(f"{ctx.author.mention}, your message has been approved and can now be posted.")

# Event when the bot receives a message
@bot.event
async def on_message(message):
    global override_requests

    # Ignore messages sent by the bot itself
    if message.author.bot:
        return
    print(message.content)
    # Process commands before any other logic
    if message.content.startswith('!'):
        await bot.process_commands(message)
        print("Command processed")
        return

    user_input = message.content.strip()

    # Check if the message matches an override request
    if message.author.id in override_requests and user_input == override_requests[message.author.id]:
        # Remove the approved override since the user posted the message
        del override_requests[message.author.id]
        # Allow the message to pass without deletion
        await bot.process_commands(message)
        return

    # Classify the message
    classification_result = classify_text(user_input)
    print(f"Classification result: {classification_result}")
    # If the classification result is 1, delete the message and warn the user
    if classification_result == 1:
        try:
            await message.delete()  # Attempt to delete the user's message
            await message.channel.send(
                f"{message.author.mention}, your message has been removed because it violates the rules. "
                f"If you believe this is a mistake, use `!allow <message>` to request approval."
            )
        except discord.Forbidden:
            await message.channel.send(
                f"{message.author.mention}, I tried to delete your message but lack the required permissions."
            )
        except discord.HTTPException as e:
            await message.channel.send(
                f"An error occurred while deleting the message: {str(e)}"
            )
        return  # Stop further processing

    # Allow the bot to process other commands (if needed)
    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
