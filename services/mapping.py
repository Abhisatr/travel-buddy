import folium
import polyline
from folium.plugins import MarkerCluster

class MapVisualizer:
    def __init__(self, api_helper):
        self.api = api_helper
    
    def create_map(self, itinerary, city):
        m = folium.Map(location=self._get_city_center(city), zoom_start=12)
        self._add_markers(m, itinerary, city)
        self._add_route(m, itinerary, city)
        return m._repr_html_()
    
    def _get_city_center(self, city):
        lat, lng = self.api.get_coordinates(city, city)
        return [lat or 28.6139, lng or 77.2090]
    
    def _add_markers(self, map_obj, itinerary, city):
        cluster = MarkerCluster().add_to(map_obj)
        colors = ["red", "blue", "green", "orange"]
        for day_idx, day in enumerate(itinerary.values()):
            for time, loc in day.items():
                lat, lng = self.api.get_coordinates(loc, city)
                if lat and lng:
                    folium.Marker(
                        [lat, lng],
                        popup=f"{time}: {loc}",
                        icon=folium.Icon(color=colors[day_idx % 4])
                    ).add_to(cluster)
    
    def _add_route(self, map_obj, itinerary, city):
        coords = []
        for day in itinerary.values():
            for loc in day.values():
                lat, lng = self.api.get_coordinates(loc, city)
                if lat and lng: coords.append((lat, lng))
        if len(coords) > 1:
            route = self.api.calculate_route(coords)
            if route:
                folium.PolyLine([[lat, lng] for lng, lat in route], color="blue").add_to(map_obj)
