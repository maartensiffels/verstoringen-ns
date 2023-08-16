import requests
import csv
import os
from datetime import datetime
import pytz

def fetch_disruptions():
    url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/disruptions"
    headers = {
        "Ocp-Apim-Subscription-Key": "dd6c3e5f733d48b59a7c83abe2161a2f"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def save_to_csv(data, year):
    filename = f"verstoringen-dienstregeling-ns-{year}.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(["ID", "Titel", "Fase ID", "Fase Label", "Oorzaak", "Impact", "Gevolg", "Beschrijving", "Minimale Extra Reistijd (min.)", "Maximale Extra Reistijd (min.)", "Station Codes", "Station Namen", "Starttijd", "Geschatte Eindtijd", "Eindtijd", "Tijdstip collectie"])
            
        for item in data:
            writer.writerow([item["ID"], item["Titel"], item["Fase ID"], item["Fase Label"], item["Oorzaak"], item["Impact"], item["Gevolg"], item["Beschrijving"], item["Minimale Extra Reistijd"], item["Maximale Extra Reistijd"], item["Station Codes"], item["Station Namen"], item["Starttijd"], item["Geschatte Eindtijd"], item["Eindtijd"], item["Tijdstip collectie"]])

# Stel de tijdzone in op Amsterdam (Nederland)
amsterdam = pytz.timezone('Europe/Amsterdam')
current_time = datetime.now(amsterdam)
formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S')
current_year = current_time.strftime('%Y')

data = fetch_disruptions()

filtered_disruptions = [
    {
        "ID": disruption.get("id"),
        "Titel": disruption.get("title", ""),
        "Fase ID": disruption.get("phase", {}).get("id", ""),
        "Fase Label": disruption.get("phase", {}).get("label", ""),
        "Oorzaak": disruption.get("timespans", [{}])[0].get("cause", {}).get("label", ""),
        "Impact": disruption.get("impact", {}).get("value", ""),
        "Gevolg": disruption.get("consequence", {}).get("description", ""),
        "Beschrijving": disruption.get("timespans", [{}])[0].get("situation", {}).get("label", ""),
        "Minimale Extra Reistijd": disruption.get("summaryAdditionalTravelTime", {}).get("minimumDurationInMinutes", ""),
        "Maximale Extra Reistijd": disruption.get("summaryAdditionalTravelTime", {}).get("maximumDurationInMinutes", ""),
        "Station Codes": ", ".join([station.get("stationCode", "") for station in disruption.get("publicationSections", [{}])[0].get("section", {}).get("stations", [])]),
        "Station Namen": ", ".join([station.get("name", "") for station in disruption.get("publicationSections", [{}])[0].get("section", {}).get("stations", [])]),
        "Starttijd": disruption.get("start", "").replace('+0200', ''),
        "Geschatte Eindtijd": disruption.get("expectedDuration", {}).get("endTime", "").replace('+0200', ''),
        "Eindtijd": disruption.get("end", "").replace('+0200', ''),
        "Tijdstip collectie": formatted_time
    }
    for disruption in data if disruption.get("type") == "DISRUPTION"
]

save_to_csv(filtered_disruptions, current_year)
for item in filtered_disruptions:
    print(f'ID: {item["ID"]}, Titel: {item["Titel"]}, Fase ID: {item["Fase ID"]}, Fase Label: {item["Fase Label"]}, Oorzaak: {item["Oorzaak"]}, Impact: {item["Impact"]}, Gevolg: {item["Gevolg"]}, Beschrijving: {item["Beschrijving"]}, Minimale Extra Reistijd: {item["Minimale Extra Reistijd"]}, Maximale Extra Reistijd: {item["Maximale Extra Reistijd"]}, Station Codes: {item["Station Codes"]}, Station Namen: {item["Station Namen"]}, Starttijd: {item["Starttijd"]}, Geschatte Eindtijd: {item["Geschatte Eindtijd"]}, Eindtijd: {item["Eindtijd"]}, Tijdstip collectie: {item["Tijdstip collectie"]}')
