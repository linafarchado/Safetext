from faker import Faker
import random
import csv

fake_eng = Faker("en_US")  # English (US)
fake_fr = Faker("fr_FR")   # French
fake_de = Faker("de_DE")   # German

# Function to generate a random phone number with 30% from France, 70% from anywhere
def get_random_phone_number():
    # Define probabilities: 30% France, 70% other
    locale_choice = random.choices(
        population=["fr", "other"],
        weights=[50, 50],
        k=1
    )[0]
    
    if locale_choice == "fr":
        return fake_fr.phone_number()  # French phone number
    else:
        # Randomly pick between English and German for the "other" category
        return random.choice([fake_eng.phone_number(), fake_de.phone_number()])

# Function to generate a random Discord-like message
def generate_message(include_sensitive=False):
    # Generate a base message
    base_message = fake_eng.sentence(nb_words=random.randint(5, 15))  # Use English for general text
    choice = "None"
    
    if include_sensitive:
        # Define probabilities for different combinations of sensitive data
        choice = random.choices(
            population=[
                "email",                # Only email
                "address",              # Only address
                "phone",                # Only phone
                "phone_address",        # Phone + Address
                "phone_email",          # Phone + Email
                "address_email",        # Address + Email
                "all_three"             # Email + Phone + Address
            ],
            weights=[30, 30, 30, 3, 3, 3, 1],  # Corresponding probabilities
            k=1
        )[0]
        
        # Generate sensitive data based on the selected choice
        sensitive_data = []
        if "email" in choice:
            sensitive_data.append(fake_eng.email())  # Keep email in English format
        if "phone" in choice:
            sensitive_data.append(get_random_phone_number())  # Randomly generate phone number
        if "address" in choice:
            sensitive_data.append(fake_fr.address())  # Use French addresses for variety
        
        # Randomly insert each piece of sensitive data into the sentence at different spots
        words = base_message.split()
        for data in sensitive_data:
            insert_position = random.randint(0, len(words))
            words.insert(insert_position, f"{data}")
        base_message = " ".join(words)
    
    return choice, base_message

# Generate dataset
def create_dataset(num_samples=1000):
    dataset = []
    for _ in range(num_samples):
        # Randomly decide if the sentence will contain sensitive data
        is_sensitive = random.choice([True, False])
        choice, sentence = generate_message(include_sensitive=is_sensitive)
        label = 1 if is_sensitive else 0
        dataset.append((sentence, choice, label))
    return dataset

# Save dataset to CSV
def save_dataset_to_csv(dataset, file_name="dataset.csv"):
    with open(file_name, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Sentence", "Contains Sensitive Data"])
        writer.writerows(dataset)