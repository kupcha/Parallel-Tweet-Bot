import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import logging
from colorama import Fore, Back, Style, init
import tweepy.asynchronous
import asyncio
from tweepy import API
import json
import schedule
import pytz
import time

def display_as_integer(value):
    return int(value)


def split_text(text, max_length=280):
    """Split the text into chunks of max_length characters without splitting words and retaining newline characters."""
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

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Determine the file extension from the URL
        file_extension = os.path.splitext(url)[1]
        if file_extension.lower() not in ['.png', '.gif']:
            logging.error(f"Unsupported file format: {file_extension}")
            return None
        
        # Save the file with the appropriate extension
        file_path = f"/tmp/temp{file_extension}"
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return file_path
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}")
        return None
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        return None

def tweet_card():
    # Load environment variables
    load_dotenv()
    
    auth = tweepy.OAuth1UserHandler(os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_API_SECRET_KEY'))
    auth.set_access_token(
        os.getenv('TWITTER_ACCESS_TOKEN'),
        os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
    )
    api = tweepy.API(auth)  

    client = tweepy.Client(os.getenv('TWITTER_BEARER_TOKEN'), os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_API_SECRET_KEY'), os.getenv('TWITTER_ACCESS_TOKEN'),
        os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
    
    
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    debug = 0
    try:
        # Load the CSV file
        df = pd.read_csv('parallel_cards.csv')
        # Randomly select a row
        row = df.sample(n=1).iloc[0].to_dict()
        
        title = row['Title']
        parallel = row['Parallel']
        card_type = row['Type']
        rarity = row['Rarity']
        edition = row['Edition Size']
        ability = row['Ability']
        cost = row['Cost']
        attack = row['Attack']
        health = row['Health']
        url = row['mp_img_url']
        lore = row['Description']
        
        img_path = download_image(url)

        character_limit = 280 - 24 # 24 characters for the image URL
        if card_type == "Unit":
            description = f"{title},\n{parallel} {card_type},\n\n{lore}"
            stats = f"Cost: {cost}, Attack: {display_as_integer(attack)}, Health: {display_as_integer(health)}\n{rarity}, Edition of {edition}\n"
        else:
            description = f"{title},\n{parallel} {card_type},\n\n{lore}"
            stats = f"Cost: {cost}\n\n{rarity}, Edition of {edition}\n"
        chunks = split_text(description)
        ability_chunks = split_text(ability)
        

        try:
            media = api.media_upload((img_path))
            print(Fore.YELLOW + f"img successfully uploaded to X")
            # Post the tweet with the image
            first_tweet = client.create_tweet(text=chunks[0], media_ids=[media.media_id])
            print(json.dumps(first_tweet, indent=4))
            reply_to_id = first_tweet.data['id']
            (f"reply_id = {reply_to_id}")
            for chunk in chunks[1:]:
                tweet = client.create_tweet(text=chunk, in_reply_to_tweet_id=reply_to_id)
                logging.info(Fore.LIGHTWHITE_EX + f"Thread tweet posted: \t{chunk}")
                reply_to_id = tweet.data['id']
            tweet = client.create_tweet(text=stats, in_reply_to_tweet_id=reply_to_id)
            reply_to_id = tweet.data['id']
            for ability_chunk in ability_chunks:
                tweet = client.create_tweet(text=ability_chunk, in_reply_to_tweet_id=reply_to_id)
                logging.info(Fore.LIGHTWHITE_EX + f"Thread tweet posted: {ability_chunk}")
                reply_to_id = tweet.data['id']

        except tweepy.TweepyException as e:
            logging.error(f"Tweepy error occurred: - {e}")
            if hasattr(e, 'response'):
                logging.error(f"HTTP error details: {e} - {e}")
        except Exception as e:
            logging.error(f"Error: {e}")
                
        os.remove(img_path)

    except tweepy.TweepyException as e:
        logging.error(f"Tweepy error occurred: {e} - {e}")
        if hasattr(e, 'response'):
            logging.error(f"HTTP error details: {e} - {e}")
    except Exception as e:
        logging.error(f"Error: {e}")
        
        
        
def schedule_tweets():
    # Schedule the tweet_with_image_from_csv function to run at 11am and 11pm EST
    est = pytz.timezone('US/Eastern')
    
    schedule.every().day.at("11:11", est).do(tweet_card)
    schedule.every().day.at("23:11", est).do(tweet_card)
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    tweet_card()
    # script_name = sys.argv[0]
    # if len(sys.argv) == 2 & sys.argv[1] == "tweet_card":
    #     print(Fore.RED + f"ERROR: INCORRECT USAGE.")
    #     print(f"Usage options:\n1.\t\"python bot.py\" to run bot in background.\n2.\tpython \"python3 bot.py tweet_card\" to generate a tweet of random card.")
    # else:
    #     print(Fore.GREEN + f"Correct usage.")
    # sys.exit(1)