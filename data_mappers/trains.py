import json
from math import radians, sin, cos, sqrt, atan2
import pandas as pd


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def assign_stations_to_regions(trains, region_coordinates):
    dataset = []
    for lat1, lon1, region_name in zip(region_coordinates['Latitude'], region_coordinates['Longitude'],
                                       region_coordinates['Location']):
        print(region_name)
        stations_in_range = []
        for train in trains['geo_shape']:
            try:
                train_data = json.loads(train)
            except json.JSONDecodeError:
                print(f"Błąd dekodowania JSON dla danych: {train}")
                continue

            for lon2, lat2 in train_data['coordinates']:
                distance = haversine(lat1, lon1, lat2, lon2)
                if distance <= 100:
                    stations_in_range.append([lat2, lon2])

            if stations_in_range:
                dataset.append({
                    'Region Name': region_name,
                    'Latitude': lat1,
                    'Longitude': lon1,
                    'Stations': stations_in_range
                })
                break

    pd.DataFrame(dataset).to_csv('../data/trains_to_regions2.csv')

    return dataset


def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False