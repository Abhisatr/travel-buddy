import streamlit as st
from config import config
from services.itinerary import ItineraryGenerator
from services.mapping import MapVisualizer
from utils.api import APIHelper
from utils.pdf import PDFGenerator

def main():
    st.title("Travel Buddy")
    api = APIHelper(config)
    itinerary_gen = ItineraryGenerator(config.cohere_key)
    map_viz = MapVisualizer(api)

    city = st.text_input("City:", "Delhi")
    days = st.slider("Days:", 1, 6, 3)
    budget = st.selectbox("Budget:", ["Low", "Medium", "High"])
    focus = st.text_input("Interests:", "sightseeing")

    if st.button("Generate"):
        try:
            text = itinerary_gen.generate(city, days, budget, focus)
            itinerary = itinerary_gen._extract_json(text)
            
            if itinerary:
                st.subheader(f"{days}-Day Itinerary")
                for day, plan in itinerary.items():
                    with st.expander(day):
                        st.json(plan)
                
                st.subheader("Map")
                st.components.v1.html(map_viz.create_map(itinerary, city), height=500)
                
                PDFGenerator.create(itinerary, city, "itinerary.pdf")
                with open("itinerary.pdf", "rb") as f:
                    st.download_button("Download PDF", f, file_name=f"{city}_itinerary.pdf")

        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
