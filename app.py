
import cohere
import json
import re
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
from folium.plugins import MarkerCluster
import polyline
from fpdf import FPDF
from datetime import datetime, timedelta
from config import config

# API Keys
COHERE_API_KEY = config.cohere_key
FOURSQUARE_API_KEY = config.foursquare_key
GOOGLE_CSE_API_KEY = config.google_cse_key
SEARCH_ENGINE_ID = config.search_id
WEATHERAPI_API_KEY = config.weather_key # WeatherAPI key


# Initialize clients and URLs
OSRM_API_URL = "http://router.project-osrm.org/route/v1/driving/"
co = cohere.Client(COHERE_API_KEY)
FOURSQUARE_BASE_URL = "https://api.foursquare.com/v3/places/search"
GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
WEATHERAPI_URL = "https://api.weatherapi.com/v1/forecast.json"

# Function to generate itinerary text using Cohere
def generate_itinerary_text(city, days, budget, focus_category):
    prompt = f"""
    Create a detailed {days}-day travel itinerary for a traveler in {city}.
    Focus heavily (70%) on these points of interest: {focus_category}.
    The traveler has a budget level of {budget}. Provide specific activities for each day.
    (Note: first fully generate a normal itinerary with one location per section of the day. Then, also include a JSON version where each section (morning, midday, evening) has only one location per day.)
    """

    response = co.chat(
        model="command-r-plus",  # Use "command-r-plus" instead of "command-xlarge-nightly"
        message = prompt
    )
    
    return response.text.strip()  # Adjust based on the response format




# Function to extract JSON itinerary from the generated text
def extract_json_from_itinerary(itinerary_text):
    json_match = re.search(r'```json\n(.*?)\n```', itinerary_text, re.DOTALL)
    if json_match:
        json_string = json_match.group(1)
        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    else:
        print("No JSON found in the itinerary text.")
        return None

