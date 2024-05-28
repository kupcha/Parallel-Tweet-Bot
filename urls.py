import requests
import os
import csv
from colorama import init, Fore, Back, Style

def write_to_csv(card, file_name):
    csv_file=f'./urls/{file_name}'
    file_exists = os.path.isfile(f'./urls/{file_name}')

    # Open the CSV file in append mode
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header only if the file does not exist
        if not file_exists:
            writer.writerow(card.keys())

        # Write the data
        writer.writerow(card.values())

def main():
    init()
    count = 0;
    
    # # alpha set search pt. 1
    # for token in range(0, 98):
    #     url = f"https://parallel.life/cards/{str(token)}"
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         print(Fore.YELLOW + f"{count}:\tFound: card exists at" + Fore.WHITE + f"{url}")
    #         card = {
    #             "Count": count,
    #             "URL": url
    #         }
    #         write_to_csv(card, 'alpha.csv')
    #     else:
    #         print(Fore.RED + f"{count}:\tNot found: card does not exist at " + Fore.WHITE + f"{url}")
    #     count += 1
        
    # # alpha set search pt. 2
    # for token in range(10101, 11109):
    #     url = f"https://parallel.life/cards/{str(token)}"
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         print(Fore.YELLOW + f"{count}:\tFound: card exists at " + Fore.WHITE + f"{url}")
    #         card = {
    #             "Count": count,
    #             "URL": url
    #         }
    #         write_to_csv(card, 'alpha.csv')
    #     else:
    #         print(Fore.RED + f"{count}:\tNot found: card does not exist at " + Fore.WHITE + f"{url}")
    #     count += 1
        
    # # Battle Pass
    # for token in range(100100033, 100100035):
    #     url = f"https://parallel.life/cards/{str(token)}"
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         print(Fore.YELLOW + f"{count}:\tFound: card exists at " + Fore.WHITE + f"{url}")
    #         card = {
    #             "Count": count,
    #             "URL": url
    #         }
    #         write_to_csv(card, 'bp.csv')
    #     else:
    #         print(Fore.RED + f"{count}:\tNot found: card does not exist at " + Fore.WHITE + f"{url}")
    #     count += 1
    
    
    #PF set
    for token in range(100200007, 100200558):
        url = f"https://parallel.life/cards/{str(token)}"
        response = requests.get(url)
        if response.status_code == 200:
            print(Fore.YELLOW + f"{count}: Found: card exists at" + Fore.BLUE + f"{url}")
            card = {
                "Count": count,
                "URL": url
            }
            write_to_csv(card, 'pf.csv')
        count += 1
            
if __name__ == "__main__":
    main()