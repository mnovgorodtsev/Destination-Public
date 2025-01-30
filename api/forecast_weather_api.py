from typing import final

import requests
import pandas as pd
import numpy as np
import json
import pprint
import time
from weather_functions import universal_weather_scaling

pd.set_option('display.max_columns', 10)
pd.options.display.width = 0

BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'

params = {
        'unitGroup': 'metric'
    }

API_KEY = 'API_KEY'

DYNAMIC_URL = f'{latitude},{longtitude}?key={API_KEY}'
COMPLETE_URL = f'{BASE_URL}{DYNAMIC_URL}'

response = requests.get(COMPLETE_URL, params=params)
data = json.loads(response.text)

# 15 days of current forecasts
# planning to update it year by year
# with open("data.json", "r") as file:
#     data = json.load(file)

#print(data)
days_list = data['days']
number_of_days = 14
counter = 0

regions_df = pd.read_csv('../data/region_coordinates.csv')

# For now let's just get the weather forecast on one single day
final_list = []
unique_regions_names = regions_df['Location'].unique()
for single_name in unique_regions_names:
        single_location = regions_df[regions_df['Location'] == single_name]
        region_name = str(single_location['Location'])
        latitude_s = float(single_location['Latitude'].iloc[0])
        longtitude_s = float(single_location['Longitude'].iloc[0])

        DYNAMIC_URL = f'{latitude_s},{longtitude_s}?key={API_KEY}'
        COMPLETE_URL = f'{BASE_URL}{DYNAMIC_URL}'

        response = requests.get(COMPLETE_URL, params=params)
        time.sleep(2.5)
        data = json.loads(response.text)
        days_list = data['days']

        for single_day in days_list:
            day = single_day
            date = day['datetime']
            precipcover = day['precipcover']
            precipprob = day['precipprob']
            preciptype = day['preciptype']
            tempmin = day['tempmin']
            tempmax = day['tempmax']
            windspeed = day['windspeed']

            if preciptype is None:
                pre_type = 0
            if preciptype is not None:
                if 'rain' in preciptype and 'snow' in preciptype:
                    pre_type = -0.85
                elif 'rain' in preciptype and 'snow' not in preciptype:
                    pre_type = -1
                elif 'snow' in preciptype and 'rain' not in preciptype:
                    pre_type = 0.1
                else:
                    pre_type = 0

            single_day_df =[]
            single_day_df.append({
                'date': date,
                'precipcover': precipcover,
                'precipprob': precipprob,
                'preciptype': preciptype,
                'tempmin': tempmin,
                'tempmax': tempmax,
                'windspeed': windspeed,
                'pre_type': pre_type
            })

            single_loc_df = pd.DataFrame(single_day_df)
            weather_score = universal_weather_scaling(single_loc_df)
            weather_score = np.round(weather_score, 2)
            weather_vector = (single_name, weather_score, date)
            final_list.append(weather_vector)
            print(date, weather_vector)

            counter += 1
            print(f'{counter} {single_name} done')

final_dataframe = pd.DataFrame(final_list, columns=['Region', 'Weather Score', 'Date'])
final_dataframe.to_csv('14_days_forecast_all_locations.csv')


