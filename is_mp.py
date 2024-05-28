import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Back, Style
import json
import time
import pandas as pd


def fetch_urls(sitemap_url):
    """ Fetches card URLs from the provided sitemap URL. """
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.content, 'xml')
    urls = [loc.text for loc in soup.find_all('loc')]
    return urls

# Function to download the card image from URL
def download_image(url, folder_path, card_name, card_type, token_id):
    if card_type == "Nonplayable":
        # Remove "Parallel Masterpiece // Alpha // " if present
        if card_name.startswith("Parallel Masterpiece // Alpha // "):
            card_name = card_name.replace("Parallel Masterpiece // Alpha // ", "").strip()
            final_path = f"{folder_path}/masterpieces"
            csv_file='mp_ids.csv'
            card = { "mp_token_id" : token_id }
            # Check if the file exists
            if os.path.exists(csv_file):
                # Open the CSV file in append mode
                with open(csv_file, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(card.values())
            else:
                writer.writerow(card.keys())
                        
        elif card_name.startswith("Parallel Masterpiece // Planetfall // "):
            print(f'PF masterpiece card detected...')
            card_name = card_name.replace("Parallel Masterpiece // Planetfall // ", "").strip()
            final_path = f"{folder_path}/masterpieces"
            csv_file='mp_ids.csv'
            card = { "mp_token_id" : token_id }
            # Check if the file exists
            if os.path.exists(csv_file):
                # Open the CSV file in append mode
                with open(csv_file, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(card.values())
            else:
                writer.writerow(card.keys())
        else:
            final_path = f"{folder_path}/non-playable"
    elif card_name.endswith("[Pl]"):
        final_path = f"{folder_path}/loops"
    else:
        final_path = folder_path
    file_extension = url.split('.')[-1]
    file_name = f"{card_name.replace(' ', '_')}.{file_extension}"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(os.path.join(final_path, file_name), 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        # print(f"img downloaded successfully.")
    else:
        print("Failed to retrieve image")

def write_to_csv(card):
    csv_file='parallel_cards.csv'
    file_exists = os.path.isfile(csv_file)

    # Open the CSV file in append mode
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header only if the file does not exist
        if not file_exists:
            writer.writerow(card.keys())

        # Write the data
        writer.writerow(card.values())

def scrape_card_data(card_url):
    """ Scrapes data from a single card URL. """
    debug_printing = 0;
    
    try:
        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless Chrome
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # Explicit wait for the element to be present
        wait = WebDriverWait(driver, 5)



        # Navigate to the URL
        driver.get(card_url)
        driver.implicitly_wait(1)
        try:
            stats = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[6]")))
        except Exception:
            stats = None
            
        if (stats):
            # Find all child elements of the parent element
            stat_list = stats.find_elements(By.XPATH, "./*")
            if len(stat_list) > 2:
                # Unit Card
                card_cost = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[6]/div[1]/div[2]").text.strip()
                card_attack = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[6]/div[2]/div[2]").text.strip()
                card_health = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[6]/div[3]/div[2]").text.strip()
                card_type = "Unit"
                if debug_printing:
                    print(Fore.LIGHTCYAN_EX + f"Unit: Cost: {card_cost}, Attack: {card_attack}, Health: {card_health}")
                    
            else:
                # Upgrade/Relic Card
                # Extract card stats for upgrade/relic
                card_cost = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[6]/div[1]/div[2]").text.strip()
                card_type = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[6]/div[2]/div[2]").text.strip().title()
                card_attack = None
                card_health = None
                if debug_printing:
                    print(Fore.LIGHTCYAN_EX + f"{card_type}: Cost: {card_cost}")
                    
            # Extract card ability
            card_ability = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[5]")
            ability = card_ability.text.strip()
            print(Fore.LIGHTCYAN_EX + f"Ability: {ability}")
                    
        else:
            # Card Back, Asset, Art Card, Masterpiece
            card_cost = None
            card_type = "Nonplayable"
            card_attack = None
            card_health = None
            ability = None
            print(Fore.LIGHTCYAN_EX + f"Nonplayable Card")

        # Extract the title
        title_element = driver.find_element(By.TAG_NAME , "h1")
        title = title_element.text.strip().title()
        
        if debug_printing:
            print(Fore.GREEN + f"{title}")
            
        description = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[2]").text.strip()
            
        # Get Parallel
        parallel = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[9]/div[2]/div[2]").text.strip().title()

        # Extract rarity, edition, and pack drop information using XPATH
        info_xpath = "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[1]/div"
        info_elements = driver.find_elements(By.XPATH, info_xpath)
        info = [element.text.strip() for element in info_elements if element.text.strip()]
        rarity = info[0].title()
        edition = info[2].title().replace("Edition of", "")
        edition = edition.replace("Edition Of ", "").strip()
        
        artist = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[12]/div[1]/div/div[3]/a").text.strip()
        
        

        if debug_printing:
            print(rarity)
            print(edition)
            print(f"Artist: {artist}")

        
        token_id = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[11]/div/div[2]").text.strip()
                        
        # Find the img element
        image = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[10]/div/div[1]/div/img")
        image = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[10]/div/div[1]/div/img")))
        # Get the src attribute of the img element
        img_src = image.get_attribute('src')
        # Close the browser
        driver.quit()
        
        card = {
            "Title": title,
            "Parallel": parallel,
            "Type": card_type,
            "Rarity": rarity,
            "Edition Size": edition,
            "Description": description,
            "Ability": ability,
            "Cost": card_cost,
            "Attack": card_attack,
            "Health": card_health,
            "Image URL": img_src,
            "Token ID": token_id,
            "Artist": artist,
        }
        
        print(Fore.WHITE + json.dumps(card, indent=4))
        # Skip cards with titles ending in [SE]
        if title.endswith("[Se]"):
            print(f"Skipping SE: {title}")
            return {}
        elif title.endswith("[Pl]"):
            print(f"Skipping PL: {title}")
            return {}
        else:
            download_image( img_src, "cards", title, card_type, token_id)
        
        if not title.endswith("[Pl]"):
            if card_type != "Nonplayable":
                write_to_csv(card)
    
    except Exception as e:
        print(f"Error scraping card: {card_url}: {str(e)}")
        return None


def scrape_set(set, starting_point):
    request_delay = 1  # One second between requests
    # Load the CSV file into a DataFrame
    csv_file_path = f'./urls/{set}.csv'
    df = pd.read_csv(csv_file_path)
    cutoff = 551
    
    # to be used in case program is interupted or rerun at some point
    card_count = 0
    
    # Iterate through each row in the 'URL' column
    for url in df['URL']:
        if card_count < starting_point:
            card_count += 1
            continue
        elif card_count >= cutoff:
            break
        print(Fore.YELLOW + f"\n#{card_count}:")
        scrape_card_data(url)
        print(f"\n")
        card_count += 1
        # time.sleep(request_delay)  # Wait for 1 second before making the next request
    
        
    
def main():
    
    init()
    
    print(Fore.YELLOW + "// Collecting all Paraellel cards... //")
    
    # Used in original version, sitemap does not contain all card urls
    # Full card URL set contained in .csv files in urls folder, obtained by running urls.py
    # sitemap_url = 'https://parallel.life/cards/sitemap.xml'
    # card_urls = fetch_urls(sitemap_url)
    
    
    # Create folder if it doesn't exist
    folder_path = 'cards'  # Folder to save the image
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.makedirs('cards/non-playable')
        os.makedirs('cards/masterpieces')
        os.makedirs('cards/loops')
    
    # Scrape Alpha, Battlepass, and Planetfall sets respectively.
        scrape_set('alpha', 0)
        scrape_set('bp', 0)
        scrape_set('pf', 0)
    
    print(Fore.GREEN + f"\n// All cards scraped successfully. //")

if __name__ == "__main__":
    main()
