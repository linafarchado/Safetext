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

# Event when the bot receives a message
@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author.bot:
        return

    # Check if the bot is mentioned in the message
    if bot.user in message.mentions:
        user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()

        if not user_input:
            await message.channel.send("Please provide some text for classification.")
            return

        # Classify the text
        classification_result = classify_text(user_input)
        await message.channel.send(f"Classification Result: {classification_result}")

    # Allow the bot to process commands (in case any are implemented)
    await bot.process_commands(message)

# Run the bot
bot.run(DISCORD_TOKEN)
