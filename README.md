# SafeText

## Overview
This project involves the development of a Discord bot designed to:
1. Detect and censor toxic behavior in chat messages.
2. Identify and prevent leaks of sensitive data.

The bot leverages Natural Language Processing (NLP) models trained on diverse datasets to achieve these goals. It is designed to integrate seamlessly into Discord servers to enhance user experience and data privacy.

## Project Structure

```
.
.
├── AUTHORS.txt                             
├── datasets                               
│   ├── labeled_data.csv                    # Dataset with labeled data for classification tasks (e.g., toxicity or sensitive data)
│   └── sensitive_data.csv                  # Dataset containing sensitive data for PII masking or related tasks
├── discord_bot                             
│   ├── blur_bot.py                         # Discord bot for PII masking using the Blur model
│   ├── combine_bot.py                      # Discord bot for combined tasks (e.g., toxicity and PII masking)
│   └── uncombined_bot.py                   # Discord bot for independent tasks without combining datasets
├── models                                  
│   ├── combine                             
│   │   ├── combine_logistic_regression_model.pkl  # Logistic Regression model for combined tasks
│   │   └── combine_tfidf_vectorizer.pkl    # TF-IDF vectorizer for combined tasks
│   ├── insults                             
│   │   ├── insults_logistic_regression_model.pkl  # Logistic Regression model for insult detection
│   │   └── insults_tfidf_lr_vectorizer.pkl # TF-IDF vectorizer for insult detection
│   └── sensitive                           
│       ├── sensitive_logistic_regression_model.pkl # Logistic Regression model for sensitive data detection
│       └── sensitive_tfidf_vectorize.pkl   # TF-IDF vectorizer for sensitive data detection
├── notebooks                               
│   ├── blur-pii.ipynb                      # Notebook to fine tune Bert to mask data
│   ├── combine.ipynb                       # Notebook for exploring combined tasks
│   ├── faker_dataset.py                    # Python script for generating synthetic data using Faker
│   ├── nlp-sensitive-data_faker.ipynb      # Notebook for handling sensitive data tasks with synthetic datasets
│   └── nlp-toxicity-data.ipynb             # Notebook for analyzing and processing toxicity/insult data
├── README.md                               
└── requirements.txt                        

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

# Technical Overview

## Datasets 

### 1. Hate Speech and Offensive Language Dataset
This dataset, sourced from Twitter data, was created to study hate speech detection. Each text entry is classified into one of three categories:
- Hate speech
- Offensive language
- Neither

### 2. PII-Masking-400k (AI4Privacy)
This dataset is specifically designed to train and evaluate models that mask **personally identifiable information (PII)** and sensitive data in text. It contains:
- **400,000 rows** of synthetically generated data
- **Six languages** to support multilingual applications

The synthetic nature of the dataset ensures that it avoids any actual data leaks while simulating realistic use cases.

### 3. Synthetic Dataset (Faker)
This dataset is entirely generated using the [Faker](https://faker.readthedocs.io/en/master/) library. It includes:
- Email addresses
- Postal addresses
- Phone numbers

---

## Data Processing and Modeling

### Data Cleaning
For the **Hate Speech and Offensive Language Dataset**, we performed:
1. **Resampling** to handle class imbalances.
2. **Data cleaning** to remove noise and improve data quality.

### Feature Engineering
- We used **TF-IDF** as a vectorizer to transform the text data into numerical representations suitable for machine learning models.

### Machine Learning Models
We applied three machine learning models to classify the data:
1. **Logistic Regression**
2. **Random Forest**
3. **Support Vector Machine (SVM)**

For hyperparameter optimization, a **GridSearch** approach was used to identify the best-performing parameters for each model.

### Fine-Tuned Model
For the PII-Masking-400k Dataset, we fine-tuned a **BERT-based model** to detect and mask Personally Identifiable Information (PII) effectively. Specifically:

- **Model Base**: We used `bert-base-multilingual-cased` initially, but switched to `bert-base-cased` since the dataset was filtered to English texts only.

- **Data Preprocessing**:
  - Filtered the dataset to include only English language texts
  - Implemented a custom tokenization strategy using BERT's tokenizer
  - Used the BIO (Begin, Inside, Outside) tagging scheme for named entity recognition

- **Training Parameters**:
  - Learning rate: 2e-5
  - Batch size: 8
  - Epochs: 3

- **Performance**:
  - Achieved high accuracy, precision, and recall
  - Final epoch metrics:
    * Accuracy: 99.6965%
    * Precision: 99.6967%
    * Recall: 99.6965%
    * F1 Score: 99.6958%