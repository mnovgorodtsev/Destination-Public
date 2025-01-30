import json
import pycountry
from sklearn.preprocessing import MinMaxScaler
from math import radians, sin, cos, sqrt, atan2
import pandas as pd


def combine_df(nuts, crimes, air_pollution, airports_to_regions, region_cords, available_airport,
               trains_to_regions, assigned_region, weather_15_days, buses, weather_history, unesco_df, month):
    # matching trains
    stations_row = select_region_with_stations(trains_to_regions, assigned_region).drop_duplicates()
    trains_to_regions = assign_stations_datapoints_to_region(stations_row, region_cords)

    # NUTS
    merged_df = pd.merge(region_cords, nuts, left_on='Location', right_on='NAME_LATN', how='left')

    # crimes
    merged_df = pd.merge(merged_df, crimes, left_on='NAME_LATN', right_on='TIME', how='left')

    # air pollution
    air_pollution['CNTR_CODE'] = air_pollution['TIME'].apply(get_country_code)
    air_pollution = air_pollution[['CNTR_CODE', '2021']]
    merged_df = pd.merge(merged_df, air_pollution, on='CNTR_CODE', how='left')

    # airports
    merged_df = pd.merge(merged_df, airports_to_regions[['Region Name', 'IATA']], left_on='NAME_LATN',
                         right_on='Region Name', how='left')
    merged_df = pd.merge(merged_df, available_airport, left_on='IATA', right_on='Away airports', how='left')
    merged_df['Air connections'] = (merged_df.groupby('Location')['Away airports'].transform(lambda x: x.notna().
                                                                                             sum()).fillna(-2))
    iata_count = (airports_to_regions.groupby('Region Name')['IATA'].nunique().reset_index())
    iata_count.columns = ['Region Name', 'IATA count']
    merged_df = pd.merge(merged_df, iata_count, on='Region Name', how='left')
    merged_df['Airports count'] = (merged_df.groupby('Region Name')['IATA'].transform('nunique'))

    # trains
    merged_df = pd.merge(merged_df, trains_to_regions, on='Region Name', how='left')

    # weather
    if weather_15_days is not None and not weather_15_days.empty:
        merged_df = pd.merge(merged_df, weather_15_days, left_on='Location', right_on='Region', how='inner')
        columns_to_remove = ['Away airports', 'IATA', 'NAME_LATN', 'TIME', 'Region Name', 'IATA count', 'Region',
                             'Date']
    else:
        weather_history = select_month(weather_history, month)
        merged_df = pd.merge(merged_df, weather_history, left_on='Location', right_on='RegionName', how='inner')
        merged_df.rename(columns={'weather_score': 'Weather Score'}, inplace=True)
        columns_to_remove = ['Away airports', 'IATA', 'NAME_LATN', 'TIME', 'Region Name', 'IATA count', 'Month',
                             'RegionName']

    # buses
    merged_df = pd.merge(merged_df, buses, on='Region Name', how='left')

    # unesco
    unesco_df = unesco_df.rename(columns={'Region': 'Region Name'})
    merged_df = pd.merge(merged_df, unesco_df, on='Region Name', how='left')

    # drop
    merged_df = merged_df.drop(columns=columns_to_remove)
    merged_df = merged_df.drop_duplicates()

    return merged_df


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def assign_stations_datapoints_to_region(stations_df, regions_df):
    matching_regions = []
    stations_df['Stations'] = (stations_df['Stations'].
                               apply(lambda x: json.loads(x) if isinstance(x, str) else x))

    for lat1, lon1, region in zip(regions_df['Latitude'],
                                  regions_df['Longitude'],
                                  regions_df['Location']):
        for _, row in stations_df.iterrows():
            for lat2, lon2 in row['Stations']:
                distance = haversine(lat1, lon1, lat2, lon2)
                if distance < 300:
                    is_close = 1
                else:
                    is_close = 0

                matching_regions.append({
                    'Region Name': region,
                    'Train Lines Count': is_close,
                })

    if not matching_regions:
        matching_regions.append({
            'Region Name': None,
            'Train Lines Count': None,
        })

    matching_regions = pd.DataFrame(matching_regions).drop_duplicates()
    return matching_regions


def select_region_with_stations(df, region):
    return df[df['Region Name'] == region]


def select_month(df, date1):
    return df[df['Month'] == date1]


def preprocess_df(merged_df):
    # convert to float
    merged_df['Air connections'] = merged_df['Air connections'].astype(float)
    merged_df['Train Lines Count'] = merged_df['Train Lines Count'].astype(float)
    merged_df['Airports count'] = merged_df['Airports count'].astype(float)
    merged_df['Weather Score'] = merged_df['Weather Score'].astype(float)
    merged_df['Bus Stops Count'] = merged_df['Bus Stops Count'].astype(float)
    merged_df['UNESCO_count'] = merged_df['UNESCO_count'].astype(float)

    # scale
    scaler = MinMaxScaler()
    merged_df.loc[:, ['2022', '2021', 'Air connections', 'Airports count', 'Bus Stops Count',
                      'Weather Score', 'UNESCO_count']] = (
        scaler.fit_transform(merged_df[['2022', '2021', 'Air connections', 'Airports count',
                                        'Bus Stops Count', 'Weather Score', 'UNESCO_count']]))

    # handle missing values
    mean_2022 = merged_df['2022'].mean()
    merged_df.loc[:, '2022'] = merged_df['2022'].fillna(mean_2022)
    mean_2021 = merged_df['2021'].mean()
    merged_df.loc[:, '2021'] = merged_df['2021'].fillna(mean_2021)
    merged_df.loc[:, 'Train Lines Count'] = merged_df['Train Lines Count'].fillna(0)
    merged_df.loc[:, 'Bus Stops Count'] = merged_df['Bus Stops Count'].fillna(0)
    merged_df.loc[:, 'Airports count'] = merged_df['Airports count'].fillna(0)
    merged_df.loc[:, 'UNESCO_count'] = merged_df['UNESCO_count'].fillna(0)
    median_air_pollution = merged_df['2021'].median()
    median_crimes_rate = merged_df['2022'].median()
    merged_df.loc[merged_df['2021'] == 0.0, '2021'] = median_air_pollution
    merged_df.loc[merged_df['2022'] == 0.0, '2022'] = median_crimes_rate

    # drop duplicates
    merged_df = merged_df.drop_duplicates()

    merged_df = merged_df.rename(columns={'2022': 'Przestępczość', '2021': 'Zanieczyszczenie Powietrza',
                                          'Weather Score': 'Pogoda',
                                          'Bus Stops Count': 'Liczba Przystanków Autobusowych', 'Airports count':
                                              'Liczba Portów Lotniczych', 'Air connections': 'Połączenia lotnicze',
                                          'Train Lines Count': 'Pobliskie Linie Kolejowe', 'Location': 'Region',
                                          'UNESCO_count': 'Ilość obiektów UNESCO'})

    return merged_df


def get_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        return None
