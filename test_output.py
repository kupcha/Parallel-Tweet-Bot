import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import logging
from colorama import Fore, init
import json

CHARACTER_LIMIT = 280 # character limit for a tweet defined by Twitter/X
IMG_CHAR_LIMIT = 24 # if image included in tweet, reduce character limit by this amount
DESCRIPTION_CHAR_LIMIT = CHARACTER_LIMIT - IMG_CHAR_LIMIT # character limit when including image

def split_text(text, max_length=DESCRIPTION_CHAR_LIMIT):
    """Split the text into chunks of max_length characters without splitting words and retaining newline characters.
    
    Args:
        text (str): The text to be split.
        max_length (int, optional): The maximum length of each chunk. Defaults to DESCRIPTION_CHAR_LIMIT.
    
    Returns:
        list: A list of chunks.
    """
    chunks = []
    current_chunk = ""
    for line in text.split('\n'):
        first_word = 1
        for word in line.split():
            # If adding the next word exceeds the max_length, finalize the current chunk
            if len(current_chunk) + len(word) + 1 > max_length:
                chunks.append(current_chunk.strip())
                current_chunk = word
            else:
                if first_word:
                    current_chunk += (word if current_chunk else word)
                    first_word = 0
                else:
                    current_chunk += (" " + word if current_chunk else word)
        current_chunk += "\n"  # Retain the newline character after each line

        # If the current chunk exceeds max_length after adding newline, split here
        if len(current_chunk.strip()) > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = ""

    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def display_as_integer(value):
    """Convert the value to an integer and return it.
    
    Args:
        value: The value to be converted.
    
    Returns:
        int: The converted integer value.
    """
    return int(value)

def test_output():
    """Test the output of the card-bot program."""
    debug = 1
    init()
    
    
    # list of all rows where length of text is > (280 - 24) characters
    too_long = []
    #Too long: [12, 33, 42, 91, 92, 93, 94, 115, 120, 128, 136, 179, 187, 189, 244, 253, 276, 281, 284, 285, 286, 302, 304, 323, 324, 337, 339, 348, 360, 363, 367, 370, 371, 373, 378, 383, 385, 394, 400, 402]
    lore_too_long = []
    # Lore too long: [35, 176, 246, 292, 373]

    
    
    # Too long: [8, 35, 176, 213, 246, 282, 292, 299, 327, 354, 373, 376, 379]
    # Lore too long: [42, 91, 92, 93, 94, 120, 128, 136, 244, 276, 286, 302, 304, 323, 324, 337, 360, 363, 367, 370, 371, 373, 385, 394, 400]
    try:
            # Load the CSV file
            df = pd.read_csv('parallel_cards.csv')
            
            # # Randomly select a card (each card is represented by a row in the .csv file)
            # random_card = df.sample(n=1)
            
            # will print output of every possible card
            for index, row in df.iterrows():
                print(Fore.YELLOW + f"{index}: ")
                title = row['Title']
                parallel = row['Parallel']
                card_type = row['Type']
                rarity = row['Rarity']
                edition = row['Edition Size']
                ability = row['Ability']
                cost = row['Cost']
                attack = row['Attack']
                health = row['Health']
                lore = row['Description']

                # Possible card types are Unit OR Relic/Effect
                if card_type == "Unit":
                    description = f"{title},\n{parallel} {card_type},\n\n{lore}"
                    stats = f"Cost: {cost}, Attack: {display_as_integer(attack)}, Health: {display_as_integer(health)}\n{rarity}, Edition of {edition}\n"
                # Relics & Effects do not have attack and health stats
                else:
                    description = f"{title},\n{parallel} {card_type},\n\n{lore}"
                    stats = f"Cost: {cost}\n\n{rarity}, Edition of {edition}\n"
                chunks = split_text(description)
                ability_chunks = split_text(ability)
            
                chunk_count = 0
                for chunk in chunks:
                    print(Fore.WHITE + f"{chunk}")
                    chunk_count += 1
                print(Fore.RED + f"Chunks: {chunk_count}")
                if chunk_count > 1:
                    too_long.append(index)
                lore_chunk_count = 0
                for lore_chunk in ability_chunks:
                    print(Fore.WHITE + f"{lore_chunk}")
                    lore_chunk_count += 1
                print(Fore.RED + f"Lore Chunks: {lore_chunk_count}")
                if lore_chunk_count > 1:
                    lore_too_long.append(index)
            print(Fore.LIGHTRED_EX + f"\n\nToo long: {too_long}")
            print(Fore.LIGHTRED_EX + f"\n\nLore too long: {lore_too_long}")
    except Exception as e:
        logging.error(f"Error tweeting with image from CSV: {e}")
        return None
    
    
test_output()