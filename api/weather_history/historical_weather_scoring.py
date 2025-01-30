import pandas as pd
import numpy as np

# preprocessed data going in
def universal_weather_scaling(historical_weather_df, snow_acceptance=1):
    # Windspeed
    def windspeed_scale(windspeed):
        if windspeed <= 5:
            return 0
        elif windspeed <= 15:
            return -2
        elif windspeed <= 20:
            return -4
        elif windspeed <= 40:
            return -8
        else:
            return -16

    historical_weather_df['wind_category'] = historical_weather_df['wspd'].apply(windspeed_scale)

    # Temperature
    # Average
    def temp_scale(temperature):
        if temperature <= -10:
            return 0
        elif temperature <= 0:
            return 5
        elif temperature <= 5:
            return 8
        elif temperature <= 10:
            return 10
        elif temperature <= 15:
            return 15
        elif temperature <= 30:
            return 20
        elif temperature <= 40:
            return 12
        else:
            return 0

    historical_weather_df['temp_category'] = historical_weather_df['tavg'].apply(temp_scale)

    # Rain
    def rain_precip_scale(precipcover):
        if precipcover <= 0:
            cover_value = 1
        elif precipcover <= 1:
            cover_value = 2
        elif precipcover <= 2:
            cover_value = 3
        elif precipcover <= 5:
            cover_value = 4
        else:
            cover_value = 1

        output_value = cover_value
        return output_value

    # Snow
    def snow_precip_scale(snow, snow_acceptance=1):
        if snow <= 5:
            cover_value = 0.03
        elif snow <= 30:
            cover_value = 1
        elif snow <= 50:
            cover_value = 1.25
        else:
            cover_value = 0
        return cover_value * snow_acceptance

    # Calculating
    historical_weather_df['snow_precip'] = historical_weather_df['snow'].apply(snow_precip_scale)
    historical_weather_df['precip_score'] = historical_weather_df.apply(lambda row: rain_precip_scale(row['prcp']), axis=1)
    historical_weather_df['precip_scaled'] = historical_weather_df['precip_score'] * -1 + historical_weather_df['snow_precip']
    historical_weather_df['weather_score'] = historical_weather_df['wind_category'] + historical_weather_df['temp_category'] + historical_weather_df['precip_scaled']
    historical_weather_df['weather_score'] = np.round(historical_weather_df['weather_score'], 2)

    return historical_weather_df[['RegionName', 'Month', 'weather_score']].reset_index(drop=True)