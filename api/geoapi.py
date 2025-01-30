import requests
import pandas as pd
import time
from app_pipeline import AppPipeline


# Rest of information that we can use
# accommodation.hotel, activity.community_center
# activity.sport_club,  airport.international, commercial.supermarket
# commercial.shopping_mall, commercial.outdoor_and_sport, commercial.hobby
# commercial.food_and_drink, catering.restaurant, catering.cafe, entertainment.culture, heritage
# leisure, natural, railway, rental, tourism, camping, beach, public_transport

def scrap_unesco():
    database_data = AppPipeline.read_data()
    regions_coords = database_data['region_coordinates']
    print(regions_coords)
    output = []
    for index, row in regions_coords.iterrows():
        time.sleep(5)
        location = row['Location']
        lat = row['Latitude']
        long = row['Longitude']

        # remember that lat and long are swapped
        url = (f"https://api.geoapify.com/v2/places?"
               f"categories=heritage.unesco&"
               f"filter=circle:{long},{lat},30000&"
               f"limit=20&"
               f"apiKey=api_key")

        response_json = requests.get(url).json()
        if len(response_json['features']) > 0:
            for i in range(0, len(response_json['features'])):
                if 'name:en' in response_json['features'][i]['properties']['datasource']['raw']:
                    name = response_json['features'][i]['properties']['datasource']['raw']['name:en']
                    print(name)
                    output.append((location, name))
                else:
                    output.append((location, None))
        else:
            output.append((location, None))

    unesco_df = pd.DataFrame(output, columns=['Region', 'UNESCO_name'])
    unesco_df = unesco_df.drop_duplicates()
    unesco_df.to_csv('Unesco_Heritage.csv')


def unesco_preprocess(unesco_df_raw):
    unesco_df = unesco_df_raw.groupby('Region').agg(
        UNESCO_count=('UNESCO_name', 'count'),
        UNESCO_list=('UNESCO_name', lambda x: x.dropna().tolist())
    ).reset_index()
    return unesco_df


unesco_df_raw = pd.read_csv('Unesco_Heritage.csv')
unesco_df = unesco_preprocess(unesco_df_raw)
print(unesco_df, unesco_df['UNESCO_count'].sum())
unesco_df.to_csv('UNESCO_DF.csv')
