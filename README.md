# SafeText

## Overview
This project involves the development of a Discord bot designed to:
1. Detect and censor toxic behavior in chat messages.
2. Identify and prevent leaks of sensitive data.

The bot leverages Natural Language Processing (NLP) models trained on diverse datasets to achieve these goals. It is designed to integrate seamlessly into Discord servers to enhance user experience and data privacy.

## Project Structure

```
.
├── discord_bot
│   ├── combine_bot.py         # Combines functionality for toxicity and sensitive data detection
│   └── uncombined_bot.py      # Uses 2 different models instead of one
├── models
│   ├── combine
│   │   ├── combine_logistic_regression_model.pkl  # Logistic Regression model for combined tasks
│   │   └── combine_tfidf_vectorizer.pkl           # TF-IDF vectorizer for combined tasks
│   ├── insults
│   │   ├── lg_insult.pkl                          # Logistic Regression model for insult detection
│   │   └── vector_insult.pkl                      # TF-IDF vectorizer for insult detection
│   └── sensitive
│       ├── random_forest_model.pkl                # Random Forest model for sensitive data detection
│       └── tfidf_vectorizer.pkl                   # TF-IDF vectorizer for sensitive data detection
├── notebooks
│   ├── combine.ipynb                              # Notebook for combined task model development
│   ├── faker_dataset.py                           # Script to generate a synthetic dataset using Faker
│   ├── nlp-sensitive-data_faker.ipynb            # Notebook for sensitive data model training and analysis
│   ├── project-offensive-language-analysis.ipynb # Notebook for offensive language analysis and model training
│   └── safetext.ipynb                             # Notebook for text safety analysis and model training
└── README.md
```

## Features
- **Toxicity Detection:**
  - Identifies offensive, insulting, or harmful language in Discord messages.

- **Sensitive Data Leak Prevention:**
  - Detects sensitive information such as personally identifiable information (PII) or confidential data.

- **Blur Sensitive Data**
  - Blur sensitive data when leaked.

## Usage

### Prerequisites
- Python 3.8 or above
- Discord API token
- Required Python packages listed in `requirements.txt`

### Setup
1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your Discord bot token in the .env file in discord_bot/
    ```bash
    DISCORD_TOKEN=<your discord token>
    ```
3. Run notebooks to train models (We have default one if you don't have time to run them)
To use them, change the names of the used models in the corresponding discord bot file.

4. Run the bot:
   ```bash
   cd discord_bot/
   python <bot to run>.py
   ```

### Model Files
The pre-trained models are stored in the `models` directory and loaded by the bot scripts for prediction.
Except for the blur bot, the model is too big for git. You need to run the ```blur-pii.ipynb``` notebook.

### Discord bot Features

**Combine Bot**

- One model trained on sensitive and toxic data.

- ```!allow``` command to bypass sensitive data censorship.

- Insults result in temporary mutes.

- Sensitive data and insults are automatically deleted.

**Uncombined Bot**

- Utilizes two models: one trained on sensitive data and another on toxic data.

- ```!allow``` command to bypass sensitive data censorship.

- Insults result in temporary mutes.

- Sensitive data and insults are automatically deleted.

**Blur Bot**

- Utilizes one Bert model fine tuned on sensitive data.

- It automatically replaces any sensitive data with a masked version (ex: Alexandre == [GIVENNAME])

- ```!allow``` command to bypass sensitive data censorship.