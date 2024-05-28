import os
from bs4 import BeautifulSoup
import requests
import csv

def fetch_urls(sitemap_url):
    """
    Fetches card URLs from the provided sitemap URL.

    Parameters:
    sitemap_url (str): The URL of the sitemap.

    Returns:
    list: A list of card URLs.
    """
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.content, 'xml')
    urls = [loc.text for loc in soup.find_all('loc')]
    return urls

def write_to_csv(card):
    """
    Writes the card information to a CSV file.

    Parameters:
    card (dict): A dictionary containing the card information.

    Returns:
    None
    """
    csv_file='card_urls.csv'
    file_exists = os.path.isfile(csv_file)

    # Open the CSV file in append mode
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header only if the file does not exist
        if not file_exists:
            writer.writerow(card.keys())

        # Write the data
        writer.writerow(card.values())
        
if __name__ == "__main__":
    sitemap_url = "https://parallel.life/cards/sitemap.xml"
    urls = fetch_urls(sitemap_url)
    print(f"Found {len(urls)} card URLs")
    count = 0
    for url in urls:
        card = {
            'URL': url,
            'Count': count
        }
        count += 1
        write_to_csv(card)
        print(f"Added '{url}' to card_urls.csv")
    print(f"{count} card URLs added to card_urls.csv")