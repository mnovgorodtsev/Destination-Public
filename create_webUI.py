from datetime import datetime, timedelta
from chatbot import *
from app_pipeline import *
import streamlit as st


class WebUI:

    def __init__(self):
        self.pipeline = AppPipeline()
        self.chatbot = Chatbot()

        st.set_page_config(
            layout="wide",
        )

    def display_frontend(self):
        self._init_frontend()

    def _init_frontend(self):
        st.markdown("## Planowanie podróży")

        col1, col2 = st.columns([1, 2])
        # start on init, no graph yet
        graph = None
        with col1:
            data = self.pipeline.read_data()
            region, date1, date2 = self._init_basic_options(data['region_coordinates'])
            preferences = self._init_user_preferences()

            if st.button("Szukaj"):
                st.markdown("## Wyniki")

                graph, top5_df = self.pipeline.main_algorithm(
                    region, date1, date2, *preferences, data
                )

        with col2:
            if graph is not None:
                st.pyplot(graph)
            else:
                st.write("Wykres pojawi się po kliknięciu 'Szukaj'")

        if graph is not None:
            with st.chat_message("assistant"):
                response = self.chatbot.describe_table(top5_df.to_string())
                st.write(response)

    @staticmethod
    def _init_basic_options(region_coords):
        region = st.selectbox(label='Region rozpoczęcia podróży', options=region_coords['Location'].unique())
        date1 = st.date_input("Data rozpoczęcia podróży", value=datetime.today() + timedelta(days=1))
        date2 = st.date_input("Data zakończenia podróży", value=datetime.today() + timedelta(days=5))
        return region, date1, date2

    @staticmethod
    def _init_user_preferences():
        options = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        unesco_options = [0, 0.5, 1]

        preferences = {
            "crime_rate": st.select_slider("Bezpieczeństwo", value=0.2, options=options),
            "trains_rate": st.select_slider("Połączenia kolejowe", value=0.4, options=options),
            "airports_rate": st.select_slider("Połączenia lotnicze", value=0.6, options=options),
            "buses_rate": st.select_slider("Połączenia autobusowe", value=0.2, options=options),
            "weather_rate": st.select_slider("Pogoda", value=0.9, options=options),
            "unesco_rate": st.select_slider("UNESCO", value=0.5, options=unesco_options)
        }

        return tuple(preferences.values())