import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import gspread
from google.oauth2.service_account import Credentials
import logging

# -------------------------
# CONFIGURATION & LOGGING
# -------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

GOOGLE_SHEET_NAME = "MotoGP Riders Data"
SERVICE_ACCOUNT_FILE = "motogp-key.json"
SLEEP_TIME = 2  # seconds between requests
MOTOGP_CATEGORY_ID = "737ab122-76e1-4081-bedb-334caaa18c70"
BASE_URL = "https://www.motogp.com"

# -------------------------
# GOOGLE SHEET SETUP
# -------------------------
def init_google_sheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)
    client = gspread.authorize(creds)
    return client.open(GOOGLE_SHEET_NAME).sheet1

# -------------------------
# FETCH RIDER LIST
# -------------------------
def fetch_rider_list():
    logging.info("Fetching MotoGP rider list...")
    url = f"{BASE_URL}/en/riders/motogp"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    riders = soup.find_all("a", class_="rider-list__rider")
    return [r for r in riders if r.get("data-rider-category-id") == MOTOGP_CATEGORY_ID]

# -------------------------
# FETCH INDIVIDUAL PROFILE
# -------------------------
def fetch_profile_details(rider):
    # Basic info
    name_container = rider.find("div", class_="rider-list__info-name")
    rider_name = " ".join([span.text.strip() for span in name_container.find_all("span")])
    team_name = rider.find("span", class_="rider-list__details-team").text.strip()
    country_name = rider.find("span", class_="rider-list__details-country").text.strip()
    profile_link = f"{BASE_URL}{rider.get('href')}"

    # Visit profile page for meta data
    logging.info(f"Requesting profile page: {profile_link}")
    profile_response = requests.get(profile_link)
    profile_soup = BeautifulSoup(profile_response.text, "html.parser")

    first_name = profile_soup.find("meta", {"name": "rider-name"})
    last_name = profile_soup.find("meta", {"name": "rider-lastname"})
    full_name = (first_name["content"] + " " + last_name["content"]) if first_name and last_name else rider_name

    time.sleep(SLEEP_TIME)
    return {
        "name": full_name,
        "team": team_name,
        "country": country_name,
        "profile_link": profile_link
    }

# -------------------------
# SAVE TO CSV
# -------------------------
def save_to_csv(data, filename="motogp_riders_full.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    logging.info(f"Data saved to CSV: {filename}")

# -------------------------
# UPDATE GOOGLE SHEET
# -------------------------
def update_google_sheet(sheet, data):
    logging.info("Updating Google Sheet...")
    sheet.clear()
    sheet.append_row(["Name", "Team", "Country", "Profile"])
    for rider in data:
        sheet.append_row([
            rider["name"],
            rider["team"],
            rider["country"],
            rider["profile_link"]
        ])
    logging.info("Google Sheet updated successfully ✅")

# -------------------------
# MAIN PIPELINE
# -------------------------
def main():
    sheet = init_google_sheet()
    riders = fetch_rider_list()
    riders_data = [fetch_profile_details(rider) for rider in riders]
    save_to_csv(riders_data)
    update_google_sheet(sheet, riders_data)
    logging.info("Scraping pipeline completed ✅")

if __name__ == "__main__":
    main()