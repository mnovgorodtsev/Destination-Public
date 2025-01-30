import pandas as pd
import numpy as np

def weather_history_preprocessing(raw_data):
    dropped_nan_data = raw_data.dropna()
    columns_of_interest = ['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']
    monthly_avg = dropped_nan_data.groupby('Month')[columns_of_interest].mean()
    monthly_avg = monthly_avg.round(2)

    numeric_columns = ['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']
    for column in numeric_columns:
        for index, row in raw_data.iterrows():
            if pd.isna(row[column]):
                month = row['Month']
                raw_data.at[index, column] = monthly_avg.at[month, column]
    """
    Optional
    combined_weather_data.to_csv('updated_historical_weather.csv', index=False)
    """
    preprocessed_data = raw_data
    return preprocessed_data