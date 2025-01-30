import requests
import geopandas as gpd
from helpers.preprocessing import *
from helpers.visualization import *
from helpers.database_operations import database
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class AppPipeline:
    def __init__(self):
        pass

    def choose_city(self, region, date1, date2, airports_to_regions):
        cached_response = database.get_cached_response(region, date1, date2)

        if cached_response is not None:
            return cached_response

        airports = self.return_all_airports_from_region(region, airports_to_regions)
        codes = airports['IATA'].drop_duplicates()
        results = []

        for code in codes:
            url = (f'https://serpapi.com/search.json?engine=google_flights&'
                   f'departure_id={code}&'
                   f'arrival_id=/m/02j9z&'
                   f'outbound_date={date1}&'
                   f'return_date={date2}&'
                   'currency=EUR&hl=en&'
                   'api_key=0b9c8e71f8c8cdfded4534c85ae9e2654c1dcded36500f298e32b3740d73a69b')

            try:
                response = requests.get(url)
                response.raise_for_status()
                flights = response.json()

                best_flights = flights.get('best_flights', [])
                other_flights = flights.get('other_flights', [])

                for flight in best_flights + other_flights:
                    results.append({'Away airports': flight['flights'][0]['arrival_airport']['id']})

            except requests.exceptions.RequestException as e:
                results.append({'Away airports': None})

        if not results:
            results.append({'Away airports': None})

        df = pd.DataFrame(results)
        database.cache_response(region, date1, date2, df.to_json())

        return df

    def main_algorithm(self, region, date1, date2, crime_rate, trains_rate, airports_rate, buses_rate, weather_rate,
                       unesco_score, data):
        weather_data = self.prepare_weather_data(data['14_days_forecast_all_locations'], date1)
        available_airport = self.choose_city(region, date1, date2, data['airports_to_regions2'])

        merged_df = combine_df(
            data['NUTS_AT'], data['crimes'], data['air_pollution'], data['airports_to_regions2'],
            data['region_coordinates'], available_airport, data['trains_to_regions2'], region, weather_data,
            data['bus_stops_to_regions'], data['regions_weather_history'], data['unesco'], self.return_month(date1)
        )

        merged_df = preprocess_df(merged_df)
        algorithm_df = self.create_algorithm(merged_df, crime_rate, airports_rate, trains_rate, buses_rate,
                                             weather_rate, unesco_score)

        tiles = self.map_algorithm(algorithm_df)
        graph = plot_map(tiles, region)
        top5_df = show_top_results(tiles, merged_df)

        print(top5_df)

        return graph, top5_df,

    @staticmethod
    def read_data():
        tables = {
            'air_pollution': ['TIME', '2021'],
            'crimes': ['TIME', '2022'],
            'NUTS_AT': ['NUTS_ID', 'NAME_LATN', 'CNTR_CODE'],
            'region_coordinates': ['Location', 'Latitude', 'Longitude'],
            'airports_to_regions2': None,
            'trains_to_regions2': ['Region Name', 'Stations'],
            '14_days_forecast_all_locations': ['Region', 'Weather Score', 'Date'],
            'bus_stops_to_regions': ['Region Name', 'Bus Stops Count'],
            'regions_weather_history': ['RegionName', 'Month', 'weather_score'],
            'unesco': ['Region', 'UNESCO_count', 'UNESCO_list']
        }

        return {
            table: database.select_from_db(table, columns)
            for table, columns in tables.items()
        }

    @staticmethod
    def prepare_weather_data(weather_data, target_date):
        weather_data['Date'] = pd.to_datetime(weather_data['Date']).dt.date
        return weather_data[weather_data['Date'] == target_date]

    @staticmethod
    def return_all_airports_from_region(region, airports_to_region_df):
        return airports_to_region_df[airports_to_region_df['Region Name'] == region]

    @staticmethod
    def return_month(date):
        return int(str(date.month).replace("0", ""))

    @staticmethod
    def create_algorithm(merged_df, crimes_rate=0.25, airports_rate=0.65, trains_rate=0.45,
                         buses_score=0.75, weather_score=0.65, unesco_score=0.50):

        merged_df['Algorytm'] = (
            -crimes_rate * merged_df['Przestępczość'] +
            -0.25 * merged_df['Zanieczyszczenie Powietrza'] +
            airports_rate * merged_df['Połączenia lotnicze'] +
            trains_rate * merged_df['Pobliskie Linie Kolejowe'] +
            buses_score * merged_df['Liczba Przystanków Autobusowych'] +
            airports_rate * merged_df['Liczba Portów Lotniczych'] +
            weather_score * merged_df['Pogoda'] +
            unesco_score * merged_df['Ilość obiektów UNESCO']
        )

        scaler = MinMaxScaler()
        merged_df[['Algorytm']] = scaler.fit_transform(merged_df[['Algorytm']])
        return merged_df

    @staticmethod
    def map_algorithm(merged_df):
        features = merged_df.set_index('NUTS_ID')['Algorytm'].to_dict()

        tiles = gpd.read_file("data/nuts2021/NUTS_RG_01M_2021_3035_LEVL_2.json", encoding="utf-8")
        tiles['Algorytm'] = tiles['NUTS_ID'].map(features)
        tiles['Algorytm'] = tiles['Algorytm'].fillna(0.0).astype(float)

        return tiles
