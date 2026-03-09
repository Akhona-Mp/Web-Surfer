import requests
import csv
from bs4 import BeautifulSoup

url = "https://www.motogp.com/en/riders/motogp"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

riders = soup.find_all("a",class_="rider-list__rider")

print(len(riders))

# for rider in riders:
#     print(rider.text)

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

    print(">",rider_name, "|", team_name, "|", country_name, "|", profile_link)


# Open CSV file in write mode
with open("motogp_riders.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # Header row
    writer.writerow(["Name", "Team", "Country", "Profile Link"])

    # Loop through filtered riders
    for rider in riders:
        if rider.get("data-rider-category-id") != "737ab122-76e1-4081-bedb-334caaa18c70":
            continue

        # Extract details
        name = " ".join([span.text.strip() for span in rider.find("div", class_="rider-list__info-name").find_all("span")])
        team = rider.find("span", class_="rider-list__details-team").text.strip()
        country = rider.find("span", class_="rider-list__details-country").text.strip()
        profile = f"https://www.motogp.com{rider.get('href')}"

        # Write row
        writer.writerow([name, team, country, profile])

print("CSV saved successfully ✅")