# Function to get coordinates using Foursquare API
def get_coordinates(place_name, city):
    headers = {"Authorization": FOURSQUARE_API_KEY}
    params = {"query": place_name, "near": city, "limit": 1}
    response = requests.get(FOURSQUARE_BASE_URL, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            lat = results[0]["geocodes"]["main"]["latitude"]
            lng = results[0]["geocodes"]["main"]["longitude"]
            return lat, lng
    return None, None

# Function to calculate the optimal route using OSRM API
def calculate_optimal_route(locations):
    coords = ";".join([f"{lng},{lat}" for lat, lng in locations])
    url = f"{OSRM_API_URL}{coords}?overview=full&geometries=geojson"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["routes"][0]["geometry"]["coordinates"]
    return None

# Function to plot the itinerary on a map using Folium
def plot_itinerary_on_map(itinerary, city="Delhi"):
    coordinates = []
    color_map = ["red", "blue", "green", "orange"]

    # Get coordinates for the center of the city
    city_lat, city_lng = get_coordinates(city, city)
    if city_lat and city_lng:
        map_center = [city_lat, city_lng]
    else:
        map_center = [28.6139, 77.2090]  # Default to Delhi if coordinates aren't found

    # Create a folium map centered around the city
    mymap = folium.Map(location=map_center, zoom_start=12)
    marker_cluster = MarkerCluster().add_to(mymap)

    # Iterate over the list of dictionaries
    for day_idx, day in enumerate(itinerary.values()):  # Iterate through the days
        for time, location in day.items():  # Directly access time-location pairs
            lat, lng = get_coordinates(location, city)
            if lat and lng:
                folium.Marker(
                    location=[lat, lng],
                    popup=f"{time.capitalize()}: {location}",
                    icon=folium.Icon(color=color_map[day_idx % len(color_map)])
                ).add_to(marker_cluster)
                coordinates.append((lat, lng))

    if len(coordinates) > 1:  # Ensure there are multiple points for a route
        route = calculate_optimal_route(coordinates)
        if route:
            # Use the route directly to draw a polyline
            folium.PolyLine(locations=[[lat, lng] for lng, lat in route], color="blue", weight=5, opacity=0.7).add_to(mymap)

    # Display the map using Streamlit
    folium_static(mymap)

# Function to fetch place images using Google CSE
def fetch_place_image(place_name):
    params = {
        "q": place_name,
        "cx": SEARCH_ENGINE_ID,
        "key": GOOGLE_CSE_API_KEY,
        "searchType": "image",
        "num": 1
    }
    response = requests.get(GOOGLE_CSE_URL, params=params)
    if response.status_code == 200:
        results = response.json().get("items", [])
        if results:
            return results[0]["link"]
    return None

# Function to fetch weather data using WeatherAPI
def fetch_weather(location, days=6):
    params = {
        "key": WEATHERAPI_API_KEY,
        "q": location,
        "days": days,  # Fetch forecast for up to 6 days
        "aqi": "no",  # Disable air quality index data
        "alerts": "no"  # Disable weather alerts
    }
    response = requests.get(WEATHERAPI_URL, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        forecast = weather_data.get("forecast", {}).get("forecastday", [])
        if forecast:
            return forecast  # Return the forecast for each day
    return None

# Function to display weather forecast for each day of the itinerary
def display_weather_forecast(itinerary):
    city = itinerary.get("city", "Delhi")  # Default city if not provided
    weather_forecast = fetch_weather(city)
    if weather_forecast:
        st.subheader(f"Weather Forecast for {city}")
        for idx, day in enumerate(weather_forecast):
            date = day["date"]
            day_temp = day["day"]["avgtemp_c"]
            condition = day["day"]["condition"]["text"]
            st.write(f"{date}: {condition} - {day_temp}Â°C")
    else:
        st.write("Weather data not available.")

# Function to display the itinerary with images and weather data
def display_itinerary_with_images_and_weather(itinerary):
    for day, schedule in itinerary.items():
        st.write(f"**{day}:**")
        for time, location in schedule.items():
            st.write(f"{time.capitalize()}: {location}")
            image_url = fetch_place_image(location)
            weather = fetch_weather(location)
            if image_url:
                st.image(image_url, caption=f"Image of {location}")
            if weather:
                weather_data = weather[0]["day"]
                temp = weather_data["avgtemp_c"]
                condition = weather_data["condition"]["text"]
                st.write(f"Weather: {condition} - {temp}Â°C")
            st.write("----")


# Function to save itinerary as PDF
def save_itinerary_as_pdf(itinerary, city):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Travel Itinerary for {city}", ln=True, align='C')
    pdf.ln(10)

    for day, schedule in itinerary.items():
        pdf.cell(200, 10, txt=f"{day}", ln=True)
        for time, location in schedule.items():
            pdf.cell(200, 10, txt=f"{time.capitalize()}: {location}", ln=True)
        pdf.ln(5)

    pdf.output("itinerary.pdf")

# Main function for Streamlit app
def main():
    st.title("Travel Buddy- Travel Assistance")

    city = st.text_input("Enter city name:", "Delhi")
    days = st.slider("Select number of days:", 1, 6, 5)  # Limit to max 6 days
    budget = st.selectbox("Select budget level:", ["Low", "Medium", "High"])
    focus_category = st.text_input("Enter your category of focus:", "sightseeing")

    if st.button("Generate Itinerary"):
        itinerary_text = generate_itinerary_text(city, days, budget, focus_category)
        st.subheader("Generated Itinerary")
        st.write(itinerary_text)

        itinerary_json = extract_json_from_itinerary(itinerary_text)
        if itinerary_json:
            display_itinerary_with_images_and_weather(itinerary_json)
            plot_itinerary_on_map(itinerary_json, city)
            save_itinerary_as_pdf(itinerary_json, city)

            
if __name__ == "__main__":
    main()
