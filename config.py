import os
import streamlit as st

class Config:
    def __init__(self):
        self.cohere_key = st.secrets.get("COHERE_API_KEY", os.getenv("COHERE_API_KEY"))
        self.foursquare_key = st.secrets.get("FOURSQUARE_API_KEY", os.getenv("FOURSQUARE_API_KEY"))
        self.google_cse_key = st.secrets.get("GOOGLE_CSE_API_KEY", os.getenv("GOOGLE_CSE_API_KEY"))
        self.search_id = st.secrets.get("SEARCH_ENGINE_ID", os.getenv("SEARCH_ENGINE_ID"))
        self.weather_key = st.secrets.get("WEATHERAPI_API_KEY", os.getenv("WEATHERAPI_API_KEY"))

config = Config()
