import pandas as pd
pd.set_option('display.max_columns', 20)
pd.options.display.width = 0

def universal_weather_scaling(weather_df):
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

    weather_df['wind_category'] = weather_df['windspeed'].apply(windspeed_scale)

    # Temperature
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

    weather_df['temp_category'] = weather_df['tempmax'].apply(temp_scale)

    # Precip scale - we have to scale it from 0 to 30 because precip_type (snow or rain)
    # defined the positive or negative value of it
    def precip_scale(precipcover, precipprob):
        if precipcover <= 20:
            cover_value = 1
        elif precipcover <= 40:
            cover_value =  2
        elif precipcover <= 60:
            cover_value =  3
        elif precipcover <= 100:
            cover_value =  4

        if precipprob <= 20:
            prob_value = 2
        elif precipprob <= 40:
            prob_value =  4
        elif precipprob <= 50:
            prob_value =  5
        elif precipprob <= 80:
            prob_value =  6
        elif precipprob <= 100:
            prob_value =  7

        output_value = prob_value + cover_value
        return output_value

    weather_df['precip_score'] = weather_df.apply(lambda row: precip_scale(row['precipcover'],
                                                                           row['precipprob']), axis=1)

    weather_df['precip_scaled'] = weather_df['precip_score'] * weather_df['pre_type']

    weather_df['weather_score'] = weather_df['wind_category'] + weather_df['temp_category'] + weather_df['precip_scaled']
    return weather_df['weather_score'].iloc[0]

# Testing phase
# weather_df = pd.read_csv('poznan_test.csv')
# print(weather_df)
# final_df = universal_weather_scaling(weather_df)
# print(final_df)