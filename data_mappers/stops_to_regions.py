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


def assign_stops_to_regions(bus_stops, region_coordinates):
    dataset = []
    for lat1, lon1, region_name in zip(region_coordinates['Latitude'], region_coordinates['Longitude'],
                                       region_coordinates['Location']):
        stops_count = 0
        for lat2, lon2 in zip(bus_stops['stop_lat'], bus_stops['stop_lon']):
            distance = haversine(lat1, lon1, lat2, lon2)
            if distance <= 50:
                stops_count += 1

        dataset.append({
            'Region Name': region_name,
            'Latitude': lat1,
            'Longitude': lon1,
            'Bus Stops Count': stops_count
        })

    pd.DataFrame(dataset).to_csv('bus_stops_to_regions.csv', index=False)

    return dataset