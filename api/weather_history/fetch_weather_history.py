from datetime import datetime
import numpy as np
import pandas as pd
from meteostat import Point, Daily

from get_raw_data import fetch_raw_data
from preprocessing import weather_history_preprocessing
from historical_weather_scoring import universal_weather_scaling

# Loading data - in future from cloud
coords_dataset = pd.read_csv('region_coordinates.csv')


raw_data = fetch_raw_data(coords_dataset)
preprocessed_data = weather_history_preprocessing(raw_data)
# output
regions_scored = universal_weather_scaling(preprocessed_data)
regions_scored.to_csv('output.csv')
print(regions_scored)