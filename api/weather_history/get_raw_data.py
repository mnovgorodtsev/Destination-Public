from datetime import datetime
import numpy as np
import pandas as pd
from meteostat import Point, Daily
pd.set_option('display.max_columns', None)

# Loading regions and coordinates
coords_dataset = pd.read_csv('region_coordinates.csv')

def fetch_raw_data(coords_dataset):

    # 2019 is the best year, only ~28 regions without historical data
    start = datetime(2019, 1, 1)
    end = datetime(2019, 12, 31)

    weather_data_list = []
    for index, row in coords_dataset.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        region_name = row['Location']
        location = Point(lat, lon)

        data = Daily(location, start, end)
        data = data.fetch()

        if not data.empty:
            data['Datetime'] = data.index
            data['Latitude'] = lat
            data['Longitude'] = lon
            monthly_data = data.resample('ME').mean()
            monthly_data['RegionName'] = region_name
            weather_data_list.append(monthly_data)
        else:
            empty_data = pd.DataFrame(np.nan, index=range(12),
                                      columns=['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun', 'Latitude', 'Longitude', 'RegionName'])
            year = 2022
            empty_data['Datetime'] = pd.to_datetime([f'{year}-{i:02d}-01' for i in range(1, 13)])
            empty_data['Latitude'] = lat
            empty_data['Longitude'] = lon
            empty_data['RegionName'] = region_name
            weather_data_list.append(empty_data)

    if weather_data_list:
        combined_weather_data = pd.concat(weather_data_list)
        numeric_columns = combined_weather_data.select_dtypes(include=[np.number])
        combined_weather_data[numeric_columns.columns] = combined_weather_data[numeric_columns.columns].apply(pd.to_numeric,
                                                                                                              errors='coerce')
        combined_weather_data['Month'] = combined_weather_data['Datetime'].dt.month
        combined_weather_data = combined_weather_data.round(2)
        return combined_weather_data
    else:
        print("No weather data collected")