import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup
import time
import gspread
from google.oauth2.service_account import Credentials
import logging

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "motogp-key.json",
    scopes=scope
)
client = gspread.authorize(creds)
sheet = client.open("MotoGP Riders Data").sheet1

url = "https://www.motogp.com/en/riders/motogp"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

riders = soup.find_all("a",class_="rider-list__rider")
riders_data = []


for rider in riders:
    # Check MotoGP class
    if rider.get("data-rider-category-id") != "737ab122-76e1-4081-bedb-334caaa18c70":
        continue  # skip non-MotoGP riders

    # Rider Name
    name_container = rider.find("div", class_="rider-list__info-name")
    rider_name = " ".join([span.text.strip() for span in name_container.find_all("span")])

    # Team
    team_name = rider.find("span", class_="rider-list__details-team").text.strip()

    # Country
    country_name = rider.find("span", class_="rider-list__details-country").text.strip()

    # Profile Link
    profile_link = f"https://www.motogp.com{rider.get('href')}" 

    # This helps see which page is being scraped
    print(f"Requesting profile page: {profile_link}")
    profile_response = requests.get(profile_link)

    print(f"Status code: {profile_response.status_code}")
    print(profile_response.text[:300])
    print("-" * 60)

    profile_soup = BeautifulSoup(profile_response.text, "html.parser")

    # Visiting each riders profile page 
    first_name = profile_soup.find("meta", {"name": "rider-name"})
    last_name = profile_soup.find("meta", {"name": "rider-lastname"})

    if first_name and last_name:
        full_name = first_name["content"] + " " + last_name["content"]
    else:
        full_name = rider_name

    riders_data.append({
        "name": full_name,
        "team": team_name,
        "country": country_name,
        "profile_link": profile_link
    })

    time.sleep(2)

# # Open CSV file in write mode
# with open("motogp_riders.csv", mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)

#     # Header row
#     writer.writerow(["Name", "Team", "Country", "Profile Link"])

#     # Loop through filtered riders
#     for rider in riders:
#         if rider.get("data-rider-category-id") != "737ab122-76e1-4081-bedb-334caaa18c70":
#             continue

#         # Extract details
#         name = " ".join([span.text.strip() for span in rider.find("div", class_="rider-list__info-name").find_all("span")])
#         team = rider.find("span", class_="rider-list__details-team").text.strip()
#         country = rider.find("span", class_="rider-list__details-country").text.strip()
#         profile = f"https://www.motogp.com{rider.get('href')}"

#         # Write row
#         writer.writerow([name, team, country, profile])


# Convert to dataframe and save in CSV file
df = pd.DataFrame(riders_data)
df.to_csv("motogp_riders_full.csv", index=False)

# Exporting to google sheet,clearing the sheet first the adding the data.
sheet.clear()
sheet.append_row(["Name", "Team", "Country", "Profile"])
for rider in riders_data:
    sheet.append_row([
        rider["name"],
        rider["team"],
        rider["country"],
        rider["profile_link"]
    ])

print("Scraping complete. CSV saved.✅")