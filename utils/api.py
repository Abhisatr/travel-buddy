import requests

class APIHelper:
    def __init__(self, config):
        self.headers = {"Authorization": config.foursquare_key}
        self.search_id = config.search_id
        self.google_key = config.google_cse_key
        self.weather_key = config.weather_key
    
    def get_coordinates(self, place, city):
        params = {"query": place, "near": city, "limit": 1}
        res = requests.get("https://api.foursquare.com/v3/places/search", headers=self.headers, params=params)
        return (res.json()["results"][0]["geocodes"]["main"]["latitude"],
                res.json()["results"][0]["geocodes"]["main"]["longitude"]) if res.ok else (None, None)
    
    def calculate_route(self, locations):
        coords = ";".join([f"{lng},{lat}" for lat, lng in locations])
        res = requests.get(f"http://router.project-osrm.org/route/v1/driving/{coords}?overview=full")
        return res.json()["routes"][0]["geometry"]["coordinates"] if res.ok else None
    
    def get_place_image(self, place):
        params = {"q": place, "cx": self.search_id, "key": self.google_key, "searchType": "image", "num": 1}
        res = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        return res.json()["items"][0]["link"] if res.ok else None
    
    def get_weather(self, location):
        params = {"key": self.weather_key, "q": location, "days": 6, "aqi": "no", "alerts": "no"}
        res = requests.get("https://api.weatherapi.com/v1/forecast.json", params=params)
        return res.json()["forecast"]["forecastday"] if res.ok else None
