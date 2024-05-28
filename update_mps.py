from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore
import time
import pandas as pd
import os   



def update_csv(title, img_src):
    csv_file='parallel_cards.csv'
    df = pd.read_csv(csv_file)

    # Search for the card title and update the 'mp_img_url' column if it exists
    if title in df['Title'].values:
        df.loc[(df['Title'] == title), 'mp_img_url'] = img_src
        # Save the DataFrame back to the CSV file
        df.to_csv(csv_file, index=False)
        print(f"Updated 'mp_img_url' for '{title}'")
    else:
        print(f"Card title '{title}' not found in the CSV file.")



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
        driver.implicitly_wait(2)


        # Extract the title
        title_element = driver.find_element(By.TAG_NAME , "h1")
        title = title_element.text.strip().title()
        
        
        if title.startswith("Parallel Masterpiece // Alpha // "):
            title = title.replace("Parallel Masterpiece // Alpha // ", "").strip()            
            # Find the img element
            image = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[10]/div/div[1]/div/img")))
            # Get the src attribute of the img element
            img_src = image.get_attribute('src')
            # Close the browser
            driver.quit()
            
            update_csv(title, img_src)
            print(Fore.GREEN + f"{title}, mp_url: {img_src} written to csv")
        elif title.startswith("Parallel Masterpiece // Planetfall // "):
            title = title.replace("Parallel Masterpiece // Planetfall // ", "").strip()            
            # Find the img element
            image = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div/div[10]/div/div[1]/div/img")))
            # Get the src attribute of the img element
            img_src = image.get_attribute('src')
            # Close the browser
            driver.quit()
            
            update_csv(title, img_src)
            print(Fore.GREEN + f"{title}, mp_url: {img_src} written to csv")
        
    except Exception as e:
        print(f"Error scraping card: {card_url}: {str(e)}")
        return None






def main():
    
    init()
    
    request_delay = 1  # One second between requests
    
    print(Fore.YELLOW + "// Collecting all Paraellel cards... //")
    csv_file='parallel_cards.csv'
    file_exists = os.path.isfile(csv_file)
    
    df = pd.read_csv('mp_ids.csv')
    for id in df['mp_token_id']:
        print(f"Scraping card data for card ID: {id}")
        card_url = f"https://parallel.life/cards/{id}"
        scrape_card_data(card_url)
        time.sleep(request_delay)

if __name__ == "__main__":
    main()
