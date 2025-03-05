import cohere
import json
import re

class ItineraryGenerator:
    def __init__(self, api_key):
        self.client = cohere.Client(api_key)
    
    def generate(self, city, days, budget, focus):
        prompt = f"""Create a detailed {days}-day travel itinerary for a traveler in {city}.
    Focus heavily (70%) on these points of interest: {focus_category}.
    The traveler has a budget level of {budget}. Provide specific activities for each day.
    (Note: first fully generate a normal itinerary with one location per section of the day. Then, also include a JSON version where each section (morning, midday, evening) has only one location per day.)
"""
        response = self.client.chat(model="command-r-plus", message=prompt)
        return self._extract_json(response.text.strip())
    
    
    def _extract_json(self, text):
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
    
