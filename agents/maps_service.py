"""
maps_service.py — Geocoding & location services for KHABAR.
Uses local Pakistan city dictionary first, then OpenStreetMap Nominatim (free).
FR-08: Detection Agent shall extract location and attempt GPS geocoding.
FR-13: Analysis Agent shall identify nearby critical infrastructure via Maps API.
"""
import os
import logging
from typing import Dict, Any, List, Optional

import httpx
import urllib3
from dotenv import load_dotenv

# Suppress TLS verification warnings in logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()


class MapsService:
    # Pakistan areas dictionary for instant offline geocoding
    PAKISTAN_LOCATIONS: Dict[str, Dict[str, Any]] = {
        "islamabad": {"lat": 33.6844, "lng": 73.0479, "city": "Islamabad"},
        "rawalpindi": {"lat": 33.5651, "lng": 73.0169, "city": "Rawalpindi"},
        "lahore": {"lat": 31.5204, "lng": 74.3587, "city": "Lahore"},
        "karachi": {"lat": 24.8607, "lng": 67.0011, "city": "Karachi"},
        "peshawar": {"lat": 34.0151, "lng": 71.5249, "city": "Peshawar"},
        "quetta": {"lat": 30.1798, "lng": 66.9750, "city": "Quetta"},
        "multan": {"lat": 30.1575, "lng": 71.5249, "city": "Multan"},
        "faisalabad": {"lat": 31.4504, "lng": 73.1350, "city": "Faisalabad"},
        "hyderabad": {"lat": 25.3960, "lng": 68.3578, "city": "Hyderabad"},
        "g-10": {"lat": 33.6938, "lng": 73.0551, "city": "Islamabad"},
        "g-11": {"lat": 33.7015, "lng": 73.0400, "city": "Islamabad"},
        "g-9": {"lat": 33.7060, "lng": 73.0630, "city": "Islamabad"},
        "f-7": {"lat": 33.7245, "lng": 73.0629, "city": "Islamabad"},
        "f-8": {"lat": 33.7180, "lng": 73.0530, "city": "Islamabad"},
        "blue area": {"lat": 33.7220, "lng": 73.0580, "city": "Islamabad"},
        "jinnah avenue": {"lat": 33.7220, "lng": 73.0580, "city": "Islamabad"},
        "murree road": {"lat": 33.6105, "lng": 73.0783, "city": "Rawalpindi"},
        "saddar rawalpindi": {"lat": 33.5980, "lng": 73.0489, "city": "Rawalpindi"},
        "dha lahore": {"lat": 31.4697, "lng": 74.4082, "city": "Lahore"},
        "gulberg lahore": {"lat": 31.5120, "lng": 74.3500, "city": "Lahore"},
        "saddar karachi": {"lat": 24.8538, "lng": 67.0174, "city": "Karachi"},
        "clifton": {"lat": 24.8072, "lng": 67.0298, "city": "Karachi"},
        "defence karachi": {"lat": 24.7898, "lng": 67.0650, "city": "Karachi"},
        "johar town": {"lat": 31.4697, "lng": 74.2712, "city": "Lahore"},
        "model town": {"lat": 31.4911, "lng": 74.3138, "city": "Lahore"},
        "hayatabad": {"lat": 34.0031, "lng": 71.4578, "city": "Peshawar"},
        "cantonment": {"lat": 33.5651, "lng": 73.0169, "city": "Rawalpindi"},
    }

    HOSPITALS_BY_CITY: Dict[str, List[Dict]] = {
        "Islamabad": [
            {"name": "PIMS Hospital", "distance_km": 2.1, "estimated_travel_time_mins": 8, "status": "OPERATIONAL"},
            {"name": "Poly Clinic Hospital", "distance_km": 3.5, "estimated_travel_time_mins": 12, "status": "OPERATIONAL"},
            {"name": "Shifa International Hospital", "distance_km": 5.2, "estimated_travel_time_mins": 18, "status": "OPERATIONAL"},
        ],
        "Rawalpindi": [
            {"name": "Holy Family Hospital", "distance_km": 1.9, "estimated_travel_time_mins": 7, "status": "OPERATIONAL"},
            {"name": "Benazir Bhutto Hospital", "distance_km": 3.0, "estimated_travel_time_mins": 12, "status": "OPERATIONAL"},
            {"name": "District Headquarters Hospital", "distance_km": 2.5, "estimated_travel_time_mins": 10, "status": "OPERATIONAL"},
        ],
        "Lahore": [
            {"name": "Mayo Hospital", "distance_km": 2.8, "estimated_travel_time_mins": 10, "status": "OPERATIONAL"},
            {"name": "Services Hospital", "distance_km": 3.5, "estimated_travel_time_mins": 14, "status": "OPERATIONAL"},
            {"name": "Jinnah Hospital", "distance_km": 4.1, "estimated_travel_time_mins": 16, "status": "OPERATIONAL"},
        ],
        "Karachi": [
            {"name": "Aga Khan University Hospital", "distance_km": 3.2, "estimated_travel_time_mins": 15, "status": "OPERATIONAL"},
            {"name": "Civil Hospital Karachi", "distance_km": 4.1, "estimated_travel_time_mins": 20, "status": "OPERATIONAL"},
            {"name": "Liaquat National Hospital", "distance_km": 5.0, "estimated_travel_time_mins": 22, "status": "OPERATIONAL"},
        ],
        "Peshawar": [
            {"name": "Lady Reading Hospital", "distance_km": 2.5, "estimated_travel_time_mins": 10, "status": "OPERATIONAL"},
            {"name": "Khyber Teaching Hospital", "distance_km": 3.0, "estimated_travel_time_mins": 12, "status": "OPERATIONAL"},
        ],
    }

    def geocode_location(self, location_text: str) -> Dict[str, Any]:
        """Geocode a Pakistani location name to lat/lng using Google Maps Geocoding API."""
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if api_key:
            try:
                response = httpx.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={"address": f"{location_text}, Pakistan", "key": api_key},
                    timeout=8.0
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK" and data.get("results"):
                        result = data["results"][0]
                        loc = result["geometry"]["location"]
                        address = result.get("formatted_address", location_text)
                        
                        # Infer city from address components
                        city = "Islamabad"
                        for comp in result.get("address_components", []):
                            if "locality" in comp.get("types", []):
                                city = comp.get("long_name", "Islamabad")
                                break
                            elif "administrative_area_level_2" in comp.get("types", []):
                                city = comp.get("long_name", "Islamabad")
                                
                        return {
                            "found": True,
                            "lat": loc["lat"],
                            "lng": loc["lng"],
                            "city": city,
                            "address": address,
                            "source": "google_maps_api",
                        }
            except Exception as e:
                logging.warning(f"[MapsService] Google Maps Geocoding API failed: {e}")

        # Fallback to local dictionary
        normalized = location_text.lower().strip()
        for key, coords in self.PAKISTAN_LOCATIONS.items():
            if key in normalized or normalized in key:
                return {
                    "found": True,
                    "lat": coords["lat"],
                    "lng": coords["lng"],
                    "city": coords["city"],
                    "address": location_text,
                    "source": "local_cache",
                }

        # Fallback to OpenStreetMap Nominatim
        try:
            response = httpx.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": f"{location_text} Pakistan", "format": "json", "limit": 1},
                headers={"User-Agent": "KhabarEmergencyApp/1.0"},
                timeout=5.0,
                verify=False,
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    city = data[0].get("display_name", "").split(",")[0]
                    return {
                        "found": True,
                        "lat": float(data[0]["lat"]),
                        "lng": float(data[0]["lon"]),
                        "city": city,
                        "address": data[0].get("display_name", location_text),
                        "source": "nominatim",
                    }
        except Exception as e:
            logging.warning(f"[MapsService] Nominatim failed: {e}")

        # Default fallback — Islamabad center
        return {
            "found": False,
            "lat": 33.6844,
            "lng": 73.0479,
            "city": "Pakistan",
            "address": location_text,
            "source": "default_fallback",
        }

    # Islamabad Resource Stations with coordinates (FR-05, FR-06)
    ISLAMABAD_RESOURCE_STATIONS = [
        {
            "station_id": "ST-01",
            "name": "Faizabad Rescue 1122 Station",
            "lat": 33.6601,
            "lng": 73.0789,
            "resource_types": ["ambulances", "traffic_units"],
            "address": "Faizabad Interchange, Islamabad"
        },
        {
            "station_id": "ST-02",
            "name": "G-10 WASA Depot",
            "lat": 33.6938,
            "lng": 73.0551,
            "resource_types": ["dewatering_pumps"],
            "address": "G-10 Markaz, Islamabad"
        },
        {
            "station_id": "ST-03",
            "name": "Blue Area Fire Headquarters",
            "lat": 33.7182,
            "lng": 73.0673,
            "resource_types": ["fire_trucks"],
            "address": "Jinnah Avenue, Blue Area, Islamabad"
        },
        {
            "station_id": "ST-04",
            "name": "F-8 NDMA Emergency Depot",
            "lat": 33.7118,
            "lng": 73.0422,
            "resource_types": ["utility_crews"],
            "address": "F-8 Markaz, Islamabad"
        }
    ]

    def calculate_islamabad_resource_eta(self, user_lat: float, user_lng: float, required_resource: str) -> Dict[str, Any]:
        """
        Calculate the closest resource station in Islamabad/Rawalpindi for the required resource,
        returning distance (km) and estimated travel time (mins) using Google Maps Distance Matrix API.
        """
        resource_map = {
            "ambulances": "ambulances",
            "dewatering_pumps": "dewatering_pumps",
            "fire_trucks": "fire_trucks",
            "utility_crews": "utility_crews",
            "traffic_units": "traffic_units"
        }
        mapped_res = resource_map.get(required_resource, "utility_crews")
        
        closest_station = None
        min_distance_km = float('inf')
        estimated_travel_time_mins = 15
        
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        valid_stations = [s for s in self.ISLAMABAD_RESOURCE_STATIONS if mapped_res in s["resource_types"]]
        if not valid_stations:
            valid_stations = [self.ISLAMABAD_RESOURCE_STATIONS[0]]
            
        if api_key:
            try:
                destinations = "|".join([f"{s['lat']},{s['lng']}" for s in valid_stations])
                origins = f"{user_lat},{user_lng}"
                
                response = httpx.get(
                    "https://maps.googleapis.com/maps/api/distancematrix/json",
                    params={"origins": origins, "destinations": destinations, "key": api_key},
                    timeout=8.0
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK" and data.get("rows"):
                        elements = data["rows"][0].get("elements", [])
                        for idx, element in enumerate(elements):
                            if element.get("status") == "OK":
                                dist_val = element["distance"]["value"] / 1000.0 # meters to km
                                dur_val = element["duration"]["value"] / 60.0 # seconds to mins
                                
                                if dist_val < min_distance_km:
                                    min_distance_km = dist_val
                                    estimated_travel_time_mins = max(2, int(dur_val))
                                    closest_station = valid_stations[idx]
            except Exception as e:
                logging.warning(f"[MapsService] Google Distance Matrix API failed: {e}")
                
        if not closest_station:
            import math
            for station in valid_stations:
                lat1, lon1 = math.radians(user_lat), math.radians(user_lng)
                lat2, lon2 = math.radians(station["lat"]), math.radians(station["lng"])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                distance = 6371 * c
                if distance < min_distance_km:
                    min_distance_km = distance
                    closest_station = station
            estimated_travel_time_mins = max(5, int((min_distance_km / 35.0) * 60.0 + 3.0))
            
        return {
            "station_name": closest_station["name"],
            "station_address": closest_station["address"],
            "distance_km": round(min_distance_km, 2),
            "estimated_travel_time_mins": estimated_travel_time_mins,
            "resource_type": mapped_res
        }

    def get_nearby_hospitals(self, lat: float, lng: float) -> List[Dict]:
        """Return nearby hospitals using Google Places API Nearby Search if key is available."""
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if api_key:
            try:
                response = httpx.get(
                    "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                    params={
                        "location": f"{lat},{lng}",
                        "radius": "5000",
                        "type": "hospital",
                        "key": api_key
                    },
                    timeout=8.0
                )
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        hospitals = []
                        valid_results = results[:3]
                        destinations = "|".join([f"{h['geometry']['location']['lat']},{h['geometry']['location']['lng']}" for h in valid_results])
                        origins = f"{lat},{lng}"
                        
                        durations = {}
                        distances = {}
                        
                        try:
                            dist_resp = httpx.get(
                                "https://maps.googleapis.com/maps/api/distancematrix/json",
                                params={"origins": origins, "destinations": destinations, "key": api_key},
                                timeout=5.0
                            )
                            if dist_resp.status_code == 200:
                                dist_data = dist_resp.json()
                                if dist_data.get("status") == "OK" and dist_data.get("rows"):
                                    elements = dist_data["rows"][0].get("elements", [])
                                    for idx, element in enumerate(elements):
                                        if element.get("status") == "OK":
                                            distances[idx] = round(element["distance"]["value"] / 1000.0, 2)
                                            durations[idx] = max(1, int(element["duration"]["value"] / 60.0))
                        except Exception as de:
                            logging.warning(f"[MapsService] Distance Matrix for hospitals failed: {de}")
                            
                        for idx, h in enumerate(valid_results):
                            dist = distances.get(idx, 2.5)
                            dur = durations.get(idx, 10)
                            hospitals.append({
                                "name": h.get("name", "Medical Center"),
                                "distance_km": dist,
                                "estimated_travel_time_mins": dur,
                                "status": "OPERATIONAL" if h.get("business_status") == "OPERATIONAL" else "LIMITED"
                            })
                        return hospitals
            except Exception as e:
                logging.warning(f"[MapsService] Google Places API hospital search failed: {e}")
                
        city = self._infer_city(lat, lng)
        return self.HOSPITALS_BY_CITY.get(city, self.HOSPITALS_BY_CITY["Islamabad"])

    def calculate_closest_rescue_hub(self, user_lat: float, user_lng: float, rescue_resources: List[Dict]) -> Dict[str, Any]:
        """
        Find closest rescue station from the list using Google Maps Distance Matrix API.
        """
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        estimated_time = "15 to 20 minutes"
        nearest_resource = "Faizabad Rescue Hub"
        distance_str = "8.5 km"
        
        if api_key and rescue_resources:
            try:
                destinations = "|".join([f"{r['lat']},{r['lng']}" for r in rescue_resources])
                origins = f"{user_lat},{user_lng}"
                
                response = httpx.get(
                    "https://maps.googleapis.com/maps/api/distancematrix/json",
                    params={"origins": origins, "destinations": destinations, "key": api_key},
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK" and data.get("rows"):
                        elements = data["rows"][0].get("elements", [])
                        min_dist_val = float('inf')
                        closest_idx = 0
                        for idx, element in enumerate(elements):
                            if element.get("status") == "OK":
                                dist_val = element["distance"]["value"]
                                if dist_val < min_dist_val:
                                    min_dist_val = dist_val
                                    closest_idx = idx
                                    
                        element = elements[closest_idx]
                        if element.get("status") == "OK":
                            estimated_time = element["duration"]["text"]
                            nearest_resource = rescue_resources[closest_idx]["name"]
                            distance_str = element["distance"]["text"]
            except Exception as e:
                logging.warning(f"[MapsService] Google Distance Matrix calculation failed: {e}")
                
        return {
            "name": nearest_resource,
            "duration": estimated_time,
            "distance": distance_str
        }

    def get_context_for_analysis(self, lat: float, lng: float, location_text: str) -> Dict[str, Any]:
        """Returns full Maps context for Analysis Agent (FR-13) with calculated resource ETAs."""
        city = self._infer_city(lat, lng)
        hospitals = self.get_nearby_hospitals(lat, lng)
        
        # Calculate ETAs for all Islamabad resource types
        resource_etas = {}
        for r_type in ["ambulances", "dewatering_pumps", "fire_trucks", "utility_crews", "traffic_units"]:
            resource_etas[r_type] = self.calculate_islamabad_resource_eta(lat, lng, r_type)
            
        return {
            "geocoded_location": {"lat": lat, "lng": lng, "city": city, "address": location_text},
            "hospitals_within_5km": [h["name"] for h in hospitals[:2]],
            "nearest_hospital": hospitals[0] if hospitals else None,
            "nearby_infrastructure": self._get_infrastructure(city),
            "city": city,
            "resource_etas": resource_etas,
        }

    def _infer_city(self, lat: float, lng: float) -> str:
        if 33.5 < lat < 33.85 and 72.8 < lng < 73.25:
            return "Islamabad" if lng > 73.0 else "Rawalpindi"
        if 24.7 < lat < 25.1 and 66.8 < lng < 67.3:
            return "Karachi"
        if 31.3 < lat < 31.7 and 74.1 < lng < 74.6:
            return "Lahore"
        if 33.9 < lat < 34.1 and 71.4 < lng < 71.7:
            return "Peshawar"
        return "Islamabad"

    def _get_infrastructure(self, city: str) -> List[str]:
        infra = {
            "Islamabad": ["CDA Power Grid", "Islamabad Expressway", "Pakistan Secretariat", "F-6 Water Treatment"],
            "Karachi": ["K-Electric Grid", "Port Qasim", "Karachi Circular Railway", "Hub Power Plant"],
            "Lahore": ["WAPDA Grid Lahore", "Ring Road", "Lahore Metro Orange Line", "Ravi River Barrage"],
            "Rawalpindi": ["Rawalpindi Cantonment", "Chaklala Air Base", "Faizabad Interchange"],
            "Peshawar": ["Ring Road Peshawar", "Peshawar BRT", "Charsadda Road"],
        }
        return infra.get(city, infra["Islamabad"])


# Singleton instance
maps_service = MapsService()
