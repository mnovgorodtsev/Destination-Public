import airportsdata
import csv
import math
import pandas as pd


def haversine_distance(airports, region_coordinates):
    dataset = []
    for lat1, lon1, region_name in zip(region_coordinates['Latitude'], region_coordinates['Longitude'],
                                       region_coordinates['Location']):
        for lat2, lon2, IATA in zip(airports['Latitude'], airports['Longitude'],
                                    airports['IATA']):
            R = 6371.0

            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)

            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad

            a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            distance = R * c

            if distance < 100:
                dataset.append({
                    'IATA': IATA,
                    'Region Name': region_name,
                    'Latitude': lat1,
                    'Longitude': lon1
                })

    pd.DataFrame(dataset).to_csv('data/airports_to_regions2.csv')

    return dataset


def save_airports_to_csv(filename):
    airports = airportsdata.load("IATA")

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(["IATA", "City", "Airport Name", "Latitude", "Longitude"])

        for code, airport in airports.items():
            writer.writerow([code, airport['city'], airport['name'], airport['lat'], airport['lon']])
