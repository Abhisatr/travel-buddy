import cohere
import json
import re

class ItineraryGenerator:
    def __init__(self, api_key):
        self.client = cohere.Client(api_key)
    
    def generate(self, city, days, budget, focus):
        prompt = f"Create {days}-day {city} itinerary focused on {focus} with {budget} budget. Include JSON."
        response = self.client.chat(model="command-r-plus", message=prompt)
        return self._extract_json(response.text)
    
    def _extract_json(self, text):
        match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        return json.loads(match.group(1)) if match else None
