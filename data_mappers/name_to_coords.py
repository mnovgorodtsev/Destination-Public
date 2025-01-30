import pandas as pd
import requests
import time
import re
import math

API_KEY = 'api_key'

region_names_df = pd.read_csv('../data/regions_names.csv')
region_names_list = region_names_df['NAME_LATN'].unique()


# change format of coordinats
def DMS_to_DD(dms_str):
    dms_parts = re.split('[°\'"]+', dms_str)

    degrees = float(dms_parts[0])
    minutes = float(dms_parts[1])
    seconds = float(dms_parts[2])
    # conversion to decimal
    decimal = degrees + (minutes / 60) + (seconds / 3600)

    if 'S' in dms_str or 'W' in dms_str:
        decimal = -decimal
    return round(decimal, 2)


def get_single_coords(location_name):
    URL = ('https://api.opencagedata.com/geocode/v1/json?'
           'q='+location_name+'&'
           'key=api_key')

    response = requests.get(URL)
    response = response.json()
    try:
        latitude_dms = response['results'][0]['annotations']['DMS']['lat']
        longitude_dms = response['results'][0]['annotations']['DMS']['lng']

        latitude = DMS_to_DD(latitude_dms)
        longitude = DMS_to_DD(longitude_dms)
    except (IndexError, KeyError) as e:
        print(f"Błąd: {e} - Współrzędne dla {location_name} nie znalezione.")
        latitude = math.nan
        longitude = math.nan

    print(location_name, 'Latitude: ', latitude, 'Longitude: ', longitude)

    # Frequency of requests
    time.sleep(5)
    return latitude, longitude


df = pd.DataFrame(columns=['Location','Latitude', 'Longitude'])
for single_location in region_names_list:
    location_name = single_location
    lat, long = get_single_coords(location_name)
    new_row = {'Location': location_name, 'Latitude': lat, 'Longitude': long}
    df = df._append(new_row, ignore_index=True)

df.to_csv('region_coordinates.csv')



